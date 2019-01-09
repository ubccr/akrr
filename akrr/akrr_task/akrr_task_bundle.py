import akrr.db
import akrr.util
import akrr.util.log as log
from akrr.util.ssh import check_dir, ssh_resource, scp_from_resource, ssh_command, scp_to_resource
from .. import cfg
import os
import datetime
import traceback
import re
import copy
import random

from akrr.parsers.akrrappkeroutputparser import AppKerOutputParser

from ..akrrerror import AkrrError

from .akrr_task_base import AkrrTaskHandlerBase, submit_commands, job_id_extract_patterns, wait_expressions, \
    active_task_default_attempt_repeat, kill_expressions


from MySQLdb import MySQLError


class AkrrTaskHandlerBundle(AkrrTaskHandlerBase):
    """Task Handler for Bundled tasks"""

    def __init__(self, task_id, resource_name, app_name, resource_param, app_param, task_param):
        super().__init__(task_id, resource_name, app_name, resource_param, app_param, task_param)

        self.subTasksId = []

        self.RemoteJobID = None
        self.TimeJobSubmetedToRemoteQueue = None
        self.fails_to_submit_to_the_queue = 0
        self.ReportFormat = None
        self.TimeJobPossiblyCompleted = None
        self.ToDoNextString = None

        self.PushToDBAttemps = 0

        self.RemoteJobID = None

    def first_step(self):
        return self.check_if_subtasks_created_job_scripts()

    def get_sub_task_info(self):
        db, cur = akrr.db.get_akrr_db()

        cur.execute('''SELECT task_id,status,datetime_stamp,resource,app,task_param FROM active_tasks
                    WHERE task_param LIKE %s AND task_param LIKE '%%masterTaskID%%'
                    ORDER BY  task_id ASC 
                    ''', ("%%%d%%" % (self.task_id,),))
        raws = cur.fetchall()
        sub_task_info = []
        for task_id, status, datetime_stamp, resource, app, task_param in raws:
            task_param = eval(task_param)
            if task_param['masterTaskID'] == self.task_id:
                sub_task_info.append([task_id, status, datetime_stamp, resource, app, task_param])

        cur.close()
        del db
        return sub_task_info

    def check_if_subtasks_created_job_scripts(self):
        print("check_if_subtasks_created_job_scripts")
        # Get current status of subtasks
        sub_task_info = self.get_sub_task_info()

        sub_tasks_have_created_job_scripts = True

        self.status_info = ""
        for task_id, status, datetime_stamp, resource, app, task_param in sub_task_info:
            self.status_info += "%d:%s\n" % (task_id, status)
            if status is not None:
                if status.count("Created batch job script") == 0:
                    sub_tasks_have_created_job_scripts = False
            else:
                sub_tasks_have_created_job_scripts = False

        # Save subtasks id
        self.subTasksId = []
        for task_id, status, datetime_stamp, resource, app, task_param in sub_task_info:
            self.subTasksId.append(task_id)

        if sub_tasks_have_created_job_scripts:
            self.set_method_to_run_next(
                "create_batch_job_script_and_submit_it", "Subtasks have created job scripts.", "")
            # check  in 1 minute
            return datetime.timedelta(days=0, hours=0, minutes=1)
        else:
            self.set_method_to_run_next(
                "check_if_subtasks_created_job_scripts", "Waiting for subtasks to create job scripts", "")
            # check  in 1 minute
            return datetime.timedelta(days=0, hours=0, minutes=1)

    def create_batch_job_script_and_submit_it(self):
        self.JobScriptName = self.appName + ".job"
        print("### Creating batch job script and submitting it to remote machine")

        # as a current bypass will create a job script remotely and copy it here
        # get ssh to remote resource

        sh = None
        try:
            sh = ssh_resource(self.resource)

            # Create remote directories if needed
            # akrr_data
            check_dir(sh, self.resource['akrr_data'], raise_on_fail=True)
            # dir for app
            check_dir(sh, os.path.join(self.resource['akrr_data'], self.appName), raise_on_fail=True)
            # dir for task
            check_dir(sh, self.remoteTaskDir, raise_on_fail=True)
            # CheckAndCreateDir(self,sh,os.path.join(self.remoteTaskDir,"batchJob_pl"))

            # cd to remoteTaskDir
            ssh_command(sh, "cd %s" % self.remoteTaskDir)

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
            except MySQLError:
                pass

            # create job-script
            batchvars = {}

            # print "#"*80
            for di in [self.resource, self.app, dbdefaults, self.resourceParam, self.appParam]:
                batchvars.update(di)

            # stack the subtasks
            sub_task_info = self.get_sub_task_info()
            if batchvars['shuffleSubtasks']:
                random.shuffle(sub_task_info)
            sub_tasks_execution = ""
            for subtask_id, subtask_status, subtask_datetime_stamp, \
                    subtask_resource, subtask_app, subtask_task_param in sub_task_info:
                remote_sub_task_dir = self.get_remote_task_dir(
                    self.resource['akrr_data'], subtask_app, subtask_datetime_stamp)
                sub_task_job_script_name = self.get_job_script_name(subtask_app)
                sub_task_job_script_path = os.path.join(remote_sub_task_dir, sub_task_job_script_name)

                sub_tasks_execution += "cd " + remote_sub_task_dir + "\n"
                # subTasksExecution+="cp "+os.path.join(self.remoteTaskDir,"job.id ")+"./\n"
                sub_tasks_execution += "echo Starting " + subtask_app + "\n"
                sub_tasks_execution += self.resource['shell'] + " " + sub_task_job_script_path + " > stdout 2> stderr\n"
                sub_tasks_execution += "echo Done with " + subtask_app + "\n" + "\n"

            batchvars['subTasksExecution'] = sub_tasks_execution

            # calculate NNodes and NCores
            if 'nnodes' in batchvars:
                tmp_num_nodes = batchvars['nnodes']
                tmp_num_cores = tmp_num_nodes * batchvars['ppn']
            else:
                tmp_num_cores = batchvars['ncores']
                if tmp_num_cores % batchvars['ppn'] == 0:
                    tmp_num_nodes = tmp_num_cores / batchvars['ppn']
                else:
                    tmp_num_nodes = (tmp_num_cores / batchvars['ppn']) + 1

            batchvars['akrrNCores'] = tmp_num_cores
            batchvars['akrrNNodes'] = tmp_num_nodes

            # Set batchvars remaps
            batchvars['akrrPPN'] = batchvars['ppn']
            batchvars['akrrNCoresToBorder'] = batchvars['akrrPPN'] * batchvars['akrrNNodes']
            batchvars['akrrTaskWorkingDir'] = self.remoteTaskDir
            batchvars['akrrWallTimeLimit'] = "%02d:%02d:00" % (
                int(batchvars['walllimit']) / 60, int(batchvars['walllimit']) % 60)
            batchvars['localPATH'] = ssh_command(sh, "echo $PATH").strip()
            batchvars['akrrAppKerName'] = self.app['name']
            batchvars['akrrResourceName'] = self.resource['name']
            batchvars['akrrTimeStamp'] = self.timeStamp
            if batchvars['akrrNNodes'] == 1:
                batchvars['akrrPPN4NodesOrCores4OneNode'] = batchvars['akrrNCores']
            else:
                batchvars['akrrPPN4NodesOrCores4OneNode'] = batchvars['akrrPPN']
            if 'nodeListSetterTemplate' not in batchvars:
                batchvars['nodeListSetterTemplate'] = batchvars['nodeListSetter'][batchvars['batchScheduler']]

            # process templates
            batchvars['akrrCommonCommands'] = akrr.util.format_recursively(
                batchvars['akrrCommonCommandsTemplate'], batchvars, keep_double_brackets=True)
            batchvars['akrrCommonCleanup'] = akrr.util.format_recursively(
                batchvars['akrrCommonCleanupTemplate'], batchvars, keep_double_brackets=True)

            # do parameters adjustment
            if 'process_params' in batchvars:
                batchvars['process_params'](batchvars)
            # generate job script
            job_script = akrr.util.format_recursively(self.resource["batchJobTemplate"], batchvars)
            fout = open(os.path.join(self.taskDir, "jobfiles", self.JobScriptName), "w")
            fout.write(job_script)
            fout.close()
            scp_to_resource(
                self.resource, os.path.join(self.taskDir, "jobfiles", self.JobScriptName),
                os.path.join(self.remoteTaskDir))

            ssh_command(sh, "cat %s " % self.JobScriptName)

            # send to queue
            from string import Template
            send_to_queue = Template(submit_commands[self.resource['batchScheduler']]).substitute(
                scriptPath=self.JobScriptName)
            msg = ssh_command(sh, send_to_queue)
            match_obj = re.search(job_id_extract_patterns[self.resource['batchScheduler']], msg, re.M | re.S)

            if match_obj:
                try:
                    job_id = int(match_obj.group(1))
                except (ValueError, IndexError):
                    raise AkrrError("Can't get job id. " + msg)
            else:
                raise AkrrError("Can't get job id. " + msg)

            ssh_command(sh, "echo %d > job.id" % job_id)

            # cp job id to subtasks
            for subtask_id, subtask_status, subtask_datetime_stamp, subtask_resource, \
                    subtask_app, subtask_task_param in sub_task_info:
                remote_sub_task_dir = self.get_remote_task_dir(
                    self.resource['akrr_data'], subtask_app, subtask_datetime_stamp)
                ssh_command(sh, "cp job.id %s" % remote_sub_task_dir)

            self.RemoteJobID = job_id
            self.TimeJobSubmetedToRemoteQueue = datetime.datetime.today()

            sh.sendline("exit")
            sh.close(force=True)
            del sh
            sh = None
            print("\nRemoteJobID=", self.RemoteJobID)
            print("copying files from remote machine")
            scp_from_resource(
                self.resource, os.path.join(self.remoteTaskDir, "*"), os.path.join(self.taskDir, "jobfiles"), "-r")

            # update DB time_submitted_to_queue
            db, cur = akrr.db.get_akrr_db()

            cur.execute('''UPDATE active_tasks
            SET time_submitted_to_queue=%s
            WHERE task_id=%s ;''', (datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"), self.task_id))

            cur.close()
            del db

            self.set_method_to_run_next(
                "check_the_job_on_remote_machine",
                "Created batch job script and have submitted it to remote queue.",
                "Remote job ID is %d" % self.RemoteJobID)

            # check first time in 1 minute
            return datetime.timedelta(days=0, hours=0, minutes=1)
        except Exception:
            if sh is not None:
                sh.sendline("exit")
                sh.close(force=True)
                del sh
            self.set_method_to_run_next(None, "ERROR Can not created batch job script and submit it to remote queue",
                                        traceback.format_exc())
            if cfg.max_fails_to_submit_to_the_queue >= 0:
                if hasattr(self, "fails_to_submit_to_the_queue"):
                    self.fails_to_submit_to_the_queue += 1
                    if self.fails_to_submit_to_the_queue > cfg.max_fails_to_submit_to_the_queue:
                        # Stop execution of the task and submit results to db
                        self.set_method_to_run_next("push_to_db")
                        result_file = os.path.join(self.taskDir, "result.xml")
                        self.write_error_xml(result_file)
                        return datetime.timedelta(seconds=3)
                else:
                    self.fails_to_submit_to_the_queue = 1
            else:
                self.fatal_errors_count += 1

            akrr.util.log.log_traceback(self.status)
            return cfg.repeat_after_fails_to_submit_to_the_queue

    def update_sub_tasks(self):
        # force to check SubTasks
        # stack the subtasks
        sub_task_info = self.get_sub_task_info()

        db, cur = akrr.db.get_akrr_db()

        for subtask_id, subtask_status, subtask_datetime_stamp, subtask_resource, \
                subtask_app, subtask_task_param in sub_task_info:
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
            m_wait_expr = wait_expressions[self.resource['batchScheduler']]
            cmd = Template(m_wait_expr[0]).substitute(jobId=str(self.RemoteJobID))
            rege = Template(m_wait_expr[2]).substitute(jobId=str(self.RemoteJobID))

            sh = ssh_resource(self.resource)
            msg = ssh_command(sh, cmd)
            sh.sendline("exit")
            sh.close(force=True)
            del sh
            sh = None

            match_obj = m_wait_expr[1](rege, msg, m_wait_expr[3])
            if match_obj:
                print("Still in queue. Either waiting or running")
                if datetime.datetime.today() - self.TimeJobSubmetedToRemoteQueue > self.taskParam.get(
                        'MaxTimeInQueue', cfg.max_time_in_queue):
                    print("ERROR:")
                    print("Job exceeds the maximal time in queue (%s). And will be terminated." % (
                        str(self.taskParam.get('MaxTimeInQueue', cfg.max_time_in_queue))))
                    print("Removing job from remote queue.")
                    self.terminate()
                    print("copying files from remote machine")
                    scp_from_resource(self.resource, os.path.join(self.remoteTaskDir, "*"),
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
                scp_from_resource(self.resource, os.path.join(self.remoteTaskDir, "*"),
                                        os.path.join(self.taskDir, "jobfiles"), "-r")

                print("Deleting all files from remote machine")
                self.delete_remote_folder()
                self.status = "Not in queue. Either exited with error or executed successfully. " \
                    "Copied all files to local machine. Deleted all files from remote machine"
                self.status_info = "Not in queue. Either exited with error or executed successfully. " \
                    "Copied all files to local machine. Deleted all files from remote machine"
                self.ToDoNextString = "check_if_subtasks_done_proccessing_results"
                self.update_sub_tasks()
                # del self.RemoteJobID
                self.TimeJobPossiblyCompleted = datetime.datetime.today()
                return datetime.timedelta(seconds=3)
            # print msg
        except:
            if sh is not None:
                sh.sendline("exit")
                sh.close(force=True)
                del sh
            self.status = "ERROR Can not check the status of the job on remote resource"
            self.status_info = traceback.format_exc()
            self.fatal_errors_count += 1
            akrr.util.log.log_traceback(self.status)
            self.ToDoNextString = "check_the_job_on_remote_machine"
            return active_task_default_attempt_repeat

    def get_result_files(self, raise_error=False):
        jobfiles_dir = os.path.join(self.taskDir, "jobfiles")
        batch_job_dir = None
        stdout_file = None
        stderr_file = None
        appstdout_file = None
        taskexeclog_file = None

        for d in os.listdir(jobfiles_dir):
            if re.match("batchJob", d):
                if batch_job_dir is None:
                    batch_job_dir = os.path.join(jobfiles_dir, d)
                else:
                    if raise_error:
                        raise IOError("Error: found multiple batchJob* Directories although it should be one")
                    else:
                        return batch_job_dir, stdout_file, stderr_file, appstdout_file

        if batch_job_dir is not None:
            for f in os.listdir(batch_job_dir):
                if re.match("sub.*\.stdout", f):
                    if stdout_file is None:
                        stdout_file = os.path.join(batch_job_dir, f)
                    elif raise_error:
                        raise IOError("Error: found multiple sub*.stdout files although it should be one")
                if re.match("sub.*\.stderr", f):
                    if stderr_file is None:
                        stderr_file = os.path.join(batch_job_dir, f)
                    elif raise_error:
                        raise IOError("Error: found multiple sub*.stderr files although it should be one")
                if re.match("sub.*\.appstdout", f):
                    if appstdout_file is None:
                        appstdout_file = os.path.join(batch_job_dir, f)
                    elif raise_error:
                        raise IOError("Error: found multiple sub*.appstdout files although it should be one")
        else:
            batch_job_dir = jobfiles_dir
            for f in os.listdir(jobfiles_dir):
                if re.match("stdout", f):
                    if stdout_file is None:
                        stdout_file = os.path.join(jobfiles_dir, f)
                    elif raise_error:
                        raise IOError("Error: found multiple sub*.stdout files although it should be one")
                if re.match("stderr", f):
                    if stderr_file is None:
                        stderr_file = os.path.join(jobfiles_dir, f)
                    elif raise_error:
                        raise IOError("Error: found multiple sub*.stderr files although it should be one")
                if re.match("appstdout", f):
                    if appstdout_file is None:
                        appstdout_file = os.path.join(jobfiles_dir, f)
                    elif raise_error:
                        raise IOError("Error: found multiple sub*.appstdout files although it should be one")
            if os.path.isfile(os.path.join(self.taskDir, "proc", "log")):
                taskexeclog_file = os.path.join(self.taskDir, "proc", "log")
        if batch_job_dir is None or stdout_file is None or stderr_file is None:
            if raise_error:
                raise IOError("Error: standard files is not present among job-files copied from remote resource.")
        return batch_job_dir, stdout_file, stderr_file, appstdout_file, taskexeclog_file

    def check_if_subtasks_done_proccessing_results(self):
        sub_task_info = self.get_sub_task_info()
        if len(sub_task_info) == 0:
            self.status = "Subtasks are done with proccessing results"
            self.status_info = "Subtasks are done with proccessing results"
            self.ToDoNextString = "process_results"
            return datetime.timedelta(seconds=3)
        else:
            self.status = "Waiting for subtasks to proccess results"
            self.status_info = "Waiting for subtasks to proccess results"
            return datetime.timedelta(minutes=5)

    def process_results(self):
        if log.verbose:
            print("Processing the output")

        result_file = None

        try:
            result_file = os.path.join(self.taskDir, "result.xml")

            if hasattr(self, 'ReportFormat'):  # i.e. fatal error and the last one is already in status/status_info
                if self.ReportFormat == "Error":
                    self.ToDoNextString = "push_to_db"
                    self.write_error_xml(result_file)
                    return datetime.timedelta(seconds=3)

            (batch_job_dir, stdout_file, stderr_file, appstdout_file, taskexeclog_file) = \
                self.get_result_files(raise_error=True)

            # get the performance data
            parser_filename = os.path.join(cfg.akrr_mod_dir, "parsers", self.app['parser'])

            import importlib.machinery
            this_appker_parser = importlib.machinery.SourceFileLoader(
                'this_app_ker_parser', parser_filename).load_module()

            resource_appker_vars = {
                'resource': self.resource,
                'app': self.app,
                'taskId': self.task_id,
                'subTasksId': self.subTasksId
            }
            resource_appker_vars['resource'].update(self.resourceParam)
            resource_appker_vars['app'].update(self.appParam)

            performance = this_appker_parser.process_appker_output(
                appstdout=appstdout_file, geninfo=os.path.join(batch_job_dir, "gen.info"),
                resource_appker_vars=resource_appker_vars)

            if performance is None:
                self.status = "ERROR: Job have not finished successfully"
                self.status_info = ""
                self.ToDoNextString = "push_to_db"
                self.write_error_xml(result_file)
            else:
                fout = open(result_file, "w")
                fout.write(performance)
                fout.close()
                self.status = "Output was processed and found that kernel either " \
                    "exited with error or executed successfully."
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
            if result_file is not None:
                self.write_error_xml(result_file)
            return datetime.timedelta(seconds=3)

    def push_to_db(self):
        db, cur = akrr.db.get_akrr_db()
        try:
            if hasattr(self, 'TimeJobPossiblyCompleted'):
                time_finished = self.TimeJobPossiblyCompleted
            else:
                time_finished = datetime.datetime.today()
            self.push_to_db_raw(cur, self.task_id, time_finished)
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
            self.PushToDBAttemps += 1

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

    def push_to_db_raw(self, cur, task_id, time_finished):
        print("Pushing to DB")
        import xml.etree.ElementTree as ElementTree
        import xml.dom.minidom

        result_file = os.path.join(self.taskDir, "result.xml")
        jobfiles_dir = os.path.join(self.taskDir, "jobfiles")
        (batch_job_dir, stdout_file, stderr_file, appstdout_file, taskexeclog_file) = self.get_result_files()

        # sanity check
        fin = open(result_file, "r")
        content = fin.read()
        fin.close()
        if content[0] != '<':
            # need to reformat
            i0 = content.find("<rep:report")
            i1 = content.find("</rep:report>")

            fout = open(result_file, "w")
            content = fout.write("<?xml version='1.0'?>\n" + content[i0:i1 + len("</rep:report>")] + "\n")
            fout.close()

        try:

            tree = ElementTree.parse(result_file)
            tree.getroot()
        except:
            self.status_info = "(1)==Resulting XML file content==\n" + content + \
                              "\n==Previous status==" + self.status + \
                              "\n==Previous status info==" + self.status_info + "\n" + \
                              traceback.format_exc()
            self.status = "Cannot process final XML file"
            self.write_error_xml(result_file, cdata=True)

        instance_id = task_id
        message = None
        stderr = None
        job_id = None

        cur.execute("""SELECT instance_id,collected,committed,resource,executionhost,reporter,
            reporternickname,status,message,stderr,body,memory,cputime,walltime,job_id
            FROM akrr_xdmod_instanceinfo WHERE instance_id=%s""", (task_id,))
        raw = cur.fetchone()
        if raw is not None:  # .i.e. not new entry
            (instance_id, collected, committed, resource, executionhost, reporter, reporternickname, status, message,
             stderr, body, memory, cputime, walltime, job_id) = raw
            if self.RemoteJobID is not None:
                job_id = self.RemoteJobID
        else:
            collected = time_finished
            committed = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
            resource = self.resourceName
            executionhost = self.resource.get('__regexp__', self.resourceName)
            reporter = self.appName
            reporternickname = akrr.util.replace_at_var_at(self.app['nickname'],
                                                           [self.resource, self.app, self.resourceParam, self.appParam])

            if hasattr(self, "RemoteJobID"):
                job_id = self.RemoteJobID

        # Process XML file
        try:

            tree = ElementTree.parse(result_file)
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

        if root is not None:
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

            try:

                t = root.find('xdtas').find('batchJob').find('status').text
                if t.upper() == "ERROR":
                    error = True
                else:
                    error = False
            except:
                error = None

            status = 0
            if completed is not None:
                if completed:
                    status = 1

            if completed is not None:
                if completed is True:
                    body_et = root.find('body').find('performance')
                    body = ElementTree.tostring(body_et)

                    xml = xml.dom.minidom.parseString(body)
                    body = xml.toprettyxml()
                    body = body.replace("""<?xml version="1.0" ?>\n""", "")

                    statistics_et = root.find('body').find('performance').find('benchmark').find('statistics')
                    for e in statistics_et:
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
    """ % reporter
            elif completed is None:
                if error is not None:  # i.e. xml with error generated afterwards
                    if error is True:
                        # fin=open(resultFile,"r")
                        # body=fin.read()
                        # fin.close
                        message = root.find('xdtas').find('batchJob').find('errorCause').text
                        stderr = root.find('xdtas').find('batchJob').find('errorMsg').text

                        body_et = root.find('xdtas')
                        body = ElementTree.tostring(body_et)
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
        nodes_file_name = os.path.join(jobfiles_dir, "nodes")
        if os.path.isfile(nodes_file_name):
            parser = AppKerOutputParser()
            parser.parse_common_params_and_stats(geninfo=os.path.join(batch_job_dir, "gen.info"))
            nodes = ";"
            for line in parser.nodesList:
                line = line.strip()
                nodes += "%s;" % line
            if len(nodes.strip().strip(';')) == 0:
                nodes = None

        if raw is not None:  # .i.e. new entry
            print("Updating")
            cur.execute("""UPDATE akrr_xdmod_instanceinfo
SET instance_id=%s,collected=%s,committed=%s,resource=%s,executionhost=%s,reporter=%s,
reporternickname=%s,status=%s,message=%s,stderr=%s,body=%s,memory=%s,cputime=%s,walltime=%s,job_id=%s,nodes=%s
WHERE instance_id=%s""",
                        (instance_id, collected, committed, resource, executionhost, reporter, reporternickname, status,
                         message, stderr, body, memory, cputime, walltime, job_id, nodes,
                         instance_id))
        else:
            cur.execute("""INSERT INTO akrr_xdmod_instanceinfo
(instance_id,collected,committed,resource,executionhost,reporter,reporternickname,status,message,stderr,body,memory,cputime,walltime,job_id,nodes)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                        (instance_id, collected, committed, resource, executionhost, reporter, reporternickname, status,
                         message, stderr, body, memory, cputime, walltime, job_id, nodes))
        if appstdout_file is not None:
            fin = open(appstdout_file, "r")
            appstdout_file_content = fin.read()
            fin.close()
        else:
            appstdout_file_content = "Does Not Present"
        if stdout_file is not None:
            fin = open(stdout_file, "r")
            stdout_file_content = fin.read()
            fin.close()
        else:
            stdout_file_content = "Does Not Present"
        if stderr_file is not None:
            fin = open(stderr_file, "r")
            stderr_file_content = fin.read()
            fin.close()
        else:
            stderr_file_content = "Does Not Present"

        if taskexeclog_file is not None:
            fin = open(taskexeclog_file, "r")
            taskexeclog_file_content = fin.read()
            fin.close()
        else:
            taskexeclog_file_content = "Does Not Present"

        cur.execute("""INSERT INTO akrr_errmsg
        (task_id,appstdout,stderr,stdout,taskexeclog)
        VALUES (%s,%s,%s,%s,%s)""",
                    (instance_id, appstdout_file_content, stderr_file_content, stdout_file_content,
                     taskexeclog_file_content))

    def task_is_complete(self):
        print("Done", self.taskDir)
        self.status = "Done"
        self.status_info = "Done"
        self.ToDoNextString = "task_is_complete"
        return None

    def terminate(self):
        #
        can_be_safely_removed = False
        if self.RemoteJobID is None:
            # i.e. not running remotely and everything is on local disk
            can_be_safely_removed = True
        else:
            #
            if self.remove_task_from_remote_queue() is None:
                # i.e. "Task is probably removed from remote queue.":
                can_be_safely_removed = True
        if can_be_safely_removed:
            # remove remote directory
            pass
        return can_be_safely_removed

    def remove_task_from_remote_queue(self):
        sh = None
        try:
            from string import Template
            kill_expr = kill_expressions[self.resource['batchScheduler']]
            cmd = Template(kill_expr[0]).substitute(jobId=str(self.RemoteJobID))
            msg = ssh_resource(self.resource, cmd)
            print(msg)
            self.status = "Task is probably removed from remote queue."
            self.status_info = copy.deepcopy(msg)
            self.ToDoNextString = "task_is_complete"
            return None
        except:
            if sh is not None:
                sh.sendline("exit")
                sh.close(force=True)
                del sh
            self.status = "ERROR Can not remove job from queue on remote resource"
            self.status_info = traceback.format_exc()
            self.fatal_errors_count += 1
            print(traceback.format_exc())
            return active_task_default_attempt_repeat
