from . import akrrcfg
import os
import sys
#namdSizes
import datetime
import time
import copy
import re


active_task_default_attempt_repeat=akrrcfg.active_task_default_attempt_repeat

submitCommands = {
    'cobalt'      : "cqsub `cat $scriptPath`",
    'dqs'         : "qsub $scriptPath",
    'loadleveler' : "llsubmit $scriptPath",
    'lsf'         : "bsub < $scriptPath",
    'pbs'         : "qsub $scriptPath",
    'pbsxt'       : "qsub $scriptPath",
    'pbssgi'      : "qsub $scriptPath",
    'sge'         : "qsub $scriptPath",
    'shell'       : "/bin/sh $scriptPath",
    'slurm'       : "sbatch $scriptPath"
}


jidExtractPatterns = {
    'cobalt'      : r'^(\d+)',
    'dqs'         : r'job (\d+)',
    'loadleveler' : r'"([^"]+)" has been submitted',
    'lsf'         : r'<(\d+)',
    'pbs'         : r'^(\d+)',
    'pbsxt'       : r'^(\d+)',
    'pbssgi'      : r'^(\d+)',
    'sge'         : r'job (\d+)',
    'shell'       : r'',                                # N/A,
    'slurm'       : r'^Submitted batch job (\d+)'
}

# Commands to detect that the job is still queued or running
waitExprs = {
    #'cobalt'      : ["cqstat 2>&1` =~ /^ *$jobId /m",
    #'dqs'         : ["qstat $jobId 2>&1` =~ /-----/",
    #'loadleveler' : ["llq $jobId` =~ /[1-9] job step/",
    #'lsf'         : ["bjobs $jobId` =~ /PEND|RUN|SUSP/",
    'pbs'         : [r"qstat $jobId 2>&1", re.search, r"-----",0],
    #'pbsxt'       : ["qstat $jobId 2>&1` =~ /-----/",
    #'pbssgi'      : ["qstat $jobId 2>&1` =~ /-----/",
    'sge'         : [r"qstat 2>&1", re.search,r"^ *$jobId ",re.M],
    'slurm'         : [r"squeue -u $$USER 2>&1", re.search,r"^ *$jobId ",re.M],
    #'shell'       : ["kill(0, $jobId)"]
} 
waitExprs['pbsxt']=waitExprs['pbs']
waitExprs['pbssgi']=waitExprs['pbs']

killExprs = {
#                cobalt      => "`cqdel $jobId`",
#                dqs         => "`qdel $jobId`",
#                loadleveler => "`llcancel $jobId`",
#                lsf         => "`bkill $jobId`",
                'pbs':["qdel $jobId"],
                #pbsxt       => "`qdel $jobId`",
                #pbssgi      => "`qdel $jobId`",
                'sge':["qdel $jobId"],
                'slurm':["scancel $jobId"],
                #shell       => "kill(9, $jobId)"
}
killExprs['pbsxt']=killExprs['pbs']
killExprs['pbssgi']=killExprs['pbs']


def GetLocalTaskDir(resourceName,appName,timeStamp):
    taskDir=os.path.join(akrrcfg.data_dir,resourceName,appName,timeStamp)
    if not os.path.isdir(taskDir):
            raise IOError("Directory %s does not exist or is not directory."%(taskDir))
    return taskDir



