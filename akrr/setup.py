import os
import sys

import datetime
import time
import inspect

import re
import types
import shutil
import getpass
import subprocess
import os
import random
import string

from . import log
from .util import which,log_input

#Since AKRR setup is the first script to execute
#Lets check python version and proper library presence.

#python version
if sys.version_info.major<3 or sys.version_info.minor<4:
    log.critical("Python should be of version 3.4+. This one is "+sys.version)
    exit(1)

#check presence of MySQLdb
try:
    import MySQLdb
    import MySQLdb.cursors
except Exception as e:
    log.critical("""python module MySQLdb is not available. Install it!
    For example by running on
        RedHat or CentOS from EPEL:
            #instale EPEL repo information
            sudo yum install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
            #install mysqlclient-python
            sudo yum install python34-mysql
            """)
    raise e

try:
    subprocess.check_output("which openssl", shell=True)
except Exception as e:
    log.error("""openssl program is not available. Install it!
    For example by running
    on CentOS
        sudo yum install openssl openssh-clients
    on Ubuntu:
        sudo apt-get install openssl""")
    raise e
#


#AKRR configuration can be in three places
# 1) AKRR_CONF if AKRR_CONF enviroment variable is defined
# 2) ~/akrr/etc/akrr.conf if initiated from RPM or global python install
# 3) <path to AKRR sources>/etc/akrr.conf for in source installation

in_src_install=False

akrr_mod_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
akrr_bin_dir = None
if os.path.isfile(os.path.join(os.path.dirname(akrr_mod_dir),'bin','akrr')):
    akrr_bin_dir=os.path.join(os.path.dirname(akrr_mod_dir),'bin')
    akrr_fullpath=os.path.join(akrr_bin_dir,'akrr')
    in_src_install=True
else:
    akrr_fullpath=which('akrr')
    akrr_bin_dir=os.path.dirname(akrr_fullpath)


#determin akrr_home
akrr_cfg=os.getenv("AKRR_CONF")
if akrr_cfg==None:
    if in_src_install:
        akrr_home=os.path.dirname(akrr_mod_dir)
        akrr_cfg=os.path.join(akrr_home,'etc','akrr.conf')
        log.info("In-source installation, AKRR configuration will be in "+akrr_cfg)
    else:
        akrr_home=os.path.expanduser("~/akrr")
        akrr_cfg=os.path.expanduser("~/akrr/etc/akrr.conf")
        log.info("AKRR configuration will be in "+akrr_cfg)
    
else:
    akrr_home=os.path.dirname(os.path.dirname(akrr_cfg))
    log.info("AKRR_CONF is set. AKRR configuration will be in "+akrr_cfg)


dry_run=False                

def _cursor_execute(cur, query, args=None):
    if not dry_run:
        cur.execute(query, args)
    else:
        if args is not None:
            if isinstance(args, dict):
                args = dict((key, cur._get_db().literal(item)) for key, item in args.items())
            else:
                args = tuple(map(cur._get_db().literal, args))
            query = query % args
            
        log.dry_run("SQL: "+query)

from .util.sql import get_con_to_db
from .util.sql import get_user_passwd_host_port
from .util.sql import db_exist
from .util.sql import cv
from .util.sql import db_check_priv
from .util.sql import get_db_client_host
 
def _os_makedirs(path):
    if not dry_run:
        log.debug("Creating directory: {}".format(path))
        os.makedirs(path)
    else:
        log.dry_run("os.makedirs({})".format(path))

def _read_username_password(
        prompt="Enter username:",
        username=None,
        password=None,
        default_username="user",
        password_on_default_user=None):
    log_input(prompt)
    
    if username is None:
        username=input('[{0}] '.format(default_username)) 
        if username=='':username=default_username
    else:
        log.info("User, "+username+", already entered.")
    
    if username==default_username and password is None and password_on_default_user is not None:
            password=password_on_default_user
    
    if password is None:
        while True:
            log_input("Please specify a password:")
            password=getpass.getpass()
            log_input("Please reenter the password:")
            password2=getpass.getpass()
            if password==password2:
                break
            log.error("Entered passwords do not match. Please try again.")
    else:
        log.info("Password already entered.")
    return username,password

