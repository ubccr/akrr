import sys
import datetime
import time
import inspect
import os
import re
import traceback
import types

import MySQLdb
import MySQLdb.cursors

import copy

from akrr import get_akrr_dirs
from .akrrlogging import *
from .util import which

#log("initial loading",highlight="ok")
# directory of this file
curdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

akrr_dirs=get_akrr_dirs()

in_src_install=akrr_dirs['in_src_install']
akrr_mod_dir=akrr_dirs['akrr_mod_dir']
akrr_bin_dir=akrr_dirs['akrr_bin_dir']
akrr_cli_fullpath=akrr_dirs['akrr_cli_fullpath']
akrr_cfg=akrr_dirs['akrr_cfg']
akrr_home=akrr_dirs['akrr_home']
cfg_dir=akrr_dirs['cfg_dir']
templates_dir=akrr_dirs['templates_dir']
default_dir=akrr_dirs['default_dir']
appker_repo_dir=akrr_dirs['appker_repo_dir']

#load default values
from .akrrcfgdefault import *

#load akrr params
exec(open(cfg_dir + "/akrr.conf").read())

#set default values for unset variables
#make absolute paths from relative
if data_dir[0] != '/':
    data_dir = os.path.abspath(os.path.join(cfg_dir, data_dir))
if completed_tasks_dir[0] != '/':
    completed_tasks_dir = os.path.abspath(os.path.join(cfg_dir, completed_tasks_dir))

if restapi_certfile != '/':
    restapi_certfile = os.path.abspath(os.path.join(cfg_dir, restapi_certfile))
#wrongfields technical fields from loading python file which we don't want to 
#see in resource and app kernel parameters dict
wrongfieldsdict = {}
exec('wrongfieldsdict="wrongfieldsdict"', wrongfieldsdict)
wrongfields = list(wrongfieldsdict.keys())

###################################################################################################
#
# Load Resources
#
###################################################################################################
resources = {}

def verifyResourceParams(resource):
    """
    Perform simplistic resource parameters validation
    
    raises error
    """
    #check that parameters for presents and type
    #format: key,type,can be None,must have parameter 
    parameters_types=[
        ['info',                        str,       False,False],
        ['localScratch',                str,       False,True],
        ['batchJobTemplate',            str,       False,True],
        ['remoteAccessNode',            str,       False,True],
        ['name',                        str,       False,False],
        ['akrrCommonCommandsTemplate',   str,       False,True],
        ['networkScratch',              str,       False,True],
        ['ppn',                         int,          False,True],
        ['remoteCopyMethod',            str,       False,True],
        ['sshUserName',                 str,       False,True],
        ['sshPassword',                 str,       True, False],
        ['sshPrivateKeyFile',           str,       True, False],
        ['sshPrivateKeyPassword',       str,       True, False],
        ['batchScheduler',              str,       False,True],
        ['remoteAccessMethod',          str,       False,True],
        ['appKerDir',                   str,       False,True],
        ['akrrCommonCleanupTemplate',    str,       False,True],
        ['akrrData',                     str,       False,True]
    ]
    
    for variable,ttype,nulable,must in parameters_types:
        if (must==True) and (variable not in resource):
            raise NameError("Syntax error in "+resource['name']+"\nVariable %s is not set"%(variable,))
        if variable not in resource:
            continue
        if type(resource[variable])==type(None) and nulable==False:
            raise TypeError("Syntax error in "+resource['name']+"\nVariable %s can not be None"%(variable,))
        if type(resource[variable])!=ttype and not (type(resource[variable])==type(None) and nulable==True):
            raise TypeError("Syntax error in "+resource['name']+
                   "\nVariable %s should be %s"%(variable,str(ttype))+
                   ". But it is "+str(type(resource[variable])))

