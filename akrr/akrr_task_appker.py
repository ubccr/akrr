import os
import datetime
import traceback
import re
import copy


import akrr.db
import akrr.util
import akrr.util.log
import akrr.util.ssh

from . import cfg
from .util import log

from .akrr_task_base import AkrrTaskHandlerBase, submit_commands, job_id_extract_patterns, wait_expressions, \
    active_task_default_attempt_repeat, kill_expressions

from akrr.appkernelsparsers.akrrappkeroutputparser import AppKerOutputParser

from .akrrerror import AkrrError


class AkrrTaskHandlerAppKer(AkrrTaskHandlerBase):
    """Task Handler for AppKernel execution and processing"""

    def __init__(self, task_id, resource_name, app_name, resource_param, app_param, task_param):
        super().__init__(task_id, resource_name, app_name, resource_param, app_param, task_param)

        self.ReportFormat = None
        self.nodesList = None

    def first_step(self):
        return self.create_batch_job_script_and_submit_it()

    def generate_batch_job_script(self):
        if self.JobScriptName is None:
            self.JobScriptName = self.get_job_script_name()

        # get walltime from DB
        dbdefaults = {}
        try:
            db, cur = akrr.db.get_akrr_db()

            cur.execute('''SELECT resource,app,resource_param,app_param FROM active_tasks
            WHERE task_id=%s ;''', (self.task_id,))
            raw = cur.fetchall()
            if len(raw) > 0:
                (resource, app, resource_param, app_param) = raw[0]

                cur.execute("""SELECT walllimit
                    FROM akrr_default_walllimit
                    WHERE resource=%s AND app=%s AND resource_param=%s AND app_param=%s """,
                            (resource, app, resource_param, app_param))
                raw = cur.fetchall()

                if len(raw) > 0:
                    dbdefaults['walllimit'] = raw[0][0]

            # db.commit()
            cur.close()
            del db
        except Exception as e:
            pass
            raise e
        # create job-script
        try:
            batchvars = {}
            appkernelOnResource = {}
            if 'appkernelOnResource' in self.app:
                if self.resourceName in self.app['appkernelOnResource']:
                    appkernelOnResource = self.app['appkernelOnResource'][self.resourceName]
                elif 'default' in self.app['appkernelOnResource']:
                    appkernelOnResource = self.app['appkernelOnResource']['default']

            # print "#"*80
            for di in [self.resource, self.app, appkernelOnResource, dbdefaults, self.resourceParam, self.appParam]:
                batchvars.update(di)

            # get autowalltime limit
            try:
                if 'autoWalltimeLimit' in batchvars and batchvars['autoWalltimeLimit'] == True:
                    print("\nautoWalltimeLimit is on, trying to estimate walltime limit...")
                    autoWalltimeLimitOverhead = 1.2
                    if 'autoWalltimeLimitOverhead' in batchvars:
                        autoWalltimeLimitOverhead = batchvars['autoWalltimeLimitOverhead'] + 1.0
                    # query last 20 executions of this appkernel on that resource with that node count

                    db, cur = akrr.db.get_akrr_db(True)

                    cur.execute('''SELECT resource,reporter,reporternickname,collected,status,walltime FROM akrr_xdmod_instanceinfo
                        WHERE  `resource`=%s AND `reporternickname` =  %s
                        ORDER BY  `akrr_xdmod_instanceinfo`.`collected` DESC 
                        LIMIT 0 , 20''', (self.resource['name'], "%s.%d" % (self.app['name'], batchvars['nnodes'])))

                    raw = cur.fetchall()

                    i = 0
                    lastFiveRunsSuccessfull = True
                    maxwalltime = 0.0
                    for r in raw:
                        if i < 5 and r['status'] == 0:
                            lastFiveRunsSuccessfull = False
                        if r['status'] == 1 and r['walltime'] > maxwalltime:
                            maxwalltime = r['walltime']
                        i += 1
                    if i < 5:
                        print("There are only %d previous run, need at least 5 for walltime limit autoset")
                    else:
                        if lastFiveRunsSuccessfull == False:
                            print("One of last 5 runs have failed. Would not use autoset.")
                        else:
                            print(
                                "Max walltime was %.1f s, will change walltime limit from %.1f minutes to %d minutes" % (
                                maxwalltime, batchvars['walllimit'],
                                int(autoWalltimeLimitOverhead * maxwalltime / 60.0 + 0.99)))
                            batchvars['walllimit'] = int((autoWalltimeLimitOverhead * maxwalltime / 60.0 + 0.99))
                    print()
                    cur.close()
                    del db
            except Exception as e:
                pass

            # calculate NNodes and NCores
            tmpNNodes = None
            tmpNCores = None
            if 'nnodes' in batchvars:
                tmpNNodes = batchvars['nnodes']
                tmpNCores = tmpNNodes * batchvars['ppn']
            else:
                tmpNCores = batchvars['ncores']
                if tmpNCores % batchvars['ppn'] == 0:
                    tmpNNodes = tmpNCores / batchvars['ppn']
                else:
                    tmpNNodes = (tmpNCores / batchvars['ppn']) + 1

            batchvars['akrrNCores'] = tmpNCores
            batchvars['akrrNNodes'] = tmpNNodes

            # Set batchvars remaps
            batchvars['akrrPPN'] = batchvars['ppn']
            batchvars['akrrNCoresToBorder'] = batchvars['akrrPPN'] * batchvars['akrrNNodes']
            batchvars['akrrTaskWorkingDir'] = self.remoteTaskDir
            batchvars['akrrWallTimeLimit'] = "%02d:%02d:00" % (
            int(batchvars['walllimit']) / 60, int(batchvars['walllimit']) % 60)
            # batchvars['localPATH']=akrrcfg.ssh_command(sh,"echo $PATH").strip()
            batchvars['akrrAppKerName'] = self.app['name']
            batchvars['akrrResourceName'] = self.resource['name']
            batchvars['akrrTimeStamp'] = self.timeStamp
            if batchvars['akrrNNodes'] == 1:
                batchvars['akrrPPN4NodesOrCores4OneNode'] = batchvars['akrrNCores']
            else:
                batchvars['akrrPPN4NodesOrCores4OneNode'] = batchvars['akrrPPN']

            if 'nodeListSetterTemplate' not in batchvars:
                batchvars['nodeListSetterTemplate'] = batchvars['nodeListSetter'][batchvars['batchScheduler']]
            # set AppKerLauncher
            # if 'runScript' in batchvars:
            #    if self.resource['name'] in batchvars['runScript']:
            #        batchvars['akrrStartAppKer']=akrrcfg.format_recursively(batchvars['runScript'][self.resource['name']],batchvars,keepDoubleBrakets=True)
            #    else:
            #        batchvars['akrrStartAppKer']=akrrcfg.format_recursively(batchvars['runScript']['default'],batchvars,keepDoubleBrakets=True)

            # process templates
            batchvars['akrrCommonCommands'] = akrr.util.format_recursively(batchvars['akrrCommonCommandsTemplate'], batchvars,
                                                                           keep_double_brackets=True)
            # batchvars['akrrCommonTests']=akrrcfg.format_recursively(batchvars['akrrCommonTestsTemplate'],batchvars,keepDoubleBrakets=True)
            # batchvars['akrrStartAppKer']=batchvars['akrrStartAppKerTemplate'].format(**batchvars)
            batchvars['akrrCommonCleanup'] = akrr.util.format_recursively(batchvars['akrrCommonCleanupTemplate'], batchvars,
                                                                          keep_double_brackets=True)

            # specially for IOR request two nodes for single node benchmark, one for read and one for write
            if batchvars['requestTwoNodesForOneNodeAppKer'] == True and batchvars[
                'akrrNNodes'] == 1 and 'batchJobHeaderTemplate' in batchvars:
                batchvars2 = copy.deepcopy(batchvars)
                batchvars2['akrrNCores'] = 2 * batchvars['akrrNCores']
                batchvars2['akrrNNodes'] = 2 * batchvars['akrrNNodes']
                batchvars2['akrrNCoresToBorder'] = 2 * batchvars['akrrNCoresToBorder']
                batchvars2['akrrPPN4NodesOrCores4OneNode'] = batchvars['akrrPPN']
                batchvars['batchJobHeaderTemplate'] = akrr.util.format_recursively(batchvars2['batchJobHeaderTemplate'],
                                                                                   batchvars2)
                pass

            # do parameters adjustment
            if 'process_params' in batchvars:
                batchvars['process_params'](batchvars)

            # generate job script
            jobScript = akrr.util.format_recursively(self.resource["batchJobTemplate"], batchvars)
            jobScriptFullPath = os.path.join(self.taskDir, "jobfiles", self.JobScriptName)
            fout = open(jobScriptFullPath, "w")
            fout.write(jobScript)
            fout.close()
        except Exception as e:
            self.status = "ERROR: Can not created batch job script"
            self.status_info = traceback.format_exc()
            akrr.util.log.log_traceback(self.status)
            raise e

    def create_batch_job_script_and_submit_it(self, doNotSubmitToQueue=False):
        self.JobScriptName = self.get_job_script_name(self.appName)
        print("### Creating batch job script and submitting it to remote machine")
        # as a current bypass will create a job script remotely and copy it here
        # get ssh to remote resource

        sh = None
        try:
            sh = akrr.util.ssh.ssh_resource(self.resource)

            # Create remote directories if needed
            def check_and_create_dir(self, sh, d):
                cmd = "if [ ! -d  \"%s\" ]\n then mkdir \"%s\"\n fi" % (d, d)
                akrr.util.ssh.ssh_command(sh, cmd)
                cmd = "if [ -d \"%s\" ]\n then \necho EXIST\n else echo DOESNOTEXIST\n fi" % (d)
                msg = akrr.util.ssh.ssh_command(sh, cmd)
                if msg.find("DOESNOTEXIST") >= 0:
                    raise AkrrError("Can not create directory %s on %s." % (d, self.resource['name']))

            # akrr_data
            check_and_create_dir(self, sh, self.resource['akrr_data'])
            # dir for app
            check_and_create_dir(self, sh, os.path.join(self.resource['akrr_data'], self.appName))
            # dir for task
            check_and_create_dir(self, sh, self.remoteTaskDir)
            # CheckAndCreateDir(self,sh,os.path.join(self.remoteTaskDir,"batchJob_pl"))

            # cd to remoteTaskDir
            akrr.util.ssh.ssh_command(sh, "cd %s" % (self.remoteTaskDir))

            # generate_batch_job_script
            self.generate_batch_job_script()

            msg = akrr.util.ssh.scp_to_resource(self.resource, os.path.join(self.taskDir, "jobfiles", self.JobScriptName),
                                                os.path.join(self.remoteTaskDir))
            if doNotSubmitToQueue:
                return
            ##akrrcfg.ssh_command_no_return(sh,"cat > %s << EOF1234567\n%s\nEOF1234567\n"%(self.JobScriptName,jobScript))
            akrr.util.ssh.ssh_command(sh, "cat %s " % (self.JobScriptName))

            # send to queue
            from string import Template
            JobID = 0
            if not 'masterTaskID' in self.taskParam:
                # i.e. submit to queue only if task is independent
                sendToQueue = Template(submit_commands[self.resource['batchScheduler']]).substitute(
                    scriptPath=self.JobScriptName)
                msg = akrr.util.ssh.ssh_command(sh, sendToQueue)
                matchObj = re.search(job_id_extract_patterns[self.resource['batchScheduler']], msg, re.M | re.S)

                if matchObj:
                    try:
                        JobID = int(matchObj.group(1))
                    except:
                        raise AkrrError("Can't get job id:\n" + msg)
                else:
                    raise AkrrError("Can't get job id:\n" + msg)

                # report
                if self.resource["gateway_reporting"]:
                    akrr.util.ssh.ssh_command(sh, "module load gateway-usage-reporting")
                    akrr.util.ssh.ssh_command(sh, r'gateway_submit_attributes -gateway_user ' + self.resource[
                        "gateway_user"] + r''' -submit_time "`date '+%F %T %:z'`" -jobid ''' + JobIDstr)

            akrr.util.ssh.ssh_command(sh, "echo %d > job.id" % (JobID))

            self.RemoteJobID = JobID
            self.TimeJobSubmetedToRemoteQueue = datetime.datetime.today()

            sh.sendline("exit")
            sh.close(force=True)
            del sh
            sh = None
            print("\nRemoteJobID=", self.RemoteJobID)
            print("copying files from remote machine")
            msg = akrr.util.ssh.scp_from_resource(self.resource, os.path.join(self.remoteTaskDir, "*"),
                                                  os.path.join(self.taskDir, "jobfiles"), "-r")

            # update DB time_submitted_to_queue
            db, cur = akrr.db.get_akrr_db()

            cur.execute('''UPDATE active_tasks
            SET time_submitted_to_queue=%s
            WHERE task_id=%s ;''', (datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"), self.task_id))

            cur.close()
            del db

            if 'masterTaskID' not in self.taskParam:
                # i.e. independent task
                self.set_method_to_run_next(
                    "check_the_job_on_remote_machine",
                    "Created batch job script and have submitted it to remote queue.",
                    "Remote job ID is %d" % self.RemoteJobID)

                # check first time in 1 minute
                return datetime.timedelta(days=0, hours=0, minutes=1)
            else:
                # i.e. this is subtask
                # i.e. dependent task
                self.set_method_to_run_next(
                    "check_the_job_on_remote_machine",
                    "Created batch job script.",
                    "Created batch job script. Waiting for master task to execute it.")

                # master task will update the time when it will finish task execution
                return datetime.timedelta(days=111 * 365)

        except Exception as e:
            if sh is not None:
                sh.sendline("exit")
                sh.close(force=True)
                del sh

            self.set_method_to_run_next(
                None, "ERROR Can not created batch job script and submit it to remote queue", traceback.format_exc())

            if cfg.max_fails_to_submit_to_the_queue >= 0:
                if hasattr(self, "fails_to_submit_to_the_queue"):
                    self.fails_to_submit_to_the_queue += 1
                    if (self.fails_to_submit_to_the_queue > cfg.max_fails_to_submit_to_the_queue or
                            (self.taskParam['test_run'] == True and self.fails_to_submit_to_the_queue >= 2)):
                        # Stop execution of the task and submit results to db
                        self.set_method_to_run_next("push_to_db")
                        resultFile = os.path.join(self.taskDir, "result.xml")
                        self.write_error_xml(resultFile)
                        return datetime.timedelta(seconds=3)
                else:
                    self.fails_to_submit_to_the_queue = 1
            else:
                self.fatal_errors_count += 1

            akrr.util.log.log_traceback(self.status)
            return cfg.repeat_after_fails_to_submit_to_the_queue

    def check_the_job_on_remote_machine(self):
        sh = None
        try:
            print("### Checking the job status on remote machine")
            from string import Template

            sh = akrr.util.ssh.ssh_resource(self.resource)

            # if it is subtask get master task id from job.id file (it should be replaced by master task)
            if self.RemoteJobID == 0:
                try:
                    print(self.remoteTaskDir)
                    self.RemoteJobID = int(
                        akrr.util.ssh.ssh_command(sh, "cat %s" % (os.path.join(self.remoteTaskDir, "job.id"))))
                except:
                    self.RemoteJobID = 0

            wE = wait_expressions[self.resource['batchScheduler']]
            cmd = Template(wE[0]).substitute(jobId=str(self.RemoteJobID))
            rege = Template(wE[2]).substitute(jobId=str(self.RemoteJobID))

            msg = akrr.util.ssh.ssh_command(sh, cmd)
            sh.sendline("exit")
            sh.close(force=True)
            del sh

            if self.RemoteJobID == 0:
                return active_task_default_attempt_repeat

            matchObj = wE[1](rege, msg, wE[3])
            if matchObj:
                print("Still in queue. Either waiting or running")
                if datetime.datetime.today() - self.TimeJobSubmetedToRemoteQueue > \
                        self.taskParam.get('MaxTimeInQueue', cfg.max_time_in_queue):
                    print("ERROR:")
                    print("Job exceeds the maximal time in queue (%s). And will be terminated." % (
                        str(self.taskParam.get('MaxTimeInQueue', cfg.max_time_in_queue))))
                    print("Removing job from remote queue.")
                    self.terminate()
                    print("copying files from remote machine")
                    akrr.util.ssh.scp_from_resource(self.resource, os.path.join(self.remoteTaskDir, "*"),
                                                    os.path.join(self.taskDir, "jobfiles"), "-r")
                    # print msg
                    print("Deleting all files from remote machine")
                    self.delete_remote_folder()

                    self.set_method_to_run_next(
                        "proccess_results",
                        "ERROR: Job exceeds the maximal time in queue (%s) and was terminated." %
                        str(self.taskParam.get('MaxTimeInQueue', cfg.max_time_in_queue)),
                        "Last Status report:\n" + msg)
                    self.ReportFormat = "Error"
                    # del self.RemoteJobID
                    return datetime.timedelta(seconds=3)

                self.set_method_to_run_next(None, "Still in queue. Either waiting or running", msg)
                return active_task_default_attempt_repeat

            print("Not in queue. Either exited with error or executed successfully.")
            print("copying files from remote machine")
            msg = akrr.util.ssh.scp_from_resource(self.resource, os.path.join(self.remoteTaskDir, "*"),
                                                  os.path.join(self.taskDir, "jobfiles"), "-r")
            # print msg
            print("Deleting all files from remote machine")
            self.delete_remote_folder()
            self.set_method_to_run_next(
                "proccess_results",
                "Not in queue. Either exited with error or executed successfully. "
                "Copied all files to local machine. Deleted all files from remote machine")
            # del self.RemoteJobID
            self.TimeJobPossiblyCompleted = datetime.datetime.today()
            return datetime.timedelta(seconds=3)
            # print msg
        except:
            if hasattr(locals(), 'sh') and sh is not None:
                sh.sendline("exit")
                sh.close(force=True)
                del sh
            self.set_method_to_run_next(
                None, "ERROR Can not check the status of the job on remote resource", traceback.format_exc())
            self.fatal_errors_count += 1
            akrr.util.log.log_traceback(self.status)
            return active_task_default_attempt_repeat

    def get_result_files(self, raiseError=False):
        jobfilesDir = os.path.join(self.taskDir, "jobfiles")
        batchJobDir = None
        stdoutFile = None
        stderrFile = None
        appstdoutFile = None
        taskexeclogFile = None

        for d in os.listdir(jobfilesDir):
            if re.match("batchJob", d):
                if batchJobDir == None:
                    batchJobDir = os.path.join(jobfilesDir, d)
                else:
                    if raiseError:
                        raise IOError("Error: found multiple batchJob* Directories although it should be one")
                    else:
                        return (batchJobDir, stdoutFile, stderrFile, appstdoutFile)

        if batchJobDir is not None:
            for f in os.listdir(batchJobDir):
                if re.match("sub.*\.stdout", f):
                    if stdoutFile == None:
                        stdoutFile = os.path.join(batchJobDir, f)
                    elif raiseError:
                        raise IOError("Error: found multiple sub*.stdout files although it should be one")
                if re.match("sub.*\.stderr", f):
                    if stderrFile == None:
                        stderrFile = os.path.join(batchJobDir, f)
                    elif raiseError:
                        raise IOError("Error: found multiple sub*.stderr files although it should be one")
                if re.match("sub.*\.appstdout", f):
                    if appstdoutFile == None:
                        appstdoutFile = os.path.join(batchJobDir, f)
                    elif raiseError:
                        raise IOError("Error: found multiple sub*.appstdout files although it should be one")
        else:
            batchJobDir = jobfilesDir
            for f in os.listdir(jobfilesDir):
                if re.match("stdout", f):
                    if stdoutFile == None:
                        stdoutFile = os.path.join(jobfilesDir, f)
                    elif raiseError:
                        raise IOError("Error: found multiple sub*.stdout files although it should be one")
                if re.match("stderr", f):
                    if stderrFile == None:
                        stderrFile = os.path.join(jobfilesDir, f)
                    elif raiseError:
                        raise IOError("Error: found multiple sub*.stderr files although it should be one")
                if re.match("appstdout", f):
                    if appstdoutFile == None:
                        appstdoutFile = os.path.join(jobfilesDir, f)
                    elif raiseError:
                        raise IOError("Error: found multiple sub*.appstdout files although it should be one")
            if os.path.isfile(os.path.join(self.taskDir, "proc", "log")):
                taskexeclogFile = os.path.join(self.taskDir, "proc", "log")
        if batchJobDir == None or stdoutFile == None or stderrFile == None:
            if raiseError: raise IOError(
                "Error: standard files is not present among job-files copied from remote resource.")
        return (batchJobDir, stdoutFile, stderrFile, appstdoutFile, taskexeclogFile)

    def proccess_results(self, Verbose=True):
        if 'parser' not in self.app:
            return self.proccess_results_old(Verbose)
        if Verbose: print("Processing the output")
        try:
            jobfilesDir = os.path.join(self.taskDir, "jobfiles")
            resultFile = os.path.join(self.taskDir, "result.xml")
            print(resultFile)
            # get job.id (from remote machine) of master node
            if self.RemoteJobID == 0:  # i.e. this is a subtask of a bundle
                if os.path.isfile(os.path.join(jobfilesDir, "job.id")):
                    fin = open(os.path.join(jobfilesDir, "job.id"), "r")
                    self.RemoteJobID = int(fin.read().strip())
                    print("Master task's RemoteJobID is ", self.RemoteJobID)
                    fin.close()

            if hasattr(self, 'ReportFormat'):  # i.e. fatal error and the last one is already in status/status_info
                if self.ReportFormat == "Error":
                    self.set_method_to_run_next("push_to_db")
                    self.write_error_xml(resultFile)
                    return datetime.timedelta(seconds=3)

            (batchJobDir, stdoutFile, stderrFile, appstdoutFile, taskexeclogFile) = self.get_result_files(raiseError=True)

            # get the performance data
            parserfilename = os.path.join(cfg.akrr_mod_dir, "appkernelsparsers", self.app['parser'])
            import imp
            with open(parserfilename, 'rb') as fp:
                thisAppKerParser = imp.load_module(
                    'thisAppKerParser', fp, parserfilename,
                    ('.py', 'rb', imp.PY_SOURCE)
                )

            appKerNResVars = {}
            appKerNResVars['resource'] = self.resource
            appKerNResVars['resource'].update(self.resourceParam)
            appKerNResVars['app'] = self.app
            appKerNResVars['app'].update(self.appParam)

            performance = thisAppKerParser.processAppKerOutput(appstdout=appstdoutFile,
                                                               stdout=stdoutFile,
                                                               stderr=stderrFile,
                                                               geninfo=os.path.join(batchJobDir, "gen.info"),
                                                               appKerNResVars=appKerNResVars)
            if performance is None:
                self.set_method_to_run_next("push_to_db", "ERROR: Job have not finished successfully", "")
                self.write_error_xml(resultFile)
            else:
                fout = open(resultFile, "w")
                content = fout.write(performance)
                fout.close()

                self.set_method_to_run_next(
                    "push_to_db",
                    "Output was processed and found that kernel either exited with error or executed successfully.",
                    "Done")
                if hasattr(performance, 'nodeList'):
                    self.nodesList = performance.nodeList
                else:
                    self.nodesList = None
            return datetime.timedelta(seconds=3)
        except:
            print(traceback.format_exc())
            self.set_method_to_run_next(
                "push_to_db", "ERROR: Error happens during processing of output.", traceback.format_exc())
            self.fatal_errors_count += 1
            akrr.util.log.log_traceback(self.status)
            self.write_error_xml(resultFile)
            return datetime.timedelta(seconds=3)

    def push_to_db(self, Verbose=True):

        db, cur = akrr.db.get_akrr_db()
        try:

            time_finished = None
            if hasattr(self, 'TimeJobPossiblyCompleted'):
                time_finished = self.TimeJobPossiblyCompleted
            else:
                time_finished = datetime.datetime.today()
            self.push_to_db_raw(cur, self.task_id, time_finished, Verbose)
            db.commit()
            cur.close()
            del db
            self.set_method_to_run_next("task_is_complete")
            return None
        except:
            print(traceback.format_exc())
            db.rollback()
            db.commit()
            cur.close()
            del db
            if hasattr(self, 'PushToDBAttemps'):
                self.PushToDBAttemps += 1
            else:
                self.PushToDBAttemps = 1

            if self.PushToDBAttemps <= cfg.export_db_max_repeat_attempts:
                akrr.util.log.log_traceback("AKRR server was not able to push to external DB.")
                self.status = "ERROR: Can not push to external DB, will try again"
                self.status_info = traceback.format_exc()
                return cfg.export_db_repeat_attempt_in
            else:
                akrr.util.log.log_traceback("AKRR server was not able to push to external DB will only update local.")
                self.set_method_to_run_next(
                    "task_is_complete", "ERROR: Can not push to external DB, will try again", traceback.format_exc())
                return None

    def push_to_db_raw(self, cur, task_id, time_finished, Verbose=True):
        print("Pushing to DB")

        resultFile = os.path.join(self.taskDir, "result.xml")
        jobfilesDir = os.path.join(self.taskDir, "jobfiles")
        (batchJobDir, stdoutFile, stderrFile, appstdoutFile, taskexeclogFile) = self.get_result_files()

        # sanity check
        fin = open(resultFile, "r")
        content = fin.read()
        fin.close()
        if content[0] != '<':
            # need to reformat
            i0 = content.find("<rep:report")
            i1 = content.find("</rep:report>")

            fout = open(resultFile, "w")
            content = fout.write("<?xml version='1.0'?>\n" + content[i0:i1 + len("</rep:report>")] + "\n")
            fout.close()

        import xml.etree.ElementTree as ET
        try:

            tree = ET.parse(resultFile)
            root = tree.getroot()
        except:
            self.set_method_to_run_next(
                None,
                "Cannot process final XML file",
                "(1)==Resulting XML file content==\n" + content +
                "\n==Previous status==" + self.status +
                "\n==Previous status info==" + self.status_info + "\n" +
                traceback.format_exc())
            self.write_error_xml(resultFile, cdata=True)

        instance_id = task_id
        collected = None
        committed = None
        resource = None
        executionhost = None
        reporter = None
        reporternickname = None
        status = None
        message = None
        stderr = None
        body = None
        memory = None
        cputime = None
        walltime = None
        memory = 0.0
        cputime = 0.0
        walltime = 0.0
        job_id = None

        cur.execute("""SELECT instance_id,collected,committed,resource,executionhost,reporter,reporternickname,status,message,stderr,body,memory,cputime,walltime,job_id
            FROM akrr_xdmod_instanceinfo WHERE instance_id=%s""", (task_id,))
        raw = cur.fetchone()
        if raw != None:  # .i.e. not new entry
            (instance_id, collected, committed, resource, executionhost, reporter, reporternickname, status, message,
             stderr, body, memory, cputime, walltime, job_id) = raw
            if hasattr(self, "RemoteJobID"): job_id = self.RemoteJobID
        else:
            collected = time_finished
            committed = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
            resource = self.resourceName
            executionhost = self.resource.get('__regexp__', self.resourceName)
            reporter = self.appName
            # reporternickname="%s.%d"%(self.appName,self.resourceParam['ncpus'])
            reporternickname = akrr.util.replace_at_var_at(self.app['nickname'],
                                                           [self.resource, self.app, self.resourceParam, self.appParam])

            if hasattr(self, "RemoteJobID"): job_id = self.RemoteJobID

        # Process XML file
        import xml.etree.ElementTree as ET
        root = None
        try:

            tree = ET.parse(resultFile)
            root = tree.getroot()
        except:
            self.status_info = "(2)==Resulting XML file content==\n" + content + \
                              "\n==Previous status==" + self.status + \
                              "\n==Previous status info==" + self.status_info
            self.status = "Cannot process final XML file"
            root = None

        memory = 0.0
        cputime = 0.0
        walltime = 0.0

        print("TTTTTTTT ", root, status)

        if root is not None:
            completed = None
            try:
                t = root.find('exitStatus').find('completed').text

                print('exitStatus:completed', t)

                if t.strip().upper() == "TRUE":
                    completed = True
                else:
                    completed = False

                if completed:
                    root.find('body').find('performance').find('benchmark').find('statistics')
                self.set_method_to_run_next(None, "Task was completed successfully.", "Done")
            except:
                pass

            print("TTTTTTTT completedstatus", completed, status)
            error = None
            try:

                t = root.find('xdtas').find('batchJob').find('status').text
                if t.upper() == "ERROR":
                    error = True
                else:
                    error = False
            except:
                pass

            status = 0
            if completed is not None:
                if completed:
                    status = 1

            print("TTTTTTTT completedstatus", completed, status)

            if completed is not None:
                if completed:
                    bodyET = root.find('body').find('performance')
                    body = ET.tostring(bodyET)
                    import xml.dom.minidom
                    xml = xml.dom.minidom.parseString(body)
                    body = xml.toprettyxml()
                    body = body.replace("""<?xml version="1.0" ?>\n""", "")

                    statisticsET = root.find('body').find('performance').find('benchmark').find('statistics')
                    for e in statisticsET:
                        if e.find('ID').text == 'Memory':
                            memory = float(e.find('value').text)
                        if e.find('ID').text == 'Wall Clock Time':
                            walltime = float(e.find('value').text)
                else:
                    # i.e. error caught by parser on resource
                    try:
                        message = "ERROR: error caught by parser"
                        stderr = root.find('exitStatus').find('errorMessage').text
                        body = """<xdtas>
      <batchJob>
       <status>Error</status>
       <errorCause>ERROR: error caught by parser</errorCause>
       <reporter>%s</reporter>
       <errorMsg>%s</errorMsg>
      </batchJob>
     </xdtas>
    """ % (reporter, stderr)
                    except:
                        message = "ERROR: error caught by parser"
                        stderr = None
                        body = """<xdtas>
      <batchJob>
       <status>Error</status>
       <errorCause>ERROR: error caught by parser</errorCause>
       <reporter>%s</reporter>
       <errorMsg></errorMsg>
      </batchJob>
     </xdtas>
    """ % (reporter)
            elif completed is None:
                if error is not None:  # i.e. xml with error generated afterwards
                    if error:
                        # fin=open(resultFile,"r")
                        # body=fin.read()
                        # fin.close
                        message = root.find('xdtas').find('batchJob').find('errorCause').text
                        stderr = root.find('xdtas').find('batchJob').find('errorMsg').text

                        bodyET = root.find('xdtas')
                        body = ET.tostring(bodyET)
                    else:
                        raise IOError("This condition should not happens")
                else:
                    raise IOError("This condition should not happens")
            else:
                raise IOError("This condition should not happens")
            # memory=None
            # cputime=None
            # walltime=None
        else:  # i.e. xml was not parsed
            status = 0
            message = self.status
            stderr = self.status_info
            body = """<xdtas>
      <batchJob>
       <status>Error</status>
       <errorCause>Unknown error</errorCause>
       <reporter>AKRR Server</reporter>
       <errorMsg>"Cannot process final XML file</errorMsg>
      </batchJob>
     </xdtas>
    """
        message = akrr.util.clean_unicode(message)
        stderr = akrr.util.clean_unicode(stderr)
        body = akrr.util.clean_unicode(body)

        # Get Nodes
        nodes = None
        nodesFileName = os.path.join(jobfilesDir, "gen.info")

        if os.path.isfile(nodesFileName):
            parser = AppKerOutputParser()
            parser.parseCommonParsAndStats(geninfo=nodesFileName)
            if hasattr(parser, 'geninfo') and 'nodeList' in parser.geninfo:
                nodesList = parser.geninfo['nodeList'].split()
                nodes = ";"
                for line in nodesList:
                    line = line.strip()
                    nodes += "%s;" % (line)
                if len(nodes.strip().strip(';')) == 0:
                    nodes = None

        internal_failure_code = 0
        if 'masterTaskID' in self.taskParam and appstdoutFile == None:
            internal_failure_code = 10004
        log.debug("completedstatus", completed, status)
        if raw is not None:  # .i.e. new entry
            print("Updating")
            cur.execute("""UPDATE akrr_xdmod_instanceinfo
SET instance_id=%s,collected=%s,committed=%s,resource=%s,executionhost=%s,reporter=%s,
reporternickname=%s,status=%s,message=%s,stderr=%s,body=%s,memory=%s,cputime=%s,walltime=%s,job_id=%s,nodes=%s,internal_failure=%s
WHERE instance_id=%s""",
                        (instance_id, collected, committed, resource, executionhost, reporter, reporternickname, status,
                         message, stderr, body, memory, cputime, walltime, job_id, nodes, internal_failure_code,
                         instance_id))
            # (instance_id,collected,committed,resource,executionhost,reporter,reporternickname,status,message,stderr,body,memory,cputime,walltime)=raw
        else:
            cur.execute("""INSERT INTO akrr_xdmod_instanceinfo
(instance_id,collected,committed,resource,executionhost,reporter,reporternickname,status,message,stderr,body,memory,cputime,walltime,job_id,nodes,internal_failure)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                        (instance_id, collected, committed, resource, executionhost, reporter, reporternickname, status,
                         message, stderr, body, memory, cputime, walltime, job_id, nodes, internal_failure_code))

        # print appstdoutFile,stdoutFile,stderrFile
        appstdoutFileContent = None
        stdoutFileContent = None
        stderrFileContent = None
        taskexeclogFileContent = None
        if appstdoutFile != None:
            fin = open(appstdoutFile, "r")
            appstdoutFileContent = fin.read()
            fin.close()
        else:
            appstdoutFileContent = "Does Not Present"
        if stdoutFile != None:
            fin = open(stdoutFile, "r")
            stdoutFileContent = fin.read()
            fin.close()
        else:
            stdoutFileContent = "Does Not Present"
        if stderrFile != None:
            fin = open(stderrFile, "r")
            stderrFileContent = fin.read()
            fin.close()
        else:
            stderrFileContent = "Does Not Present"

        if taskexeclogFile != None:
            fin = open(taskexeclogFile, "r")
            taskexeclogFileContent = fin.read()
            fin.close()
        else:
            taskexeclogFileContent = "Does Not Present"

        cur.execute("""SELECT task_id
            FROM akrr_errmsg WHERE task_id=%s""", (task_id,))
        raw = cur.fetchall()

        cur.execute("""SELECT @@max_allowed_packet""")
        max_allowed_packet = cur.fetchall()[0][0]

        if (len(appstdoutFileContent) + len(stderrFileContent) + len(stdoutFileContent) + len(
                taskexeclogFileContent)) > 0.9 * max_allowed_packet:
            print("WARNING: length of files exceed max_allowed_packet will trancate files")

            if len(appstdoutFileContent) > 0.2 * max_allowed_packet:
                appstdoutFileContent = appstdoutFileContent[:int(0.2 * max_allowed_packet)]
                appstdoutFileContent += "\nWARNING: File was trancated because it length of files exceed max_allowed_packet\n"
            if len(stderrFileContent) > 0.2 * max_allowed_packet:
                stderrFileContent = stderrFileContent[:int(0.2 * max_allowed_packet)]
                stderrFileContent += "\nWARNING: File was trancated because it length of files exceed max_allowed_packet\n"
            if len(stdoutFileContent) > 0.2 * max_allowed_packet:
                stdoutFileContent = stdoutFileContent[:int(0.2 * max_allowed_packet)]
                stdoutFileContent += "\nWARNING: File was trancated because it length of files exceed max_allowed_packet\n"
            if len(taskexeclogFileContent) > 0.2 * max_allowed_packet:
                taskexeclogFileContent = taskexeclogFileContent[:int(0.2 * max_allowed_packet)]
                taskexeclogFileContent += "\nWARNING: File was trancated because it length of files exceed max_allowed_packet\n"

        appstdoutFileContent = akrr.util.clean_unicode(appstdoutFileContent)
        stderrFileContent = akrr.util.clean_unicode(stderrFileContent)
        stdoutFileContent = akrr.util.clean_unicode(stdoutFileContent)
        taskexeclogFileContent = akrr.util.clean_unicode(taskexeclogFileContent)

        if len(raw) > 0:  # .i.e. updating existing entry
            print("Updating", raw)
            cur.execute("""UPDATE akrr_errmsg
                SET appstdout=%s,stderr=%s,stdout=%s,taskexeclog=%s
                WHERE task_id=%s""",
                        ((appstdoutFileContent), (stderrFileContent), (stdoutFileContent), taskexeclogFileContent,
                         instance_id))
        else:
            cur.execute("""INSERT INTO akrr_errmsg
                (task_id,appstdout,stderr,stdout,taskexeclog)
                VALUES (%s,%s,%s,%s,%s)""",
                        (instance_id, (appstdoutFileContent), (stderrFileContent), (stdoutFileContent),
                         taskexeclogFileContent))
        # (instance_id,akrrcfg.clean_unicode(appstdoutFileContent),akrrcfg.clean_unicode(stderrFileContent),akrrcfg.clean_unicode(stdoutFileContent)))

    def task_is_complete(self):
        print("Done", self.taskDir)
        self.set_method_to_run_next("task_is_complete", "Done", "Done")
        return None

    def terminate(self):
        #
        CanBeSafelyRemoved = False
        if not hasattr(self, "RemoteJobID"):
            # i.e. not running remotely and everything is on local disk
            CanBeSafelyRemoved = True
        else:
            #
            if self.remove_task_from_remote_queue() == None:
                # i.e. "Task is probably removed from remote queue.":
                CanBeSafelyRemoved = True
        if CanBeSafelyRemoved:
            # remove remote directory
            pass
        return CanBeSafelyRemoved

    def remove_task_from_remote_queue(self):
        sh = None
        try:
            from string import Template
            kE = kill_expressions[self.resource['batchScheduler']]
            cmd = Template(kE[0]).substitute(jobId=str(self.RemoteJobID))
            msg = akrr.util.ssh.ssh_resource(self.resource, cmd)
            print(msg)
            self.set_method_to_run_next(
                "task_is_complete", "Task is probably removed from remote queue.", copy.deepcopy(msg))
            return None
        except:
            if sh is not None:
                sh.sendline("exit")
                sh.close(force=True)
                del sh
            self.set_method_to_run_next(
                None, "ERROR Can not remove job from queue on remote resource", traceback.format_exc())
            self.fatal_errors_count += 1
            print(traceback.format_exc())
            return active_task_default_attempt_repeat