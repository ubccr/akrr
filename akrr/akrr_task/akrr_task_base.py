import os
import datetime
import time
import copy
import re

import akrr.util.ssh
from .. import cfg
from ..util import log

active_task_default_attempt_repeat = cfg.active_task_default_attempt_repeat

# Batch job submit commands for different workload managers
submit_commands = {
    # 'lsf': "bsub < $scriptPath",
    'pbs': "qsub $scriptPath",
    'sge': "qsub $scriptPath",
    'shell': "nohup bash $scriptPath > stdout 2> stderr & echo PID of last background process is $$!",
    'slurm': "sbatch $scriptPath",
    'openstack': "nohup bash $scriptPath > stdout 2> stderr & echo PID of last background process is $$!"
}

# Regular expression for extracting job id of submitted batch script
job_id_extract_patterns = {
    # 'lsf': r'<(\d+)',
    'pbs': r'^(\d+)',
    'sge': r'job (\d+)',
    'shell': r'^PID of last background process is (\d+)',
    'slurm': r'^Submitted batch job (\d+)',
    'openstack': r'^PID of last background process is (\d+)'
}

# Command and regular expression to detect that the job is still queued or running
wait_expressions = {
    # 'lsf'         : ["bjobs $jobId` =~ /PEND|RUN|SUSP/",
    'pbs': [r"qstat $jobId 2>&1", re.search, r"-----", 0],
    'sge': [r"qstat 2>&1", re.search, r"^ *$jobId ", re.M],
    'slurm': [r"squeue -u $$USER 2>&1", re.search, r"^ *$jobId ", re.M],
    'shell': [r"ps -p $jobId 2>&1", re.search, r"^ *$jobId ", re.M],
    'openstack': [r"ps -p $jobId 2>&1", re.search, r"^ *$jobId ", re.M]
}

kill_expressions = {
    # 'lsf': ["bkill $jobId"],
    'pbs': ["qdel $jobId"],
    'sge': ["qdel $jobId"],
    'slurm': ["scancel $jobId"],
    'shell': ["kill -9  $jobId"],
    'openstack': ["kill -9  $jobId"]
}