def loadResource(resource_name):
    """
    load resource configuration file, do minimalistic validation
    return dict with resource parameters
    
    raises error if can not load
    """
    try:
        default_resource_cfg_filename=os.path.join(default_dir,"default.resource.conf")
        resource_cfg_filename=os.path.join(cfg_dir,'resources',resource_name,"resource.conf")
        
        if not os.path.isfile(default_resource_cfg_filename):
            akrrError(ERROR_GENERAL,"Default resource configuration file do not exists (%s)!"%default_resource_cfg_filename)
        if not os.path.isfile(resource_cfg_filename):
            akrrError(ERROR_GENERAL,"Resource configuration file do not exists (%s)!"%resource_cfg_filename)
        
        tmp={}
        exec(open(default_resource_cfg_filename).read(),tmp)
        exec(open(resource_cfg_filename).read(), tmp)
        resource={}
        for key,val in tmp.items():
            if inspect.ismodule(val):continue
            if wrongfields.count(key)>0:continue
            resource[key]=val
        
        #mapped options in resource input file to those used in AKRR
        if 'akrrData' in resource:resource['akrrdata']=resource['akrrData']
        if 'appKerDir' in resource:resource['AppKerDir']=resource['appKerDir']
        if 'name' not in resource:resource['name']=resource_name
        
        #last modification time for future reloading
        resource['default_resource_cfg_filename']=default_resource_cfg_filename
        resource['resource_cfg_filename']=resource_cfg_filename
        resource['default_resource_cfg_file_mtime']=os.path.getmtime(default_resource_cfg_filename)
        resource['resource_cfg_file_mtime']=os.path.getmtime(resource_cfg_filename)
        
        #here should be validation
        verifyResourceParams(resource)
        
        return resource
    except Exception as e:
        raise akrrError(ERROR_GENERAL,"Can not load resource configuration for "+resource_name+":\n"+str(e))
def loadAllResources():
    """
    load all resources from configuration directory
    """
    global resources
    for resource_name in os.listdir(cfg_dir + "/resources"):
        if resource_name not in ['notactive','templates']:
            # log("loading "+resource_name)
            try:
                resource=loadResource(resource_name)
                resources[resource_name]=resource
            except Exception as e:
                logerr(str(e),traceback.format_exc())

def FindResourceByName(resource_name):
    """
    return resource parameters
    if resource configuration file was modified will reload it
    
    raises error if can not find
    """
    global resources
    if resource_name not in resources:
        resource=loadResource(resource_name)
        resources[resource_name]=resource
    
    resource=resources[resource_name]
    if (os.path.getmtime(resource['default_resource_cfg_filename'])!=resource['default_resource_cfg_file_mtime'] or
        os.path.getmtime(resource['resource_cfg_filename'])!=resource['resource_cfg_file_mtime']):
        del resources[resource_name]
        resource=loadResource(resource_name)
        resources[resource_name]=resource
    return resources[resource_name]

loadAllResources()
###################################################################################################
#check rest-api certificate
#
if not os.path.isfile(restapi_certfile):
    #assuming it is relative to akrrcfg
    restapi_certfile = os.path.abspath(os.path.join(cfg_dir, restapi_certfile))
if not os.path.isfile(restapi_certfile):
    raise ValueError('Cannot locate SSL certificate for rest-api HTTPS server', restapi_certfile)

###################################################################################################
#
# Load App Kernels
#
###################################################################################################
apps = {}

def verifyAppParams(app):
    """
    Perform simplistic app parameters validation
    
    raises error
    """
    #check that parameters for presents and type
    #format: key,type,can be None,must have parameter 
    parameters_types=[
        ['parser',               str,      False,True],
        ['executable',           str,       True,True],
        ['input',                str,       True,True],
        ['walllimit',            int,         False,True],
        ['runScript',            dict,        False,False]
    ]
    
    for variable,ttype,nulable,must in parameters_types:
        if (must==True) and (variable not in app):
            raise NameError("Syntax error in "+app['name']+"\nVariable %s is not set"%(variable,))
        if variable not in app:
            continue
        if type(app[variable])==type(None) and nulable==False:
            raise TypeError("Syntax error in "+app['name']+"\nVariable %s can not be None"%(variable,))
        if type(app[variable])!=ttype and not (type(app[variable])==type(None) and nulable==True):
            raise TypeError("Syntax error in "+app['name']+
                   "\nVariable %s should be %s"%(variable,str(ttype))+
                   ". But it is "+str(type(app[variable])))

