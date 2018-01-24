from . import akrrcfg
import os
import sys
#namdSizes
import datetime
import time

import re

from .akrrtaskappker import akrrTaskHandlerAppKer
from .akrrtaskbundle import akrrTaskHandlerBundle


def GetLocalTaskDir(resourceName,appName,timeStamp,TaskIsActive=True):
    if TaskIsActive:
        taskDir=os.path.join(akrrcfg.data_dir,resourceName,appName,timeStamp)
        if not os.path.isdir(taskDir):
                raise IOError("Directory %s does not exist or is not directory."%(taskDir))
        return taskDir
    else:
        taskDir=os.path.join(akrrcfg.completed_tasks_dir,resourceName,appName,timeStamp)
        if not os.path.isdir(taskDir):
                raise IOError("Directory %s does not exist or is not directory."%(taskDir))
        return taskDir


   
original_stderr=None
original_stdout=None
log_file=None

def RedirectStdoutToLog(logfilename):
    global original_stderr
    global original_stdout
    global log_file
    
    if log_file!=None:
        raise IOError("stdout was already redirected once")
    
    
    log_file = open(logfilename, "a")
    original_stderr = sys.stderr
    original_stdout = sys.stdout
    
    sys.stderr = log_file
    sys.stdout = log_file
    
    timenow=datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    print(">>> "+timenow+" "+">"*96)
    
def RedirectStdoutBack():
    global original_stderr
    global original_stdout
    global log_file
    
    if log_file!=None:
        
        
        timenow=datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        print("<<< "+timenow+" "+"<"*96+"\n")
        
        sys.stderr=original_stderr
        sys.stdout=original_stdout
        
        log_file.close()
        
        original_stderr=None
        original_stdout=None
        log_file=None
    else:
        raise IOError("stdout was not redirected here")
def akrrGetNewTaskHandler(task_id,resourceName,appName,resourceParam,appParam,task_param,timeToSubmit=None,repetition=None,timeStamp=None):
    """return new instance of akrrTaskHandler. based on resourceName,appName,resourceParam,appParam it can give different handlers...in the feture"""
    if appName.count("bundle")>0:
        return akrrTaskHandlerBundle(task_id,resourceName,appName,resourceParam,appParam,task_param,timeToSubmit,repetition,timeStamp)
    else:
        return akrrTaskHandlerAppKer(task_id,resourceName,appName,resourceParam,appParam,task_param,timeToSubmit,repetition,timeStamp)
def akrrGetTaskHandler(resourceName,appName,timeStamp):
    """return instance of akrrTaskHandler"""
    procTaskDir=os.path.join(akrrcfg.data_dir,resourceName,appName,timeStamp,'proc')
    LastPickledState=-1
    for f in os.listdir(procTaskDir):
        m=re.match("(\d+).st",f,0)
        if m!=None:
            istate=int(m.group(1))
            if istate>LastPickledState:LastPickledState=istate
    if LastPickledState<0:
        raise IOError("Can not find pickeled file (%s) for task handler"%(procTaskDir+"/*.st"))
    picklefilename=os.path.join(procTaskDir,"%06d.st"%(LastPickledState))
    print("Read pickeled task handler from:\n\t%s\n"%(picklefilename))
    return akrrGetTaskHandlerFromPkl(picklefilename)

def akrrGetTaskHandlerFromJobDir(job_dir):
    procTaskDir=os.path.abspath(os.path.join(job_dir,"..","proc"))
    if os.path.isdir(procTaskDir):
        LastPickledState=-1
        for f in os.listdir(procTaskDir):
            m=re.match("(\d+).st",f,0)
            if m!=None:
                istate=int(m.group(1))
                if istate>LastPickledState:LastPickledState=istate
        if LastPickledState<0:
            raise IOError("Can not find pickeled file (%s) for task handler"%(procTaskDir+"/*.st"))
        picklefilename=os.path.join(procTaskDir,"%06d.st"%(LastPickledState))
        print("Read pickeled task handler from:\n\t%s\n"%(picklefilename))
        return akrrGetTaskHandlerFromPkl(picklefilename)
    return None
    
def akrrGetTaskHandlerFromPkl(picklefilename):
    import pickle
    fin=open(picklefilename,"rb")
    th=pickle.load(fin)
    fin.close()
    import copy
    
    #Compatibility with old versions
    #*resource misspelling 
    if hasattr(th, 'resourseName'):
        th.resourceName=th.resourseName
        del th.resourseName
    
    #renew and update some variables
    th.oldstatus=copy.deepcopy(th.status)
    th.oldToDoNextString=copy.deepcopy(th.ToDoNextString)
    
    th.resource = akrrcfg.FindResourceByName(th.resourceName)
    th.app = akrrcfg.FindAppByName(th.appName)
    
    return th
def akrrDumpTaskHandler(th):
    th.LastPickledState+=1
    picklefilename=os.path.join(th.taskDir,"proc/","%06d.st"%(th.LastPickledState))
    import pickle
    resource = th.resource
    app = th.app
    th.resource = None
    th.app = None
    
    fout=open(picklefilename,"wb")
    pickle.dump(th,fout,akrrcfg.task_pickling_protocol)
    fout.close()
    
    print("\nSaved pickeled task handler to:\n\t%s"%(picklefilename))
    th.resource = resource
    th.app = app
#if __name__ == '__main__':  
#    def addTask(resourceName,appName,resourceParam,appParam,timeToSubmit=None,repetition=None):
#        """
#        
#        timeToSubmit==None means start right now
#        """
#        
#        #if not os.access(akrrcfg.data_dir, os.W_OK)
#        
#        #if not os.path.isdir(akrrcfg.data_dir):
#        
#        print timeToSubmit
#        print repetition
#        print (timeToSubmit+repetition)
#        print akrrcfg.data_dir
#        
#    
#    
#    t=akrrTask('ranger','xdmod.app.md.namd',{},{'ncpus':16},
#        datetime.datetime.today(),
#        datetime.timedelta(7))
#    t.Activate()
#    
#    while True:
#        t.ToDoNext()
#        time.sleep(60)
if __name__ == "__main__":
    """stand alone testing"""
    print("stand alone testing")
    if len(sys.argv)<=1:
        print("wrong number of arguments")
        exit()
    
    akrrcfg.PrintOutResourceAndAppSummary()
    
    if sys.argv[1]=="start":
        if len(sys.argv)<5:
            print("Not enough arguments")
            exit()
        print(sys.argv)
        resourceName=sys.argv[2]
        appName=sys.argv[3]
        resourceParam=sys.argv[4]
        appParam="{}"
        if len(sys.argv)>6:appParam=sys.argv[5]
        taskParam="{}"
        if len(sys.argv)>7:taskParam=sys.argv[6]
        groupID="Test"
        if len(sys.argv)>8:groupID=sys.argv[7]
        task_id=1
        
        print("resourceName:",resourceName)
        print("appName:",appName)
        print("resourceParam:",resourceParam)
        print("appParam:",appParam)
        print("taskParam:",taskParam)
        print("groupID:",groupID)
        print() 
        
        TaskHandler=akrrGetNewTaskHandler(task_id,resourceName,appName,resourceParam,appParam,taskParam,timeStamp='test')
        TaskHandler.CreateBatchJobScriptAndSubmitIt()
        #resourceName,"xdmod.benchmark.hpcc","{'ncpus':%d}"%(ncpus),"{}","{}",groupid)
    
