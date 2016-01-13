import unittest

import sys
import datetime
import time
import inspect
import os
import re
import traceback
import types
import shutil

import MySQLdb
import MySQLdb.cursors

import subprocess

try:
    import argparse
except:
    #add argparse directory to path and try again
    curdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    argparsedir=os.path.abspath(os.path.join(curdir,"..","..","3rd_party","argparse-1.3.0"))
    if argparsedir not in sys.path:sys.path.append(argparsedir)
    import argparse

curdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
akrr_arch_home = os.path.abspath(os.path.join(curdir, "./../.."))
#Append paths to 3rd party libraries
if (akrr_arch_home + "/3rd_party") not in sys.path:
    sys.path.append(akrr_arch_home + "/3rd_party")
    sys.path.append(akrr_arch_home + "/3rd_party/pexpect-3.2")

#add check_output fuction to subprocess module if python is old
if "check_output" not in dir( subprocess ): # duck punch it in!
    def f(*popenargs, **kwargs):
        if 'stdout' in kwargs:
            raise ValueError('stdout argument not allowed, it will be overridden.')
        process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
        output, unused_err = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            raise subprocess.CalledProcessError(retcode, cmd)
        return output
    subprocess.check_output = f

import pexpect

verbosity=1
python_bin=sys.executable
prompt='ProMpt> '
cfg=None

def testUtilSetVerbosity(v):
    global verbosity
    verbosity=v

class InstallationCfg:
    """test installation configuration"""
    def __init__(self, filename):    
        wrongfieldsdict = {}
        exec 'wrongfieldsdict="wrongfieldsdict"' in wrongfieldsdict
        wrongfields = wrongfieldsdict.keys()
        
        tmp={}
        execfile(filename,tmp)
        for key,val in tmp.iteritems():
            if inspect.ismodule(val):continue
            if wrongfields.count(key)>0:continue
            setattr(self, key, val)

def loadInstallationCfg(cfgFilename):
    global cfg
    cfg=InstallationCfg(cfgFilename)

