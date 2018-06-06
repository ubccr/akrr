import os
import datetime
import time
import copy
import re

import akrr.util.ssh
from . import cfg
from .akrrerror import AkrrError
from .util import log

active_task_default_attempt_repeat = cfg.active_task_default_attempt_repeat

# Batch job submit commands for different workload managers
submit_commands = {
    # 'lsf': "bsub < $scriptPath",
    'pbs': "qsub $scriptPath",
    'sge': "qsub $scriptPath",
    # 'shell': "/bin/sh $scriptPath",
    'slurm': "sbatch $scriptPath"
}

# Regular expression for extracting job id of submitted batch script
job_id_extract_patterns = {
    # 'lsf': r'<(\d+)',
    'pbs': r'^(\d+)',
    'sge': r'job (\d+)',
    # 'shell': r'',  # N/A,
    'slurm': r'^Submitted batch job (\d+)'
}

# Command and regular expression to detect that the job is still queued or running
wait_expressions = {
    # 'lsf'         : ["bjobs $jobId` =~ /PEND|RUN|SUSP/",
    'pbs': [r"qstat $jobId 2>&1", re.search, r"-----", 0],
    'sge': [r"qstat 2>&1", re.search, r"^ *$jobId ", re.M],
    'slurm': [r"squeue -u $$USER 2>&1", re.search, r"^ *$jobId ", re.M],
    # 'shell'       : ["kill(0, $jobId)"]
}

