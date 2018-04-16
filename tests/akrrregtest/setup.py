"""
Routings for setup tests.

Several setup scenario should be tested

* Stand-alone, AKRR running from source code somewhere in user directory
    * It uses localhost sql server for all databases and can get super user 
      for MySQL server.
        * Create user if needed, gran priveleges and create db.
          If db exists it should be empty
    * It uses localhost sql server for all databases and user and db already
      created there is no access to su

* Same as previous but rpm-installed 
  

"""

from . import log

from .util import get_bash

from .cfg import dry_run
from . import cfg

#Setup empty string means default

#empty string means that when asked user accept default value
#None means that there is no expectation that this value will be asked


akrr_db_user_name=""
akrr_db_user_password=""
akrr_db_host=None
akrr_db_port=None
akrr_db_name=None

akrr_db_su_user_name="root"
akrr_db_su_user_password=""
        
ak_db_user_name=""
ak_db_user_password=None
ak_db_host=None
ak_db_port=None
ak_db_name=None
        
ak_db_su_user_name=None
ak_db_su_user_password=None
        
xd_db_user_name=""
xd_db_user_password=None
xd_db_host=None
xd_db_port=None
xd_db_name=None
        
xd_db_su_user_name=None
xd_db_su_user_password=None

cron_email=""




testMissmatchingPassword=False
testInvalidAdministrativeDatabaseUser=False

dry_run_flag=""

fasttimeout=3

def _send_user_password(bash,expect, user, password, 
                        testMissmatchingPassword=True):
    
    bash.expectSendline(expect,user,timeout=fasttimeout)
    
    bash.justExpect("\n")
    
    if password is None:
        return
    
    if testMissmatchingPassword:
        log.info("Entering not matching password")
        bash.expectSendline(
            r'.*INPUT.* Please specify a password.*\n',
            'password',timeout=fasttimeout)
        bash.expectSendline(
            r'.*INPUT.* Please reenter the password.*\n',
            'passwordpassword',timeout=fasttimeout)
        bash.justExpect(
            r'.*ERROR.* Entered passwords do not match. Please try again.',timeout=fasttimeout)
        log.info("\nEntering matching password")
    bash.expectSendline(
        r'.*INPUT.* Please specify a password.*\n',
        password,timeout=fasttimeout)
    bash.expectSendline(
        r'.*INPUT.* Please reenter the password.*\n',
        password,timeout=fasttimeout)

def _send_su_user_password(bash, user, password):
    if user is None:
        return
    #set AKRR database root user
    if testInvalidAdministrativeDatabaseUser:
        log.info("Entering invalid administrative database user")
        bash.expectSendline(
            r'.*INPUT.* Please provide an administrative database user.*\nUsername:',
            "invalid",timeout=fasttimeout)
        bash.expectSendline(
            r'.*INPUT.* Please provide the password.*\n',
            "invalid",timeout=fasttimeout)
        bash.justExpect(
            r'.*ERROR.* Entered credential is not valid. Please try again.',timeout=fasttimeout)
        log.info("\nEntering valid administrative database user")
        
    bash.expectSendline(
        r'.*INPUT.* Please provide an administrative database user.*\nUsername:',
        user,timeout=fasttimeout)
    bash.expectSendline(
        r'.*INPUT.* Please provide the password.*\n',
        password,timeout=fasttimeout)
    
def _run_setup():    
    """Run Preparatory Script"""
    #start bash shell
    bash = get_bash()
    bash.output=""
    bash.timeoutMessage='Unexpected behavior of prep.sh (premature EOF or TIMEOUT)'
    
    bash.runcmd('which python3',printOutput=True)
    bash.runcmd('which '+cfg.which_akrr,printOutput=True)
    
    #start akrr setup
    bash.startcmd(cfg.which_akrr+" setup "+dry_run_flag)
    
    #set database user for AKRR
    _send_user_password(
        bash,
        r'Please specify a database user to access mod_akrr database.*\n\[\S+\]',
        akrr_db_user_name,akrr_db_user_password
        )
    _send_su_user_password(bash,akrr_db_su_user_name,akrr_db_su_user_password)
    
    #AK database:
    _send_user_password(
        bash,
        r'Please specify a database user to access mod_appkernel database.*\n\[\S+\]',
        ak_db_user_name,ak_db_user_password
        )
    _send_su_user_password(bash,ak_db_su_user_name,ak_db_su_user_password)
        
    #XD database:
    _send_user_password(
        bash,
        r'Please specify the user that will be connecting to the XDMoD database.*\n\[\S+\]',
        ak_db_user_name,ak_db_user_password
        )
    _send_su_user_password(bash,ak_db_su_user_name,ak_db_su_user_password)
    
    
    bash.expectSendline(r'.*INPUT.* Please enter the e-mail where cron will send messages.*\n',
                        "" if cron_email is None else cron_email)
    #wait for prompt
    bash.justExpect(bash.prompt,timeout=60)
    
    log.info(bash.output)
    
    if bash.output.count("AKRR is set up and is running.")==0:
        
        log.critical("AKRR was not set up")
        exit(1)
    else:
        log.info("AKRR is set up and is running.")
    return


def setup():
    log.info("AKRR Setup")
    
    if cfg.which_akrr is None:
        log.critical("Can not find akrr. It should be in PATH or set in conf.")
        exit(1)
    
    #set config
    globals().update(cfg.yml["setup"])
    
    if dry_run:
        global dry_run_flag
        dry_run_flag=" --dry-run "
    _run_setup()
    