def loadApp(app_name):
    """
    load app configuration file, do minimalistic validation
    return dict with app parameters
    
    raises error if can not load
    """
    try:
        default_app_cfg_filename=os.path.join(default_dir,"default.app.conf")
        app_cfg_filename=os.path.join(default_dir,app_name+".app.conf")
        
        if not os.path.isfile(default_app_cfg_filename):
            akrrError(ERROR_GENERAL,"Default application kernel configuration file do not exists (%s)!"%default_app_cfg_filename)
        if not os.path.isfile(app_cfg_filename):
            akrrError(ERROR_GENERAL,"application kernel configuration file do not exists (%s)!"%app_cfg_filename)
        
        tmp={}
        exec(open(default_app_cfg_filename).read(), tmp)
        exec(open(app_cfg_filename).read(), tmp)
        app={}
        for key,val in tmp.items():
            if inspect.ismodule(val):continue
            if wrongfields.count(key)>0:continue
            app[key]=val
        #load resource specific parameters
        for resource_name in os.listdir(os.path.join(cfg_dir, "resources")):
            if resource_name not in ['notactive','templates']:
                resource_specific_app_cfg_filename=os.path.join(cfg_dir, "resources",resource_name,app_name+".app.conf")
                if os.path.isfile(resource_specific_app_cfg_filename):
                    tmp=copy.deepcopy(app['appkernelOnResource']['default'])
                    exec(compile(open(resource_specific_app_cfg_filename).read(), resource_specific_app_cfg_filename, 'exec'),tmp)
                    app['appkernelOnResource'][resource_name]={}
                    for key,val in tmp.items():
                        if inspect.ismodule(val):continue
                        if wrongfields.count(key)>0:continue
                        app['appkernelOnResource'][resource_name][key]=val
                    app['appkernelOnResource'][resource_name]['resource_specific_app_cfg_filename']=resource_specific_app_cfg_filename
                    app['appkernelOnResource'][resource_name]['resource_specific_app_cfg_file_mtime']=os.path.getmtime(resource_specific_app_cfg_filename)
        
        #mapped options in app input file to those used in AKRR
        if 'name' not in app:app['name']=app_name
        if 'nickname' not in app:app['nickname']=app_name+".@nnodes@"
        
        #last modification time for future reloading
        app['default_app_cfg_filename']=default_app_cfg_filename
        app['app_cfg_filename']=app_cfg_filename
        app['default_app_cfg_file_mtime']=os.path.getmtime(default_app_cfg_filename)
        app['app_cfg_file_mtime']=os.path.getmtime(app_cfg_filename)
        
        #here should be validation
        verifyAppParams(app)
        
        return app
    except Exception as e:
        raise akrrError(ERROR_GENERAL,"Can not load app configuration for "+app_name+":\n"+str(e)+traceback.format_exc())

def loadAllApp():
    """
    load all resources from configuration directory
    """
    global apps
    for fl in os.listdir(os.path.join(curdir,'default_conf')):
        if fl=="default.app.conf":
            continue
        if fl.endswith(".app.conf"):
            app_name=re.sub('.app.conf$','',fl)
            #log("loading "+app_name)
            try:
                app=loadApp(app_name)
                apps[app_name]=app
            except Exception as e:
                logerr(str(e),traceback.format_exc())

def FindAppByName(app_name):
    """
    return apps parameters
    if resource configuration file was modified will reload it
    
    raises error if can not find
    """
    global apps
    if app_name not in apps:
        app=loadApp(app_name)
        apps[app_name]=app
        return apps[app_name]
    
    reloadAppCfg=False
    app=apps[app_name]
    #
    if (os.path.getmtime(app['default_app_cfg_filename'])!=app['default_app_cfg_file_mtime'] or
        os.path.getmtime(app['app_cfg_filename'])!=app['app_cfg_file_mtime']):
        reloadAppCfg=True
    
    #check if new resources was added
    for resource_name in os.listdir(os.path.join(cfg_dir, "resources")):
        if resource_name not in ['notactive','templates']:
            resource_specific_app_cfg_filename=os.path.join(cfg_dir, "resources",resource_name,app_name+".app.conf")
            if os.path.isfile(resource_specific_app_cfg_filename):
                if resource_name not in app['appkernelOnResource']:
                    reloadAppCfg=True
                else:
                    if app['appkernelOnResource'][resource_name]['resource_specific_app_cfg_file_mtime']!=os.path.getmtime(resource_specific_app_cfg_filename):
                        reloadAppCfg=True
    #check if new resources were removed
    for resource_name in app['appkernelOnResource']:
        if resource_name not in ['default']:
            resource_specific_app_cfg_filename=os.path.join(cfg_dir, "resources",resource_name,app_name+".app.conf")
            if not os.path.isfile(resource_specific_app_cfg_filename):
                reloadAppCfg=True
            
    if reloadAppCfg:
        del apps[app_name]
        app=loadApp(app_name)
        apps[app_name]=app
    return apps[app_name]

