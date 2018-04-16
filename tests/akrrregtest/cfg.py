dry_run=False

yml=None

#
#By default performs setup in akrr config in default location i.e. $HOME/akrr.
#
#Options --in-src and --akrr-conf change that behaviour.
#
#In all cases akrr command line interface will be taken from $PATH

#install next to source code
in_source_install=True
#location of config
akrr_conf=None

akrr_conf_dir=None
akrr_log_dir=None

which_akrr="akrr"

#top level configuration largely same as AKRR
from akrr.akrrcfgdefault import *


xd_db_user = "akrruser"
xd_db_passwd = ""

akrr_db_user = xd_db_user
akrr_db_passwd = xd_db_passwd

ak_db_user = xd_db_user
ak_db_passwd = xd_db_passwd


#administrative database user under which the installation sql script should
sql_root_name="root"
sql_root_password="ccrub"


class InstallationCfg:
    """test installation configuration"""
    def __init__(self, filename):
        import inspect
        wrongfieldsdict = {}
        exec('wrongfieldsdict="wrongfieldsdict"', wrongfieldsdict)
        wrongfields = list(wrongfieldsdict.keys())
        
        tmp={}
        exec(compile(open(filename).read(), filename, 'exec'),tmp)
        for key,val in tmp.items():
            if inspect.ismodule(val):continue
            if wrongfields.count(key)>0:continue
            setattr(self, key, val)

def loadCfg(cfgFilename):
    "load configuration for reg test from file"
    import yaml
    
    global yml
    yml=yaml.load(open(cfgFilename).read())
    
    exec(yml['global'],globals())
    

def set_default_value_for_unset_vars():
    "post process settings"
    import os
    from .util import run_cmd_getoutput
    from . import log
    
    global which_akrr
    global akrr_conf
    global akrr_conf_dir
    global akrr_log_dir
    
    if which_akrr is None or which_akrr=="akrr":
        try:
            which_akrr=run_cmd_getoutput("which akrr").strip()
        except:
            which_akrr=None
    
    if which_akrr is not None:
        if akrr_conf is None:
            if os.path.dirname(which_akrr)=="/usr/bin":
                akrr_conf=os.path.expanduser("~/akrr/etc/akrr.conf")
                akrr_conf_dir=os.path.expanduser("~/akrr/etc")
                akrr_log_dir=os.path.expanduser("~/akrr/etc")
            else:
                akrr_conf_dir=os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(which_akrr)),"etc"))
                akrr_conf=os.path.join(akrr_conf_dir,'akrr.conf')
                akrr_log_dir=os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(which_akrr)),"log"))
        else:
            akrr_conf_dir=os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(akrr_conf)),"etc"))
            akrr_log_dir=os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(akrr_conf)),"log"))

    log.debug(
        "AKRR conf dir and log dir locations:\n"\
        "    akrr_conf: {}\n"\
        "    akrr_conf_dir: {}\n"\
        "    akrr_log_dir: {}\n"\
        "".format(akrr_conf,akrr_conf_dir,akrr_log_dir))
    