class akrrTaskHandlerBase:
    """
    the schadule will activate the task on timeToSubmit and reschedule new task on repetition
    
    timeToSubmit==None means run now
    reschedule==None means run only once
    
    possible statuses
    Scheduled
    """
    def __init__(self,task_id,resourceName,appName,resourceParam,appParam,taskParam,timeToSubmit=None,repetition=None,timeStamp=None):
        self.resourceName=resourceName
        self.appName=appName
        self.resourceParam=eval(resourceParam)
        self.appParam=eval(appParam)
        self.taskParam=copy.deepcopy(akrrcfg.default_task_params)
        self.taskParam.update(eval(taskParam))
        self.timeToSubmit=timeToSubmit
        self.repetition=repetition
        self.task_id=task_id
        
        self.resource = None
        self.app = None
        
        #just check that resource and app exists
        self.resource = akrrcfg.FindResourceByName(self.resourceName)
        self.app = akrrcfg.FindAppByName(self.appName)
        
        
        
        self.timeStamp=self.CreateLocalDirectoryForTask()
        #set a directory for task already should exists
        self.SetDirNames(akrrcfg.data_dir)
        self.remoteTaskDir=self.GetRemoteTaskDir(self.resource['akrrdata'],self.appName,self.timeStamp)
        
        self.oldstatus="Does not exist"
        self.status="Activated"
        self.statusinfo="Activated"
        self.LastPickledState=-1
        self.FatalErrorsCount=0
        self.ToDoNextString="FirstStep"
        self.oldToDoNextString="Does not exist"
    def SetDirNames(self,akrrdata_dir):
        self.resourceDir=os.path.join(akrrdata_dir,self.resourceName)
        self.appDir=os.path.join(self.resourceDir,self.appName)
        self.taskDir=os.path.join(self.appDir,self.timeStamp)
    def GetRemoteTaskDir(self,akrrdata_dir,appName,timeStamp):
        return os.path.join(akrrdata_dir,appName,timeStamp)
    def GetJobScriptName(self,appName):
        return appName+".job"
    def IsStateChanged(self):
        if self.oldstatus==self.status and self.ToDoNextString==self.oldToDoNextString:return False
        else: return True
        
    def ToDoNext(self):
        ""
        funToDo=getattr(self,self.ToDoNextString)
        if funToDo==None:
            raise IOError("ToDoNext is None!")
        return funToDo()
            
    def Terminate(self):
        """return True is task can be safely removed from the DB"""
        return True
    def CreateLocalDirectoryForTask(self):
        #create a directory for task
        resourceDir=os.path.join(akrrcfg.data_dir,self.resourceName)
        appDir=os.path.join(resourceDir,self.appName)
        timeStamp=datetime.datetime.today().strftime("%Y.%m.%d.%H.%M.%S.%f")
        taskDir=os.path.join(appDir,timeStamp)
        #print timeStamp
        #print taskDir
        
        if not os.path.isdir(akrrcfg.data_dir):
            raise IOError("Directory %s does not exist or is not directory."%(akrrcfg.data_dir))
        if not os.path.isdir(resourceDir):
            print("Directory %s does not exist, creating it."%(resourceDir))
            os.mkdir(resourceDir)
        if not os.path.isdir(appDir):
            print("Directory %s does not exist, creating it."%(appDir))
            os.mkdir(appDir)
        if not os.path.isdir(akrrcfg.completed_tasks_dir):
            raise IOError("Directory %s does not exist or is not directory."%(akrrcfg.completed_tasks_dir))
        if not os.path.isdir(os.path.join(akrrcfg.completed_tasks_dir,self.resourceName)):
            print("Directory %s does not exist, creating it."%(os.path.join(akrrcfg.completed_tasks_dir,self.resourceName)))
            os.mkdir(os.path.join(akrrcfg.completed_tasks_dir,self.resourceName))
        if not os.path.isdir(os.path.join(akrrcfg.completed_tasks_dir,self.resourceName,self.appName)):
            print("Directory %s does not exist, creating it."%(os.path.join(akrrcfg.completed_tasks_dir,self.resourceName,self.appName)))
            os.mkdir(os.path.join(akrrcfg.completed_tasks_dir,self.resourceName,self.appName))
            
        while os.path.exists(taskDir)==True:
            print(os.path.exists(taskDir))
            timeStamp=datetime.datetime.today().strftime("%Y.%m.%d.%H.%M.%S.%f")
            taskDir=os.path.join(appDir,timeStamp)
        print("Creating task directory: %s"%(taskDir))
        os.mkdir(taskDir)
        print("Creating task directories: \n\t%s\n\t%s"%(os.path.join(taskDir,"jobfiles"),os.path.join(taskDir,"proc")))
        os.mkdir(os.path.join(taskDir,"jobfiles"))
        os.mkdir(os.path.join(taskDir,"proc"))
        return timeStamp
    def IamDone(self):
        print("IamDone",self.taskDir)
        time.sleep(1)
        self.status="Done"
        self.statusinfo="IamDone"
        return None
    def FirstStep(self):
        print("IamDone",self.taskDir)
        time.sleep(1)
        self.status="FirstStep"
        self.statusinfo="FirstStep"
        self.ToDoNextString="IamDone"
        return datetime.timedelta(days=0, hours=0, minutes=3)
    def Activate123(self):
        """Set the task directory initiate all scripts"""
        self.status="Activating"
        
        #find resource
        self.resource = akrrcfg.FindResourceByName(self.resourceName)
        if self.resource.get('active',True)==False:
            raise akrrcfg.akrrError(akrrcfg.ERROR_CANT_CONNECT,"%s is marked as inactive in AKRR"%(self.resourceName))
        
        #find app
        self.app = akrrcfg.FindAppByName(self.appName)
        
        
        self.CreateBatchJobScriptAndSubmitIt()
        #creating batch files input files etc
        self.status="Activated"
        self.ToDoNext=self.CheckTheQueue