loadAllApp()

def PrintOutResourceAndAppSummary():
    print(">" * 112)
    print("# Resources:")
    print("#" * 112)
    for k,r in resources.items():
        print(r['name'])
    print("#" * 112)
    print("# Applications:")
    print("#" * 112)
    for k,a in apps.items():
        print(a['name'], "'walllimit':" + str(a['walllimit']))
    print("<" * 112)
#PrintOutResourceAndAppSummary()


#SSH remote access
sshTimeout = 60
shellPrompt = "PROMPTtTtT"
sshTimeSleep = 0.25
sshCommandStartEcho = "StArTEd_ExeCUTEtIoM_SucCeSsFully"
sshCommandEndEcho = "ExeCUTEd_SucCeSsFully"

promptsCollection={}

def sshAccess(remotemachine, ssh='ssh', username=None, password=None, PrivateKeyFile=None, PrivateKeyPassword=None,
              logfile=None, command=None, pwd1=None, pwd2=None):
    """login to remote machine and return pexpect.spawn instance.
    if command!=None will execute commands and return the output"""
    #pack command line and arguments
    cmd = ssh
    mode = 'ssh'
    if ssh.find('scp') >= 0:
        mode = 'scp'

    cmdarg = []
    #Add identity file if needed
    if PrivateKeyFile != None:
        cmdarg.extend(["-i", PrivateKeyFile])
        cmd += " -i " + PrivateKeyFile
    #Add username@host
    if mode == 'ssh':
        if username != None:
            cmdarg.append("%s@%s" % (username, remotemachine))
            cmd += " %s@%s" % (username, remotemachine)
        else:
            cmdarg.append("%s" % (remotemachine))
            cmd += " %s" % (remotemachine)

        if command != None and ssh!='ssh-copy-id':
            cmdarg.append("\" %s;echo %s\"" % (command, sshCommandStartEcho))
            cmd += " \"echo %s;%s;echo %s\"" % (sshCommandStartEcho, command, sshCommandEndEcho)
    else:
        command = pwd2
        cmd += " %s %s" % (pwd1, pwd2)
    print(cmd)
    
    #find the prompt
    #if 
    #tmp=$(set +x; (PS4=$PS1; set -x; :) 2>&1); tmp=${tmp#*.}; echo ${tmp%:}
    
    
    #Try to get access
    from . import pexpect

    rsh = None
    try:
        rsh = pexpect.spawn(cmd, encoding='utf-8')  #, logfile=logfile)
        #rsh.setwinsize(256,512)

        rsh.logfile_read = logfile
        
        expect = [
            "Are you sure you want to continue connecting (yes/no)?",
            '[Pp]assword:',
            "Enter passphrase for key",
            
            #username+'.*[\$>]\s*$',
            #'[#\$>]\s*',
            #'[^#]*[#\$]\s*',
            #':~>\s*$'#,
            #shellPrompt
        ]
        addedPromptSearch=False
        if mode == 'ssh' and command == None and password==None and PrivateKeyPassword==None:
            #i.e. expecting passwordless access
            expect.append('[#\$>]\s*')
            addedPromptSearch=True
        bOnHeadnode = False

        
        sshTimeoutNew = sshTimeout
        if mode == 'ssh' and command == None:
            sshTimeoutNew=2.0
        countPasses=0
        PasswordCount = 0
        PrivateKeyPasswordCount = 0
        
        while not bOnHeadnode:
            i=-1
            try:
                i = rsh.expect(expect, timeout=sshTimeoutNew)
            except pexpect.TIMEOUT as e:
                if mode == 'ssh' and command == None:
                    #add prompts
                    if countPasses==0:
                        if password==None and PrivateKeyPassword==None:
                            expect.append('[#\$>]\s*')
                            addedPromptSearch=True
                            sshTimeoutNew = sshTimeout
                        i=6
                    else:
                        #assuming it has unrecognized prompt
                        #lets try to sent it
                        rsh.sendline(" export PS1='%s '" % (shellPrompt))
                        rsh.expect(shellPrompt, timeout=sshTimeout) #twice because one from echo
                        rsh.expect(shellPrompt, timeout=sshTimeout)
                        i=6
                else:
                    raise e
            countPasses+=1
            if i == 0:  #Are you sure you want to continue connecting (yes/no)?
                rsh.sendline('yes')
            if i == 1:  #[pP]assword
                if password != None:
                    if PasswordCount > 0:
                        rsh.sendcontrol('c')
                        rsh.close(force=True)
                        del rsh
                        raise akrrError(ERROR_CANT_CONNECT, "Password for %s is incorrect." % (remotemachine))
                    time.sleep(sshTimeSleep)  #so that the remote host have some time to turn off echo
                    rsh.sendline(password)
                    #add prompt search since password already asked
                    expect.append('[#\$>]\s*')
                    addedPromptSearch=True
                    PasswordCount += 1
                else:
                    rsh.sendcontrol('c')
                    rsh.close(force=True)
                    del rsh
                    raise akrrError(ERROR_CANT_CONNECT,
                                   " %s had requested a password and one was not provided." % (remotemachine))
            if i == 2:
                if PrivateKeyPassword != None:
                    if PrivateKeyPasswordCount > 0:
                        #i.e. PrivateKeyPassword was entered several times incorrectly and now remote servise asking for password
                        rsh.sendcontrol('c')
                        rsh.close(force=True)
                        del rsh
                        raise akrrError(ERROR_CANT_CONNECT,
                                       "Private key password for %s is incorrect." % (remotemachine))
                    time.sleep(sshTimeSleep)  #so that the remote host have some time to turn off echo
                    rsh.sendline(PrivateKeyPassword)
                    #add prompt search since password already asked
                    expect.append('[#\$>]\s*')
                    addedPromptSearch=True
                    PrivateKeyPasswordCount += 1
                else:
                    rsh.sendcontrol('c')
                    rsh.close(force=True)
                    del rsh
                    raise akrrError(ERROR_CANT_CONNECT,
                                   "%s had requested a private key password and one was not provided." % (
                                       remotemachine))
            if i >= 3:
                bOnHeadnode = True
                #are we really there?
                
        if mode == 'ssh' and command == None:
            rsh.sendline(" echo %s;\\\nexport PS1='%s ';\\\necho %s" % (sshCommandStartEcho, shellPrompt, sshCommandEndEcho))
            rsh.sendline(" ")
            rsh.sendline(" ")
            r=sshCommandEndEcho+r'.+'+shellPrompt+r'.+'+shellPrompt+r'.+'+shellPrompt
            rsh.expect(r, timeout=sshTimeout)  #this pattern ensure proper handling when it thinks that in ssh hello message there is a prompt
            
            time.sleep(1)
            #test that we really in prompt
            msg=sshCommand(rsh,"echo TeStTeStTeStThEproMPT")
            if msg.strip()!="TeStTeStTeStThEproMPT":
                raise akrrError(ERROR_CANT_CONNECT,
                                       "%s can not determine prompt." % (
                                           remotemachine))
        rsh.remotemachine=remotemachine
        if logfile != None: logfile.flush()
        #print expect[i]
    except pexpect.TIMEOUT as e:
        #print "pexpect.TIMEOUT"
        msg = copy.deepcopy(rsh.before)
        rsh.close(force=True)
        del rsh
        raise akrrError(ERROR_CANT_CONNECT,
                       "Timeout period elapsed prior establishing the connection to %s." % (remotemachine) + msg, e)
    except pexpect.EOF as e:
        ExeCUTEd_SucCeSsFully = False
        if command != None:
            ll = rsh.before.splitlines(False)
            if len(ll) > 1:
                if ll[-1].endswith(sshCommandEndEcho) or ll[-2].endswith(sshCommandEndEcho):
                    ExeCUTEd_SucCeSsFully = True
            if len(ll) > 0:
                if ll[-1].endswith(sshCommandEndEcho):
                    ExeCUTEd_SucCeSsFully = True
            if mode == 'scp':
                ExeCUTEd_SucCeSsFully = True
            if ssh == 'ssh-copy-id':
                ExeCUTEd_SucCeSsFully = True
        if command == None or (command != None and ExeCUTEd_SucCeSsFully == False):
            msg = copy.deepcopy(rsh.before)
            rsh.close(force=True)
            del rsh
            raise akrrError(ERROR_CANT_CONNECT, "Probably %s refused the connection. " % (remotemachine) + msg, e)
        else:
            #user trying to execute command remotely
            msg = copy.deepcopy(rsh.before)
            rsh.close(force=True)
            del rsh
            return msg[(msg.find('\n', msg.find(sshCommandStartEcho) + 5) + len("\n") + 0):msg.rfind(sshCommandEndEcho)]
    #print "}"*100
    if mode == 'ssh' and command != None:
        #print "!"*100
        #print rsh.before
        #print "!"*100
        return copy.deepcopy(rsh.before)
    return rsh


