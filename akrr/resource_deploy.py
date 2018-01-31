"""Validate resource parameters and deploy app. kernel stack to remote resource"""
import sys
import traceback
import io
import datetime
import time
import copy

import os
import types

import argparse

verbose=True



#import requests
import json

import xml.etree.ElementTree as ET

import pprint
pp = pprint.PrettyPrinter(indent=4)



from . import akrrcfg
from . import akrrrestclient

import logging as log


def CheckDirSimple(sh,d):
    """
    check directory existance and verify accessability
    return None,message if does not exists
    return True,message if can write there
    return False,message if can not write there
    """
    dir(sh)
    cmd="if [ -d \"%s\" ]\n then \necho EXIST\n else echo DOESNOTEXIST\n fi"%(d)
    msg=akrrcfg.sshCommand(sh,cmd)
    if msg.find("DOESNOTEXIST")>=0:
        return (None,"Directory %s:%s does not exists!"%(sh.remotemachine,d))
    
    cmd="echo test > "+os.path.join(d,'akrrtestwrite')
    #print cmd
    msg=akrrcfg.sshCommand(sh,cmd)
    #print msg
    cmd="cat "+os.path.join(d,'akrrtestwrite')
    #print cmd
    msg=akrrcfg.sshCommand(sh,cmd)
    #print msg
    if msg.strip()=="test":
        cmd="rm "+os.path.join(d,'akrrtestwrite')
        akrrcfg.sshCommand(sh,cmd)
        return (True,"Directory exist and accessible for read/write")
    else:
        return (False,"Directory %s:%s is NOT accessible for read/write!"%(sh.remotemachine,d))
    
def CheckDir(sh, d,exitOnFail=True,tryToCreate=True):
    status,msg=CheckDirSimple(sh, d)
    if tryToCreate==True and status==None:
        log.info("Directory %s:%s does not exists, will try to create it"%(sh.remotemachine,d))
        cmd="mkdir -p \"%s\""%(d)
        akrrcfg.sshCommand(sh,cmd)
        status,msg=CheckDirSimple(sh, d)
    if exitOnFail==False:
        return status,msg
    
    if status==None:
        log.error("Directory %s:%s does not exists!"%(sh.remotemachine,d))
        exit()
    elif status==True:
        return (True,msg)
    else:
        log.error("Directory %s:%s is NOT accessible for read/write!"%(sh.remotemachine,d))
        exit()
        
def makeResultsSummary(verbose,resource_name,app_name,completed_tasks,akrr_xdmod_instanceinfo,akrr_errmsg):
    def addFileRef(comment,filename,addIfExists=True):
        if os.path.exists(filename):
            return comment+": "+filename+"\n"
        else:
            return comment+": "+"Not Present"+"\n"
    
    task_dir=os.path.join(akrrcfg.completed_tasks_dir,resource_name,app_name,completed_tasks['datetimestamp'])
    
    msg=""
    #if verbosity==0:
    msg+="status: "+str(akrr_xdmod_instanceinfo['status'])+"\n"
    if akrr_xdmod_instanceinfo['status']==0:
                    msg+="\tstatus2: "+completed_tasks['status']+"\n"
    msg+="statusinfo: "+completed_tasks['statusinfo']+"\n"
    msg+='processing message:\n'
    msg+=str(akrr_xdmod_instanceinfo['message'])+"\n"
    
    msg+=addFileRef("Local working directory for this task",task_dir)
    msg+='Location of some important generated files:\n'
    msg+="\t"+addFileRef("Batch job script",os.path.join(task_dir,'jobfiles',app_name+".job"))
    msg+="\t"+addFileRef("Application kernel output",os.path.join(task_dir,'jobfiles','appstdout'))
    msg+="\t"+addFileRef("Batch job standard output",os.path.join(task_dir,'jobfiles','stdout'))
    msg+="\t"+addFileRef("Batch job standard error output",os.path.join(task_dir,'jobfiles','stderr'))
    msg+="\t"+addFileRef("XML processing results",os.path.join(task_dir,'result.xml'))
    msg+="\t"+addFileRef("Task execution logs",os.path.join(task_dir,'proc','log'))
    #else:
    return msg

