"""Validate resource parameters and deploy app. kernel stack to remote resource"""
import sys
import inspect
import traceback
import cStringIO
import datetime
import time
import copy

import os
import types

try:
    import argparse
except:
    #add argparse directory to path and try again
    curdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    argparsedir=os.path.abspath(os.path.join(curdir,"..","..","3rd_party","argparse-1.3.0"))
    if argparsedir not in sys.path:sys.path.append(argparsedir)
    import argparse

args=None
verbose=True



#import requests
import json

import xml.etree.ElementTree as ET

import pprint
pp = pprint.PrettyPrinter(indent=4)

#modify python_path
curdir=os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) 
if (curdir+"/../../src") not in sys.path:
    sys.path.append(curdir+"/../../src")

#if __name__ != '__main__':
import akrr
import akrrrestclient
#import akrr
from akrrlogging import *


def CheckDirSimple(sh,d):
    """
    check directory existance and verify accessability
    return None,message if does not exists
    return True,message if can write there
    return False,message if can not write there
    """
    dir(sh)
    cmd="if [ -d \"%s\" ]\n then \necho EXIST\n else echo DOESNOTEXIST\n fi"%(d)
    msg=akrr.sshCommand(sh,cmd)
    if msg.find("DOESNOTEXIST")>=0:
        return (None,"Directory %s:%s does not exists!"%(sh.remotemachine,d))
    
    cmd="echo test > "+os.path.join(d,'akrrtestwrite')
    #print cmd
    msg=akrr.sshCommand(sh,cmd)
    #print msg
    cmd="cat "+os.path.join(d,'akrrtestwrite')
    #print cmd
    msg=akrr.sshCommand(sh,cmd)
    #print msg
    if msg.strip()=="test":
        cmd="rm "+os.path.join(d,'akrrtestwrite')
        akrr.sshCommand(sh,cmd)
        return (True,"Directory exist and accessible for read/write")
    else:
        return (False,"Directory %s:%s is NOT accessible for read/write!"%(sh.remotemachine,d))
    
def CheckDir(sh, d,exitOnFail=True,tryToCreate=True):
    status,msg=CheckDirSimple(sh, d)
    if tryToCreate==True and status==None:
        log("Directory %s:%s does not exists, will try to create it"%(sh.remotemachine,d))
        cmd="mkdir -p \"%s\""%(d)
        akrr.sshCommand(sh,cmd)
        status,msg=CheckDirSimple(sh, d)
    if exitOnFail==False:
        return status,msg
    
    if status==None:
        logerr("Directory %s:%s does not exists!"%(sh.remotemachine,d))
        exit()
    elif status==True:
        return (True,msg)
    else:
        logerr("Directory %s:%s is NOT accessible for read/write!"%(sh.remotemachine,d))
        exit()