class ShellSpawn(pexpect.spawn):
    def runcmd(self,cmd,clearSpecialSymbols=False,printOutput=False, addAfter=True):
        self.sendline(cmd)
        self.expect(self.prompt)
        self.lastcmd=cmd+"\n"
        output=self.getCmdOutput(clearSpecialSymbols=clearSpecialSymbols,addAfter=addAfter,replaceCMD=False)
        output=self.getCmdOutput(clearSpecialSymbols=False,addAfter=addAfter,replaceCMD=False)
        if hasattr(self, 'output'):self.output+=output
        if verbosity>=3:
            sys.stdout.write(output)
            sys.stdout.flush()
        return output
    
    def getPromptBefore(self,clearSpecialSymbols=False, addAfter=False):
        s=self.prompt+" "+self.before
        if addAfter and isinstance(self.after, (str, unicode)):
            s+=self.after
        s=s.replace("\r",'')
        if clearSpecialSymbols:
            return ClearOutputText(s)
        else:
            return s
    def getCmdOutput(self,clearSpecialSymbols=True, addAfter=False,replaceCMD=True):
        s=self.before
        if addAfter and isinstance(self.after, (str, unicode)):
            s+=self.after
        s=s.replace("\r",'')
        if replaceCMD:
            s=s.replace(self.lastcmd,'',1)
        if clearSpecialSymbols:
            return ClearOutputText(s)
        else:
            return s
    def justExpect(self,pattern,timeoutMessage="EOF or TIMEOUT",replaceCMD=False,addAfter=True,**kwargs):
        """custom expect helper.
        It added EOF and TIMEOUT patterns and raise excemption with timeoutMessage message in match case. 
        It also print to stdout the output if verbosity>=3.
        If a pattern is list return index of match
        If pattern is not list return output cleared from special symbols"""
        
        p=[pexpect.EOF, pexpect.TIMEOUT]
        if type(pattern) is list:
            p+=pattern
        else:
            p.append(pattern)
        imatch=self.expect(p,**kwargs)
        output=self.getCmdOutput(clearSpecialSymbols=False,addAfter=addAfter,replaceCMD=False)
        if hasattr(self, 'output'):self.output+=output
        if verbosity>=3:
            sys.stdout.write(output)
            sys.stdout.flush()
        if imatch==0 or imatch==1:
            msg=timeoutMessage
            if hasattr(self, 'timeoutMessage') and timeoutMessage=="EOF or TIMEOUT":
                msg=self.timeoutMessage
            raise Exception(msg)
        
        if type(pattern) is list:
            return imatch-2
        else:
            return self.getCmdOutput(clearSpecialSymbols=True, addAfter=addAfter,replaceCMD=replaceCMD)
        
    def sendlineExpect(self,cmd,pattern,timeoutMessage="EOF or TIMEOUT",replaceCMD=True,addAfter=True,**kwargs):
        """custom expect helper.
        It added EOF and TIMEOUT patterns and raise excemption with timeoutMessage message in match case. 
        It also print to stdout the output if verbosity>=3.
        If a pattern is list return index of match
        If pattern is not list return output cleared from special symbols"""
        self.lastcmd=cmd+"\n"
        self.sendline(cmd)
        
        p=[pexpect.EOF, pexpect.TIMEOUT]
        if type(pattern) is list:
            p+=pattern
        else:
            p.append(pattern)
        imatch=self.expect(p,**kwargs)
        output=self.getCmdOutput(clearSpecialSymbols=False,addAfter=addAfter,replaceCMD=False)
        if hasattr(self, 'output'):self.output+=output
        if verbosity>=3:
            sys.stdout.write(output)
            sys.stdout.flush()
        if imatch==0 or imatch==1:
            msg=timeoutMessage
            if hasattr(self, 'timeoutMessage') and timeoutMessage=="EOF or TIMEOUT":
                msg=self.timeoutMessage
            raise Exception(msg)
        
        if type(pattern) is list:
            return imatch-2
        else:
            return self.getCmdOutput(clearSpecialSymbols=True, addAfter=addAfter,replaceCMD=replaceCMD)
    
    def expectSendline(self,pattern,cmd,timeoutMessage="EOF or TIMEOUT",replaceCMD=True,addAfter=True,**kwargs):
        """custom expect helper.
        It added EOF and TIMEOUT patterns and raise excemption with timeoutMessage message in match case. 
        It also print to stdout the output if verbosity>=3.
        If a pattern is list return index of match
        If pattern is not list return output cleared from special symbols"""
        
        p=[pexpect.EOF, pexpect.TIMEOUT]
        if type(pattern) is list:
            p+=pattern
        else:
            p.append(pattern)
        imatch=self.expect(p,**kwargs)
        output=self.getCmdOutput(clearSpecialSymbols=False,addAfter=addAfter,replaceCMD=False)
        if hasattr(self, 'output'):self.output+=output
        if verbosity>=3:
            sys.stdout.write(output)
            sys.stdout.flush()
        if imatch==0 or imatch==1:
            msg=timeoutMessage
            if hasattr(self, 'timeoutMessage') and timeoutMessage=="EOF or TIMEOUT":
                msg=self.timeoutMessage
            raise Exception(msg)
        
        self.lastcmd=cmd+"\n"
        self.sendline(cmd)
        
        if type(pattern) is list:
            return imatch-2
        else:
            return self.getCmdOutput(clearSpecialSymbols=True, addAfter=addAfter,replaceCMD=replaceCMD)
    def startcmd(self,cmd):
        self.lastcmd=cmd+"\n"
        self.sendline(cmd)
    
def printNote(msg):
    if verbosity>=3:
        print "\033[100m\033[36m"+msg+"\033[0m"

regcolorremove = re.compile("\033\[[0-9;]+m") 
def ClearOutputText(s):
    if s == None: return None
    replacements = {
        u'\u2018': "'",
        u'\u2019': "'"
    }
    for src, dest in replacements.iteritems():
        s = s.replace(src, dest)
    s=regcolorremove.sub('',s)
    return s

class TestCase(unittest.TestCase):    
    def run(self, result=None):
        if result.failures or result.errors:
            print "aborted"
        else:
            super(TestCase, self).run(result)
    def patternsToHave(self,s,patterns, reflags=0):
        for p in patterns:self.assertNotEqual(re.search(p,s,reflags),None,"Can not find pattern:"+p)

def getAKDB(dictCursor=True,user=None,password=None,host='localhost',port=3306,db_name='mod_akrr'):
    if dictCursor:
        db = MySQLdb.connect(host=host, port=port, user=cfg.akrr_db_user if user==None else user,
                             passwd=cfg.akrr_db_passwd if password==None else password, db=db_name,
                             cursorclass=MySQLdb.cursors.DictCursor)
    else:
        db = MySQLdb.connect(host=host, port=port, user=cfg.akrr_db_user if user==None else user,
                             passwd=cfg.akrr_db_passwd if password==None else password, db=db_name)
    cur = db.cursor()
    return db, cur