class AkrrTaskHandlerBase:
    """
    the scheduler will activate the task on timeToSubmit and reschedule new task on repetition
    
    timeToSubmit==None means run now
    reschedule==None means run only once
    
    possible statuses
    Scheduled
    """

    def __init__(self, task_id, resource_name, app_name, resource_param, app_param, task_param):
        self.resourceName = resource_name
        self.appName = app_name
        self.resourceParam = eval(resource_param)
        self.appParam = eval(app_param)
        self.taskParam = copy.deepcopy(cfg.default_task_params)
        self.taskParam.update(eval(task_param))
        self.timeToSubmit = None
        self.repetition = None
        self.task_id = task_id

        self.resource = None
        self.app = None

        # just check that resource and app exists
        self.resource = cfg.find_resource_by_name(self.resourceName)
        self.app = cfg.find_app_by_name(self.appName)

        self.resourceDir = None
        self.appDir = None
        self.taskDir = None

        self.timeStamp = self.create_local_directory_for_task()
        # set a directory for task already should exists
        self.set_dir_names(cfg.data_dir)
        self.remoteTaskDir = self.get_remote_task_dir(self.resource['akrr_data'], self.appName, self.timeStamp)

        self.JobScriptName = None

        self.LastPickledState = -1
        self.fatal_errors_count = 0

        self._method_to_run_next = "first_step"
        self.status = "Activated"
        self.status_info = "Activated"
        self._old_method_to_run_next = "Does not exist"
        self._old_status = "Does not exist"

    def set_dir_names(self, akrr_data_dir):
        self.resourceDir = os.path.join(akrr_data_dir, self.resourceName)
        self.appDir = os.path.join(self.resourceDir, self.appName)
        self.taskDir = os.path.join(self.appDir, self.timeStamp)

    @staticmethod
    def get_remote_task_dir(akrr_data_dir, app_name, time_stamp):
        return os.path.join(akrr_data_dir, app_name, time_stamp)

    def get_job_script_name(self, app_name=None):
        if app_name is not None:
            return app_name + ".job"
        return self.appName + ".job"

    def set_method_to_run_next(self, method_to_run_next=None, status=None, status_info=None):
        """
        update method_to_run_next, status and status_info if they are not None
        """
        if method_to_run_next is not None:
            self._old_method_to_run_next = self._method_to_run_next
            self._method_to_run_next = method_to_run_next

        if status is not None:
            self._old_status = self.status
            self.status = status

        if status_info is not None:
            self.status_info = status_info
        elif status is not None:
            self.status_info = status

    def state_changed(self):
        if self._old_status == self.status and self._method_to_run_next == self._old_method_to_run_next:
            return False
        else:
            return True

    def to_do_next(self):
        """
        Returns method which should be executed next
        """
        if self._method_to_run_next is None:
            raise ValueError("Can not find _method_to_run_next it is None!")

        method_to_run = getattr(self, self._method_to_run_next)
        if method_to_run is None:
            raise ValueError("Can not find _method_to_run_next!")
        return method_to_run()

    def terminate(self):
        """
        return True is task can be safely removed from the DB
        """
        return True

    def create_local_directory_for_task(self):
        """
        Create a directory for task
        """
        resource_dir = os.path.join(cfg.data_dir, self.resourceName)
        app_dir = os.path.join(resource_dir, self.appName)
        time_stamp = datetime.datetime.today().strftime("%Y.%m.%d.%H.%M.%S.%f")
        task_dir = os.path.join(app_dir, time_stamp)

        if not os.path.isdir(cfg.data_dir):
            raise IOError("Directory %s does not exist or is not directory." % cfg.data_dir)
        if not os.path.isdir(resource_dir):
            log.info("Directory %s does not exist, creating it." % resource_dir)
            os.mkdir(resource_dir)
        if not os.path.isdir(app_dir):
            log.info("Directory %s does not exist, creating it." % app_dir)
            os.mkdir(app_dir)
        if not os.path.isdir(cfg.completed_tasks_dir):
            raise IOError("Directory %s does not exist or is not directory." % cfg.completed_tasks_dir)
        if not os.path.isdir(os.path.join(cfg.completed_tasks_dir, self.resourceName)):
            log.info("Directory %s does not exist, creating it." % (
                os.path.join(cfg.completed_tasks_dir, self.resourceName)))
            os.mkdir(os.path.join(cfg.completed_tasks_dir, self.resourceName))
        if not os.path.isdir(os.path.join(cfg.completed_tasks_dir, self.resourceName, self.appName)):
            log.info("Directory %s does not exist, creating it." % (
                os.path.join(cfg.completed_tasks_dir, self.resourceName, self.appName)))
            os.mkdir(os.path.join(cfg.completed_tasks_dir, self.resourceName, self.appName))

        # Generate unique time_stamp
        while os.path.exists(task_dir):
            log.debug2(os.path.exists(task_dir))
            time_stamp = datetime.datetime.today().strftime("%Y.%m.%d.%H.%M.%S.%f")
            task_dir = os.path.join(app_dir, time_stamp)
        log.info("Creating task directory: %s" % task_dir)
        os.mkdir(task_dir)
        log.info("Creating task directories: \n\t%s\n\t%s" % (os.path.join(task_dir, "jobfiles"),
                                                              os.path.join(task_dir, "proc")))
        os.mkdir(os.path.join(task_dir, "jobfiles"))
        os.mkdir(os.path.join(task_dir, "proc"))
        return time_stamp

    def first_step(self):
        log.info("first_step, task_dir: %s", self.taskDir)
        time.sleep(1)
        self.set_method_to_run_next("task_is_complete", "first_step", "first_step")
        return datetime.timedelta(days=0, hours=0, minutes=3)

    def process_results(self):
        pass

    def push_to_db_raw(self, cur, task_id, time_finished):
        pass

    def process_output(self):
        self.status = "Processing output files"
        self.status = "Output files were processed"

    def archiving(self):
        self.status = "archiving results"
        self.status = "Done"

    def delete_local_folder(self):
        if os.path.isdir(self.taskDir):
            if self.taskDir != '/' and self.taskDir != os.getenv("HOME"):
                import shutil
                shutil.rmtree(self.taskDir, True)

    def delete_remote_folder(self):
        # trying to be carefull
        if self.remoteTaskDir == '/':
            raise IOError("can not remove /")

        # should remove ../../ etc
        rt = os.path.normpath(self.remoteTaskDir)
        ad = os.path.normpath(self.resource['akrr_data'])
        if rt == ad:
            raise IOError("can not remove akrr_data")
        if os.path.commonprefix([rt, ad]) != ad:
            raise IOError("can not remove remote task folder. The folder should be in akrr_data")

        log.info("removing remote task folder:\n\t%s" % self.remoteTaskDir)
        msg = akrr.util.ssh.ssh_resource(self.resource, "rm -rf \"%s\"" % self.remoteTaskDir)
        log.info(msg)

    def write_error_xml(self, filename, cdata=False):
        content = ("<body>\n"
                   "<xdtas>\n"
                   "  <batchJob>\n"
                   "   <status>Error</status>\n"
                   "   <errorCause>%s</errorCause>\n"
                   "   <reporter>%s</reporter>\n"
                   "   <errorMsg>%s</errorMsg>\n"
                   "  </batchJob>\n"
                   " </xdtas>\n"
                   "</body> \n") % (self.status, self.appName, self.status_info)
        if cdata:
            content = ("<body>\n"
                       " <xdtas>\n"
                       "  <batchJob>\n"
                       "   <status>Error</status>\n"
                       "   <errorCause>%s</errorCause>\n"
                       "   <reporter>%s</reporter>\n"
                       "   <errorMsg><![CDATA[%s]]></errorMsg>\n"
                       "  </batchJob>\n"
                       " </xdtas>\n"
                       "</body>\n") % (self.status, self.appName, self.status_info)
        # now lets try to read to parce it
        import xml.etree.ElementTree
        try:
            xml.etree.ElementTree.fromstring(content)
        except Exception as e:
            log.error("Cannot write readable XML file (%s), will try CDATA declaration" % str(e))
            content = ("<body>\n"
                       " <xdtas>\n"
                       "  <batchJob>\n"
                       "   <status>Error</status>\n"
                       "   <errorCause>%s</errorCause>\n"
                       "   <reporter>%s</reporter>\n"
                       "   <errorMsg><![CDATA[%s]]></errorMsg>\n"
                       "  </batchJob>\n"
                       " </xdtas>\n"
                       "</body>\n") % (self.status, self.appName, self.status_info)
            try:
                xml.etree.ElementTree.fromstring(content)
            except Exception as e2:
                log.error("Cannot write readable XML file!!! %s" % str(e2))

        fout = open(filename, "w")
        fout.write(content)
        fout.close()
