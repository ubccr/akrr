import os
import sys
import subprocess
import shutil

from . import log

from . import cfg

from .cfg import dry_run

from .db import get_akrr_db,get_ak_db,get_xd_db


def _get_akrr_pids():
    akrr_daemon_pids=[]
    
    try:
        output=subprocess.check_output(
            """ ps --no-headers -U $USER -o "uname,pid,ppid,cmd"|grep -P 'akrr daemon start'|grep -v "grep" """,
            shell=True)
        
        for l in output.splitlines():
            akrr_daemon_pids.append(l.decode("utf-8").split()[1])
    except subprocess.CalledProcessError:
        pass
    if len(akrr_daemon_pids)>0:
        return akrr_daemon_pids
    else:
        return None
    
def _stop_akrr():
    akrr_daemon_pids=_get_akrr_pids()
    if akrr_daemon_pids is None:
        log.info("AKRR daemon is not running.")
        return
    
    log.info("AKRR daemon is running, trying to stop it.")
    
    try:
        if os.path.exists(os.path.join(cfg.which_akrr)):
            cmd="{} {} daemon stop".format(sys.executable,cfg.which_akrr)
            if not dry_run:
                subprocess.check_output(
                    cmd, shell=True,timeout=60)
            else:
                log.dry_run("should execute: "+cmd)
    except subprocess.CalledProcessError:
        pass
    
    akrr_daemon_pids=_get_akrr_pids()
    if akrr_daemon_pids is None:
        return
    
    try:
        for pid in akrr_daemon_pids:
            cmd="kill -9 {}".format(pid)
            if not dry_run:
                subprocess.check_output(
                    cmd, shell=True,timeout=60)
            else:
                log.dry_run("should execute: "+cmd)
    except subprocess.CalledProcessError:
        pass
    
    akrr_daemon_pids=_get_akrr_pids()
    if akrr_daemon_pids is None:
        return
    
    if dry_run:
        log.dry_run("at this point AKRR daemon should be stopped"+cmd)
        return
    
    raise Exception("was not able to stop AKRR daemon")

def _remove_user():
    "remove user from dbs"
    dbs=get_akrr_db(su=True),get_ak_db(su=True),get_xd_db(su=True)
    users = cfg.akrr_db_user,cfg.ak_db_user,cfg.xd_db_user
    
    for user,(db,cur) in zip(users,dbs):
        #see if user exists
        cur.execute("SELECT * FROM mysql.user WHERE user = %s",(user,))
        
        records=cur.fetchall()
        
        for rec in records:
            log.info("Removing %s@%s from %s ",rec["User"],rec["Host"],str(db))
            msg="DRY RUN:\n" if dry_run else ""
            msg=msg+"SQL(%s): "%(str(db),)
            msg=msg+"DROP USER IF EXISTS %s@%s"%(rec["User"],rec["Host"])
            
            if dry_run:log.info(msg)
            else:log.dry_run(msg)
                        
            if dry_run: continue
            
            #remove user
            cur.execute("DROP USER IF EXISTS %s@%s",(rec["User"],rec["Host"]))
            db.commit()
        if len(records)==0:
            log.info("There is no user with name %s on %s ",user,str(db))

        
def _remove_db(db,cur,dbname):
    "remove dbname database from db,cur connection"
    cur.execute("SHOW databases")
    databases=cur.fetchall()
    if dbname in {v["Database"] for v in databases}:
        log.info("Removing %s database from %s ",dbname,str(db))
        msg="SQL(%s): "%(str(db),)
        msg=msg+"DROP DATABASE IF EXISTS %s"%(dbname,)
        
        if dry_run:log.info("DRY RUN:\n"+msg)
        else:log.dry_run(msg)
                    
        if dry_run: return
        
        #remove user
        cur.execute("DROP DATABASE IF EXISTS %s"%(dbname,))
        db.commit()
    else:
        log.info("Database %s is not present on %s ",dbname,str(db))


def _remove_akrr_db():
    "remove mod_akrr"
    _remove_db(*get_akrr_db(su=True),dbname=cfg.akrr_db_name)

def _remove_ak_db():
    "remove mod_appkernel"
    _remove_db(*get_ak_db(su=True),dbname=cfg.ak_db_name)
    