def makeResultsSummary(verbose,resource_name,app_name,completed_tasks,akrr_xdmod_instanceinfo,akrr_errmsg):
    def addFileRef(comment,filename,addIfExists=True):
        if os.path.exists(filename):
            return comment+": "+filename+"\n"
        else:
            return comment+": "+"Not Present"+"\n"
    
    task_dir=os.path.join(akrr.completed_tasks_dir,resource_name,app_name,completed_tasks['datetimestamp'])
    
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
def resource_validation_and_deployment():
    
    # TIME: to get to parsing
    parser = argparse.ArgumentParser('Resource configuration validation and deployment')

    # SETUP: the arguments that we're going to support
    parser.add_argument('-v', '--verbose', action='store_true', help="turn on verbose logging")
    parser.add_argument('resource', help="name of resource for validation and deployment'")
    # PARSE: them arguments
    
    args = parser.parse_args()
    global verbose
    verbose=args.verbose
    
    if len(sys.argv)!=2:
        print __doc__
        print "format:"
        print "  python "+__file__+" resource_name"
        exit()
    
    errorCount=0
    warningCount=0
    
    resource_name=sys.argv[1]
    default_resource_param_filename=os.path.abspath(curdir+"/../../src/default.resource.inp.py")
    resource_param_filename=os.path.abspath(curdir+"/../../cfg/resources/"+resource_name+"/resource.inp.py")
    app_name='test'
    
    ###############################################################################################
    #validating resource parameter file
    
    log("#"*80)
    log("Validating %s parameters from %s"%(resource_name,resource_param_filename))
    
    if not os.path.isfile(resource_param_filename):
        logerr("resource parameters file (%s) do not exists!"%(resource_param_filename,))
        exit()
    
    #check syntax
    try:
        tmp={}
        execfile(default_resource_param_filename,tmp)
        execfile(resource_param_filename,tmp)
    except Exception,e:
        logerr("Can not load resource from """+resource_param_filename+"\n"+
               "Probably invalid syntax, see full error report below",traceback.format_exc())
        exit()
    
    #now we can load akrr
    #import akrr
    #import akrrrestclient
    resource=akrr.FindResourceByName(resource_name)
    
    #check that parameters for presents and type
    #format: key,type,can be None,must have parameter 
    parameters_types=[
        ['info',                        types.StringType,       False,False],
        ['localScratch',                types.StringType,       False,True],
        ['batchJobTemplate',            types.StringType,       False,True],
        ['remoteAccessNode',            types.StringType,       False,True],
        ['name',                        types.StringType,       False,False],
        ['akrrCommonCommandsTemplate',   types.StringType,       False,True],
        ['networkScratch',              types.StringType,       False,True],
        ['ppn',                         types.IntType,          False,True],
        #['akrrStartAppKerTemplate',      types.StringType,       False,True],
        ['remoteCopyMethod',            types.StringType,       False,True],
        ['sshUserName',                 types.StringType,       False,True],
        ['sshPassword',                 types.StringType,       True, False],
        ['sshPrivateKeyFile',           types.StringType,       True, False],
        ['sshPrivateKeyPassword',       types.StringType,       True, False],
        ['batchScheduler',              types.StringType,       False,True],
        ['remoteAccessMethod',          types.StringType,       False,True],
        ['appKerDir',                   types.StringType,       False,True],
        ['akrrCommonCleanupTemplate',    types.StringType,       False,True],
        #['nodeListSetterTemplate',      types.StringType,       False,True],
        ['akrrData',                     types.StringType,       False,True]
    ]
    
    for variable,ttype,nulable,must in parameters_types:
        if (must==True) and (variable not in resource):
            logerr("Syntax error in "+resource_param_filename+"\nVariable %s is not set"%(variable,))
            exit()
        if variable not in resource:
            continue
        if type(resource[variable])==types.NoneType and nulable==False:
            logerr("Syntax error in "+resource_param_filename+"\nVariable %s can not be None"%(variable,))
            exit()
        if type(resource[variable])!=ttype and not (type(resource[variable])==types.NoneType and nulable==True):
            logerr("Syntax error in "+resource_param_filename+
                   "\nVariable %s should be %s"%(variable,str(ttype))+
                   ". But it is "+str(type(resource[variable])))
            exit()
        #print variable,ttype,nulable,must
    log("Syntax of %s is correct and all necessary parameters are present."%resource_param_filename,highlight="ok")
    #log("="*80)
    
    ###############################################################################################
    #connect to resource
    log("#"*80)
    log("Validating resource accessibility. Connecting to %s."%(resource['name']))
    if resource['sshPrivateKeyFile']!=None and os.path.isfile(resource['sshPrivateKeyFile'])==False:
        logerr("Can not access ssh private key (%s)"""%(resource['sshPrivateKeyFile'],))
        exit()
    
    str_io=cStringIO.StringIO()
    try:
        sys.stdout = sys.stderr = str_io
        rsh=akrr.sshResource(resource)
        
        sys.stdout=sys.__stdout__
        sys.stderr=sys.__stderr__
    except Exception,e:
        msg2=str_io.getvalue()
        msg2+="\n"+traceback.format_exc()
        sys.stdout=sys.__stdout__
        sys.stderr=sys.__stderr__
        logerr("Can not connect to """+resource['name']+"\n"+
               "Probably invalid credential, see full error report below",msg2)
        exit()
    print "="*80
    log("Successfully connected to %s\n\n"%(resource['name']),highlight="ok")
    
    ###############################################################################################
    log("Checking if shell is BASH\n")
    msg=akrr.sshCommand(rsh,"echo $BASH")
    if msg.count("bash")>0:
        log("Shell is BASH\n",highlight="ok")
    else:
        logerr("Shell on headnode of %s is not BASH, change it to bash and try again.\n"%(resource_name,))
        exit()
    
    ###############################################################################################
    log("Checking directory locations\n")
    
    d=resource['akrrData']
    log("Checking: %s:%s"%(resource['remoteAccessNode'],d))
    status,msg=CheckDir(rsh, d,exitOnFail=True,tryToCreate=True)
    log(msg+"\n",highlight="ok")
    
    d=resource['appKerDir']
    log("Checking: %s:%s"%(resource['remoteAccessNode'],d))
    status,msg=CheckDir(rsh, d,exitOnFail=True,tryToCreate=True)
    log(msg+"\n",highlight="ok")
    
    d=resource['networkScratch']
    log("Checking: %s:%s"%(resource['remoteAccessNode'],d))
    status,msg=CheckDir(rsh, d,exitOnFail=False,tryToCreate=False)
    if status==True:
        log(msg,highlight="ok")
    else:
        log(msg,highlight="warning")
        log("WARNING %d: network scratch might be have a different location on head node, so if it is by design it is ok"%(warningCount+1),highlight="warning")
        warningCount+=1
    log("")
    
    d=resource['localScratch']
    log("Checking: %s:%s"%(resource['remoteAccessNode'],d))
    status,msg=CheckDir(rsh, d,exitOnFail=False,tryToCreate=False)
    if status==True:
        log(msg,highlight="ok")
    else:
        log(msg,highlight="warning")
        log("WARNING %d: local scratch might be have a different location on head node, so if it is by design it is ok"%(warningCount+1),highlight="warning")
        warningCount+=1
    log("")
    
    ###############################################################################################
    #copy exec sources and inputs to remote resource
    log("#"*80)
    log("Preparing to copy application signature calculator,\n    app. kernel input files and \n    HPCC,IMB,IOR and Graph500 source code to remote resource\n\n")
    
    
    str_io=cStringIO.StringIO()
    try:
        #sys.stdout = sys.stderr = str_io
        akrr.sshCommand(rsh,"cd %s"%resource['appKerDir'])
        out=akrr.sshCommand(rsh,"ls "+resource['appKerDir'])
        files_in_appKerDir=out.strip().split()
        
        if not ("inputs" in files_in_appKerDir or "inputs/" in files_in_appKerDir):
            log("Copying app. kernel input tarball to %s"%resource['appKerDir'])
            akrr.scpToResource(resource,curdir+"/../../appker_repo/inputs.tar.gz",resource['appKerDir'],logfile=str_io)
            log("Unpacking app. kernel input files to %s/inputs"%resource['appKerDir'])
            
            print >>str_io, akrr.sshCommand(rsh,"tar xvfz %s/inputs.tar.gz"%resource['appKerDir'])
            
            out=akrr.sshCommand(rsh,"df -h %s/inputs"%resource['appKerDir'])
            if out.count("No such file or directory")==0:
                log("App. kernel input files are in %s/inputs\n"%resource['appKerDir'],highlight="ok")
            else:
                print >>str_io, out
                raise Exception("files are not copied!")
        else:
            log("WARNING %d: App. kernel inputs directory %s/inputs is present, assume they are correct.\n"%(warningCount+1,resource['appKerDir']),highlight='warning')
            warningCount+=1
        
        str_io=cStringIO.StringIO()
        
        if not ("execs" in files_in_appKerDir or "execs/" in files_in_appKerDir):
            log("Copying app. kernel execs tarball to %s"%resource['appKerDir'])
            log("It contains HPCC,IMB,IOR and Graph500 source code and app.signature calculator")
            akrr.scpToResource(resource,curdir+"/../../appker_repo/execs.tar.gz",resource['appKerDir'],logfile=str_io)
            log("Unpacking HPCC,IMB,IOR and Graph500 source code and app.signature calculator files to %s/execs"%resource['appKerDir'])
            
            print >>str_io, akrr.sshCommand(rsh,"tar xvfz %s/execs.tar.gz"%resource['appKerDir'])
            
            out=akrr.sshCommand(rsh,"df -h %s/execs"%resource['appKerDir'])
            if out.count("No such file or directory")==0:
                log("HPCC,IMB,IOR and Graph500 source code and app.signature calculator are in %s/execs\n"%resource['appKerDir'],highlight="ok")
            else:
                print >>str_io, out
                raise Exception("files are not copied!")
        else:
            log("WARNING %d: App. kernel executables directory %s/execs is present, assume they are correct."%(warningCount+1,resource['appKerDir']),highlight='warning')
            log("It should contain HPCC,IMB,IOR and Graph500 source code and app.signature calculator\n")
            warningCount+=1
        
        out=akrr.sshCommand(rsh,"rm execs.tar.gz  inputs.tar.gz")
        sys.stdout=sys.__stdout__
        sys.stderr=sys.__stderr__
    except Exception,e:
        msg2=str_io.getvalue()
        msg2+="\n"+traceback.format_exc()
        sys.stdout=sys.__stdout__
        sys.stderr=sys.__stderr__
        logerr("Can not copy files to """+resource['name']+"\n"+
               "See full error report below",msg2)
        exit()
    #
    log("Testing app.signature calculator on headnode\n")
    out=akrr.sshCommand(rsh,"%s/execs/bin/appsigcheck.sh `which md5sum`"%(resource['appKerDir'],))
    if out.count("===ExeBinSignature===")>0 and out.count("MD5:")>0:
        log("App.signature calculator is working on headnode\n",highlight="ok")
    else:
        logerr("App.signature calculator is not working\n"+
               "See full error report below",out)
        exit()
    #close connection we don't need it any more
    rsh.close(force=True)
    del rsh    
    ###############################################################################################
    #send test job to queue
    
    log("#"*80)
    log("Will send test job to queue, wait till it executed and will analyze the output")
    
    print "Will use AKRR REST API at",akrrrestclient.restapi_host
    #get check connection 
    try:
        r = akrrrestclient.get('/scheduled_tasks')
        if r.status_code!=200:
            logerr("Can not get token for AKRR REST API ( """+akrrrestclient.restapi_host+" )\n"+
               "See server response below",json.dumps(r.json(),indent=4))
            exit()
    except Exception,e:
        logerr("Can not connect to AKRR REST API ( """+akrrrestclient.restapi_host+" )\n"+
               "Is it running?\n"+
               "See full error report below",traceback.format_exc())
        exit()
    
    #check if the test job is already submitted
    task_id=None
    test_job_lock_filename=os.path.join(akrr.data_dir,resource_name+"_test_task.dat")
    if os.path.isfile(test_job_lock_filename):
        fin=open(test_job_lock_filename,"r")
        task_id=int(fin.readline())
        fin.close()
        
        r = akrrrestclient.get('/tasks/'+str(task_id))
        if r.status_code!=200:
            task_id=None
        else:
            log("\nWARNING %d: Seems this is rerun of this script, will monitor task with task_id = "%(warningCount+1)+str(task_id),highlight="warning")
            log("To submit new task delete "+test_job_lock_filename+"\n",highlight="warning")
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
                logerr("Can not submit task through AKRR REST API ( """+akrrrestclient.restapi_host+" )\n"+
                   "See server response below",json.dumps(r.json(),indent=4))
                exit()
            task_id=r.json()['data']['task_id']
        except Exception,e:
            logerr("Can not submit task through AKRR REST API ( """+akrrrestclient.restapi_host+" )\n"+
                   "Is it still running?\n"+
                   "See full error report below",traceback.format_exc())
            exit()
        #write file with tast_id
        fout=open(os.path.join(test_job_lock_filename),"w")
        print >>fout,task_id
        fout.close()
        log("\nSubmitted test job to AKRR, task_id is "+str(task_id)+"\n")
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
                print "\n\n"+msg_body
                print tail_msg,
                sys.stdout.flush()
            else:
                print "\r"+tail_msg,
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
    log("\n\n")
    log("#"*80)
    log("Test job is completed analyzing output\n",highlight="ok")
    r = akrrrestclient.get('/tasks/'+str(task_id))
    
    
    
    if r.status_code!=200:
        logerr("Can not get information about task\n"+
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
            logerr("Can not created batch job script and/or submit it to remote queue\n"+
                   "See full error report below",
                   results_summary)
        else:
            logerr(completed_tasks['status']+"\n"+
                   "See full error report below",
                   results_summary)
        os.remove(test_job_lock_filename)
        exit()
    
    #execution was not successful
    if akrr_xdmod_instanceinfo['status']==0:
        logerr("Task execution was not successful\n"+
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
        logerr("Shell on compute nodes of %s is not BASH, change it to bash and try again.\n"%(resource_name,))
        errorCount+=1
    for fileExists in filesExists:
        if statistics[fileExists]=='0':
            logerr(fileExists.replace('exists','does not exist'))
            errorCount+=1
    for dirAccess in dirsAccess:
        if statistics[dirAccess]=='0':
            logerr(dirAccess.replace('accessible','is not accessible'))
            errorCount+=1
    
    if parameters['App:ExeBinSignature']=='':
        logerr("Application signature calculator is not working, you might need to recompile it. see application output for more hints")
        errorCount+=1
    
    #test the nodes, log to headnode and ping them
    if parameters['RunEnv:Nodes']=='':
        logerr("Nodes are not detected, check batchJobTemplate and setup of AKRR_NODELIST variable")
        errorCount+=1
    
    
    nodes=parameters['RunEnv:Nodes'].split()
    
    requested_nodes=eval(completed_tasks['resource_param'])['nnodes']
    
    str_io=cStringIO.StringIO()
    try:
        sys.stdout = sys.stderr = str_io
        rsh=akrr.sshResource(resource)
        
        NumberOfUnknownHosts=0
        for node in set(nodes):
            print node
            out=akrr.sshCommand(rsh,"ping -c 1 %s"%node)
            if out.count("unknown host")>0:
                NumberOfUnknownHosts+=1
            
        rsh.close(force=True)
        del rsh    
        
        sys.stdout=sys.__stdout__
        sys.stderr=sys.__stderr__
        
        if NumberOfUnknownHosts>0:
            logerr("ERROR %d: Can not ping compute nodes from head node\n"%(errorCount+1)+
                   "Nodes on which test job was executed detected as "+parameters['RunEnv:Nodes']+"\n"+
                   "If these names does not have sense check batchJobTemplate and setup of AKRR_NODELIST variable in resource configuration file")
            errorCount+=1
    except Exception,e:
        msg2=str_io.getvalue()
        msg2+="\n"+traceback.format_exc()
        sys.stdout=sys.__stdout__
        sys.stderr=sys.__stderr__
        logerr("Can not connect to """+resource['name']+"\n"+
               "Probably invalid credential, see full error report below",msg2)
        exit()
    
    #check ppn count
    if requested_nodes*resource['ppn']!=len(nodes):
        logerr("ERROR %d: Number of requested processes (processes per node * nodes) do not match actual processes executed"%(errorCount+1)+
            "Either\n"+
            "    AKRR_NODELIST variable is set incorrectly\n"+
            "Or\n"+
            "    processes per node (PPN) is wrong\n")
        errorCount+=1
    log("\nTest kernel execution summary:",highlight="ok")
    print results_summary
    print 
    log("\nThe output looks good.\n",highlight="ok")
    
    if(errorCount==0):
        #append enviroment variables to .bashrc
        log("\nAdding AKRR enviroment variables to resource's .bashrc!\n",highlight="ok")
        str_io=cStringIO.StringIO()
        try:
            sys.stdout = sys.stderr = str_io
            rsh=akrr.sshResource(resource)
            akrrHeader='AKRR Remote Resource Environment Variables'
            
            out=akrr.sshCommand(rsh,'''if [ -e $HOME/.bashrc ]
then
   if [[ `grep "\#'''+akrrHeader+''' \[Start\]" $HOME/.bashrc` == *"'''+akrrHeader+''' [Start]"* ]]
   then
       echo "Updating AKRR record in $HOME/.bashrc, backing to $HOME/.bashrc_akrrbak"
       cp $HOME/.bashrc $HOME/.bashrc_akrrbak
       head -n "$(( $(grep -n '\#'''+akrrHeader+''' \[Start\]' $HOME/.bashrc_akrrbak | head -n 1 | cut -d ":" -f 1) - 1 ))" $HOME/.bashrc_akrrbak > $HOME/.bashrc
       tail -n "+$(( $(grep -n '\#'''+akrrHeader+''' \[End\]' $HOME/.bashrc_akrrbak | head -n 1 | cut -d ":" -f 1) + 1 ))" $HOME/.bashrc_akrrbak  >> $HOME/.bashrc
   fi
fi''')
            out=akrr.sshCommand(rsh,'''
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
        except Exception,e:
            msg2=str_io.getvalue()
            msg2+="\n"+traceback.format_exc()
            sys.stdout=sys.__stdout__
            sys.stderr=sys.__stderr__
            logerr("Can not connect to """+resource['name']+"\n"+
                   "Probably invalid credential, see full error report below",msg2)
            exit()
        #enabling resource for execution
        try:
            dbAK,curAK=akrr.getAKDB(True)
            
            curAK.execute('''SELECT * FROM resource WHERE nickname=%s''', (resource_name,))
            resource_in_AKDB = curAK.fetchall()
            if len(resource_in_AKDB)==0:
                log("There is no record of %s in mod_appkernel.resource will add one."%(resource_name,),highlight="warning")
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
            log("Enabled %s in mod_appkernel.resource for tasks execution and made it visible to XDMoD UI."%(resource_name),highlight="ok")
        except Exception,e:
            logerr("Can not connect to AK DB\n"+
                   "Probably invalid credential, see full error report below",traceback.format_exc())
        #enabling resource for execution
        try:
            r = akrrrestclient.put('/resources/'+resource_name+'/on')
            if r.status_code==200:
                log('Successfully enabled '+resource_name)
            else:
                logerr("Can not enable resource through AKRR REST API ( """+akrrrestclient.restapi_host+" )\n"+
                   "See server response below",json.dumps(r.json(),indent=4))
        except Exception,e:
            logerr("Can not enable resource through AKRR REST API ( """+akrrrestclient.restapi_host+" )\n"+
                   "Is it still running?\n"+
                   "See full error report below",traceback.format_exc())
        
    log("#"*80)
    log("Result:")
    if(errorCount>0):
        logerr("There are %d errors, fix them."%errorCount)
        
    if(warningCount>0):
        log("\nThere are %d warnings.\nif warnings have sense (highlighted in yellow), you can move to next step!\n"%warningCount,highlight="warning")
    if(errorCount==0 and warningCount==0):
        log("\nDONE, you can move to next step!\n",highlight="ok")
    os.remove(test_job_lock_filename)
    
if __name__ == '__main__':
    resource_validation_and_deployment()
    