def resource_deploy(resource_name,verbose=False):
    globals()['verbose']=verbose
    
    errorCount=0
    warningCount=0
    
    default_resource_param_filename=os.path.join(akrrcfg.akrr_mod_dir,"default_conf","default.resource.conf")
    resource_param_filename=os.path.join(akrrcfg.cfg_dir,"resources",resource_name,"resource.conf")
    app_name='test'
    
    ###############################################################################################
    #validating resource parameter file
    
    log.info("#"*80)
    log.info("Validating %s parameters from %s"%(resource_name,resource_param_filename))
    
    if not os.path.isfile(resource_param_filename):
        log.error("resource parameters file (%s) do not exists!"%(resource_param_filename,))
        exit()
    
    #check syntax
    try:
        tmp={}
        exec(compile(open(default_resource_param_filename).read(), default_resource_param_filename, 'exec'),tmp)
        exec(compile(open(resource_param_filename).read(), resource_param_filename, 'exec'),tmp)
    except Exception as e:
        log.exception("Can not load resource from """+resource_param_filename+"\n"+
               "Probably invalid syntax.")
        exit()
    
    #now we can load akrr
    #import akrr
    #import akrrrestclient
    resource=akrrcfg.FindResourceByName(resource_name)
    
    #check that parameters for presents and type
    #format: key,type,can be None,must have parameter 
    parameters_types=[
        ['info',                        bytes,       False,False],
        ['localScratch',                bytes,       False,True],
        ['batchJobTemplate',            bytes,       False,True],
        ['remoteAccessNode',            bytes,       False,True],
        ['name',                        bytes,       False,False],
        ['akrrCommonCommandsTemplate',   bytes,       False,True],
        ['networkScratch',              bytes,       False,True],
        ['ppn',                         int,          False,True],
        #['akrrStartAppKerTemplate',      types.StringType,       False,True],
        ['remoteCopyMethod',            bytes,       False,True],
        ['sshUserName',                 bytes,       False,True],
        ['sshPassword',                 bytes,       True, False],
        ['sshPrivateKeyFile',           bytes,       True, False],
        ['sshPrivateKeyPassword',       bytes,       True, False],
        ['batchScheduler',              bytes,       False,True],
        ['remoteAccessMethod',          bytes,       False,True],
        ['appKerDir',                   bytes,       False,True],
        ['akrrCommonCleanupTemplate',    bytes,       False,True],
        #['nodeListSetterTemplate',      types.StringType,       False,True],
        ['akrrData',                     bytes,       False,True]
    ]
    
    for variable,ttype,nulable,must in parameters_types:
        if (must==True) and (variable not in resource):
            log.error("Syntax error in "+resource_param_filename+"\nVariable %s is not set"%(variable,))
            exit()
        if variable not in resource:
            continue
        if type(resource[variable])==type(None) and nulable==False:
            log.error("Syntax error in "+resource_param_filename+"\nVariable %s can not be None"%(variable,))
            exit()
        if type(resource[variable])!=ttype and not (type(resource[variable])==type(None) and nulable==True):
            log.error("Syntax error in "+resource_param_filename+
                   "\nVariable %s should be %s"%(variable,str(ttype))+
                   ". But it is "+str(type(resource[variable])))
            exit()
        #print variable,ttype,nulable,must
    log.info("Syntax of %s is correct and all necessary parameters are present."%resource_param_filename,highlight="ok")
    #log.info("="*80)
    
    ###############################################################################################
    #connect to resource
    log.info("#"*80)
    log.info("Validating resource accessibility. Connecting to %s."%(resource['name']))
    if resource['sshPrivateKeyFile']!=None and os.path.isfile(resource['sshPrivateKeyFile'])==False:
        log.error("Can not access ssh private key (%s)"""%(resource['sshPrivateKeyFile'],))
        exit()
    
    str_io=io.StringIO()
    try:
        sys.stdout = sys.stderr = str_io
        rsh=akrrcfg.sshResource(resource)
        
        sys.stdout=sys.__stdout__
        sys.stderr=sys.__stderr__
    except Exception as e:
        msg2=str_io.getvalue()
        msg2+="\n"+traceback.format_exc()
        sys.stdout=sys.__stdout__
        sys.stderr=sys.__stderr__
        log.error("Can not connect to """+resource['name']+"\n"+
               "Probably invalid credential, see full error report below",msg2)
        exit()
    print("="*80)
    log.info("Successfully connected to %s\n\n"%(resource['name']),highlight="ok")
    
    ###############################################################################################
    log.info("Checking if shell is BASH\n")
    msg=akrrcfg.sshCommand(rsh,"echo $BASH")
    if msg.count("bash")>0:
        log.info("Shell is BASH\n",highlight="ok")
    else:
        log.error("Shell on headnode of %s is not BASH, change it to bash and try again.\n"%(resource_name,))
        exit()
    
    ###############################################################################################
    log.info("Checking directory locations\n")
    
    d=resource['akrrData']
    log.info("Checking: %s:%s"%(resource['remoteAccessNode'],d))
    status,msg=CheckDir(rsh, d,exitOnFail=True,tryToCreate=True)
    log.info(msg+"\n",highlight="ok")
    
    d=resource['appKerDir']
    log.info("Checking: %s:%s"%(resource['remoteAccessNode'],d))
    status,msg=CheckDir(rsh, d,exitOnFail=True,tryToCreate=True)
    log.info(msg+"\n",highlight="ok")
    
    d=resource['networkScratch']
    log.info("Checking: %s:%s"%(resource['remoteAccessNode'],d))
    status,msg=CheckDir(rsh, d,exitOnFail=False,tryToCreate=False)
    if status==True:
        log.info(msg,highlight="ok")
    else:
        log.info(msg,highlight="warning")
        log.info("WARNING %d: network scratch might be have a different location on head node, so if it is by design it is ok"%(warningCount+1),highlight="warning")
        warningCount+=1
    log.info("")
    
    d=resource['localScratch']
    log.info("Checking: %s:%s"%(resource['remoteAccessNode'],d))
    status,msg=CheckDir(rsh, d,exitOnFail=False,tryToCreate=False)
    if status==True:
        log.info(msg,highlight="ok")
    else:
        log.info(msg,highlight="warning")
        log.info("WARNING %d: local scratch might be have a different location on head node, so if it is by design it is ok"%(warningCount+1),highlight="warning")
        warningCount+=1
    log.info("")
    
    ###############################################################################################
    #copy exec sources and inputs to remote resource
    log.info("#"*80)
    log.info("Preparing to copy application signature calculator,\n    app. kernel input files and \n    HPCC,IMB,IOR and Graph500 source code to remote resource\n\n")
    
    
    str_io=io.StringIO()
    try:
        #sys.stdout = sys.stderr = str_io
        akrrcfg.sshCommand(rsh,"cd %s"%resource['appKerDir'])
        out=akrrcfg.sshCommand(rsh,"ls "+resource['appKerDir'])
        files_in_appKerDir=out.strip().split()
        
        if not ("inputs" in files_in_appKerDir or "inputs/" in files_in_appKerDir):
            log.info("Copying app. kernel input tarball to %s"%resource['appKerDir'])
            akrrcfg.scpToResource(resource,akrrcfg.appker_repo_dir+"/inputs.tar.gz",resource['appKerDir'],logfile=str_io)
            log.info("Unpacking app. kernel input files to %s/inputs"%resource['appKerDir'])
            
            print(akrrcfg.sshCommand(rsh,"tar xvfz %s/inputs.tar.gz"%resource['appKerDir']), file=str_io)
            
            out=akrrcfg.sshCommand(rsh,"df -h %s/inputs"%resource['appKerDir'])
            if out.count("No such file or directory")==0:
                log.info("App. kernel input files are in %s/inputs\n"%resource['appKerDir'],highlight="ok")
            else:
                print(out, file=str_io)
                raise Exception("files are not copied!")
        else:
            log.info("WARNING %d: App. kernel inputs directory %s/inputs is present, assume they are correct.\n"%(warningCount+1,resource['appKerDir']),highlight='warning')
            warningCount+=1
        
        str_io=io.StringIO()
        
        if not ("execs" in files_in_appKerDir or "execs/" in files_in_appKerDir):
            log.info("Copying app. kernel execs tarball to %s"%resource['appKerDir'])
            log.info("It contains HPCC,IMB,IOR and Graph500 source code and app.signature calculator")
            akrrcfg.scpToResource(resource,akrrcfg.appker_repo_dir+"/execs.tar.gz",resource['appKerDir'],logfile=str_io)
            log.info("Unpacking HPCC,IMB,IOR and Graph500 source code and app.signature calculator files to %s/execs"%resource['appKerDir'])
            
            print(akrrcfg.sshCommand(rsh,"tar xvfz %s/execs.tar.gz"%resource['appKerDir']), file=str_io)
            
            out=akrrcfg.sshCommand(rsh,"df -h %s/execs"%resource['appKerDir'])
            if out.count("No such file or directory")==0:
                log.info("HPCC,IMB,IOR and Graph500 source code and app.signature calculator are in %s/execs\n"%resource['appKerDir'],highlight="ok")
            else:
                print(out, file=str_io)
                raise Exception("files are not copied!")
        else:
            log.info("WARNING %d: App. kernel executables directory %s/execs is present, assume they are correct."%(warningCount+1,resource['appKerDir']),highlight='warning')
            log.info("It should contain HPCC,IMB,IOR and Graph500 source code and app.signature calculator\n")
            warningCount+=1
        
        out=akrrcfg.sshCommand(rsh,"rm execs.tar.gz  inputs.tar.gz")
        sys.stdout=sys.__stdout__
        sys.stderr=sys.__stderr__
    except Exception as e:
        msg2=str_io.getvalue()
        msg2+="\n"+traceback.format_exc()
        sys.stdout=sys.__stdout__
        sys.stderr=sys.__stderr__
        log.error("Can not copy files to """+resource['name']+"\n"+
               "See full error report below",msg2)
        exit()
    #
    log.info("Testing app.signature calculator on headnode\n")
    out=akrrcfg.sshCommand(rsh,"%s/execs/bin/appsigcheck.sh `which md5sum`"%(resource['appKerDir'],))
    if out.count("===ExeBinSignature===")>0 and out.count("MD5:")>0:
        log.info("App.signature calculator is working on headnode\n",highlight="ok")
    else:
        log.error("App.signature calculator is not working\n"+
               "See full error report below",out)
        exit()
    #close connection we don't need it any more
    rsh.close(force=True)
    del rsh    
    ###############################################################################################
    #send test job to queue
    
    log.info("#"*80)
    log.info("Will send test job to queue, wait till it executed and will analyze the output")
    
    print("Will use AKRR REST API at",akrrrestclient.restapi_host)
    #get check connection 
    try:
        r = akrrrestclient.get('/scheduled_tasks')
        if r.status_code!=200:
            log.error("Can not get token for AKRR REST API ( """+akrrrestclient.restapi_host+" )\n"+
               "See server response below",json.dumps(r.json(),indent=4))
            exit()
    except Exception as e:
        log.exception("Can not connect to AKRR REST API ( """+akrrrestclient.restapi_host+" )\n"+
               "Is it running?\n"+
               "See full error report below")
        exit()
    
    #check if the test job is already submitted
    task_id=None
    test_job_lock_filename=os.path.join(akrrcfg.data_dir,resource_name+"_test_task.dat")
    if os.path.isfile(test_job_lock_filename):
        fin=open(test_job_lock_filename,"r")
        task_id=int(fin.readline())
        fin.close()
        
        r = akrrrestclient.get('/tasks/'+str(task_id))
        if r.status_code!=200:
            task_id=None
        else:
            log.info("\nWARNING %d: Seems this is rerun of this script, will monitor task with task_id = "%(warningCount+1)+str(task_id),highlight="warning")
            log.info("To submit new task delete "+test_job_lock_filename+"\n",highlight="warning")
            warningCount+=1
        #check how old is it
    #submit test job
    if task_id==None:
        try:
            payload={'resource':resource_name,
                     'app':app_name,
                     'resource_param':"{'nnodes':2}",
                     'task_param':"{'test_run':True}"
                     }
            r = akrrrestclient.post('/scheduled_tasks', data=payload)
            if r.status_code!=200:
                log.error("Can not submit task through AKRR REST API ( """+akrrrestclient.restapi_host+" )\n"+
                   "See server response below",json.dumps(r.json(),indent=4))
                exit()
            task_id=r.json()['data']['task_id']
        except Exception as e:
            log.exception("Can not submit task through AKRR REST API ( """+akrrrestclient.restapi_host+" )\n"+
                   "Is it still running?\n"+
                   "See full error report below",traceback.format_exc())
            exit()
        #write file with tast_id
        fout=open(os.path.join(test_job_lock_filename),"w")
        print(task_id, file=fout)
        fout.close()
        log.info("\nSubmitted test job to AKRR, task_id is "+str(task_id)+"\n")
    #now wait till job is done
    msg_body0=""
    msg_body=""
    
    #response_json0={}
    #response_json=r.json()
    while True:
        t=datetime.datetime.now()
        #try:
        r = akrrrestclient.get('/tasks/'+str(task_id))
        
        response_json=r.json()
        if r.status_code==200:
            response_json=r.json()
            
            msg_body="="*80
            msg_body+="\nTast status:\n"
                        
            if response_json["data"]["queue"]=="scheduled_tasks":
                msg_body+="Task is in scheduled_tasks queue.\n"
                msg_body+="It schedule to be started on"+response_json["data"]["data"]['time_to_start']+"\n"
            elif response_json["data"]["queue"]=="active_tasks":
                msg_body+="Task is in active_tasks queue.\n"
                msg_body+="Status: "+str(response_json["data"]["data"]['status'])+"\n"
                msg_body+="Status info:\n"+str(response_json["data"]["data"]['statusinfo'])+"\n"
            elif response_json["data"]["queue"]=="completed_tasks":
                msg_body+="Task is completed!\n"
                completed_tasks=r.json()['data']['data']['completed_tasks']
                akrr_xdmod_instanceinfo=r.json()['data']['data']['akrr_xdmod_instanceinfo']
                akrr_errmsg=r.json()['data']['data']['akrr_errmsg']
                if verbose:
                    msg_body+="completed_tasks table entry:\n"+pp.pformat(completed_tasks)+"\n"
                    msg_body+="akrr_xdmod_instanceinfo table entry:\n"+pp.pformat(akrr_xdmod_instanceinfo)+"\n"
                    msg_body+='output parsing results:\n'+akrr_xdmod_instanceinfo['body']+"\n"
                else:
                    msg_body+="\tstatus: "+str(akrr_xdmod_instanceinfo['status'])+"\n"
                    if akrr_xdmod_instanceinfo['status']==0:
                        msg_body+="\tstatus2: "+completed_tasks['status']+"\n"
                    msg_body+="\tstatusinfo: "+completed_tasks['statusinfo']+"\n"
            else:
                msg_body+=r.text+"\n"
            
            tail_msg="time: "+t.strftime("%Y-%m-%d %H:%M:%S")
            
            if msg_body!=msg_body0:
                print("\n\n"+msg_body)
                print(tail_msg, end=' ')
                sys.stdout.flush()
            else:
                print("\r"+tail_msg, end=' ')
                sys.stdout.flush()
                
            msg_body0=copy.deepcopy(msg_body)
            
            if response_json["data"]["queue"]=="completed_tasks":
                break
        #try to update:
        try:
            payload={'next_check_time':''}
            r = akrrrestclient.put('/active_tasks/'+str(task_id), data=payload)
        except:
            pass
        time.sleep(5)
    ###############################################################################################
    #analysing the output
    log.info("\n\n")
    log.info("#"*80)
    log.info("Test job is completed analyzing output\n",highlight="ok")
    r = akrrrestclient.get('/tasks/'+str(task_id))
    
    
    
    if r.status_code!=200:
        log.error("Can not get information about task\n"+
                   "See full error report below",
                   "AKRR server response:\n"+r.text)
        exit()
    completed_tasks=r.json()['data']['data']['completed_tasks']    
    akrr_xdmod_instanceinfo=r.json()['data']['data']['akrr_xdmod_instanceinfo']
    akrr_errmsg=r.json()['data']['data']['akrr_errmsg']
    
    results_summary=makeResultsSummary(verbose,resource_name,app_name,completed_tasks,akrr_xdmod_instanceinfo,akrr_errmsg)
    #execution was not successful
    if completed_tasks['status'].count("ERROR")>0:
        if completed_tasks['status'].count("ERROR Can not created batch job script and submit it to remote queue")>0:
            log.error("Can not created batch job script and/or submit it to remote queue\n"+
                   "See full error report below",
                   results_summary)
        else:
            log.error(completed_tasks['status']+"\n"+
                   "See full error report below",
                   results_summary)
        os.remove(test_job_lock_filename)
        exit()
    
    #execution was not successful
    if akrr_xdmod_instanceinfo['status']==0:
        log.error("Task execution was not successful\n"+
                   "See full error report below",
                   results_summary)
        os.remove(test_job_lock_filename)
        exit()
    #see what is in report
    elm_perf = ET.fromstring(akrr_xdmod_instanceinfo['body'])
    elm_parameters=elm_perf.find('benchmark').find('parameters')
    elm_statistics=elm_perf.find('benchmark').find('statistics')
    
    parameters={'RunEnv:Nodes': '', 
                'App:ExeBinSignature': ''
    }
    statistics={'Wall Clock Time': '0.0',
                'Network scratch directory exists': '0',
                'Network scratch directory accessible': '0',
                'App kernel input exists': '0',
                'Task working directory accessible': '0',
                'local scratch directory accessible': '0',
                'local scratch directory exists': '0',
                'App kernel executable exists': '0',
                'Task working directory exists': '0',
                'Shell is BASH':'0'
    }

    for elm in list(elm_parameters):
        variable=elm.findtext('ID')
        if variable!=None:variable=variable.strip()
        value=elm.findtext('value')
        if value!=None:value=value.strip()
        units=elm.findtext('units')
        if units!=None:units=units.strip()
        
        if variable=='App:ExeBinSignature' or variable=='RunEnv:Nodes':
            value=os.popen('echo "%s"|base64 -d|gzip -d'%(value)).read()
        parameters[variable]=value
    
    for elm in list(elm_statistics):
        variable=elm.findtext('ID')
        if variable!=None:variable=variable.strip()
        value=elm.findtext('value')
        if value!=None:value=value.strip()
        units=elm.findtext('units')
        if units!=None:units=units.strip()
        statistics[variable]=value
    filesExists=['Network scratch directory exists',
                'App kernel input exists',
                'local scratch directory exists',
                'App kernel executable exists',
                'Task working directory exists']
    dirsAccess=['Network scratch directory accessible',
                'Task working directory accessible',
                'local scratch directory accessible']
    
    if statistics['Shell is BASH']=='0':
        log.error("Shell on compute nodes of %s is not BASH, change it to bash and try again.\n"%(resource_name,))
        errorCount+=1
    for fileExists in filesExists:
        if statistics[fileExists]=='0':
            log.error(fileExists.replace('exists','does not exist'))
            errorCount+=1
    for dirAccess in dirsAccess:
        if statistics[dirAccess]=='0':
            log.error(dirAccess.replace('accessible','is not accessible'))
            errorCount+=1
    
    if parameters['App:ExeBinSignature']=='':
        log.error("Application signature calculator is not working, you might need to recompile it. see application output for more hints")
        errorCount+=1
    
    #test the nodes, log to headnode and ping them
    if parameters['RunEnv:Nodes']=='':
        log.error("Nodes are not detected, check batchJobTemplate and setup of AKRR_NODELIST variable")
        errorCount+=1
    
    
    nodes=parameters['RunEnv:Nodes'].split()
    
    requested_nodes=eval(completed_tasks['resource_param'])['nnodes']
    
    str_io=io.StringIO()
    try:
        sys.stdout = sys.stderr = str_io
        rsh=akrrcfg.sshResource(resource)
        
        NumberOfUnknownHosts=0
        for node in set(nodes):
            print(node)
            out=akrrcfg.sshCommand(rsh,"ping -c 1 %s"%node)
            if out.count("unknown host")>0:
                NumberOfUnknownHosts+=1
            
        rsh.close(force=True)
        del rsh    
        
        sys.stdout=sys.__stdout__
        sys.stderr=sys.__stderr__
        
        if NumberOfUnknownHosts>0:
            log.error("ERROR %d: Can not ping compute nodes from head node\n"%(errorCount+1)+
                   "Nodes on which test job was executed detected as "+parameters['RunEnv:Nodes']+"\n"+
                   "If these names does not have sense check batchJobTemplate and setup of AKRR_NODELIST variable in resource configuration file")
            errorCount+=1
    except Exception as e:
        msg2=str_io.getvalue()
        msg2+="\n"+traceback.format_exc()
        sys.stdout=sys.__stdout__
        sys.stderr=sys.__stderr__
        log.error("Can not connect to """+resource['name']+"\n"+
               "Probably invalid credential, see full error report below",msg2)
        exit()
    
    #check ppn count
    if requested_nodes*resource['ppn']!=len(nodes):
        log.error("ERROR %d: Number of requested processes (processes per node * nodes) do not match actual processes executed"%(errorCount+1)+
            "Either\n"+
            "    AKRR_NODELIST variable is set incorrectly\n"+
            "Or\n"+
            "    processes per node (PPN) is wrong\n")
        errorCount+=1
    log.info("\nTest kernel execution summary:",highlight="ok")
    print(results_summary)
    print() 
    log.info("\nThe output looks good.\n",highlight="ok")
    
    if(errorCount==0):
        #append enviroment variables to .bashrc
        log.info("\nAdding AKRR enviroment variables to resource's .bashrc!\n",highlight="ok")
        str_io=io.StringIO()
        try:
            sys.stdout = sys.stderr = str_io
            rsh=akrrcfg.sshResource(resource)
            akrrHeader='AKRR Remote Resource Environment Variables'
            
            out=akrrcfg.sshCommand(rsh,'''if [ -e $HOME/.bashrc ]
then
   if [[ `grep "\#'''+akrrHeader+''' \[Start\]" $HOME/.bashrc` == *"'''+akrrHeader+''' [Start]"* ]]
   then
       echo "Updating AKRR record in $HOME/.bashrc, backing to $HOME/.bashrc_akrrbak"
       cp $HOME/.bashrc $HOME/.bashrc_akrrbak
       head -n "$(( $(grep -n '\#'''+akrrHeader+''' \[Start\]' $HOME/.bashrc_akrrbak | head -n 1 | cut -d ":" -f 1) - 1 ))" $HOME/.bashrc_akrrbak > $HOME/.bashrc
       tail -n "+$(( $(grep -n '\#'''+akrrHeader+''' \[End\]' $HOME/.bashrc_akrrbak | head -n 1 | cut -d ":" -f 1) + 1 ))" $HOME/.bashrc_akrrbak  >> $HOME/.bashrc
   fi
fi''')
            out=akrrcfg.sshCommand(rsh,'''
echo "Appending AKRR records to $HOME/.bashrc"
echo "#'''+akrrHeader+''' [Start]" >> $HOME/.bashrc
echo "export AKRR_NETWORK_SCRATCH=\\"'''+resource['networkScratch']+'''\\"" >> $HOME/.bashrc
echo "export AKRR_LOCAL_SCRATCH=\\"'''+resource['localScratch']+'''\\"" >> $HOME/.bashrc
echo "export AKRR_APPKER_DIR=\\"'''+resource['appKerDir']+'''\\"" >> $HOME/.bashrc
echo "export AKRR_AKRR_DIR=\\"'''+resource['akrrData']+'''\\"" >> $HOME/.bashrc
echo "#'''+akrrHeader+''' [End]" >> $HOME/.bashrc
''')
            #print out
            rsh.close(force=True)
            del rsh    
            
            sys.stdout=sys.__stdout__
            sys.stderr=sys.__stderr__
        except Exception as e:
            msg2=str_io.getvalue()
            msg2+="\n"+traceback.format_exc()
            sys.stdout=sys.__stdout__
            sys.stderr=sys.__stderr__
            log.error("Can not connect to """+resource['name']+"\n"+
                   "Probably invalid credential, see full error report below",msg2)
            exit()
        #enabling resource for execution
        try:
            dbAK,curAK=akrrcfg.getAKDB(True)
            
            curAK.execute('''SELECT * FROM resource WHERE nickname=%s''', (resource_name,))
            resource_in_AKDB = curAK.fetchall()
            if len(resource_in_AKDB)==0:
                log.info("There is no record of %s in mod_appkernel.resource will add one."%(resource_name,),highlight="warning")
                curAK.execute('''INSERT INTO resource (resource,nickname,description,enabled,visible)
                            VALUES(%s,%s,%s,0,0);''',
                            (resource_name,resource_name,resource['info']))
                dbAK.commit()
                
                curAK.execute('''SELECT * FROM resource WHERE nickname=%s''', (resource_name,))
                resource_in_AKDB = curAK.fetchall()
            resource_in_AKDB=resource_in_AKDB[0]
            #enable and make visible
            curAK.execute('''UPDATE resource
                            SET enabled=1,visible=1
                            WHERE resource_id=%s;''',
                            (resource_in_AKDB['resource_id'],))
            dbAK.commit()
            log.info("Enabled %s in mod_appkernel.resource for tasks execution and made it visible to XDMoD UI."%(resource_name),highlight="ok")
        except Exception as e:
            log.exception("Can not connect to AK DB\n"+
                   "Probably invalid credential, see full error report below")
        #enabling resource for execution
        try:
            r = akrrrestclient.put('/resources/'+resource_name+'/on')
            if r.status_code==200:
                log.info('Successfully enabled '+resource_name)
            else:
                log.error("Can not enable resource through AKRR REST API ( """+akrrrestclient.restapi_host+" )\n"+
                   "See server response below",json.dumps(r.json(),indent=4))
        except Exception as e:
            log.exception("Can not enable resource through AKRR REST API ( """+akrrrestclient.restapi_host+" )\n"+
                   "Is it still running?\n"+
                   "See full error report below")
        
    log.info("#"*80)
    log.info("Result:")
    if(errorCount>0):
        log.error("There are %d errors, fix them."%errorCount)
        
    if(warningCount>0):
        log.info("\nThere are %d warnings.\nif warnings have sense (highlighted in yellow), you can move to next step!\n"%warningCount,highlight="warning")
    if(errorCount==0 and warningCount==0):
        log.info("\nDONE, you can move to next step!\n",highlight="ok")
    os.remove(test_job_lock_filename)


if __name__ == '__main__':
    # TIME: to get to parsing
    parser = argparse.ArgumentParser('Resource configuration validation and deployment')

    # SETUP: the arguments that we're going to support
    parser.add_argument('-v', '--verbose', action='store_true', help="turn on verbose logging")
    parser.add_argument('resource', help="name of resource for validation and deployment'")
    # PARSE: them arguments
    
    args = parser.parse_args()
    
    resource_deploy(args.resource,args.verbose)
    