def _read_sql_su_creds(host,port):
    while True:
        log_input(
            "Please provide an administrative database user (for {}:{}) "\
            "under which the installation sql script should "\
            "run (This user must have privileges to create "\
            "users and databases).".format(host,port))
        su_username=input("Username: ")
        log_input("Please provide the password for the the user which you previously entered:")
        su_password=getpass.getpass()
        
        try:
            get_con_to_db(su_username,su_password,host,port)
            return su_username,su_password
        except Exception as e:
            log.error("MySQL error: "+str(e))
            log.error("Entered credential is not valid. Please try again.")
            
            
class akrr_setup:
    default_akrr_user='akrruser'
    def __init__(
            self,
            akrr_db="localhost:3306",
            ak_db="localhost:3306",
            xd_db="localhost:3306",
            install_cron_scripts=True,stand_alone=False):
        
        self.akrr_db_user_name,\
        self.akrr_db_user_password,\
        self.akrr_db_host,\
        self.akrr_db_port=get_user_passwd_host_port(akrr_db)
        self.akrr_db_name="mod_akrr"
        
        #su will remain None if akrr user and db already exists and user has proper rights
        self.akrr_db_su_user_name=None
        self.akrr_db_su_user_password=None
        
        self.ak_db_user_name,\
        self.ak_db_user_password,\
        self.ak_db_host,\
        self.ak_db_port=get_user_passwd_host_port(ak_db)
        self.ak_db_name="mod_appkernel"
        
        self.ak_db_su_user_name=None
        self.ak_db_su_user_password=None
        
        self.xd_db_user_name,\
        self.xd_db_user_password,\
        self.xd_db_host,\
        self.xd_db_port=get_user_passwd_host_port(xd_db)
        self.xd_db_name="modw"
        
        self.xd_db_su_user_name=None
        self.xd_db_su_user_password=None
        
        self.cron_email=None
        self.stand_alone=stand_alone
        self.install_cron_scripts_flag=install_cron_scripts
        
    def check_previous_installation(self):
        if(os.path.exists(akrr_cfg)):
            msg="This is a fresh installation script. "+akrr_home+\
                     " contains previous AKRR installation. Either uninstall it or see documentation on updates.\n\n";
            msg+="To uninstall AKRR manually:\n\t1)remove "+akrr_cfg+"\n\t\trm "+akrr_cfg+"\n"
            msg+="\t2) (optionally for totally fresh start) drop mod_akrr and mod_appkernel database\n"
            msg+="\t\tDROP DATABASE mod_appkernel;\n"
            msg+="\t\tDROP DATABASE mod_akrr;\n\n"
            
            log.error(msg)
            exit(1)
    def check_utils(self):
        from distutils.spawn import find_executable
        
        errmsg=""
        if not find_executable('ssh'):
            errmsg+="Can not find ssh in PATH, please install it.\n"
        if not find_executable('openssl'):
            errmsg+="Can not find openssl in PATH, please install it.\n"
        
        if errmsg!="":
            log.error(errmsg)
            exit(1)
    def read_db_creds(self):
        ###
        #mod_akrr
        log.info("Before Installation continues we need to setup the database.")
        
        self.akrr_db_user_name,\
        self.akrr_db_user_password=_read_username_password(
            "Please specify a database user to access mod_akrr database (Used by AKRR)"\
            "(This user will be created if it does not already exist):",
            self.akrr_db_user_name,
            self.akrr_db_user_password,
            self.default_akrr_user)
        log.emptyline()
        
        #check if user, db already there
        user_exists=False
        db_exists=False
        user_priv_is_correct=False
        try:
            #connect with provided user, Exception will raise if user can not connect
            _,cur=get_con_to_db(self.akrr_db_user_name,self.akrr_db_user_password,self.akrr_db_host,self.akrr_db_port)
            client_host=get_db_client_host(cur)
            user_exists=True
            
            db_exists=db_exist(cur,self.akrr_db_name)
            if not db_exists:
                log.debug("Database {} doesn't exists on {}".format(self.akrr_db_name,self.akrr_db_host))
            user_priv_is_correct=db_check_priv(cur, self.akrr_db_name, "ALL", self.akrr_db_user_name, client_host)      
            if not user_priv_is_correct:
                log.debug(
                    "User {} doesn't have right privelege on {}, should be ALL".format(
                        self.akrr_db_user_name,self.akrr_db_name))      
        except Exception as e:
            user_exists=False
            log.debug("User ({}) does not exists on {}".format(self.akrr_db_user_name,self.akrr_db_host))
        
        #ask for su user on this machine if needed
        if not user_exists or not db_exists or not user_priv_is_correct:
            self.akrr_db_su_user_name,\
            self.akrr_db_su_user_password=_read_sql_su_creds(self.akrr_db_host,self.akrr_db_port)
        log.emptyline()
        ###
        #mod_appkernel
        same_host_as_ak=self.ak_db_host==self.akrr_db_host and self.ak_db_port==self.akrr_db_port
        
        self.ak_db_user_name,\
        self.ak_db_user_password=_read_username_password(
            "Please specify a database user to access mod_appkernel database "\
            "(Used by XDMoD appkernel module, AKRR creates and syncronize resource and appkernel description)"\
            "(This user will be created if it does not already exist):",
            self.ak_db_user_name,
            self.ak_db_user_password,
            self.akrr_db_user_name,
            self.akrr_db_user_password if same_host_as_ak else None
            )
        log.emptyline()
        
        #ask for su user on this machine
        user_exists=False
        db_exists=False
        user_priv_is_correct=False
        try:
            _,cur=get_con_to_db(self.ak_db_user_name,self.ak_db_user_password,self.ak_db_host,self.ak_db_port)
            client_host=get_db_client_host(cur)
            user_exists=True
            
            db_exists=db_exist(cur,self.ak_db_name)
            if not db_exists:
                log.debug("Database {} doesn't exists on {}".format(self.ak_db_name,self.ak_db_host))
            user_priv_is_correct=db_check_priv(cur, self.ak_db_name, "ALL", self.ak_db_user_name, client_host)
            if not user_priv_is_correct:
                log.debug(
                    "User {} doesn't have right privelege on {}, should be ALL".format(
                        self.ak_db_user_name,self.ak_db_name)) 
        except Exception as e:
            user_exists=False
            log.debug("User ({}) does not exists on {}".format(self.akrr_db_user_name,self.akrr_db_host))
        
        if not user_exists or not db_exists or not user_priv_is_correct:
            self.ak_db_su_user_name=self.akrr_db_su_user_name
            self.ak_db_su_user_password=self.akrr_db_su_user_password
            try:
                get_con_to_db(self.ak_db_su_user_name,self.ak_db_su_user_password,self.ak_db_host,self.ak_db_port)
            except:
                self.ak_db_su_user_name,\
                self.ak_db_su_user_password=_read_sql_su_creds(self.ak_db_host,self.ak_db_port)
        log.emptyline()
        
        ##
        #modw
        same_host_as_xd=self.xd_db_host==self.ak_db_host and self.xd_db_port==self.ak_db_port
        
        self.xd_db_user_name,\
        self.xd_db_user_password=_read_username_password(
            "Please specify the user that will be connecting to the XDMoD database (modw):",
            self.xd_db_user_name,
            self.xd_db_user_password,
            self.ak_db_user_name,
            self.ak_db_user_password if same_host_as_xd else None
            )
        log.emptyline()
        
        #ask for su user on this machine
        user_exists=False
        db_exists=False
        user_priv_is_correct=False
        try:
            
            _,cur=get_con_to_db(self.xd_db_user_name,self.xd_db_user_password,self.xd_db_host,self.xd_db_port)
            client_host=get_db_client_host(cur)
            user_exists=True
            
            db_exists=db_exist(cur,"modw")
            if not db_exists:
                log.debug("Database {} doesn't exists on {}".format(self.xd_db_name,self.xd_db_host))
            user_priv_is_correct=db_check_priv(cur, self.xd_db_name, "SELECT", self.xd_db_user_name, client_host)     
            if not user_priv_is_correct:
                log.debug(
                    "User {} doesn't have right privelege on {}, should be at least SELECT".format(
                        self.xd_db_user_name,self.xd_db_name))
        except Exception as e:
            user_exists=False
            log.debug("User ({}) does not exists on {}".format(self.xd_db_user_name,self.xd_db_host))
        
        if not user_exists or not db_exists or not user_priv_is_correct:
            self.xd_db_su_user_name=self.ak_db_su_user_name
            self.xd_db_su_user_password=self.ak_db_su_user_password
            try:
                get_con_to_db(self.xd_db_su_user_name,self.xd_db_su_user_password,self.xd_db_host,self.xd_db_port)
            except:
                self.ak_db_su_user_name,\
                self.ak_db_su_user_password=_read_sql_su_creds(self.xd_db_host,self.xd_db_port)
        log.emptyline()
        
        
    def get_akrr_db(self,su=False,dbname=""):
        
        
        return get_con_to_db(
            self.akrr_db_user_name if not su else self.akrr_db_su_user_name,
            self.akrr_db_user_password if not su else self.akrr_db_su_user_password,
            self.akrr_db_host,self.akrr_db_port,
            self.akrr_db_name if dbname =="" else dbname)
        
    def get_ak_db(self,su=False,dbname=""):
        return get_con_to_db(
            self.ak_db_user_name if not su else self.ak_db_su_user_name,
            self.ak_db_user_password if not su else self.ak_db_su_user_password,
            self.ak_db_host,self.ak_db_port,
            self.ak_db_name if dbname =="" else dbname)
        
    def get_xd_db(self,su=False,dbname=""):
        return get_con_to_db(
            self.xd_db_user_name if not su else self.xd_db_su_user_name,
            self.xd_db_user_password if not su else self.xd_db_su_user_password,
            self.xd_db_host,self.xd_db_port,
            self.xd_db_name if dbname =="" else dbname)
        
    def get_random_password(self):
        length = 16
        chars = string.ascii_letters + string.digits
        # + '@#$%^&*'
        password=""
        while len(password)<length:
            i=os.urandom(1)
            if ord(i)>(255/len(chars))*len(chars):
                continue
            password+=chars[ord(i)%len(chars)]
        return password

    def init_dir(self):
        try:
            log.info("Creating directories structure.")
            if not os.path.isdir(akrr_home):
                _os_makedirs(akrr_home)
            if not os.path.isdir(os.path.join(akrr_home,'etc')):
                _os_makedirs(os.path.join(akrr_home,'etc'))
            if not os.path.isdir(os.path.join(akrr_home,'etc','resources')):
                _os_makedirs(os.path.join(akrr_home,'etc','resources'))
            if not os.path.isdir(os.path.join(akrr_home,'etc','resources')):
                _os_makedirs(os.path.join(akrr_home,'etc','resources'))
            if not os.path.isdir(os.path.join(akrr_home,'log')):
                _os_makedirs(os.path.join(akrr_home,'log'))
            if not os.path.isdir(os.path.join(akrr_home,'log','data')):
                _os_makedirs(os.path.join(akrr_home,'log','data'))
            if not os.path.isdir(os.path.join(akrr_home,'log','comptasks')):
                _os_makedirs(os.path.join(akrr_home,'log','comptasks'))
            if not os.path.isdir(os.path.join(akrr_home,'log','akrrd')):
                _os_makedirs(os.path.join(akrr_home,'log','akrrd'))
        except Exception as e:
            log.error("Can not create directories: "+str(e))
            exit(1)
    def init_mysql_dbs(self):
        try:
            
            def _create_db_user_gran_priv_if_needed(con_fun,user,password,db,priv):
                log.info("Creating %s and user to access it if needed"%(db,))
                su_con,su_cur=con_fun(True,None)
                client_host=get_db_client_host(su_cur)
                
                _cursor_execute(su_cur,"CREATE DATABASE IF NOT EXISTS %s"%(cv(db),))
                _cursor_execute(su_cur,"CREATE USER IF NOT EXISTS %s@%s IDENTIFIED BY %s",(user,client_host,password))
                _cursor_execute(su_cur,"GRANT "+cv(priv)+" ON "+cv(db)+".* TO %s@%s",(user, client_host))
                
                su_con.commit()
            
            #During self.read_db_creds db and user was checked and
            #if they do not  exist or not good enough super user credentials 
            #was asked so if they not None that means that 
            #either user or db or user priv needed to be set
            if self.akrr_db_su_user_name is not None:
                _create_db_user_gran_priv_if_needed(
                    self.get_akrr_db, self.akrr_db_user_name, self.akrr_db_user_password, self.akrr_db_name,"ALL")
            if self.ak_db_su_user_name is not None:
                _create_db_user_gran_priv_if_needed(
                    self.get_ak_db, self.ak_db_user_name, self.ak_db_user_password, self.ak_db_name,"ALL")
            if self.xd_db_su_user_name is not None:
                _create_db_user_gran_priv_if_needed(
                    self.get_xd_db, self.xd_db_user_name, self.xd_db_user_password, self.xd_db_name,"SELECT")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            log.error("Can not execute the sql setup script: "+str(e))
            exit(1)
    def generate_self_signed_certificate(self):
        log.info("Generating self-signed certificate for REST-API")
            
        cmd="""
            openssl req \
                -new \
                -newkey rsa:4096 \
                -days 365 \
                -nodes \
                -x509 \
                -subj "/C=US/ST=Denial/L=Springfield/O=Dis/CN=localhost" \
                -keyout {akrr_cfg_dir}/server.key \
                -out {akrr_cfg_dir}/server.cert
            cp {akrr_cfg_dir}/server.key {akrr_cfg_dir}/server.pem
            cat {akrr_cfg_dir}/server.cert >> {akrr_cfg_dir}/server.pem
            """.format(akrr_cfg_dir=os.path.join(akrr_home,'etc'))
        if not dry_run:
            output=subprocess.check_output(cmd, shell=True)
            log.info(output.decode("utf-8"))
            log.info("New self-signed certificate have been generated")
        else:
            log.dry_run("run command: "+cmd)

    def generate_settings_file(self):
        log.info("Generating Settings File...")
        with open(os.path.join(akrr_mod_dir,'templates','akrr.conf'),'r') as f:
            akrr_inp_template=f.read()
        restapi_rw_password=self.get_random_password()
        restapi_ro_password=self.get_random_password()
        var={
            'akrr_db_user_name':self.akrr_db_user_name,
            'akrr_db_user_password':self.akrr_db_user_password,
            'xd_db_user_name':self.xd_db_user_name,
            'xd_db_user_password':self.xd_db_user_password,
            'restapi_rw_password':restapi_rw_password,
            'restapi_ro_password':restapi_ro_password
        }
        akrr_inp=akrr_inp_template.format(**var)
        if not dry_run:
            with open(akrr_cfg,'w') as f:
                akrr_inp_template=f.write(akrr_inp)
            log.info("Settings written to: {0}".format(akrr_cfg))
        else:
            log.dry_run("New config should be written to: {}".format(akrr_cfg))
            log.debug2(akrr_inp)
        
    def set_permission_on_files(self):
        log.info("Removing access for group members and everybody for all files as it might contain sensitive information.")
        if not dry_run:
            subprocess.check_output("""
                chmod -R g-rwx {akrr_home}
                chmod -R o-rwx {akrr_home}
                """.format(akrr_home=akrr_home), shell=True)
    def db_check(self):
        log.info("Checking acces to DBs.")
        if dry_run:return
        
        from . import akrrdb_check
        if not akrrdb_check.akrrdb_check(mod_appkernel=not self.stand_alone,modw=not self.stand_alone):
            exit(1)
    def generate_tables(self):
        log.info("Creating tables and populating them with initial values.")
        
        from .akrrgenerate_tables import create_and_populate_mod_akrr_tables,create_and_populate_mod_appkernel_tables
        
        create_and_populate_mod_akrr_tables(dry_run)
        create_and_populate_mod_appkernel_tables(dry_run)
        
    def start_daemon(self):
        """Start the daemon"""
        log.info("Starting AKRR daemon")
        if dry_run:return
        
        akrr_cli=os.path.join(akrr_bin_dir,'akrr')
        status=subprocess.call(akrr_cli+" daemon start", shell=True)
        if status!=0:exit(status)
    def check_daemon(self):
        """Check that the daemon is running"""
        log.info("Checking that AKRR daemon is running")
        if dry_run:return
        
        akrr_cli=os.path.join(akrr_bin_dir,'akrr')
        status=subprocess.call(akrr_cli+" daemon check", shell=True)
        if status!=0:exit(status)
    
    def ask_cron_email(self):
        """ask_cron_email."""
        try:
            crontanContent=subprocess.check_output("crontab -l", shell=True)
            crontanContent=crontanContent.decode("utf-8").splitlines(True)
        except:
            #probably no crontab was setup yet
            crontanContent=[]
        for l in crontanContent:
            if len(l.strip())>1 and l.strip()[0]!="#":
                m=re.match(r'^MAILTO\s*=\s*(.*)',l.strip())
                if m:
                    self.cron_email=m.group(1)
                    self.cron_email=self.cron_email.replace('"','')
        if self.cron_email==None:
            log_input("Please enter the e-mail where cron will send messages (leave empty to opt out):")
            self.cron_email=input()
        else:
            log_input("Please enter the e-mail where cron will send messages:")
            cron_email=input('[{0}] '.format(self.cron_email)) 
            if cron_email!="":self.cron_email=cron_email
        if self.cron_email=="":self.cron_email=None
    def install_cron_scripts(self):
        """Install cron scripts."""
        log.info("Installing cron entries")
        if dry_run:return
        
        if self.cron_email:mail="MAILTO = "+self.cron_email
        else: mail=None
        restart="50 23 * * * "+akrr_bin_dir+"/akrr daemon -cron restart"
        checknrestart="33 * * * * "+akrr_bin_dir+"/akrr daemon -cron checknrestart"
        
        try:
            crontanContent=subprocess.check_output("crontab -l", shell=True)
            crontanContent=crontanContent.decode("utf-8").splitlines(True)
        except:
            log.info("Crontab does not have user's crontab yet")
            crontanContent=[]
        
        mailUpdated=False
        mailThere=False
        restartThere=False
        checknrestartThere=False
        
        for i in range(len(crontanContent)):
            l=crontanContent[i]
            if len(l.strip())>1 and l.strip()[0]!="#":
                m=re.match(r'^MAILTO\s*=\s*(.*)',l.strip())
                if m:
                    cron_email=m.group(1)
                    cron_email=self.cron_email.replace('"','')
                    mailThere=True
                    if self.cron_email!=cron_email:
                        if mail:
                            crontanContent[i]=mail
                        else:
                            crontanContent[i]="#"+crontanContent[i]
                        mailUpdated=True
                if l.count("akrr") and l.count("daemon") and l.count("restart")>0:
                    restartThere=True
                if l.count("akrr") and l.count("daemon") and l.count("checknrestart")>0:
                    checknrestartThere=True
        if mailUpdated:
            log.info("Cron's MAILTO was updated")
        if ((self.cron_email!=None and mailThere) or (self.cron_email==None and mailThere==False)) and restartThere and checknrestartThere and mailUpdated==False:
            log.warning("All AKRR crond entries found. No modifications necessary.")
            return
        if self.cron_email!=None and mailThere==False:
            crontanContent.insert(0, mail+"\n")
        if restartThere==False:
            crontanContent.append(restart+"\n")
        if checknrestartThere==False:
            crontanContent.append(checknrestart+"\n")
        
        with open(os.path.expanduser('.crontmp'),'w') as f:
            for l in crontanContent:
                f.write(l)
        subprocess.call("crontab .crontmp", shell=True)
        os.remove(".crontmp")
        log.info("Cron Scripts Processed!")
    def update_bashrc(self):
        """Add AKRR enviroment variables to .bashrc"""
        log.info("Updating .bashrc")
        
        bashcontentNew=[]
        akrrHeader='#AKRR Server Environment Variables'
        if os.path.exists(os.path.expanduser("~/.bashrc")):
            log.info("Updating AKRR record in $HOME/.bashrc, backing to $HOME/.bashrc_akrrbak")
            if not dry_run:
                subprocess.call("cp ~/.bashrc ~/.bashrcakrr", shell=True)
            with open(os.path.expanduser('~/.bashrc'),'r') as f:
                bashcontent=f.readlines()
                inAKRR=False
                for l in bashcontent:
                    if l.count(akrrHeader+' [Start]')>0:inAKRR=True
                    if not inAKRR:bashcontentNew.append(l)
                    if l.count(akrrHeader+' [End]')>0:inAKRR=False
        bashcontentNew.append("\n"+akrrHeader+" [Start]\n")
        bashcontentNew.append("export PATH=\"{0}/bin:$PATH\"\n".format(akrr_home))
        bashcontentNew.append(akrrHeader+" [End]\n\n")
        if not dry_run:
            with open(os.path.expanduser('~/.bashrc'),'w') as f:
                for l in bashcontentNew:
                    f.write(l)
            log.info("Appended AKRR records to $HOME/.bashrc")
        else:
            log.debug("New .bashrc should be like"+"\n".join(bashcontentNew))

    def run(self):
        #check 
        self.check_utils()
        self.check_previous_installation()
        
        #ask info
        self.read_db_creds()
        
        if self.install_cron_scripts_flag:
            self.ask_cron_email()
        
        #if it is dry_run
        #all question are asked, this is dry run, so nothing else to do")
        
        self.init_mysql_dbs()
        self.init_dir()
        self.generate_self_signed_certificate()
        self.generate_settings_file()
        self.set_permission_on_files()
        self.db_check()
        
        self.generate_tables()
        
        self.start_daemon()
        self.check_daemon()
        if self.install_cron_scripts_flag:
            self.install_cron_scripts()
        
        if in_src_install:
            self.update_bashrc()
            
        log.info("AKRR is set up and is running.")
    

def cli_add_command(parent_parser):
    """Initial AKRR Setup"""
    parser = parent_parser.add_parser('setup',
        description='Initial AKRR Setup')
    parser.add_argument("--dry-run", action="store_true", help="Dry run, print commands if possble")
    
    parser.add_argument(
        "--akrr-db", 
        default="localhost:3306", 
        help="mod_akrr database location in [user[:password]@]host[:port] format, missing values willbe asked. Default: localhost:3306")
    parser.add_argument(
        "--ak-db", 
        default="localhost:3306", 
        help="mod_appkernel database location. Usually same host as XDMoD's databases host. Default: localhost:3306")
    parser.add_argument(
        "--xd-db", 
        default="localhost:3306", 
        help="XDMoD modw database location. It is XDMoD's databases host. Default: localhost:3306")
    
    def setup_handler(args):
        """call routine for initial AKRR setup"""
        global dry_run
        dry_run=args.dry_run
        return akrr_setup(
            akrr_db=args.akrr_db,
            ak_db=args.akrr_db,
            xd_db=args.akrr_db
            ).run()
        
    parser.set_defaults(func=setup_handler)
