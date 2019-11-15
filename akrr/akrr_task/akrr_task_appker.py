import os
import datetime
import traceback
import re
import copy
from typing import Optional


import akrr.db
import akrr.util
import akrr.util.log
import akrr.util.ssh as ssh
import akrr.util.openstack

from .. import cfg
from ..util import log

from .akrr_task_base import AkrrTaskHandlerBase, submit_commands, job_id_extract_patterns, wait_expressions, \
    active_task_default_attempt_repeat, kill_expressions

from akrr.parsers.akrrappkeroutputparser import AppKerOutputParser

from ..akrrerror import AkrrError


class AkrrTaskHandlerAppKer(AkrrTaskHandlerBase):
    """Task Handler for AppKernel execution and processing"""

    def __init__(self, task_id, resource_name, app_name, resource_param, app_param, task_param):
        super().__init__(task_id, resource_name, app_name, resource_param, app_param, task_param)

        self.ReportFormat = None  # type: Optional[str]
        self.nodesList = None
        self.RemoteJobID = None  # type: Optional[int]

        self.TimeJobSubmetedToRemoteQueue = None  # type: Optional[datetime.datetime]
        self.TimeJobPossiblyCompleted = None  # type: Optional[datetime.datetime]

        self.fails_to_submit_to_the_queue = 0  # type: int
        self.PushToDBAttemps = 0  # type: Optional[int]

        self.openstack_server_ip = None  # type: Optional[str]

    def first_step(self):
        if self.resource['batch_scheduler'].lower() == "openstack":
            return self.start_openstack_server()
        else:
            return self.create_batch_job_script_and_submit_it()

    def start_openstack_server(self):
        if self.resource['batch_scheduler'].lower() == "openstack":
            # Start instance if it is cloud
            openstack_server = akrr.util.openstack.OpenStackServer(resource=self.resource)
            openstack_server.create()
            self.openstack_server_ip = openstack_server.ip
            self.resource['remote_access_node'] = openstack_server.ip

        self.set_method_to_run_next(
            "create_batch_job_script_and_submit_it",
            "start_openstack_server ... Done",
            "start_openstack_server ... Done")

        # check first time in 1 minute
        return datetime.timedelta(days=0, hours=0, minutes=1)

    def generate_batch_job_script(self):
        if self.JobScriptName is None:
            self.JobScriptName = self.get_job_script_name()

        # get walltime from DB
        db_defaults = {}
        try:
            db, cur = akrr.db.get_akrr_db()

            cur.execute('''SELECT resource,app,resource_param,app_param FROM active_tasks
            WHERE task_id=%s ;''', (self.task_id,))
            raw = cur.fetchall()
            if len(raw) > 0:
                (resource, app, resource_param, app_param) = raw[0]

                cur.execute("""SELECT walltime_limit
                    FROM akrr_default_walllimit
                    WHERE resource=%s AND app=%s AND resource_param=%s AND app_param=%s """,
                            (resource, app, resource_param, app_param))
                raw = cur.fetchall()

                if len(raw) > 0:
                    db_defaults['walltime_limit'] = raw[0][0]

            # db.commit()
            cur.close()
            del db
        except Exception as e:
            pass
            raise e
        # create job-script
        try:
            batch_vars = {}
            appkernel_on_resource = {}
            if 'appkernel_on_resource' in self.app:
                if self.resourceName in self.app['appkernel_on_resource']:
                    appkernel_on_resource = self.app['appkernel_on_resource'][self.resourceName]
                elif 'default' in self.app['appkernel_on_resource']:
                    appkernel_on_resource = self.app['appkernel_on_resource']['default']

            for di in [self.resource, self.app, appkernel_on_resource, db_defaults, self.resourceParam, self.appParam]:
                batch_vars.update(di)

            # get auto-walltime limit
            try:
                if 'auto_walltime_limit' in batch_vars and batch_vars['auto_walltime_limit'] is True:
                    log.info("auto_walltime_limit is on, trying to estimate walltime limit...")
                    auto_walltime_limit_overhead = 1.2
                    if 'auto_walltime_limit_overhead' in batch_vars:
                        auto_walltime_limit_overhead = batch_vars['auto_walltime_limit_overhead'] + 1.0
                    # query last 20 executions of this appkernel on that resource with that node count

                    db, cur = akrr.db.get_akrr_db(True)

                    cur.execute('''SELECT resource,reporter,reporternickname,collected,status,walltime FROM akrr_xdmod_instanceinfo
                        WHERE  `resource`=%s AND `reporternickname` =  %s
                        ORDER BY  `akrr_xdmod_instanceinfo`.`collected` DESC 
                        LIMIT 0 , 20''', (self.resource['name'], "%s.%d" % (self.app['name'], batch_vars['nnodes'])))

                    raw = cur.fetchall()

                    i = 0
                    last_five_runs_successfull = True
                    max_walltime = 0.0
                    for r in raw:
                        if i < 5 and r['status'] == 0:
                            last_five_runs_successfull = False
                        if r['status'] == 1 and r['walltime'] > max_walltime:
                            max_walltime = r['walltime']
                        i += 1
                    if i < 5:
                        log.info("There are only %d previous run, need at least 5 for walltime limit autoset" % i)
                    else:
                        if not last_five_runs_successfull:
                            log.warning("One of last 5 runs have failed. Would not use autoset.")
                        else:
                            if max_walltime < 120:
                                log.info("Previous walltime was less than 2 minutes, will set walltime limit to 2 minutes")
                                max_walltime = 120
                                batch_vars['walltime_limit'] = 2
                            else:
                                log.info(
                                    "Max walltime was %.1f s, will change walltime limit from %.1f minutes to %d minutes" %
                                    (max_walltime, batch_vars['walltime_limit'],
                                    int(auto_walltime_limit_overhead * max_walltime / 60.0 + 0.99)))
                                batch_vars['walltime_limit'] = int((auto_walltime_limit_overhead * max_walltime / 60.0 + 0.99))
                    cur.close()
                    del db
            except Exception as e:
                log.error("Exception happened in AkrrTaskHandlerAppKer.generate_batch_job_script: %s" % str(e))

            # calculate NNodes and NCores
            if 'nnodes' in batch_vars:
                tmp_num_nodes = batch_vars['nnodes']
                tmp_num_cores = tmp_num_nodes * batch_vars['ppn']
            else:
                tmp_num_cores = batch_vars['ncores']
                if tmp_num_cores % batch_vars['ppn'] == 0:
                    tmp_num_nodes = tmp_num_cores / batch_vars['ppn']
                else:
                    tmp_num_nodes = (tmp_num_cores / batch_vars['ppn']) + 1

            assert isinstance(tmp_num_nodes, int)
            assert isinstance(tmp_num_cores, int)

            batch_vars['akrr_num_of_cores'] = tmp_num_cores
            batch_vars['akrr_num_of_nodes'] = tmp_num_nodes

            # Set batch_vars remaps
            batch_vars['akrr_ppn'] = batch_vars['ppn']
            batch_vars['akrrNCoresToBorder'] = batch_vars['akrr_ppn'] * batch_vars['akrr_num_of_nodes']
            batch_vars['akrr_task_work_dir'] = self.remoteTaskDir
            batch_vars['akrr_walltime_limit'] = "%02d:%02d:00" % (
                int(batch_vars['walltime_limit']) / 60, int(batch_vars['walltime_limit']) % 60)
            batch_vars['akrr_appkernel_name'] = self.app['name']
            batch_vars['akrr_resource_name'] = self.resource['name']
            batch_vars['akrr_time_stamp'] = self.timeStamp
            if batch_vars['akrr_num_of_nodes'] == 1:
                batch_vars['akrrPPN4NodesOrCores4OneNode'] = batch_vars['akrr_num_of_cores']
            else:
                batch_vars['akrrPPN4NodesOrCores4OneNode'] = batch_vars['akrr_ppn']

            if 'node_list_setter_template' not in batch_vars:
                batch_vars['node_list_setter_template'] = batch_vars['node_list_setter'][batch_vars['batch_scheduler']]

            # process templates
            batch_vars['akrrCommonCommands'] = akrr.util.format_recursively(
                batch_vars['akrr_common_commands_template'], batch_vars, keep_double_brackets=True)

            batch_vars['akrrCommonCleanup'] = akrr.util.format_recursively(
                batch_vars['akrr_common_cleanup_template'], batch_vars, keep_double_brackets=True)

            # specially for IOR request two nodes for single node benchmark, one for read and one for write
            if batch_vars['appkernel_requests_two_nodes_for_one'] is True and batch_vars['akrr_num_of_nodes'] == 1 and \
                    'batch_job_header_template' in batch_vars:
                batch_vars2 = copy.deepcopy(batch_vars)
                batch_vars2['akrr_num_of_cores'] = 2 * batch_vars['akrr_num_of_cores']
                batch_vars2['akrr_num_of_nodes'] = 2 * batch_vars['akrr_num_of_nodes']
                batch_vars2['akrrNCoresToBorder'] = 2 * batch_vars['akrrNCoresToBorder']
                batch_vars2['akrrPPN4NodesOrCores4OneNode'] = batch_vars['akrr_ppn']
                batch_vars['batch_job_header_template'] = akrr.util.format_recursively(
                    batch_vars2['batch_job_header_template'], batch_vars2)

            # do parameters adjustment
            if 'process_params' in batch_vars:
                batch_vars['process_params'](batch_vars)

            # generate job script
            job_script = akrr.util.format_recursively(self.resource["batch_job_template"], batch_vars)
            job_script_full_path = os.path.join(self.taskDir, "jobfiles", self.JobScriptName)
            fout = open(job_script_full_path, "w")
            fout.write(job_script)
            fout.close()
        except Exception as e:
            self.status = "ERROR: Can not created batch job script"
            self.status_info = traceback.format_exc()
            akrr.util.log.log_traceback(self.status)
            raise e

    def create_batch_job_script_and_submit_it(self, do_not_submit_to_queue=False):
        self.JobScriptName = self.get_job_script_name(self.appName)
        log.info("Creating batch job script and submitting it to remote machine")
        # as a current bypass will create a job script remotely and copy it here
        # get ssh to remote resource

        sh = None
        try:
            sh = ssh.ssh_resource(self.resource)

            # akrr_data
            ssh.check_dir(sh, self.resource['akrr_data'], try_to_create=True)
            # dir for app
            ssh.check_dir(sh, os.path.join(self.resource['akrr_data'], self.appName), try_to_create=True)
            # dir for task
            ssh.check_dir(sh, self.remoteTaskDir, try_to_create=True)
            # cd to remoteTaskDir
            ssh.ssh_command(sh, "cd %s" % self.remoteTaskDir)

            # generate_batch_job_script
            self.generate_batch_job_script()

            ssh.scp_to_resource(self.resource, os.path.join(self.taskDir, "jobfiles", self.JobScriptName),
                                os.path.join(self.remoteTaskDir))
            if do_not_submit_to_queue:
                return

            ssh.ssh_command(sh, "cat %s " % self.JobScriptName)

            # send to queue
            from string import Template
            job_id = 0
            if 'masterTaskID' not in self.taskParam:
                # i.e. submit to queue only if task is independent
                send_to_queue = Template(submit_commands[self.resource['batch_scheduler']]).substitute(
                    scriptPath=self.JobScriptName)
                msg = ssh.ssh_command(sh, send_to_queue)
                match_obj = re.search(job_id_extract_patterns[self.resource['batch_scheduler']], msg, re.M | re.S)

                if match_obj:
                    try:
                        job_id = int(match_obj.group(1))
                    except (ValueError, TypeError, IndexError):
                        raise AkrrError("Can't get job id:\n" + msg)
                else:
                    raise AkrrError("Can't get job id:\n" + msg)

                # report
                if self.resource["gateway_reporting"]:
                    ssh.ssh_command(sh, "module load gateway-usage-reporting")
                    ssh.ssh_command(sh, r'gateway_submit_attributes -gateway_user ' + self.resource[
                        "gateway_user"] + r''' -submit_time "`date '+%F %T %:z'`" -jobid ''' + str(job_id))

            ssh.ssh_command(sh, "echo %d > job.id" % job_id)

            self.RemoteJobID = job_id
            self.TimeJobSubmetedToRemoteQueue = datetime.datetime.today()

            sh.sendline("exit")
            sh.close(force=True)
            del sh
            sh = None
            print("\nRemoteJobID=", self.RemoteJobID)
            print("copying files from remote machine")
            ssh.scp_from_resource(self.resource, os.path.join(self.remoteTaskDir, "*"),
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

            log.error("Got exception during attempt to create and submit job: %s", str(e))

            if cfg.max_fails_to_submit_to_the_queue >= 0:
                self.fails_to_submit_to_the_queue += 1

                if self.fails_to_submit_to_the_queue > cfg.max_fails_to_submit_to_the_queue or \
                        (self.taskParam['test_run'] is True and self.fails_to_submit_to_the_queue >= 2):
                    # Stop execution of the task and submit results to db
                    self.set_method_to_run_next("push_to_db")
                    result_file = os.path.join(self.taskDir, "result.xml")
                    self.write_error_xml(result_file)
                    return datetime.timedelta(seconds=3)
            else:
                self.fatal_errors_count += 1

            akrr.util.log.log_traceback(self.status)
            return cfg.repeat_after_fails_to_submit_to_the_queue

    def check_the_job_on_remote_machine(self):
        sh = None
        try:
            print("### Checking the job status on remote machine")
            from string import Template

            sh = ssh.ssh_resource(self.resource)

            # if it is subtask get master task id from job.id file (it should be replaced by master task)
            if self.RemoteJobID == 0:
                try:
                    self.RemoteJobID = int(
                        ssh.ssh_command(sh, "cat %s" % (os.path.join(self.remoteTaskDir, "job.id"))))
                except Exception as e:
                    log.error("Can not get remote job ID: %s", str(e))
                    self.RemoteJobID = 0

            m_wait_expression = wait_expressions[self.resource['batch_scheduler']]
            cmd = Template(m_wait_expression[0]).substitute(jobId=str(self.RemoteJobID))
            rege = Template(m_wait_expression[2]).substitute(jobId=str(self.RemoteJobID))

            msg = ssh.ssh_command(sh, cmd)
            sh.sendline("exit")
            sh.close(force=True)
            del sh

            if self.RemoteJobID == 0:
                return active_task_default_attempt_repeat

            match_obj = m_wait_expression[1](rege, msg, m_wait_expression[3])
            if match_obj:
                log.info("Still in queue. Either waiting or running")
                if datetime.datetime.today() - self.TimeJobSubmetedToRemoteQueue > \
                        self.taskParam.get('MaxTimeInQueue', cfg.max_time_in_queue):
                    log.error("Job exceeds the maximal time in queue (%s). And will be terminated. "
                              "Removing job from remote queue." % (
                               str(self.taskParam.get('MaxTimeInQueue', cfg.max_time_in_queue))))
                    self.terminate()

                    log.info("copying files from remote machine")
                    ssh.scp_from_resource(self.resource, os.path.join(self.remoteTaskDir, "*"),
                                          os.path.join(self.taskDir, "jobfiles"), "-r")
                    # print msg
                    log.info("Deleting all files from remote machine")
                    self.delete_remote_folder()

                    self.set_method_to_run_next(
                        "process_results",
                        "ERROR: Job exceeds the maximal time in queue (%s) and was terminated." %
                        str(self.taskParam.get('MaxTimeInQueue', cfg.max_time_in_queue)),
                        "Last Status report:\n" + msg)
                    self.ReportFormat = "Error"
                    # del self.RemoteJobID
                    return datetime.timedelta(seconds=3)

                self.set_method_to_run_next(None, "Still in queue. Either waiting or running", msg)
                return active_task_default_attempt_repeat

            log.info("Not in queue. Either exited with error or executed successfully.")
            log.info("copying files from remote machine")
            msg = ssh.scp_from_resource(self.resource, os.path.join(self.remoteTaskDir, "*"),
                                        os.path.join(self.taskDir, "jobfiles"), "-r")

            log.info("Deleting all files from remote machine")
            self.delete_remote_folder()
            self.set_method_to_run_next(
                "process_results",
                "Not in queue. Either exited with error or executed successfully. "
                "Copied all files to local machine. Deleted all files from remote machine")

            self.TimeJobPossiblyCompleted = datetime.datetime.today()
            return datetime.timedelta(seconds=3)

        except Exception as e:
            if hasattr(locals(), 'sh') and sh is not None:
                sh.sendline("exit")
                sh.close(force=True)
                del sh
            log.error("Got exception during check_the_job_on_remote_machine: %s", e)
            self.set_method_to_run_next(
                None, "ERROR Can not check the status of the job on remote resource", traceback.format_exc())
            self.fatal_errors_count += 1
            akrr.util.log.log_traceback(self.status)
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

    def process_results(self):
        if 'parser' not in self.app:
            return self.process_results_old()

        log.info("Processing the output")
        result_file = None
        try:
            jobfiles_dir = os.path.join(self.taskDir, "jobfiles")
            result_file = os.path.join(self.taskDir, "result.xml")
            # get job.id (from remote machine) of master node
            if self.RemoteJobID == 0:  # i.e. this is a subtask of a bundle
                if os.path.isfile(os.path.join(jobfiles_dir, "job.id")):
                    fin = open(os.path.join(jobfiles_dir, "job.id"), "r")
                    self.RemoteJobID = int(fin.read().strip())
                    print("Master task's RemoteJobID is ", self.RemoteJobID)
                    fin.close()

            if self.ReportFormat == "Error":
                # i.e. fatal error and the last one is already in status/status_info
                self.set_method_to_run_next("push_to_db")
                self.write_error_xml(result_file)
                return datetime.timedelta(seconds=3)

            (batchJobDir, stdoutFile, stderrFile, appstdoutFile, taskexeclogFile) = self.get_result_files(
                raise_error=True)

            # get the performance data
            parser_filename = os.path.join(cfg.akrr_mod_dir, "parsers", self.app['parser'])

            import importlib.machinery
            this_appker_parser = importlib.machinery.SourceFileLoader(
                'this_app_ker_parser', parser_filename).load_module()

            resource_appker_vars = {
                'resource': self.resource,
                'app': self.app
            }
            resource_appker_vars['resource'].update(self.resourceParam)
            resource_appker_vars['app'].update(self.appParam)

            performance = this_appker_parser.process_appker_output(
                appstdout=appstdoutFile, stdout=stdoutFile, stderr=stderrFile,
                geninfo=os.path.join(batchJobDir, "gen.info"), resource_appker_vars=resource_appker_vars)
            if performance is None:
                self.set_method_to_run_next("push_to_db", "ERROR: Job have not finished successfully", "")
                self.write_error_xml(result_file)
            else:
                fout = open(result_file, "w")
                fout.write(performance)
                fout.close()

                self.set_method_to_run_next(
                    "push_to_db",
                    "Output was processed and found that kernel either exited with error or executed successfully.",
                    "Done")
                if hasattr(performance, 'node_list'):
                    self.nodesList = performance.node_list
                else:
                    self.nodesList = None
            return datetime.timedelta(seconds=3)
        except Exception as e:

            log.exception("Got exception in process_results_old: %s\n%s", e, traceback.format_exc())
            self.set_method_to_run_next(
                "push_to_db", "ERROR: Error happens during processing of output.", traceback.format_exc())
            self.fatal_errors_count += 1
            akrr.util.log.log_traceback(self.status)
            if result_file is not None:
                self.write_error_xml(result_file)
            return datetime.timedelta(seconds=3)

    def process_results_old(self):
        log.info("Processing the output")
        result_file = None
        try:
            result_file = os.path.join(self.taskDir, "result.xml")

            if self.ReportFormat == "Error":
                # i.e. fatal error and the last one is already in status/status_info
                self.set_method_to_run_next("PushToDB")
                self.write_error_xml(result_file)
                return datetime.timedelta(seconds=3)

            (batch_job_dir, stdout_file, stderr_file, appstdout_file, taskexeclog_file) = \
                self.get_result_files(raise_error=True)

            # now check if stdoutFile is empty or not
            fin = open(stdout_file, "r")
            remstdout = fin.read()
            fin.close()

            if len(remstdout) < 5:
                fin = open(stderr_file, "r")
                remstderr = fin.readlines()
                fin.close()
                for l in remstderr:
                    if re.search('job killed: walltime *\d+ *exceeded limit *\d+', l):
                        self.status = "ERROR: Job was killed on remote resource due to walltime exceeded limit"
                        self.status_info = l
                        self.set_method_to_run_next("PushToDB")
                        self.write_error_xml(result_file)
                        return datetime.timedelta(seconds=3)

                log.info("stdout is too short meaning that application kernel exit prematurely")
                self.set_method_to_run_next(
                    "PushToDB",
                    "ERROR: stdout is too short meaning that application kernel exit prematurely",
                    "stdout is too short meaning that application kernel exit prematurely")
                self.write_error_xml(result_file)
                return datetime.timedelta(seconds=3)
            # here we need to check file
            if remstdout.count("<rep:report") == 0:
                self.set_method_to_run_next("PushToDB", "ERROR: unknown error", "stdout:\n" + remstdout)
                if appstdout_file is not None:
                    fin = open(appstdout_file, "r")
                    remappstdout = fin.read()
                    fin.close()
                    self.status_info += "\nappstdout:\n" + remappstdout

                self.write_error_xml(result_file)
                return datetime.timedelta(seconds=3)

            self.set_method_to_run_next(
                "PushToDB",
                "Output was processed and found that kernel either exited with error or executed successfully.",
                "Done")
            import shutil

            shutil.copy2(stdout_file, result_file)
            # need to extract xml part file, some resource put servise information above and below
            fin = open(result_file, "r")
            content = fin.read()
            fin.close()
            if content[0] != '<' or content[-2] != '>':
                # need to reformat
                i0 = content.find("<rep:report")
                i1 = content.find("</rep:report>")

                fout = open(result_file, "w")
                fout.write("<?xml version='1.0'?>\n" + content[i0:i1 + len("</rep:report>")] + "\n")
                fout.close()
            return datetime.timedelta(seconds=3)
        except Exception as e:
            self.set_method_to_run_next("PushToDB", "ERROR: Error happens during processing of output.",
                                        traceback.format_exc())
            self.fatal_errors_count += 1
            log.log_traceback(self.status)
            log.exception("Got exception in process_results_old: %s", e)
            if result_file is not None:
                self.write_error_xml(result_file)
            return datetime.timedelta(seconds=3)

    def push_to_db(self):

        db, cur = akrr.db.get_akrr_db()
        try:
            if self.TimeJobPossiblyCompleted is not None:
                time_finished = self.TimeJobPossiblyCompleted
            else:
                time_finished = datetime.datetime.today()
            self.push_to_db_raw(cur, self.task_id, time_finished)
            db.commit()
            cur.close()
            del db
            self.set_method_to_run_next("task_is_complete")
            return datetime.timedelta(seconds=3)
        except Exception as e:
            log.exception("Got exception in process_results_old: %s\n%s\n", e, traceback.format_exc())
            db.rollback()
            db.commit()
            cur.close()
            del db
            self.PushToDBAttemps += 1

            if self.PushToDBAttemps <= cfg.export_db_max_repeat_attempts:
                akrr.util.log.log_traceback("AKRR server was not able to push to external DB.")
                self.set_method_to_run_next(
                    None, "ERROR: Can not push to external DB, will try again", traceback.format_exc())
                return cfg.export_db_repeat_attempt_in
            else:
                akrr.util.log.log_traceback("AKRR server was not able to push to external DB will only update local.")
                self.set_method_to_run_next(
                    "task_is_complete", "ERROR: Can not push to external DB, will try again", traceback.format_exc())
                return None

    def push_to_db_raw(self, cur, task_id, time_finished):
        import xml.etree.ElementTree
        log.info("Pushing to DB")

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

            tree = xml.etree.ElementTree.parse(result_file)
            tree.getroot()
        except Exception as e:
            log.exception("Got exception in push_to_db_raw, during xml read: %s", e)

            self.set_method_to_run_next(
                None,
                "Cannot process final XML file",
                "(1)==Resulting XML file content==\n" + content +
                "\n==Previous status==" + self.status +
                "\n==Previous status info==" + self.status_info + "\n" +
                traceback.format_exc())
            self.write_error_xml(result_file, cdata=True)

        instance_id = task_id
        status = None
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
            if hasattr(self, "RemoteJobID"):
                job_id = self.RemoteJobID
        else:
            collected = time_finished
            committed = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
            resource = self.resourceName
            executionhost = self.resource.get('__regexp__', self.resourceName)
            reporter = self.appName
            # reporternickname="%s.%d"%(self.appName,self.resourceParam['ncpus'])
            reporternickname = akrr.util.replace_at_var_at(self.app['nickname'],
                                                           [self.resource, self.app, self.resourceParam, self.appParam])

            if hasattr(self, "RemoteJobID"):
                job_id = self.RemoteJobID

        # Process XML file
        try:
            tree = xml.etree.ElementTree.parse(result_file)
            root = tree.getroot()
        except Exception as e:
            log.exception("Got exception in push_to_db_raw, during xml read: %s", e)
            self.status_info = "(2)==Resulting XML file content==\n" + content + \
                               "\n==Previous status==" + self.status + \
                               "\n==Previous status info==" + self.status_info
            self.status = "Cannot process final XML file"
            root = None

        memory = 0.0
        cputime = 0.0
        walltime = 0.0

        completed = None

        log.debug("%s %s", root, status)

        if root is not None:
            if root.find('exitStatus') is not None and root.find('exitStatus').find('completed') is not None:
                try:
                    t = root.find('exitStatus').find('completed').text

                    log.debug('exitStatus:completed %s', t)

                    if t.strip().upper() == "TRUE":
                        completed = True
                    else:
                        completed = False

                    if completed:
                        root.find('body').find('performance').find('benchmark').find('statistics')
                    self.set_method_to_run_next(None, "Task was completed successfully.", "Done")
                except Exception as e:
                    log.exception("Got exception in push_to_db_raw: %s", e)

            log.debug("completedstatus %s %s", completed, status)
            error = None
            if root.find('xdtas') is not None and root.find('xdtas').find('batchJob') is not None and \
                    root.find('xdtas').find('batchJob').find('status') is not None:
                try:

                    t = root.find('xdtas').find('batchJob').find('status').text
                    if t.upper() == "ERROR":
                        error = True
                    else:
                        error = False
                except Exception as e:
                    log.exception("Got exception in push_to_db_raw: %s", e)

            status = 0
            if completed is not None:
                if completed:
                    status = 1

            log.debug("completedstatus %s %s", completed, status)

            if completed is not None:
                if completed:
                    body_et = root.find('body').find('performance')
                    body = xml.etree.ElementTree.tostring(body_et, encoding="unicode")
                    import xml.dom.minidom
                    xml = xml.dom.minidom.parseString(body)
                    body = xml.toprettyxml(indent="    ")
                    body = body.replace("""<?xml version="1.0" ?>\n""", "")

                    body = akrr.util.strip_empty_lines(body)

                    statistics_et = root.find('body').find('performance').find('benchmark').find('statistics')
                    for e in statistics_et:
                        if e.find('ID').text == 'Memory':
                            memory = float(e.find('value').text)
                        if e.find('ID').text == 'Wall Clock Time':
                            walltime = float(e.find('value').text)
                else:
                    # i.e. error caught by parser on resource
                    if root and root.find('exitStatus') and root.find('exitStatus').find('errorMessage'):
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
                    else:
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
                    if error:
                        # fin=open(resultFile,"r")
                        # body=fin.read()
                        # fin.close
                        message = root.find('xdtas').find('batchJob').find('errorCause').text
                        stderr = root.find('xdtas').find('batchJob').find('errorMsg').text

                        body_et = root.find('xdtas')
                        body = xml.etree.ElementTree.tostring(body_et)
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
        nodes_filename = os.path.join(jobfiles_dir, "gen.info")

        if os.path.isfile(nodes_filename):
            parser = AppKerOutputParser()
            parser.parse_common_params_and_stats(geninfo=nodes_filename)
            if hasattr(parser, 'geninfo') and parser.geninfo is not None and 'node_list' in parser.geninfo:
                nodes_list = parser.geninfo['node_list'].split()
                nodes = ";"
                for line in nodes_list:
                    line = line.strip()
                    nodes += "%s;" % line
                if len(nodes.strip().strip(';')) == 0:
                    nodes = None

        internal_failure_code = 0
        if 'masterTaskID' in self.taskParam and appstdout_file is None:
            internal_failure_code = 10004
        log.debug("completedstatus %s %s", completed, status)
        if raw is not None:  # .i.e. new entry
            print("Updating")
            cur.execute("""UPDATE akrr_xdmod_instanceinfo
SET instance_id=%s,collected=%s,committed=%s,resource=%s,executionhost=%s,reporter=%s,
reporternickname=%s,status=%s,message=%s,stderr=%s,body=%s,memory=%s,cputime=%s,walltime=%s,job_id=%s,nodes=%s,
internal_failure=%s
WHERE instance_id=%s""",
                        (instance_id, collected, committed, resource, executionhost, reporter, reporternickname, status,
                         message, stderr, body, memory, cputime, walltime, job_id, nodes, internal_failure_code,
                         instance_id))
        else:
            cur.execute("""INSERT INTO akrr_xdmod_instanceinfo
(instance_id,collected,committed,resource,executionhost,reporter,reporternickname,status,message,stderr,body,memory,
cputime,walltime,job_id,nodes,internal_failure)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                        (instance_id, collected, committed, resource, executionhost, reporter, reporternickname, status,
                         message, stderr, body, memory, cputime, walltime, job_id, nodes, internal_failure_code))

        if appstdout_file is not None:
            fin = open(appstdout_file, "r", encoding="utf-8")
            appstdout_file_content = fin.read()
            fin.close()
        else:
            appstdout_file_content = "Does Not Present"
        if stdout_file is not None:
            fin = open(stdout_file, "r", encoding="utf-8")
            stdout_file_content = fin.read()
            fin.close()
        else:
            stdout_file_content = "Does Not Present"
        if stderr_file is not None:
            fin = open(stderr_file, "r", encoding="utf-8")
            stderr_file_content = fin.read()
            fin.close()
        else:
            stderr_file_content = "Does Not Present"

        if taskexeclog_file is not None:
            fin = open(taskexeclog_file, "r", encoding="utf-8")
            taskexeclog_file_content = fin.read()
            fin.close()
        else:
            taskexeclog_file_content = "Does Not Present"

        assert isinstance(appstdout_file_content, str)
        assert isinstance(stdout_file_content, str)
        assert isinstance(stderr_file_content, str)
        assert isinstance(taskexeclog_file_content, str)

        cur.execute("""SELECT task_id
            FROM akrr_errmsg WHERE task_id=%s""", (task_id,))
        raw = cur.fetchall()

        cur.execute("""SELECT @@max_allowed_packet""")
        max_allowed_packet = cur.fetchall()[0][0]

        if (len(appstdout_file_content) + len(stderr_file_content) + len(stdout_file_content) + len(
                taskexeclog_file_content)) > 0.9 * max_allowed_packet:
            print("WARNING: length of files exceed max_allowed_packet will trancate files")

            if len(appstdout_file_content) > 0.2 * max_allowed_packet:
                appstdout_file_content = appstdout_file_content[:int(0.2 * max_allowed_packet)]
                appstdout_file_content += \
                    "\nWARNING: File was trancated because it length of files exceed max_allowed_packet\n"
            if len(stderr_file_content) > 0.2 * max_allowed_packet:
                stderr_file_content = stderr_file_content[:int(0.2 * max_allowed_packet)]
                stderr_file_content += \
                    "\nWARNING: File was trancated because it length of files exceed max_allowed_packet\n"
            if len(stdout_file_content) > 0.2 * max_allowed_packet:
                stdout_file_content = stdout_file_content[:int(0.2 * max_allowed_packet)]
                stdout_file_content += \
                    "\nWARNING: File was trancated because it length of files exceed max_allowed_packet\n"
            if len(taskexeclog_file_content) > 0.2 * max_allowed_packet:
                taskexeclog_file_content = taskexeclog_file_content[:int(0.2 * max_allowed_packet)]
                taskexeclog_file_content += \
                    "\nWARNING: File was trancated because it length of files exceed max_allowed_packet\n"

        appstdout_file_content = akrr.util.clean_unicode(appstdout_file_content)
        stderr_file_content = akrr.util.clean_unicode(stderr_file_content)
        stdout_file_content = akrr.util.clean_unicode(stdout_file_content)
        taskexeclog_file_content = akrr.util.clean_unicode(taskexeclog_file_content)

        if len(raw) > 0:  # .i.e. updating existing entry
            print("Updating", raw)
            cur.execute("""UPDATE akrr_errmsg
                SET appstdout=%s,stderr=%s,stdout=%s,taskexeclog=%s
                WHERE task_id=%s""",
                        (appstdout_file_content, stderr_file_content, stdout_file_content,
                         taskexeclog_file_content, instance_id))
        else:
            cur.execute("""INSERT INTO akrr_errmsg
                (task_id,appstdout,stderr,stdout,taskexeclog)
                VALUES (%s,%s,%s,%s,%s)""",
                        (instance_id, appstdout_file_content, stderr_file_content, stdout_file_content,
                         taskexeclog_file_content))

    def task_is_complete(self):
        if self.resource['batch_scheduler'].lower() == "openstack":
            openstack_server = akrr.util.openstack.OpenStackServer(resource=self.resource)
            openstack_server.delete()
        log.info("Done")
        self.set_method_to_run_next("task_is_complete", "Done", "Done")
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
        if self.resource['batch_scheduler'].lower() == "openstack":
            openstack_server = akrr.util.openstack.OpenStackServer(resource=self.resource)
            openstack_server.delete()
        return can_be_safely_removed

    def remove_task_from_remote_queue(self):
        sh = None
        try:
            from string import Template
            m_kill_expression = kill_expressions[self.resource['batch_scheduler']]
            cmd = Template(m_kill_expression[0]).substitute(jobId=str(self.RemoteJobID))
            msg = ssh.ssh_resource(self.resource, cmd)
            log.debug(msg)
            self.set_method_to_run_next(
                "task_is_complete", "Task is probably removed from remote queue.", copy.deepcopy(msg))
            return None
        except Exception as e:
            log.exception("Got exception in process_results_old: %s\n%s\n", e, traceback.format_exc())

            if sh is not None:
                sh.sendline("exit")
                sh.close(force=True)
                del sh
            self.set_method_to_run_next(
                None, "ERROR Can not remove job from queue on remote resource", traceback.format_exc())
            self.fatal_errors_count += 1
            return active_task_default_attempt_repeat