def getXDDB(dictCursor=True,user=None,password=None,host='localhost',port=3306,db_name='modw'):
    if dictCursor:
        db = MySQLdb.connect(host=host, port=port, user=cfg.xd_db_user if user==None else user,
                             passwd=cfg.xd_db_passwd if password==None else password, db=db_name,
                             cursorclass=MySQLdb.cursors.DictCursor)
    else:
        db = MySQLdb.connect(host=host, port=port, user=cfg.xd_db_user if user==None else user,
                             passwd=cfg.xd_db_passwd if password==None else password, db=db_name)
    cur = db.cursor()
    return db, cur


def clearInstallation(
                      stopAKRR=False,
                      clearBashRC=False,
                      clearCronTab=False,
                      clearCronTabMailTo=False,
                      dropAKRR_DB=False,
                      dropAKRR_DB_User=False,
                      dropXD_DB=False,
                      dropXD_DB_User=False,
                      drop_modw_DB=False,
                      emptyResourceTables=False,
                      rmBuildDir=False,
                      rmTestAKRRHome=False
                      ):
    if verbosity>=3:
        print "Cleaning installation"
    db_root,cur_root=getAKDB(user=cfg.akrr_db_admin_user,password=cfg.akrr_db_admin_passwd,db_name="mysql")
    
    if clearBashRC and os.path.exists(os.path.expanduser('~/.bashrc')):
        AKRRpresent=False
        for akrrHeader in ['#AKRR Enviromental Varables','#AKRR Server Environment Variables']:
            with open(os.path.expanduser('~/.bashrc'),'r') as f:
                bashcontent=f.readlines()
                for l in bashcontent:
                    if l.count(akrrHeader+' [Start]')>0: AKRRpresent=True
            if AKRRpresent:
                if verbosity>=3:
                    print "AKRR Section present in ~/.bashrc. Cleaning ~/.bashrc."
                with open(os.path.expanduser('~/.bashrc'),'w') as f:
                    inAKRR=False
                    for l in bashcontent:
                        if l.count(akrrHeader+' [Start]')>0:inAKRR=True
                        if not inAKRR:f.write(l)
                        if l.count(akrrHeader+' [End]')>0:inAKRR=False
    
    if clearCronTab:
        crontanContent=subprocess.check_output("crontab -l", shell=True)
        newCronTab=False
        crontanContent=crontanContent.splitlines(True)
        with open(os.path.expanduser('.crontmp'),'w') as f:
            for l in crontanContent:
                notAKRR=True
                if l.count('akrr')>0 and (l.count('checknrestart.sh')>0 or l.count('restart.sh')>0):
                    notAKRR=False
                if clearCronTabMailTo and l.count('MAILTO')>0:
                    notAKRR=False
                if notAKRR:f.write(l)
                else: newCronTab=True
        if newCronTab:
            if verbosity>=3:
                print "AKRR Section present in crontab. Cleaning crontab."
            output=subprocess.check_output("crontab .crontmp", shell=True)
            if verbosity>=3:
                print output
            os.remove(".crontmp")
            
        
                
        #clearCronTabMailTo
    
    #stop AKRR if needed
    if stopAKRR and os.path.exists(os.path.join(cfg.akrr_home,'src','akrrscheduler.py')):
        if verbosity>=3:
            print "Stopping AKRR if needed"
        try:
            output=subprocess.check_output("""
                {python_bin} {akrr_home}/src/akrrscheduler.py stop
                """.format(akrr_home=cfg.akrr_home,python_bin=python_bin), shell=True)
        except subprocess.CalledProcessError,e:
            output=e.output
            #if output.count("Can not stop AKRR server because none is running.")==0:
            #    raise e
        if verbosity>=3:
            print output
    
    def dropDB(dbName):
        cur_root.execute("SHOW DATABASES")
        dbsNames=[v['Database'] for v in cur_root.fetchall() if v['Database']==dbName]
        if len(dbsNames)>0:
            if verbosity>=3:
                print "DROP DATABASE "+dbName
            cur_root.execute("SHOW PROCESSLIST")
            proclist=[v['Id'] for v in cur_root.fetchall() if v['User']!=cfg.akrr_db_admin_user and v['db']==dbName]
            if len(proclist)>0:raise Exception("Other users access mod_akrr, can not drop table now!")
            cur_root.execute("DROP DATABASE "+dbName)
            db_root.commit()
    def dropUser(username):
        cur_root.execute("SELECT User,Host FROM mysql.user WHERE User like %s",username)
        if len(cur_root.fetchall())>0:
            cur_root.execute("SHOW PROCESSLIST")
            proclist=[v['Id'] for v in cur_root.fetchall() if v['User']==username]
            if len(proclist)>0: raise Exception("Users currently uses DB, can not drop it!")
            while 1:
                cur_root.execute("SELECT User,Host FROM mysql.user WHERE User like %s",username)
                user=cur_root.fetchall()
                if len(user)==0:break
                user=user[0]
                if verbosity>=3:
                    print "DROP user '%s'@'%s'"%(user['User'],user['Host'])
                cur_root.execute("DROP user %s@%s",(user['User'],user['Host']))
                db_root.commit()
    def emptyTable(tableName):
            if verbosity>=3:
                print "TRUNCATE TABLE "+tableName
            cur_root.execute("TRUNCATE TABLE "+tableName)
            db_root.commit()
    
    if dropAKRR_DB:
        dropDB('mod_akrr')
    if dropAKRR_DB_User:
        dropUser(cfg.akrr_db_user)
    if dropXD_DB:
        dropDB('mod_appkernel')
    if dropXD_DB_User:
        dropUser(cfg.xd_db_user)
    if drop_modw_DB:
        dropDB('modw')
    if emptyResourceTables:
        if not dropAKRR_DB:
            emptyTable('mod_akrr.resources')
        if not dropXD_DB:
            emptyTable('mod_appkernel.resource')
    if rmBuildDir:
        build_dir=os.path.abspath(os.path.join(akrr_arch_home, "build"))
        if os.path.exists(build_dir):
            if verbosity>=3: print "rm -rf "+build_dir
            shutil.rmtree(build_dir)
    if rmTestAKRRHome:
        if os.path.exists(cfg.akrr_home):
            if verbosity>=3: print "rm -rf "+cfg.akrr_home
            shutil.rmtree(cfg.akrr_home)
        