def sshResource(resource, command=None):
    name = resource['name']
    headnode = resource.get('remoteAccessNode', name)
    remoteAccessMethod = resource.get('remoteAccessMethod', 'ssh')
    username = resource.get('sshUserName', None)
    sshPassword = resource.get('sshPassword', None)
    sshPrivateKeyFile = resource.get('sshPrivateKeyFile', None)
    sshPrivateKeyPassword = resource.get('sshPrivateKeyPassword', None)

    logfile = sys.stdout
    #logfile=None

    rsh = sshAccess(headnode, ssh=remoteAccessMethod, username=username, password=sshPassword,
                    PrivateKeyFile=sshPrivateKeyFile, PrivateKeyPassword=sshPrivateKeyPassword, logfile=logfile,
                    command=command)
    return rsh


def scpFromResource(resource, pwd1, pwd2, opt=""):
    name = resource['name']
    remotemachine = resource.get('remoteAccessNode', name)
    remoteInvocationMethod = resource.get('remoteCopyMethod', 'scp') + " " + opt + " "
    username = resource.get('sshUserName', None)
    sshPassword = resource.get('sshPassword', None)
    sshPrivateKeyFile = resource.get('sshPrivateKeyFile', None)
    sshPrivateKeyPassword = resource.get('sshPrivateKeyPassword', None)

    logfile = sys.stdout
    #logfile=None
    pwd1fin = ""
    if username != None:
        pwd1fin += " %s@%s:%s" % (username, remotemachine, pwd1)
    else:
        pwd1fin += " %s:%s" % (remotemachine, pwd1)

    rsh = sshAccess(remotemachine, ssh=remoteInvocationMethod, username=username, password=sshPassword,
                    PrivateKeyFile=sshPrivateKeyFile, PrivateKeyPassword=sshPrivateKeyPassword, logfile=logfile,
                    pwd1=pwd1fin, pwd2=pwd2)
    return rsh