kill_expressions = {
    # 'lsf': ["bkill $jobId"],
    'pbs': ["qdel $jobId"],
    'sge': ["qdel $jobId"],
    'slurm': ["scancel $jobId"],
    # shell       => "kill(9, $jobId)"
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

        self.timeStamp = self.CreateLocalDirectoryForTask()
        # set a directory for task already should exists
        self.SetDirNames(cfg.data_dir)
        self.remoteTaskDir = self.GetRemoteTaskDir(self.resource['akrr_data'], self.appName, self.timeStamp)

        self.oldstatus = "Does not exist"
        self.status = "Activated"
        self.status_info = "Activated"
        self.LastPickledState = -1
        self.fatal_errors_count = 0
        self.ToDoNextString = "FirstStep"
        self.oldToDoNextString = "Does not exist"

    def SetDirNames(self, akrr_data_dir):
        self.resourceDir = os.path.join(akrr_data_dir, self.resourceName)
        self.appDir = os.path.join(self.resourceDir, self.appName)
        self.taskDir = os.path.join(self.appDir, self.timeStamp)

    def GetRemoteTaskDir(self, akrr_data_dir, app_name, time_stamp):
        return os.path.join(akrr_data_dir, app_name, time_stamp)

    def GetJobScriptName(self, app_name=None):
        if app_name is not None:
            return app_name + ".job"
        return self.appName + ".job"

    def IsStateChanged(self):
        if self.oldstatus == self.status and self.ToDoNextString == self.oldToDoNextString:
            return False
        else:
            return True

    def ToDoNext(self):
        """
        Returns method which should be executed next
        """
        method_to_run = getattr(self, self.ToDoNextString)
        if method_to_run is None:
            raise IOError("ToDoNext is None!")
        return method_to_run()

    def Terminate(self):
        """
        return True is task can be safely removed from the DB
        """
        return True

    def CreateLocalDirectoryForTask(self):
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
        log.info("Creating task directory: %s" % (task_dir))
        os.mkdir(task_dir)
        log.info("Creating task directories: \n\t%s\n\t%s" % (os.path.join(task_dir, "jobfiles"),
                                                              os.path.join(task_dir, "proc")))
        os.mkdir(os.path.join(task_dir, "jobfiles"))
        os.mkdir(os.path.join(task_dir, "proc"))
        return time_stamp

    def IamDone(self):
        print("IamDone", self.taskDir)
        time.sleep(1)
        self.status = "Done"
        self.status_info = "IamDone"
        return None

    def FirstStep(self):
        print("IamDone", self.taskDir)
        time.sleep(1)
        self.status = "FirstStep"
        self.status_info = "FirstStep"
        self.ToDoNextString = "IamDone"
        return datetime.timedelta(days=0, hours=0, minutes=3)

    def Activate123(self):
        """Set the task directory initiate all scripts"""
        self.status = "Activating"

        # find resource
        self.resource = cfg.find_resource_by_name(self.resourceName)
        if not self.resource.get('active', True):
            raise AkrrError("%s is marked as inactive in AKRR" % self.resourceName)

        # find app
        self.app = cfg.find_app_by_name(self.appName)

        self.CreateBatchJobScriptAndSubmitIt()
        # creating batch files input files etc
        self.status = "Activated"
        self.ToDoNext = self.CheckTheQueue

    def CopyOutputFilesFromRemoteMachine(self):
        self.status = "Copying output files from remote machine"
        print(self.status)
        exit(0)
        self.status = "Output files was copied from remote machine"

    def ProcessOutput(self):
        self.status = "Processing output files"
        self.status = "Output files were processed"

    def Archiving(self):
        self.status = "Archiving results"
        self.status = "Done"

    def CreateBatchJobScriptOnSrv(self):
        import subprocess
        import sys
        self.JobScriptName = self.appName + ".job"

        # switch working directory to taskDir
        wd = os.getcwd()
        os.chdir(self.taskDir)

        print("Writing JobScript to:", os.path.join(self.taskDir, self.JobScriptName))
        fout = open(os.path.join(self.taskDir, self.JobScriptName), 'w')

        # arg_bin_path=self.app['arg_bin_path']
        execstr = "%s -bin_path=\"%s\" -help=%s -log=%d -verbose=%d -version=%s" % (self.app['name'],
                                                                                    self.resource['bin_path'],
                                                                                    self.app.get('arg_help', 'no'),
                                                                                    self.app.get('arg_log', 0),
                                                                                    self.app.get('arg_verbose', 1),
                                                                                    self.app.get('arg_version', 'no'),
                                                                                    )

        args = """     export PERL5LIB=/home/mikola/xdtas/incaReporterManager-edge/lib/perl:\
/home/mikola/xdtas/incaReporterManager-edge/var/reporter-packages/lib/perl   
~/xdtas/incaReporterManager-edge/var/reporter-packages/bin/xdmod.batch.wrapper \
-scheduler="sge" -queue="normal" -submitparam="-V" -nodes=:8:8 -type="16way" \
-walllimit=13 -exec="%s"
        """ % (execstr)
        subprocess.call(args, stdout=fout, stderr=sys.stdout, shell=True)
        fout.close()

        # switch working directory back
        os.chdir(wd)

    def DeleteLocalFolder(self):
        if os.path.isdir(self.taskDir):
            if self.taskDir != '/' and self.taskDir != os.getenv("HOME"):
                import shutil
                shutil.rmtree(self.taskDir, True)

    def DeleteRemoteFolder(self):
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

    def WriteErrorXML(self, filename, bCDATA=False):
        content = """<body>
 <xdtas>
  <batchJob>
   <status>Error</status>
   <errorCause>%s</errorCause>
   <reporter>%s</reporter>
   <errorMsg>%s</errorMsg>
  </batchJob>
 </xdtas>
</body> 
""" % (self.status, self.appName, self.status_info)
        if bCDATA:
            content = """<body>
 <xdtas>
  <batchJob>
   <status>Error</status>
   <errorCause>%s</errorCause>
   <reporter>%s</reporter>
   <errorMsg><![CDATA[%s]]></errorMsg>
  </batchJob>
 </xdtas>
</body> 
""" % (self.status, self.appName, self.status_info)
        # now lets try to read to parce it
        import xml.etree.ElementTree as ET
        try:
            tree = ET.fromstring(content)
        except:
            print("Cannot write readable XML file, will try CDATA declaration")
            content = """<body>
 <xdtas>
  <batchJob>
   <status>Error</status>
   <errorCause>%s</errorCause>
   <reporter>%s</reporter>
   <errorMsg><![CDATA[%s]]></errorMsg>
  </batchJob>
 </xdtas>
</body> 
""" % (self.status, self.appName, self.status_info)
            try:
                tree = ET.fromstring(content)
            except:
                print("Cannot write readable XML file!!!")
                # raise

        fout = open(filename, "w")
        fout.write(content)
        fout.close()
