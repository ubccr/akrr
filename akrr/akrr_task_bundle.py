import akrr.db
import akrr.util
import akrr.util.log
import akrr.util.ssh
from . import cfg
import os
import sys
# namdSizes
import datetime
import time
import traceback
import re
import copy
import random

from .akrrerror import AkrrError

from .akrr_task_base import AkrrTaskHandlerBase, submit_commands, job_id_extract_patterns, wait_expressions, \
    active_task_default_attempt_repeat, kill_expressions


class akrrTaskHandlerBundle(AkrrTaskHandlerBase):
    """Task Handler for Bundled tasks"""

    def __init__(self, task_id, resource_name, app_name, resource_param, app_param, task_param):
        super().__init__(task_id, resource_name, app_name, resource_param, app_param, task_param)

        self.subTasksId = []

    def first_step(self):
        #
        self.subTasksId = []
        # self.status="FirstStep2"
        # self.status_info="FirstStep2"
        # self.ToDoNextString="FirstStep2"
        # return datetime.timedelta(days=0, hours=0, minutes=1)
        return self.check_if_subtasks_created_job_scripts()

    def get_sub_task_info(self):
        db, cur = akrr.db.get_akrr_db()

        cur.execute('''SELECT task_id,status,datetime_stamp,resource,app,task_param FROM active_tasks
                    WHERE task_param LIKE %s AND task_param LIKE '%%masterTaskID%%'
                    ORDER BY  task_id ASC 
                    ''', ("%%%d%%" % (self.task_id,),))
        raws = cur.fetchall()
        subTaskInfo = []
        for task_id, status, datetime_stamp, resource, app, task_param in raws:
            task_param = eval(task_param)
            if task_param['masterTaskID'] == self.task_id:
                subTaskInfo.append([task_id, status, datetime_stamp, resource, app, task_param])

        cur.close()
        del db
        return subTaskInfo

    def check_if_subtasks_created_job_scripts(self):
        print("check_if_subtasks_created_job_scripts")
        # Get current status of subtasks
        subTaskInfo = self.get_sub_task_info()

        subTasksHaveCreatedJobScripts = True

        self.status_info = ""
        for task_id, status, datetime_stamp, resource, app, task_param in subTaskInfo:
            self.status_info += "%d:%s\n" % (task_id, status)
            if status != None:
                if status.count("Created batch job script") == 0:
                    subTasksHaveCreatedJobScripts = False
            else:
                subTasksHaveCreatedJobScripts = False

        # Save subtasksid
        self.subTasksId = []
        for task_id, status, datetime_stamp, resource, app, task_param in subTaskInfo:
            self.subTasksId.append(task_id)

        if subTasksHaveCreatedJobScripts:
            self.status = "Subtasks have created job scripts."
            # self.status_info="Waiting for subtasks to create job scripts"
            self.ToDoNextString = "create_batch_job_script_and_submit_it"
            # check  in 1 minute
            return datetime.timedelta(days=0, hours=0, minutes=1)
        else:
            self.status = "Waiting for subtasks to create job scripts"
            # self.status_info="Waiting for subtasks to create job scripts"
            self.ToDoNextString = "check_if_subtasks_created_job_scripts"
            # check  in 1 minute
            return datetime.timedelta(days=0, hours=0, minutes=1)

    def create_batch_job_script_and_submit_it(self):
        self.JobScriptName = self.appName + ".job"
        print("### Creating batch job script and submitting it to remote machine")

        # as a current bypass will create a job script remotely and copy it here
        # get ssh to remote resource

        sh = None
        try:
            sh = akrr.util.ssh.ssh_resource(self.resource)

            # Create remote directories if needed
            def CheckAndCreateDir(self, sh, d):
                cmd = "if [ ! -d  \"%s\" ]\n then mkdir \"%s\"\n fi" % (d, d)
                akrr.util.ssh.ssh_command(sh, cmd)
                cmd = "if [ -d \"%s\" ]\n then \necho EXIST\n else echo DOESNOTEXIST\n fi" % (d)
                msg = akrr.util.ssh.ssh_command(sh, cmd)
                if msg.find("DOESNOTEXIST") >= 0:
                    raise AkrrError("Can not create directory %s on %s." % (d, self.resource['name']))

            # akrr_data
            CheckAndCreateDir(self, sh, self.resource['akrr_data'])
            # dir for app
            CheckAndCreateDir(self, sh, os.path.join(self.resource['akrr_data'], self.appName))
            # dir for task
            CheckAndCreateDir(self, sh, self.remoteTaskDir)
            # CheckAndCreateDir(self,sh,os.path.join(self.remoteTaskDir,"batchJob_pl"))

            # cd to remoteTaskDir
            akrr.util.ssh.ssh_command(sh, "cd %s" % (self.remoteTaskDir))

            # get walltime from DB
            dbdefaults = {}
            try:
                db, cur = akrr.db.get_akrr_db()

                cur.execute('''SELECT resource,app,resource_param,app_param FROM active_tasks
                WHERE task_id=%s ;''', (self.task_id,))
                raw = cur.fetchall()
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

            # create job-script
            batchvars = {}

            # print "#"*80
            for di in [self.resource, self.app, dbdefaults, self.resourceParam, self.appParam]:
                batchvars.update(di)

            # stack the subtasks
            subTaskInfo = self.get_sub_task_info()
            if batchvars['shuffleSubtasks']:
                random.shuffle(subTaskInfo)
            subTasksExecution = ""
            for subtask_id, subtask_status, subtask_datetime_stamp, subtask_resource, subtask_app, subtask_task_param in subTaskInfo:
                remoteSubTaskDir = self.get_remote_task_dir(self.resource['akrr_data'], subtask_app, subtask_datetime_stamp)
                SubTaskJobScriptName = self.get_job_script_name(subtask_app)
                SubTaskJobScriptPath = os.path.join(remoteSubTaskDir, SubTaskJobScriptName)

                subTasksExecution += "cd " + remoteSubTaskDir + "\n"
                # subTasksExecution+="cp "+os.path.join(self.remoteTaskDir,"job.id ")+"./\n"
                subTasksExecution += "echo Starting " + subtask_app + "\n"
                subTasksExecution += self.resource['shell'] + " " + SubTaskJobScriptPath + " > stdout 2> stderr\n"
                subTasksExecution += "echo Done with " + subtask_app + "\n" + "\n"

            batchvars['subTasksExecution'] = subTasksExecution

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
            batchvars['localPATH'] = akrr.util.ssh.ssh_command(sh, "echo $PATH").strip()
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
            # if self.resource['name'] in batchvars['runScript']:
            #    batchvars['akrrStartAppKer']=akrrcfg.format_recursively(batchvars['runScript'][self.resource['name']],batchvars,keepDoubleBrakets=True)
            # else:
            #    batchvars['akrrStartAppKer']=akrrcfg.format_recursively(batchvars['runScript']['default'],batchvars,keepDoubleBrakets=True)

            # process templates
            batchvars['akrrCommonCommands'] = akrr.util.format_recursively(batchvars['akrrCommonCommandsTemplate'], batchvars,
                                                                           keep_double_brackets=True)
            # batchvars['akrrCommonTests']=akrrcfg.format_recursively(batchvars['akrrCommonTestsTemplate'],batchvars,keepDoubleBrakets=True)
            # batchvars['akrrStartAppKer']=batchvars['akrrStartAppKerTemplate'].format(**batchvars)
            batchvars['akrrCommonCleanup'] = akrr.util.format_recursively(batchvars['akrrCommonCleanupTemplate'], batchvars,
                                                                          keep_double_brackets=True)

            # do parameters adjustment
            if 'process_params' in batchvars:
                batchvars['process_params'](batchvars)
            # generate job script
            jobScript = akrr.util.format_recursively(self.resource["batchJobTemplate"], batchvars)
            fout = open(os.path.join(self.taskDir, "jobfiles", self.JobScriptName), "w")
            fout.write(jobScript)
            fout.close()
            msg = akrr.util.ssh.scp_to_resource(self.resource, os.path.join(self.taskDir, "jobfiles", self.JobScriptName),
                                                os.path.join(self.remoteTaskDir))

            ##akrrcfg.ssh_command_no_return(sh,"cat > %s << EOF1234567\n%s\nEOF1234567\n"%(self.JobScriptName,jobScript))
            akrr.util.ssh.ssh_command(sh, "cat %s " % (self.JobScriptName))

            # send to queue
            from string import Template
            sendToQueue = Template(submit_commands[self.resource['batchScheduler']]).substitute(
                scriptPath=self.JobScriptName)
            msg = akrr.util.ssh.ssh_command(sh, sendToQueue)
            matchObj = re.search(job_id_extract_patterns[self.resource['batchScheduler']], msg, re.M | re.S)

            JobID = None
            if matchObj:
                try:
                    JobID = int(matchObj.group(1))
                except:
                    raise AkrrError("Can't get job id. " + msg)
            else:
                raise AkrrError("Can't get job id. " + msg)

            akrr.util.ssh.ssh_command(sh, "echo %d > job.id" % (JobID))

            # cp job id to subtasks
            for subtask_id, subtask_status, subtask_datetime_stamp, subtask_resource, subtask_app, subtask_task_param in subTaskInfo:
                remoteSubTaskDir = self.get_remote_task_dir(self.resource['akrr_data'], subtask_app, subtask_datetime_stamp)
                akrr.util.ssh.ssh_command(sh, "cp job.id %s" % (remoteSubTaskDir))

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

            self.status = "Created batch job script and have submitted it to remote queue."
            self.status_info = "Remote job ID is %d" % (self.RemoteJobID)
            self.ToDoNextString = "check_the_job_on_remote_machine"

            # check first time in 1 minute
            return datetime.timedelta(days=0, hours=0, minutes=1)
        except Exception as e:
            if sh != None:
                sh.sendline("exit")
                sh.close(force=True)
                del sh
            self.status = "ERROR Can not created batch job script and submit it to remote queue"
            self.status_info = traceback.format_exc()
            if cfg.max_fails_to_submit_to_the_queue >= 0:
                if hasattr(self, "fails_to_submit_to_the_queue"):
                    self.fails_to_submit_to_the_queue += 1
                    if self.fails_to_submit_to_the_queue > cfg.max_fails_to_submit_to_the_queue:
                        # Stop execution of the task and submit results to db
                        self.ToDoNextString = "push_to_db"
                        resultFile = os.path.join(self.taskDir, "result.xml")
                        self.write_error_xml(resultFile)
                        return datetime.timedelta(seconds=3)
                else:
                    self.fails_to_submit_to_the_queue = 1
            else:
                self.fatal_errors_count += 1

            akrr.util.log.log_traceback(self.status)
            return cfg.RepeateAfterfails_to_submit_to_the_queue

    def update_sub_tasks(self):
        # force to check SubTasks
        # stack the subtasks
        subTaskInfo = self.get_sub_task_info()

        db, cur = akrr.db.get_akrr_db()

        for subtask_id, subtask_status, subtask_datetime_stamp, subtask_resource, subtask_app, subtask_task_param in subTaskInfo:
            cur.execute('''UPDATE active_tasks
                            SET next_check_time=%s
                            WHERE task_id=%s ;''', (datetime.datetime.today(), subtask_id))

        db.commit()
        cur.close()
        del db

    def check_the_job_on_remote_machine(self):
        sh = None
        try:
            print("### Checking the job status on remote machine")
            from string import Template
            wE = wait_expressions[self.resource['batchScheduler']]
            cmd = Template(wE[0]).substitute(jobId=str(self.RemoteJobID))
            rege = Template(wE[2]).substitute(jobId=str(self.RemoteJobID))

            sh = akrr.util.ssh.ssh_resource(self.resource)
            msg = akrr.util.ssh.ssh_command(sh, cmd)
            sh.sendline("exit")
            sh.close(force=True)
            del sh
            sh = None

            matchObj = wE[1](rege, msg, wE[3])
            if matchObj:
                print("Still in queue. Either waiting or running")
                if datetime.datetime.today() - self.TimeJobSubmetedToRemoteQueue > self.taskParam.get('MaxTimeInQueue',
                                                                                                      cfg.max_time_in_queue):
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
                    self.status = "ERROR: Job exceeds the maximal time in queue (%s) and was terminated." % (
                        str(self.taskParam.get('MaxTimeInQueue', cfg.max_time_in_queue)))
                    self.status_info = "\nLast Status report:\n" + msg
                    self.ReportFormat = "Error"
                    self.ToDoNextString = "check_if_subtasks_done_proccessing_results"

                    self.update_sub_tasks()
                    # del self.RemoteJobID
                    return datetime.timedelta(seconds=3)

                self.status = "Still in queue. Either waiting or running"
                self.status_info = msg
                return active_task_default_attempt_repeat
            else:
                print("Not in queue. Either exited with error or executed successfully.")
                print("copying files from remote machine")
                msg = akrr.util.ssh.scp_from_resource(self.resource, os.path.join(self.remoteTaskDir, "*"),
                                                      os.path.join(self.taskDir, "jobfiles"), "-r")
                # print msg
                print("Deleting all files from remote machine")
                self.delete_remote_folder()
                self.status = "Not in queue. Either exited with error or executed successfully. Copied all files to local machine. Deleted all files from remote machine"
                self.status_info = "Not in queue. Either exited with error or executed successfully. Copied all files to local machine. Deleted all files from remote machine"
                self.ToDoNextString = "check_if_subtasks_done_proccessing_results"
                self.update_sub_tasks()
                # del self.RemoteJobID
                self.TimeJobPossiblyCompleted = datetime.datetime.today()
                return datetime.timedelta(seconds=3)
            # print msg
        except:
            if sh != None:
                sh.sendline("exit")
                sh.close(force=True)
                del sh
            self.status = "ERROR Can not check the status of the job on remote resource"
            self.status_info = traceback.format_exc()
            self.fatal_errors_count += 1
            akrr.util.log.log_traceback(self.status)
            self.ToDoNextString = "check_the_job_on_remote_machine"
            return active_task_default_attempt_repeat
        self.status = "check_the_job_on_remote_machine"
        self.status_info = "check_the_job_on_remote_machine"
        self.ToDoNextString = "check_the_job_on_remote_machine"
        return datetime.timedelta(days=0, hours=0, minutes=2)

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

        if batchJobDir != None:
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

    def check_if_subtasks_done_proccessing_results(self):
        subTaskInfo = self.get_sub_task_info()
        if len(subTaskInfo) == 0:
            self.status = "Subtasks are done with proccessing results"
            self.status_info = "Subtasks are done with proccessing results"
            self.ToDoNextString = "proccess_results"
            return datetime.timedelta(seconds=3)
        else:
            self.status = "Waiting for subtasks to proccess results"
            self.status_info = "Waiting for subtasks to proccess results"
            return datetime.timedelta(minutes=5)

    def proccess_results(self, Verbose=True):
        if Verbose: print("Processing the output")
        try:
            jobfilesDir = os.path.join(self.taskDir, "jobfiles")
            resultFile = os.path.join(self.taskDir, "result.xml")

            if hasattr(self, 'ReportFormat'):  # i.e. fatal error and the last one is already in status/status_info
                if self.ReportFormat == "Error":
                    self.ToDoNextString = "push_to_db"
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
            appKerNResVars['taskId'] = self.task_id
            appKerNResVars['subTasksId'] = self.subTasksId

            performance = thisAppKerParser.processAppKerOutput(appstdout=appstdoutFile,
                                                               geninfo=os.path.join(batchJobDir, "gen.info"),
                                                               appKerNResVars=appKerNResVars)
            if performance == None:
                self.status = "ERROR: Job have not finished successfully"
                self.status_info = ""
                self.ToDoNextString = "push_to_db"
                self.write_error_xml(resultFile)
            else:
                fout = open(resultFile, "w")
                content = fout.write(performance)
                fout.close()
                self.status = "Output was processed and found that kernel either exited with error or executed successfully."
                self.status_info = "Done"
                self.ToDoNextString = "push_to_db"
            return datetime.timedelta(seconds=3)
        except:
            print(traceback.format_exc())
            self.status = "ERROR: Error happens during processing of output."
            self.status_info = traceback.format_exc()
            self.fatal_errors_count += 1
            akrr.util.log.log_traceback(self.status)
            self.ToDoNextString = "push_to_db"
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
            self.ToDoNextString = "task_is_complete"
            return None
        except:
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
                self.status = "ERROR: Can not push to external DB, will try again"
                self.status_info = traceback.format_exc()
                self.ToDoNextString = "task_is_complete"
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
            self.status_info = "(1)==Resulting XML file content==\n" + content + \
                              "\n==Previous status==" + self.status + \
                              "\n==Previous status info==" + self.status_info + "\n" + \
                              traceback.format_exc()
            self.status = "Cannot process final XML file"
            self.write_error_xml(resultFile, bCDATA=True)

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

        if root != None:
            completed = None
            try:
                t = root.find('exitStatus').find('completed').text

                if t.upper() == "TRUE":
                    completed = True
                else:
                    completed = False

                if completed:
                    root.find('body').find('performance').find('benchmark').find('statistics')
                self.status = "Task was completed successfully."
                self.status_info = "Done"
            except:
                completed = None

            error = None
            try:

                t = root.find('xdtas').find('batchJob').find('status').text
                if t.upper() == "ERROR":
                    error = True
                else:
                    error = False
            except:
                error = None

            status = 0
            if completed != None:
                if completed:
                    status = 1

            if completed != None:
                if completed == True:
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
            elif completed == None:
                if error != None:  # i.e. xml with error generated afterwards
                    if error == True:
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
        nodesFileName = os.path.join(jobfilesDir, "nodes")
        if (os.path.isfile(nodesFileName)):
            parser = AppKerOutputParser()
            parser.parseCommonParsAndStats(geninfo=geninfo)
            nodes = ";"
            for line in parser.nodesList:
                line = line.strip()
                nodes += "%s;" % (line)
            if len(nodes.strip().strip(';')) == 0:
                nodes = None

        import xml.dom.minidom
        # print "#"*120
        # print resultFile
        # print instance_id,collected,committed,resource,executionhost,reporter,reporternickname,status,message,stderr,memory,cputime,walltime
        # print body
        # cur.execute("""SELECT * FROM akrr_xdmod_instanceinfo WHERE instance_id=%s""",(task_id,))
        if raw != None:  # .i.e. new entry
            print("Updating")
            cur.execute("""UPDATE akrr_xdmod_instanceinfo
SET instance_id=%s,collected=%s,committed=%s,resource=%s,executionhost=%s,reporter=%s,
reporternickname=%s,status=%s,message=%s,stderr=%s,body=%s,memory=%s,cputime=%s,walltime=%s,job_id=%s,nodes=%s
WHERE instance_id=%s""",
                        (instance_id, collected, committed, resource, executionhost, reporter, reporternickname, status,
                         message, stderr, body, memory, cputime, walltime, job_id, nodes,
                         instance_id))
            # (instance_id,collected,committed,resource,executionhost,reporter,reporternickname,status,message,stderr,body,memory,cputime,walltime)=raw
        else:
            cur.execute("""INSERT INTO akrr_xdmod_instanceinfo
(instance_id,collected,committed,resource,executionhost,reporter,reporternickname,status,message,stderr,body,memory,cputime,walltime,job_id,nodes)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                        (instance_id, collected, committed, resource, executionhost, reporter, reporternickname, status,
                         message, stderr, body, memory, cputime, walltime, job_id, nodes))

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

        cur.execute("""INSERT INTO akrr_errmsg
        (task_id,appstdout,stderr,stdout,taskexeclog)
        VALUES (%s,%s,%s,%s,%s)""",
                    (instance_id, (appstdoutFileContent), (stderrFileContent), (stdoutFileContent),
                     taskexeclogFileContent))
        # (instance_id,akrrcfg.clean_unicode(appstdoutFileContent),akrrcfg.clean_unicode(stderrFileContent),akrrcfg.clean_unicode(stdoutFileContent)))

    def task_is_complete(self):
        print("Done", self.taskDir)
        self.status = "Done"
        self.status_info = "Done"
        self.ToDoNextString = "task_is_complete"
        return None

    def terminate(self):
        #
        CanBeSafelyRemoved = False
        if not hasattr(self, "RemoteJobID"):
            # i.e. not running remotely and everything is on local disk
            CanBeSafelyRemoved = True
        else:
            #
            if self.remove_task_from_remote_queue() is None:
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
            self.status = "Task is probably removed from remote queue."
            self.status_info = copy.deepcopy(msg)
            self.ToDoNextString = "task_is_complete"
            return None
        except:
            if sh != None:
                sh.sendline("exit")
                sh.close(force=True)
                del sh
            self.status = "ERROR Can not remove job from queue on remote resource"
            self.status_info = traceback.format_exc()
            self.fatal_errors_count += 1
            print(traceback.format_exc())
            return active_task_default_attempt_repeat
