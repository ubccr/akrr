import akrr
import os
import sys
#namdSizes
import datetime
import time
import traceback
import re
import copy
import MySQLdb

from akrrtaskbase import akrrTaskHandlerBase,submitCommands,jidExtractPatterns,waitExprs,active_task_default_attempt_repeat,killExprs
from akrrappkeroutputparser import AppKerOutputParser
 
class akrrTaskHandlerAppKer(akrrTaskHandlerBase):
    """Task Handler for AppKernel execution and processing"""
    def FirstStep(self):
        #
        #self.status="FirstStep2"
        #self.statusinfo="FirstStep2"
        #self.ToDoNextString="FirstStep2"
        #return datetime.timedelta(days=0, hours=0, minutes=1)
        return self.CreateBatchJobScriptAndSubmitIt()
    def GenerateBatchJobScript(self):
        if not hasattr(self, 'JobScriptName'):
            self.JobScriptName=self.GetJobScriptName(self.appName)
        #get walltime from DB
        dbdefaults={}
        try:
            db,cur=akrr.getDB()
            
            cur.execute('''SELECT resource,app,resource_param,app_param FROM ACTIVETASKS
            WHERE task_id=%s ;''',(self.task_id,))
            raw=cur.fetchall()
            if len(raw)>0:
                (resource,app,resource_param,app_param)=raw[0]
            
                cur.execute("""SELECT walllimit
                    FROM akrr_default_walllimit
                    WHERE resource=%s AND app=%s AND resource_param=%s AND app_param=%s """,(resource,app,resource_param,app_param))
                raw=cur.fetchall()
            
                if len(raw)>0:
                    dbdefaults['walllimit']=raw[0][0]
            
            #db.commit()
            cur.close()
            del db
        except Exception as e:
            pass
            raise e
        #create job-script
        try:
            batchvars={}
            appkernelOnResource={}
            if 'appkernelOnResource' in self.app:
                if  self.resourceName in self.app['appkernelOnResource']:
                    appkernelOnResource=self.app['appkernelOnResource'][self.resourceName]
                elif 'default' in self.app['appkernelOnResource']:
                    appkernelOnResource=self.app['appkernelOnResource']['default']
                
            #print "#"*80
            for di in [self.resource,self.app,appkernelOnResource,dbdefaults,self.resourceParam, self.appParam]:
                batchvars.update(di)
            
                     
            #get autowalltime limit
            try:
                if 'autoWalltimeLimit' in batchvars and batchvars['autoWalltimeLimit']==True:
                    print "\nautoWalltimeLimit is on, trying to estimate walltime limit..."
                    autoWalltimeLimitOverhead=1.2
                    if 'autoWalltimeLimitOverhead' in batchvars:
                        autoWalltimeLimitOverhead=batchvars['autoWalltimeLimitOverhead']+1.0
                    #query last 20 executions of this appkernel on that resource with that node count
                
                    db,cur=akrr.getDB(True)
                    
                    cur.execute('''SELECT resource,reporter,reporternickname,collected,status,walltime FROM akrr_xdmod_instanceinfo
                        WHERE  `resource`=%s AND `reporternickname` =  %s
                        ORDER BY  `akrr_xdmod_instanceinfo`.`collected` DESC 
                        LIMIT 0 , 20''',(self.resource['name'],"%s.%d"%(self.app['name'],batchvars['nnodes'])))
                    
                    raw=cur.fetchall()
                    
                    i=0
                    lastFiveRunsSuccessfull=True
                    maxwalltime=0.0
                    for r in raw:
                        if i<5 and r['status']==0:
                            lastFiveRunsSuccessfull=False
                        if r['status']==1 and r['walltime']>maxwalltime:
                            maxwalltime=r['walltime']
                        i+=1
                    if i<5:
                        print "There are only %d previous run, need at least 5 for walltime limit autoset"
                    else:
                        if lastFiveRunsSuccessfull == False:
                            print "One of last 5 runs have failed. Would not use autoset."
                        else:
                            print "Max walltime was %.1f s, will change walltime limit from %.1f minutes to %d minutes"%(maxwalltime,batchvars['walllimit'],int(autoWalltimeLimitOverhead*maxwalltime/60.0+0.99))
                            batchvars['walllimit']=int((autoWalltimeLimitOverhead*maxwalltime/60.0+0.99))
                    print
                    cur.close()
                    del db
            except Exception as e:
                pass
            
            
            #calculate NNodes and NCores
            tmpNNodes=None
            tmpNCores=None
            if batchvars.has_key('nnodes'):
                tmpNNodes=batchvars['nnodes']
                tmpNCores=tmpNNodes*batchvars['ppn']
            else:
                tmpNCores=batchvars['ncores']
                if tmpNCores%batchvars['ppn']==0:
                    tmpNNodes=tmpNCores/batchvars['ppn']
                else:
                    tmpNNodes=(tmpNCores/batchvars['ppn'])+1
            
            batchvars['akrrNCores']=tmpNCores
            batchvars['akrrNNodes']=tmpNNodes
            
            #Set batchvars remaps
            batchvars['akrrPPN']=batchvars['ppn']
            batchvars['akrrNCoresToBorder']=batchvars['akrrPPN']*batchvars['akrrNNodes']
            batchvars['akrrTaskWorkingDir']=self.remoteTaskDir
            batchvars['akrrWallTimeLimit']="%02d:%02d:00"%(int(batchvars['walllimit'])/60,int(batchvars['walllimit'])%60)
            #batchvars['localPATH']=akrr.sshCommand(sh,"echo $PATH").strip()
            batchvars['akrrAppKerName']=self.app['name']
            batchvars['akrrResourceName']=self.resource['name']
            batchvars['akrrTimeStamp']= self.timeStamp
            if batchvars['akrrNNodes']==1: batchvars['akrrPPN4NodesOrCores4OneNode']=batchvars['akrrNCores']
            else: batchvars['akrrPPN4NodesOrCores4OneNode']=batchvars['akrrPPN']
            
            if 'nodeListSetterTemplate' not in batchvars:
                batchvars['nodeListSetterTemplate']=batchvars['nodeListSetter'][batchvars['batchScheduler']]
            #set AppKerLauncher
            #if 'runScript' in batchvars:
            #    if self.resource['name'] in batchvars['runScript']:
            #        batchvars['akrrStartAppKer']=akrr.formatRecursively(batchvars['runScript'][self.resource['name']],batchvars,keepDoubleBrakets=True)
            #    else:
            #        batchvars['akrrStartAppKer']=akrr.formatRecursively(batchvars['runScript']['default'],batchvars,keepDoubleBrakets=True)
                
            
            #process templates
            batchvars['akrrCommonCommands']=akrr.formatRecursively(batchvars['akrrCommonCommandsTemplate'],batchvars,keepDoubleBrakets=True)
            #batchvars['akrrCommonTests']=akrr.formatRecursively(batchvars['akrrCommonTestsTemplate'],batchvars,keepDoubleBrakets=True)
            #batchvars['akrrStartAppKer']=batchvars['akrrStartAppKerTemplate'].format(**batchvars)
            batchvars['akrrCommonCleanup']=akrr.formatRecursively(batchvars['akrrCommonCleanupTemplate'],batchvars,keepDoubleBrakets=True)
            
            #specially for IOR request two nodes for single node benchmark, one for read and one for write
            if batchvars['requestTwoNodesForOneNodeAppKer']==True and batchvars['akrrNNodes']==1 and 'batchJobHeaderTemplate' in batchvars:
                batchvars2=copy.deepcopy(batchvars)
                batchvars2['akrrNCores']=2*batchvars['akrrNCores']
                batchvars2['akrrNNodes']=2*batchvars['akrrNNodes']
                batchvars2['akrrNCoresToBorder']=2*batchvars['akrrNCoresToBorder']
                batchvars2['akrrPPN4NodesOrCores4OneNode']=batchvars['akrrPPN']
                batchvars['batchJobHeaderTemplate']=akrr.formatRecursively(batchvars2['batchJobHeaderTemplate'],batchvars2)
                pass
            
            #do parameters adjustment
            if 'process_params' in batchvars:
                batchvars['process_params'](batchvars)
            
            #generate job script
            jobScript=akrr.formatRecursively(self.resource["batchJobTemplate"],batchvars)
            jobScriptFullPath=os.path.join(self.taskDir,"jobfiles",self.JobScriptName)
            fout=open(jobScriptFullPath,"w")
            fout.write(jobScript)
            fout.close()
        except Exception as e:
            self.status="ERROR: Can not created batch job script"
            self.statusinfo=traceback.format_exc()
            akrr.printException(self.status)
            raise e
    def CreateBatchJobScriptAndSubmitIt(self,doNotSubmitToQueue=False):
        self.JobScriptName=self.GetJobScriptName(self.appName)
        print "### Creating batch job script and submitting it to remote machine"
        #as a current bypass will create a job script remotely and copy it here
        #get ssh to remote resource
        
        sh=None
        try:
            sh=akrr.sshResource(self.resource)
            #Create remote directories if needed
            def CheckAndCreateDir(self,sh,d):
                cmd="if [ ! -d  \"%s\" ]\n then mkdir \"%s\"\n fi"%(d,d)
                akrr.sshCommand(sh,cmd)
                cmd="if [ -d \"%s\" ]\n then \necho EXIST\n else echo DOESNOTEXIST\n fi"%(d)
                msg=akrr.sshCommand(sh,cmd)
                if msg.find("DOESNOTEXIST")>=0:
                    raise akrr.akrrError(akrr.ERROR_REMOTE_FILES,"Can not create directory %s on %s."%(d,self.resource['name']))
            #akrrdata
            CheckAndCreateDir(self,sh,self.resource['akrrdata'])
            #dir for app
            CheckAndCreateDir(self,sh,os.path.join(self.resource['akrrdata'],self.appName))
            #dir for task
            CheckAndCreateDir(self,sh,self.remoteTaskDir)
            #CheckAndCreateDir(self,sh,os.path.join(self.remoteTaskDir,"batchJob_pl"))
            
            #cd to remoteTaskDir
            akrr.sshCommand(sh,"cd %s"%(self.remoteTaskDir))
            
            #GenerateBatchJobScript
            self.GenerateBatchJobScript()
            
            msg=akrr.scpToResource(self.resource,os.path.join(self.taskDir,"jobfiles",self.JobScriptName),os.path.join(self.remoteTaskDir))
            if doNotSubmitToQueue:
                return
            ##akrr.sshCommandNoReturn(sh,"cat > %s << EOF1234567\n%s\nEOF1234567\n"%(self.JobScriptName,jobScript))
            akrr.sshCommand(sh,"cat %s "%(self.JobScriptName))
            
            #send to queue
            from string import Template
            JobID=0
            if not 'masterTaskID' in self.taskParam:
                #i.e. submit to queue only if task is independent
                sendToQueue=Template(submitCommands[self.resource['batchScheduler']]).substitute(scriptPath=self.JobScriptName)
                msg=akrr.sshCommand(sh,sendToQueue)
                matchObj=re.search(jidExtractPatterns[self.resource['batchScheduler']],msg,re.M|re.S)
                
                if matchObj:
                    try:
                        JobID=int(matchObj.group(1))
                    except:
                        raise akrr.akrrError(akrr.ERROR_REMOTE_JOB,"Can't get job id:\n"+msg)
                else:
                    raise akrr.akrrError(akrr.ERROR_REMOTE_JOB,"Can't get job id:\n"+msg)
            
            akrr.sshCommand(sh,"echo %d > job.id"%(JobID))
            
            self.RemoteJobID=JobID
            self.TimeJobSubmetedToRemoteQueue=datetime.datetime.today()
            
            
            sh.sendline("exit")
            sh.close(force=True)
            del sh
            sh=None
            print "\nRemoteJobID=",self.RemoteJobID
            print "copying files from remote machine"
            msg=akrr.scpFromResource(self.resource,os.path.join(self.remoteTaskDir,"*"),os.path.join(self.taskDir,"jobfiles"),"-r")
            
            #update DB time_submitted_to_queue
            db,cur=akrr.getDB()
            
            cur.execute('''UPDATE ACTIVETASKS
            SET time_submitted_to_queue=%s
            WHERE task_id=%s ;''',(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"),self.task_id))
            
            cur.close()
            del db
            
            if not 'masterTaskID' in self.taskParam:
                #i.e. idepentent task
                self.status="Created batch job script and have submitted it to remote queue."
                self.statusinfo="Remote job ID is %d"%(self.RemoteJobID)
                self.ToDoNextString="CheckTheJobOnRemoteMachine"
                
                #check first time in 1 minute
                return datetime.timedelta(days=0, hours=0, minutes=1)
            else:
                #i.e. this is subtask
                 #i.e. idepentent task
                self.status="Created batch job script."
                self.statusinfo="Created batch job script. Waiting for master task to execute it."
                self.ToDoNextString="CheckTheJobOnRemoteMachine"
                
                #master task will update the time when it will finish task execution 
                return datetime.timedelta(days=111*365)
            
        except Exception as e:
            if sh!=None:
                sh.sendline("exit")
                sh.close(force=True)
                del sh
            self.status="ERROR Can not created batch job script and submit it to remote queue"
            self.statusinfo=traceback.format_exc()
            if akrr.max_fails_to_submit_to_the_queue>=0:
                if hasattr(self, "FailsToSubmitToTheQueue"):
                    self.FailsToSubmitToTheQueue+=1
                    if (self.FailsToSubmitToTheQueue>akrr.max_fails_to_submit_to_the_queue or
                            (self.taskParam['test_run']==True and self.FailsToSubmitToTheQueue>=2)):
                        #Stop execution of the task and submit results to db
                        self.ToDoNextString="PushToDB"
                        resultFile=os.path.join(self.taskDir,"result.xml")
                        self.WriteErrorXML(resultFile)
                        return  datetime.timedelta(seconds=3)
                else:
                    self.FailsToSubmitToTheQueue=1
            else:
                self.FatalErrorsCount+=1
            
            akrr.printException(self.status)
            return akrr.repeat_after_fails_to_submit_to_the_queue
    def CheckTheJobOnRemoteMachine(self):
        sh=None
        try:
            print "### Checking the job status on remote machine"
            from string import Template
            
            sh=akrr.sshResource(self.resource)
            
            #if it is subtask get master task id from job.id file (it should be replaced by master task)
            if self.RemoteJobID==0:
                try:
                    print self.remoteTaskDir
                    self.RemoteJobID=int(akrr.sshCommand(sh,"cat %s"%(os.path.join(self.remoteTaskDir,"job.id"))))
                except:
                    self.RemoteJobID=0
            
            wE=waitExprs[self.resource['batchScheduler']]
            cmd =Template(wE[0]).substitute(jobId=str(self.RemoteJobID))
            rege=Template(wE[2]).substitute(jobId=str(self.RemoteJobID))
            
            
            msg=akrr.sshCommand(sh,cmd)
            sh.sendline("exit")
            sh.close(force=True)
            del sh
            
            if self.RemoteJobID==0:
                return active_task_default_attempt_repeat
            
            matchObj= wE[1](rege,msg,wE[3])
            if matchObj:
                print "Still in queue. Either waiting or running"
                if datetime.datetime.today()-self.TimeJobSubmetedToRemoteQueue>self.taskParam.get('MaxTimeInQueue',akrr.max_time_in_queue):
                    print "ERROR:"
                    print "Job exceeds the maximal time in queue (%s). And will be terminated."%(str(self.taskParam.get('MaxTimeInQueue',akrr.max_time_in_queue)))
                    print "Removing job from remote queue."
                    self.Terminate()
                    print "copying files from remote machine"
                    akrr.scpFromResource(self.resource,os.path.join(self.remoteTaskDir,"*"),os.path.join(self.taskDir,"jobfiles"),"-r")
                    #print msg
                    print "Deleting all files from remote machine"
                    self.DeleteRemoteFolder()
                    self.status="ERROR: Job exceeds the maximal time in queue (%s) and was terminated."%(str(self.taskParam.get('MaxTimeInQueue',akrr.max_time_in_queue)))
                    self.statusinfo="\nLast Status report:\n"+msg
                    self.ReportFormat="Error"
                    self.ToDoNextString="ProccessResults"
                    #del self.RemoteJobID
                    return datetime.timedelta(seconds=3)
                
                self.status="Still in queue. Either waiting or running"
                self.statusinfo=msg
                return active_task_default_attempt_repeat
            else:
                print "Not in queue. Either exited with error or executed successfully."
                print "copying files from remote machine"
                msg=akrr.scpFromResource(self.resource,os.path.join(self.remoteTaskDir,"*"),os.path.join(self.taskDir,"jobfiles"),"-r")
                #print msg
                print "Deleting all files from remote machine"
                self.DeleteRemoteFolder()
                self.status="Not in queue. Either exited with error or executed successfully. Copied all files to local machine. Deleted all files from remote machine"
                self.statusinfo="Not in queue. Either exited with error or executed successfully. Copied all files to local machine. Deleted all files from remote machine"
                self.ToDoNextString="ProccessResults"
                #del self.RemoteJobID
                self.TimeJobPossiblyCompleted=datetime.datetime.today()
                return datetime.timedelta(seconds=3)
            #print msg
        except:
            if hasattr(locals(),'sh') and sh!=None:
                sh.sendline("exit")
                sh.close(force=True)
                del sh
            self.status="ERROR Can not check the status of the job on remote resource"
            self.statusinfo=traceback.format_exc()
            self.FatalErrorsCount+=1
            akrr.printException(self.status)
            return active_task_default_attempt_repeat
        self.status="CheckTheJobOnRemoteMachine"
        self.statusinfo="CheckTheJobOnRemoteMachine"
        self.ToDoNextString="CheckTheJobOnRemoteMachine"
        return datetime.timedelta(days=0, hours=0, minutes=2)
    def GetResultFiles(self,raiseError=False):
        jobfilesDir=os.path.join(self.taskDir,"jobfiles")
        batchJobDir=None
        stdoutFile=None
        stderrFile=None
        appstdoutFile=None
        taskexeclogFile=None
        
        for d in os.listdir(jobfilesDir):
            if re.match("batchJob",d):
                if batchJobDir==None: batchJobDir=os.path.join(jobfilesDir,d)
                else:
                    if raiseError:raise IOError("Error: found multiple batchJob* Directories although it should be one")
                    else: return (batchJobDir,stdoutFile,stderrFile,appstdoutFile)
                
        if batchJobDir!=None:
            for f in os.listdir(batchJobDir):
                if re.match("sub.*\.stdout",f):
                    if stdoutFile==None: stdoutFile=os.path.join(batchJobDir,f)
                    elif raiseError: raise IOError("Error: found multiple sub*.stdout files although it should be one")
                if re.match("sub.*\.stderr",f):
                    if stderrFile==None: stderrFile=os.path.join(batchJobDir,f)
                    elif raiseError: raise IOError("Error: found multiple sub*.stderr files although it should be one")
                if re.match("sub.*\.appstdout",f):
                    if appstdoutFile==None: appstdoutFile=os.path.join(batchJobDir,f)
                    elif raiseError: raise IOError("Error: found multiple sub*.appstdout files although it should be one")
        else:
            batchJobDir=jobfilesDir
            for f in os.listdir(jobfilesDir):
                if re.match("stdout",f):
                    if stdoutFile==None: stdoutFile=os.path.join(jobfilesDir,f)
                    elif raiseError: raise IOError("Error: found multiple sub*.stdout files although it should be one")
                if re.match("stderr",f):
                    if stderrFile==None: stderrFile=os.path.join(jobfilesDir,f)
                    elif raiseError: raise IOError("Error: found multiple sub*.stderr files although it should be one")
                if re.match("appstdout",f):
                    if appstdoutFile==None: appstdoutFile=os.path.join(jobfilesDir,f)
                    elif raiseError: raise IOError("Error: found multiple sub*.appstdout files although it should be one")
            if os.path.isfile(os.path.join(self.taskDir,"proc","log")):
                taskexeclogFile=os.path.join(self.taskDir,"proc","log")
        if batchJobDir==None or stdoutFile==None or stderrFile==None:
            if raiseError:raise IOError("Error: standard files is not present among job-files copied from remote resource.")
        return (batchJobDir,stdoutFile,stderrFile,appstdoutFile,taskexeclogFile)
    def ProccessResults(self,Verbose=True):
        if not self.app.has_key('parser'):
            return self.ProccessResultsOld(Verbose)
        if Verbose:print "Processing the output"
        try:
            jobfilesDir=os.path.join(self.taskDir,"jobfiles")
            resultFile=os.path.join(self.taskDir,"result.xml")
            print resultFile
            #get job.id (from remote machine) of master node
            if self.RemoteJobID==0: #i.e. this is a subtask of a bundle
                if os.path.isfile(os.path.join(jobfilesDir,"job.id")):
                    fin=open(os.path.join(jobfilesDir,"job.id"),"r")
                    self.RemoteJobID=int(fin.read().strip())
                    print "Master task's RemoteJobID is ",self.RemoteJobID
                    fin.close()
                        
            if hasattr(self, 'ReportFormat'):#i.e. fatal error and the last one is already in status/statusinfo
                if self.ReportFormat=="Error":
                    self.ToDoNextString="PushToDB"
                    self.WriteErrorXML(resultFile)
                    return datetime.timedelta(seconds=3)
            
            (batchJobDir,stdoutFile,stderrFile,appstdoutFile,taskexeclogFile)=self.GetResultFiles(raiseError=True)
            
            #get the performance data
            parserfilename=os.path.join(akrr.curdir,"appkernelsparsers",self.app['parser'])
            import imp
            with open(parserfilename, 'rb') as fp:
                thisAppKerParser = imp.load_module(
                    'thisAppKerParser', fp, parserfilename,
                    ('.py', 'rb', imp.PY_SOURCE)
                )
            
            appKerNResVars={}
            appKerNResVars['resource']=self.resource
            appKerNResVars['resource'].update(self.resourceParam)
            appKerNResVars['app']=self.app
            appKerNResVars['app'].update(self.appParam)
            
            performance=thisAppKerParser.processAppKerOutput(appstdout=appstdoutFile,
                                                             stdout=stdoutFile,
                                                             stderr=stderrFile,
                                                             geninfo=os.path.join(batchJobDir,"gen.info"),
                                                             appKerNResVars=appKerNResVars)
            if performance==None:
                self.status="ERROR: Job have not finished successfully"
                self.statusinfo=""
                self.ToDoNextString="PushToDB"
                self.WriteErrorXML(resultFile)
            else:
                fout=open(resultFile,"w")
                content=fout.write(performance)
                fout.close()
                self.status="Output was processed and found that kernel either exited with error or executed successfully."
                self.statusinfo="Done"
                self.ToDoNextString="PushToDB"
                if hasattr(performance,'nodeList'):
                    self.nodesList=performance.nodeList
                else:
                    self.nodesList=None
            return datetime.timedelta(seconds=3)
        except:
            print traceback.format_exc()
            self.status="ERROR: Error happens during processing of output."
            self.statusinfo=traceback.format_exc()
            self.FatalErrorsCount+=1
            akrr.printException(self.status)
            self.ToDoNextString="PushToDB"
            self.WriteErrorXML(resultFile)
            return  datetime.timedelta(seconds=3)
    def ProccessResultsOld(self,Verbose=True):
        if Verbose:print "Processing the output"
        try:
            jobfilesDir=os.path.join(self.taskDir,"jobfiles")
            resultFile=os.path.join(self.taskDir,"result.xml")
                        
            if hasattr(self, 'ReportFormat'):#i.e. fatal error and the last one is already in status/statusinfo
                if self.ReportFormat=="Error":
                    self.ToDoNextString="PushToDB"
                    self.WriteErrorXML(resultFile)
                    return datetime.timedelta(seconds=3)
            
            (batchJobDir,stdoutFile,stderrFile,appstdoutFile,taskexeclogFile)=self.GetResultFiles(raiseError=True)
            
            #now check if stdoutFile is empty or not
            fin=open(stdoutFile,"r")
            remstdout=fin.read()
            fin.close()
            
            
            if len(remstdout) < 5:
                fin=open(stderrFile,"r")
                remstderr=fin.readlines()
                fin.close()
                for l in remstderr:
                    if re.search('job killed: walltime *\d+ *exceeded limit *\d+',l):
                        self.status="ERROR: Job was killed on remote resource due to walltime exceeded limit"
                        self.statusinfo=l
                        self.ToDoNextString="PushToDB"
                        self.WriteErrorXML(resultFile)
                        return datetime.timedelta(seconds=3)
                    
                
                if Verbose:print "stdout is too short meaning that application kernel exit prematurely"
                self.status="ERROR: stdout is too short meaning that application kernel exit prematurely"
                self.statusinfo="stdout is too short meaning that application kernel exit prematurely"
                self.WriteErrorXML(resultFile)
                self.ToDoNextString="PushToDB"
                return datetime.timedelta(seconds=3)
            #here we need to check file
            if remstdout.count("<rep:report")==0:
                self.status="ERROR: unknown error"
                self.statusinfo="stdout:\n"+remstdout
                if appstdoutFile!=None:
                    fin=open(appstdoutFile,"r")
                    remappstdout=fin.read()
                    fin.close()
                    self.statusinfo+="\nappstdout:\n"+remappstdout
            
                self.WriteErrorXML(resultFile)
                self.ToDoNextString="PushToDB"
                return datetime.timedelta(seconds=3)
                
            self.status="Output was processed and found that kernel either exited with error or executed successfully."
            self.statusinfo="Done"
            self.ToDoNextString="PushToDB"
            import shutil
            
            shutil.copy2(stdoutFile,resultFile)
            #need to extract xml part file, some resource put servise information above and below
            fin=open(resultFile,"r")
            content=fin.read()
            fin.close()
            if content[0]!='<' or content[-2]!='>':
                #need to reformat
                i0=content.find("<rep:report")
                i1=content.find("</rep:report>")
                
                fout=open(resultFile,"w")
                content=fout.write("<?xml version='1.0'?>\n"+content[i0:i1+len("</rep:report>")]+"\n")
                fout.close()
            return datetime.timedelta(seconds=3)
        except:
            self.status="ERROR: Error happens during processing of output."
            self.statusinfo=traceback.format_exc()
            self.FatalErrorsCount+=1
            akrr.printException(self.status)
            self.ToDoNextString="PushToDB"
            self.WriteErrorXML(resultFile)
            return  datetime.timedelta(seconds=3)
    def PushToDB(self,Verbose=True):
        
        db,cur=akrr.getExportDB()
        try:
            
            time_finished=None
            if hasattr(self,'TimeJobPossiblyCompleted'):
                time_finished=self.TimeJobPossiblyCompleted
            else:
                time_finished=datetime.datetime.today()
            self.PushToDBRaw(cur,self.task_id,time_finished,Verbose)
            db.commit()
            cur.close()
            del db
            self.ToDoNextString="IamDone"
            return None
        except:
            print traceback.format_exc()
            db.rollback()
            db.commit()
            cur.close()
            del db
            if hasattr(self, 'PushToDBAttemps'):
                self.PushToDBAttemps+=1
            else:
                self.PushToDBAttemps=1
                
            
            if self.PushToDBAttemps <= akrr.export_db_max_repeat_attempts:
                akrr.printException("AKRR server was not able to push to external DB.")
                self.status="ERROR: Can not push to external DB, will try again"
                self.statusinfo=traceback.format_exc()
                return akrr.export_db_repeat_attempt_in
            else:
                akrr.printException("AKRR server was not able to push to external DB will only update local.")
                self.status="ERROR: Can not push to external DB, will try again"
                self.statusinfo=traceback.format_exc()
                self.ToDoNextString="IamDone"
                return None
    def PushToDBRaw(self,cur,task_id,time_finished,Verbose=True):
        print "Pushing to DB"
        
                
        
        resultFile=os.path.join(self.taskDir,"result.xml")
        jobfilesDir=os.path.join(self.taskDir,"jobfiles")
        (batchJobDir,stdoutFile,stderrFile,appstdoutFile,taskexeclogFile)=self.GetResultFiles()
        
        #sanity check
        fin=open(resultFile,"r")
        content=fin.read()
        fin.close()
        if content[0]!='<':
            #need to reformat
            i0=content.find("<rep:report")
            i1=content.find("</rep:report>")
            
            fout=open(resultFile,"w")
            content=fout.write("<?xml version='1.0'?>\n"+content[i0:i1+len("</rep:report>")]+"\n")
            fout.close()
        
        import xml.etree.ElementTree as ET
        try:
            
            tree = ET.parse(resultFile)
            root = tree.getroot()
        except:
            self.statusinfo = "(1)==Resulting XML file content==\n"+content+\
                "\n==Previous status=="+self.status+\
                "\n==Previous status info=="+self.statusinfo+"\n"+\
                traceback.format_exc()
            self.status="Cannot process final XML file" 
            self.WriteErrorXML(resultFile,bCDATA=True)
            
        
        
        
        instance_id=task_id
        collected=None
        committed=None
        resource=None
        executionhost=None
        reporter=None
        reporternickname=None
        status=None
        message=None
        stderr=None
        body=None
        memory=None
        cputime=None
        walltime=None
        memory=0.0
        cputime=0.0
        walltime=0.0
        job_id=None
        
        cur.execute("""SELECT instance_id,collected,committed,resource,executionhost,reporter,reporternickname,status,message,stderr,body,memory,cputime,walltime,job_id
            FROM akrr_xdmod_instanceinfo WHERE instance_id=%s""",(task_id,))
        raw=cur.fetchone()
        if raw!=None: #.i.e. not new entry
            (instance_id,collected,committed,resource,executionhost,reporter,reporternickname,status,message,stderr,body,memory,cputime,walltime,job_id)=raw
            if hasattr(self,"RemoteJobID"):job_id=self.RemoteJobID
        else:
            collected=time_finished
            committed=datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
            resource=self.resourceName
            executionhost=self.resource.get('__regexp__',self.resourceName)
            reporter=self.appName
            #reporternickname="%s.%d"%(self.appName,self.resourceParam['ncpus'])
            reporternickname=akrr.replaceATvarAT(self.app['nickname'],[self.resource,self.app,self.resourceParam, self.appParam])
            
            if hasattr(self,"RemoteJobID"):job_id=self.RemoteJobID
        
        #Process XML file
        import xml.etree.ElementTree as ET
        root=None
        try:
            
            tree = ET.parse(resultFile)
            root = tree.getroot()
        except:
            self.statusinfo = "(2)==Resulting XML file content==\n"+content+\
                "\n==Previous status=="+self.status+\
                "\n==Previous status info=="+self.statusinfo
            self.status="Cannot process final XML file" 
            root=None
    
        memory=0.0
        cputime=0.0
        walltime=0.0
        
        print "TTTTTTTT ",root,status
        
        if root!=None:
            completed=None
            try:
                t=root.find('exitStatus').find('completed').text
                
                print 'exitStatus:completed',t
                
                if t.strip().upper()=="TRUE":completed=True
                else: completed=False
                
                if completed:
                    root.find('body').find('performance').find('benchmark').find('statistics')
                self.status="Task was completed successfully."
                self.statusinfo="Done"
            except:
                completed=None
            
            print "TTTTTTTT completedstatus",completed,status
            error=None
            try:
                
                t=root.find('xdtas').find('batchJob').find('status').text
                if t.upper()=="ERROR":error=True
                else: error=False
            except:
                error=None
            
            
            status=0
            if completed!=None:
                if completed:
                    status=1
                    
            print "TTTTTTTT completedstatus",completed,status
            
            if completed!=None:
                if completed==True:
                    bodyET=root.find('body').find('performance')
                    body=ET.tostring(bodyET)
                    import xml.dom.minidom
                    xml = xml.dom.minidom.parseString(body)
                    body = xml.toprettyxml()
                    body=body.replace("""<?xml version="1.0" ?>\n""","")
                    
                    statisticsET=root.find('body').find('performance').find('benchmark').find('statistics')
                    for e in statisticsET:
                        if e.find('ID').text=='Memory':
                            memory=float(e.find('value').text)
                        if e.find('ID').text=='Wall Clock Time':
                            walltime=float(e.find('value').text)
                else:
                    #i.e. error caught by parser on resource
                    try:
                        message="ERROR: error caught by parser"
                        stderr=root.find('exitStatus').find('errorMessage').text
                        body="""<xdtas>
      <batchJob>
       <status>Error</status>
       <errorCause>ERROR: error caught by parser</errorCause>
       <reporter>%s</reporter>
       <errorMsg>%s</errorMsg>
      </batchJob>
     </xdtas>
    """%(reporter,stderr)
                    except:
                        message="ERROR: error caught by parser"
                        stderr=None
                        body="""<xdtas>
      <batchJob>
       <status>Error</status>
       <errorCause>ERROR: error caught by parser</errorCause>
       <reporter>%s</reporter>
       <errorMsg></errorMsg>
      </batchJob>
     </xdtas>
    """%(reporter)
            elif completed==None:
                if error!=None: # i.e. xml with error generated afterwards
                    if error==True:
                        #fin=open(resultFile,"r")
                        #body=fin.read()
                        #fin.close
                        message=root.find('xdtas').find('batchJob').find('errorCause').text
                        stderr=root.find('xdtas').find('batchJob').find('errorMsg').text
                        
                        bodyET=root.find('xdtas')
                        body=ET.tostring(bodyET)
                    else:
                        raise IOError("This condition should not happens")
                else:
                    raise IOError("This condition should not happens")
            else:
                    raise IOError("This condition should not happens")
                #memory=None
                #cputime=None
                #walltime=None
        else:#i.e. xml was not parsed
            status=0
            message=self.status
            stderr=self.statusinfo
            body="""<xdtas>
      <batchJob>
       <status>Error</status>
       <errorCause>Unknown error</errorCause>
       <reporter>AKRR Server</reporter>
       <errorMsg>"Cannot process final XML file</errorMsg>
      </batchJob>
     </xdtas>
    """
        message=akrr.CleanUnicode(message)
        stderr=akrr.CleanUnicode(stderr)
        body=akrr.CleanUnicode(body)
        
        #Get Nodes
        nodes=None
        nodesFileName=os.path.join(jobfilesDir,"gen.info")
        
        if(os.path.isfile(nodesFileName)):
            parser=AppKerOutputParser()
            parser.parseCommonParsAndStats(geninfo=nodesFileName)
            if hasattr(parser,'geninfo') and 'nodeList' in parser.geninfo:
                nodesList=parser.geninfo['nodeList'].split()
                nodes=";"
                for line in nodesList:
                    line=line.strip()
                    nodes+="%s;"%(line)
                if len(nodes.strip().strip(';'))==0:
                    nodes=None
            
        import xml.dom.minidom
        #print "#"*120
        #print resultFile
        #print instance_id,collected,committed,resource,executionhost,reporter,reporternickname,status,message,stderr,memory,cputime,walltime 
        #print body
        #cur.execute("""SELECT * FROM akrr_xdmod_instanceinfo WHERE instance_id=%s""",(task_id,))
        internal_failure_code=0
        if 'masterTaskID' in self.taskParam and appstdoutFile==None:
            internal_failure_code=10004
        print "TTTTTTTT completedstatus",completed,status
        if raw!=None: #.i.e. new entry
            print "Updating"
            cur.execute("""UPDATE akrr_xdmod_instanceinfo
SET instance_id=%s,collected=%s,committed=%s,resource=%s,executionhost=%s,reporter=%s,
reporternickname=%s,status=%s,message=%s,stderr=%s,body=%s,memory=%s,cputime=%s,walltime=%s,job_id=%s,nodes=%s,internal_failure=%s
WHERE instance_id=%s""",
(instance_id,collected,committed,resource,executionhost,reporter,reporternickname,status,message,stderr,body,memory,cputime,walltime,job_id,nodes,internal_failure_code,
instance_id))
            #(instance_id,collected,committed,resource,executionhost,reporter,reporternickname,status,message,stderr,body,memory,cputime,walltime)=raw
        else:
            cur.execute("""INSERT INTO akrr_xdmod_instanceinfo
(instance_id,collected,committed,resource,executionhost,reporter,reporternickname,status,message,stderr,body,memory,cputime,walltime,job_id,nodes,internal_failure)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
(instance_id,collected,committed,resource,executionhost,reporter,reporternickname,status,message,stderr,body,memory,cputime,walltime,job_id,nodes,internal_failure_code))
        
        
        #print appstdoutFile,stdoutFile,stderrFile
        appstdoutFileContent=None
        stdoutFileContent=None
        stderrFileContent=None
        taskexeclogFileContent=None
        if appstdoutFile!=None:
            fin=open(appstdoutFile,"r")
            appstdoutFileContent=fin.read()
            fin.close()
        else:
            appstdoutFileContent="Does Not Present"
        if stdoutFile!=None:
            fin=open(stdoutFile,"r")
            stdoutFileContent=fin.read()
            fin.close()
        else:
            stdoutFileContent="Does Not Present"
        if stderrFile!=None:
            fin=open(stderrFile,"r")
            stderrFileContent=fin.read()
            fin.close()
        else:
            stderrFileContent="Does Not Present"
        
        if taskexeclogFile!=None:
            fin=open(taskexeclogFile,"r")
            taskexeclogFileContent=fin.read()
            fin.close()
        else:
            taskexeclogFileContent="Does Not Present"
        
        cur.execute("""SELECT task_id
            FROM akrr_errmsg WHERE task_id=%s""",(task_id,))
        raw=cur.fetchall()
        
        cur.execute("""SELECT @@max_allowed_packet""")
        max_allowed_packet=cur.fetchall()[0][0]
        
        if (len(appstdoutFileContent)+len(stderrFileContent)+len(stdoutFileContent)+len(taskexeclogFileContent))>0.9*max_allowed_packet:
            print "WARNING: length of files exceed max_allowed_packet will trancate files"
            
            if len(appstdoutFileContent)>0.2*max_allowed_packet:
                appstdoutFileContent=appstdoutFileContent[:int(0.2*max_allowed_packet)]
                appstdoutFileContent+="\nWARNING: File was trancated because it length of files exceed max_allowed_packet\n"
            if len(stderrFileContent)>0.2*max_allowed_packet:
                stderrFileContent=stderrFileContent[:int(0.2*max_allowed_packet)]
                stderrFileContent+="\nWARNING: File was trancated because it length of files exceed max_allowed_packet\n"
            if len(stdoutFileContent)>0.2*max_allowed_packet:
                stdoutFileContent=stdoutFileContent[:int(0.2*max_allowed_packet)]
                stdoutFileContent+="\nWARNING: File was trancated because it length of files exceed max_allowed_packet\n"
            if len(taskexeclogFileContent)>0.2*max_allowed_packet:
                taskexeclogFileContent=taskexeclogFileContent[:int(0.2*max_allowed_packet)]
                taskexeclogFileContent+="\nWARNING: File was trancated because it length of files exceed max_allowed_packet\n"
            
        
        if len(raw)>0: #.i.e. updating existing entry
            print "Updating",raw
            cur.execute("""UPDATE akrr_errmsg
                SET appstdout=%s,stderr=%s,stdout=%s,taskexeclog=%s
                WHERE task_id=%s""",
                ((appstdoutFileContent),(stderrFileContent),(stdoutFileContent),taskexeclogFileContent,instance_id))
        else:
            cur.execute("""INSERT INTO akrr_errmsg
                (task_id,appstdout,stderr,stdout,taskexeclog)
                VALUES (%s,%s,%s,%s,%s)""",
                (instance_id,(appstdoutFileContent),(stderrFileContent),(stdoutFileContent),taskexeclogFileContent))
        #(instance_id,akrr.CleanUnicode(appstdoutFileContent),akrr.CleanUnicode(stderrFileContent),akrr.CleanUnicode(stdoutFileContent)))
                
    def IamDone(self):
        print "Done",self.taskDir
        self.status="Done"
        self.statusinfo="Done"
        self.ToDoNextString="IamDone"
        return None
    def Terminate(self):
        #
        CanBeSafelyRemoved=False
        if not hasattr(self,"RemoteJobID"):
            #i.e. not running remotely and everything is on local disk
            CanBeSafelyRemoved=True
        else:
            #
            if self.RemoveTaskFromRemoteQueue() == None:
                #i.e. "Task is probably removed from remote queue.":
                CanBeSafelyRemoved=True
        if CanBeSafelyRemoved:
            #remove remote directory
            pass
        return CanBeSafelyRemoved
    def RemoveTaskFromRemoteQueue(self):
        sh=None
        try:
            from string import Template
            kE=killExprs[self.resource['batchScheduler']]
            cmd =Template(kE[0]).substitute(jobId=str(self.RemoteJobID))
            msg=akrr.sshResource(self.resource,cmd)
            print msg
            self.status="Task is probably removed from remote queue."
            self.statusinfo=copy.deepcopy(msg)
            self.ToDoNextString="IamDone"
            return None
        except:
            if sh!=None:
                sh.sendline("exit")
                sh.close(force=True)
                del sh
            self.status="ERROR Can not remove job from queue on remote resource"
            self.statusinfo=traceback.format_exc()
            self.FatalErrorsCount+=1
            print traceback.format_exc()
            return active_task_default_attempt_repeat