#    def CopyInputFilesToRemoteMachine(self):
#        self.status="Copying input files to remote machine"
#        self.status="Input files was copied to remote machine"
#    def SubmitJobToQueue(self):
#        self.status="Submiting job to queue"
#        self.status="Job was submited to queue"
#    def CheckTheQueue(self):
#        sh=None
#        try:
#            from string import Template
#            wE=waitExprs[self.resource['batchScheduler']]
#            cmd =Template(wE[0]).substitute(jobId=str(self.RemoteJobID))
#            rege=Template(wE[2]).substitute(jobId=str(self.RemoteJobID))
#            msg=akrrcfg.sshResource(self.resource,cmd)
#            matchObj= wE[1](rege,msg,wE[3])
#            if matchObj:
#                print "Still in queue. Either waiting or running"
#            else:
#                print "Not in queue. Either exited with error or executed successfully."
#                self.ToDoNext=self.CopyOutputFilesFromRemoteMachine
#            #print msg
#        except:
#            if sh!=None:
#                sh.sendline("exit")
#                sh.close(force=True)
#                del sh
#            raise
#        if 0:
#            self.status="Checking the queue"
#            self.status="Still in the queue"
#            self.status="Running"
#            self.status="PossibleProblems"
#            self.status="Done"
    def CopyOutputFilesFromRemoteMachine(self):
        self.status="Copying output files from remote machine"
        print(self.status)
        exit(0)
        self.status="Output files was copied from remote machine"
    def ProcessOutput(self):
        self.status="Processing output files"
        self.status="Output files were processed"
    def Archiving(self):
        self.status="Archiving results"
        self.status="Done"
        
    
    def CreateBatchJobScriptOnSrv(self):
        import subprocess
        import sys
        self.JobScriptName=self.appName+".job"
        
        #switch working directory to taskDir
        wd=os.getcwd()
        os.chdir(self.taskDir)
        
        print("Writing JobScript to:",os.path.join(self.taskDir,self.JobScriptName))
        fout=open(os.path.join(self.taskDir,self.JobScriptName),'w')
        
        #arg_bin_path=self.app['arg_bin_path']
        execstr="%s -bin_path=\"%s\" -help=%s -log=%d -verbose=%d -version=%s"%(self.app['name'],
            self.resource['bin_path'],
            self.app.get('arg_help','no'),
            self.app.get('arg_log',0),
            self.app.get('arg_verbose',1),
            self.app.get('arg_version','no'),
        )
        
        args="""     export PERL5LIB=/home/mikola/xdtas/incaReporterManager-edge/lib/perl:\
/home/mikola/xdtas/incaReporterManager-edge/var/reporter-packages/lib/perl   
~/xdtas/incaReporterManager-edge/var/reporter-packages/bin/xdmod.batch.wrapper \
-scheduler="sge" -queue="normal" -submitparam="-V" -nodes=:8:8 -type="16way" \
-walllimit=13 -exec="%s"
        """%(execstr)
        subprocess.call(args, stdout=fout,stderr=sys.stdout, shell=True)
        fout.close()
        
        #switch working directory back
        os.chdir(wd)
    def DeleteLocalFolder(self):
        if os.path.isdir(self.taskDir):
            if self.taskDir!='/' and self.taskDir!=os.getenv("HOME"):
                import shutil
                shutil.rmtree(self.taskDir,True)
    def DeleteRemoteFolder(self):
        #trying to be carefull 
        if self.remoteTaskDir=='/':
            raise IOError("can not remove /")
        
        #should remove ../../ etc
        rt=os.path.normpath(self.remoteTaskDir)
        ad=os.path.normpath(self.resource['akrrdata'])
        if rt==ad:
            raise IOError("can not remove akrrdata")
        if os.path.commonprefix([rt,ad])!=ad:
            raise IOError("can not remove remote task folder. The folder should be in akrrdata")
        
        print("removing remote task folder:\n\t%s"%(self.remoteTaskDir))
        msg=akrrcfg.sshResource(self.resource,"rm -rf \"%s\""%(self.remoteTaskDir))
        print(msg)
        
  
    def WriteErrorXML(self, filename,bCDATA=False):
        content="""<body>
 <xdtas>
  <batchJob>
   <status>Error</status>
   <errorCause>%s</errorCause>
   <reporter>%s</reporter>
   <errorMsg>%s</errorMsg>
  </batchJob>
 </xdtas>
</body> 
"""%(self.status,self.appName,self.statusinfo)
        if bCDATA:
            content="""<body>
 <xdtas>
  <batchJob>
   <status>Error</status>
   <errorCause>%s</errorCause>
   <reporter>%s</reporter>
   <errorMsg><![CDATA[%s]]></errorMsg>
  </batchJob>
 </xdtas>
</body> 
"""%(self.status,self.appName,self.statusinfo)
        #now lets try to read to parce it
        import xml.etree.ElementTree as ET
        try:
            tree = ET.fromstring(content)
        except:
            print("Cannot write readable XML file, will try CDATA declaration")
            content="""<body>
 <xdtas>
  <batchJob>
   <status>Error</status>
   <errorCause>%s</errorCause>
   <reporter>%s</reporter>
   <errorMsg><![CDATA[%s]]></errorMsg>
  </batchJob>
 </xdtas>
</body> 
"""%(self.status,self.appName,self.statusinfo)
            try:
                tree = ET.fromstring(content)
            except:
                print("Cannot write readable XML file!!!")
                #raise
        
        fout=open(filename,"w")
        fout.write(content)
        fout.close()