def scpToResource(resource, pwd1, pwd2, opt="",logfile=None):
    if logfile==None:
        logfile=sys.stdout
    name = resource['name']
    remotemachine = resource.get('remoteAccessNode', name)
    remoteInvocationMethod = resource.get('remoteCopyMethod', 'scp') + " " + opt + " "
    username = resource.get('sshUserName', None)
    sshPassword = resource.get('sshPassword', None)
    sshPrivateKeyFile = resource.get('sshPrivateKeyFile', None)
    sshPrivateKeyPassword = resource.get('sshPrivateKeyPassword', None)

    #logfile = sys.stdout
    #logfile=None
    pwd2fin = ""
    if username != None:
        pwd2fin += " %s@%s:%s" % (username, remotemachine, pwd2)
    else:
        pwd2fin += " %s:%s" % (remotemachine, pwd2)

    rsh = sshAccess(remotemachine, ssh=remoteInvocationMethod, username=username, password=sshPassword,
                    PrivateKeyFile=sshPrivateKeyFile, PrivateKeyPassword=sshPrivateKeyPassword, logfile=logfile,
                    pwd1=pwd1, pwd2=pwd2fin)
    return rsh


def sshCommandNoReturn(sh, cmd):
    cmdfin = " "+cmd
    try:
        #flush the buffer
        sh.read_nonblocking (1000000, 0)
    except:
        pass
    
    sh.sendline(cmdfin)
    sh.expect(shellPrompt, timeout=sshTimeout)

    msg = sh.before
    return msg