def set_modw():
    if verbosity>=3:
        print "set modw for XDMoD faking"
    db_root,cur_root=getAKDB(user=cfg.akrr_db_admin_user,password=cfg.akrr_db_admin_passwd,db_name='mysql')
    cur_root.execute("SHOW DATABASES")
    dbsNames=[v['Database'] for v in cur_root.fetchall() if v['Database']=='modw']
    if len(dbsNames)>0:
        if verbosity>=3: print "modw already exists"
        return
    
    cur_root.execute("""
        CREATE DATABASE modw;
        
        USE modw;
        
        CREATE TABLE `resourcefact`
        (
          `id` INT NOT NULL,
          `resourcetype_id` INT,
          `organization_id` INT,
          `name` VARCHAR(200),
          `code` VARCHAR(64) NOT NULL,
          `description` VARCHAR(1000),
          `start_date` DATETIME,
          `start_date_ts` INT DEFAULT 0 NOT NULL,
          `end_date` DATETIME,
          `end_date_ts` INT,
          PRIMARY KEY (`id`, `start_date_ts`)
        );
        CREATE INDEX `aggregation_index` ON `resourcefact` (`resourcetype_id`, `id`);
    """)
    while cur_root.nextset() is not None: pass
    cur_root.execute("""
        INSERT INTO modw.resourcefact (id, resourcetype_id, organization_id, name, code, description, start_date, start_date_ts, end_date, end_date_ts) VALUES (1000000, 1, 35, 'rush-taccstats.ccr.buffalo.edu', 'RUSH-TACCSTATS', null, '2010-01-01 00:00:00.0', 1262322000, null, null);
        INSERT INTO modw.resourcefact (id, resourcetype_id, organization_id, name, code, description, start_date, start_date_ts, end_date, end_date_ts) VALUES (1000001, 1, 35, 'rush-pcp.ccr.buffalo.edu', 'RUSH-PCP', null, '2010-01-01 00:00:00.0', 1262322000, null, null); 
    """)
    while cur_root.nextset() is not None: pass
    db_root.commit()