def _remove_dir(path):
    if os.path.exists(path):
        log.info("Deleting "+path)
        if not dry_run:
            shutil.rmtree(path) 
    else:
        log.info("Directory "+path+" doesn't exists.")
    
def _remove_conf_dir():
    "remove mod_appkernel"
    if cfg.akrr_conf_dir is None:
        log.warn("akrr_conf_dir is None")
        return
    _remove_dir(cfg.akrr_conf_dir)

def _remove_log_dir():
    "remove mod_appkernel"
    if cfg.akrr_log_dir is None:
        log.warn("akrr_log_dir is None")
        return
    _remove_dir(cfg.akrr_log_dir)

def _remove_from_bashrc():
    "remove from bashrc"
    bashrc=os.path.expanduser('~/.bashrc')
    if not os.path.exists(bashrc):
        log.info("~/.bashrc file doesn't exists.")
        return
    
    any_akrr_section=False
    
    for akrrHeader in ['#AKRR Enviromental Varables','#AKRR Server Environment Variables']:
        AKRRpresent=False
        with open(os.path.expanduser('~/.bashrc'),'r') as f:
            bashcontent=f.readlines()
            for l in bashcontent:
                if l.count(akrrHeader+' [Start]')>0: AKRRpresent=True
        if AKRRpresent:
            any_akrr_section=True
            log.info("AKRR Section present in ~/.bashrc. Cleaning ~/.bashrc.")
            if not dry_run:
                with open(os.path.expanduser('~/.bashrc'),'w') as f:
                    inAKRR=False
                    for l in bashcontent:
                        if l.count(akrrHeader+' [Start]')>0:inAKRR=True
                        if not inAKRR:f.write(l)
                        if l.count(akrrHeader+' [End]')>0:inAKRR=False
    if not any_akrr_section:
        log.info("AKRR Section doesn't present in ~/.bashrc.")
    
def _remove_from_crontab(remove_mailto=False):
    "remove from cron"
    
    try:
        
        crontanContent=subprocess.check_output("crontab -l", shell=True)
    except:
        log.error("Can not run crontab -l")
        return
    
    newCronTab=False
    crontanContent=crontanContent.decode("utf-8").splitlines(True)
    
    with open(os.path.expanduser('.crontmp'),'w') as f:
        for l in crontanContent:
            notAKRR=True
            if l.count('akrr')>0 and (l.count('checknrestart.sh')>0 or l.count('restart.sh')>0):
                notAKRR=False
            if remove_mailto and l.count('MAILTO')>0:
                notAKRR=False
            if notAKRR:f.write(l)
            else: newCronTab=True
    if newCronTab:
        log.info("AKRR Section present in crontab. Cleaning crontab.")
        try:
            if not dry_run:
                output=subprocess.check_output("crontab .crontmp", shell=True).decode("utf-8")
                log.debug(output)
            else:
                log.info("DRY RUN: should run `crontab .crontmp`. .crontmp:"+open(".crontmp","rt").read())
        except:
            log.error("Can not run crontab .crontmp")
        os.remove(".crontmp")
    else:
        log.info("There was no AKRR records detected in crontab list")

def remove(
        db_akrr=False, db_appkernel=False, db_user=False, 
        conf_dir=False,log_dir=False,
        bashrc=False,
        crontab=False,crontab_remove_mailto=False,
        **kwargs):
    log.debug(
        "Removal options for removal:\n"\
        "    db_akrr: {}\n"\
        "    db_appkernel: {}\n"\
        "    db_user: {}\n"\
        "    conf_dir: {}\n"\
        "    log_dir: {}\n"\
        "    bashrc: {}\n"\
        "    crontab: {} , crontab_remove_mailto: {}\n"\
        "".format(
            db_akrr,db_appkernel,db_user,conf_dir,log_dir,bashrc,crontab,crontab_remove_mailto)
    )
    _stop_akrr()
    
    if db_user:_remove_user()
    if db_akrr:_remove_akrr_db()
    if db_akrr:_remove_ak_db()
    if conf_dir:_remove_conf_dir()
    if log_dir:_remove_log_dir()
    if bashrc:_remove_from_bashrc()
    if crontab:_remove_from_crontab(crontab_remove_mailto)