def sshCommand(sh, cmd):
    cmdfin = " echo %s;\\\n%s;\\\necho %s" % (sshCommandStartEcho, cmd, sshCommandEndEcho)
    try:
        #flush the buffer
        sh.read_nonblocking (1000000, 0)
    except:
        pass
    
    sh.sendline(cmdfin)
    sh.expect(shellPrompt, timeout=sshTimeout)
    msg = sh.before
    msg=msg[(msg.find('\n', msg.rfind(sshCommandStartEcho) + 5) + len("\n") + 0):msg.rfind(sshCommandEndEcho)]
    regex = re.compile(r'\x1b[^m]*m')
    return regex.sub("",msg)


def replaceATvarAT(s, ds):
    """ replaces @variable@ by ds[any]['variable'] """
    d = {}
    #print "#"*80
    for di in ds:
        d.update(di)
    while s.find("@") >= 0:
        #print s
        at1 = s.find("@")
        at2 = s.find("@", at1 + 1)
        varname = s[at1 + 1:at2]
        varvalue = d[varname]
        #print "#",varname,varvalue
        s = s.replace("@" + varname + "@", str(varvalue))
        #print s
    return s


def printException(Str=None):
    import traceback

    print("###### Exception ######" + ">" * 97)
    if Str != None:
        print(Str)
        print("-" * 120)
    print(traceback.format_exc())
    print("###### Exception ######" + "<" * 97)


def CleanUnicode(s):
    if s == None: return None
    replacements = {
        '\u2018': "'",
        '\u2019': "'",
    }
    for src, dest in replacements.items():
        s = s.replace(src, dest)
    return s


def formatRecursively(s, d, keepDoubleBrakets=False):
    s = s.replace('{{', 'LeFtyCurlyBrrakkets')
    s = s.replace('}}', 'RiGhTyCurlyBrrakkets')
    s0 = s.format(**d)
    while s0 != s:
        s = s0
        s = s.replace('{{', 'LeFtyCurlyBrrakkets')
        s = s.replace('}}', 'RiGhTyCurlyBrrakkets')
        s0 = s.format(**d)
    if keepDoubleBrakets:
        s0 = s0.replace('LeFtyCurlyBrrakkets', '{{')
        s0 = s0.replace('RiGhTyCurlyBrrakkets', '}}')
    else:
        s0 = s0.replace('LeFtyCurlyBrrakkets', '{')
        s0 = s0.replace('RiGhTyCurlyBrrakkets', '}')
    return s0


def getDB(dictCursor=False):
    if dictCursor:
        db = MySQLdb.connect(host=akrr_db_host, port=akrr_db_port, user=akrr_db_user,
                             passwd=akrr_db_passwd, db=akrr_db_name, cursorclass=MySQLdb.cursors.DictCursor)
    else:
        db = MySQLdb.connect(host=akrr_db_host, port=akrr_db_port, user=akrr_db_user,
                             passwd=akrr_db_passwd, db=akrr_db_name)
    cur = db.cursor()
    return (db, cur)


def getAKDB(dictCursor=False):
    if dictCursor:
        db = MySQLdb.connect(host=ak_db_host, port=ak_db_port, user=ak_db_user,
                             passwd=ak_db_passwd, db=ak_db_name, cursorclass=MySQLdb.cursors.DictCursor)
    else:
        db = MySQLdb.connect(host=ak_db_host, port=ak_db_port, user=ak_db_user,
                             passwd=ak_db_passwd, db=ak_db_name)
    cur = db.cursor()
    return db, cur


def getXDDB(dictCursor=False):
    if dictCursor:
        db = MySQLdb.connect(host=xd_db_host, port=xd_db_port, user=xd_db_user,
                             passwd=xd_db_passwd, db=xd_db_name, cursorclass=MySQLdb.cursors.DictCursor)
    else:
        db = MySQLdb.connect(host=xd_db_host, port=xd_db_port, user=xd_db_user,
                             passwd=xd_db_passwd, db=xd_db_name)
    cur = db.cursor()
    return db, cur

def getExportDB(dictCursor=False):
    if dictCursor:
        db = MySQLdb.connect(host=export_db_host, port=export_db_port, user=export_db_user,
                             passwd=export_db_passwd, db=export_db_name, cursorclass=MySQLdb.cursors.DictCursor)
    else:
        db = MySQLdb.connect(host=export_db_host, port=export_db_port, user=export_db_user,
                             passwd=export_db_passwd, db=export_db_name)
    cur = db.cursor()
    return (db, cur)

from .util import getFormatedRepeatIn,getTimeDeltaRepeatIn,getFormatedTimeToStart,getDatatimeTimeToStart
