dry_run = False
verbose = False
yml = None

#
# By default performs setup in akrr config in default location i.e. $HOME/akrr.
#
# Options --in-src and --akrr-conf change that behaviour.
#
# In all cases akrr command line interface will be taken from $PATH

# install next to source code
in_source_install = False
rpm_install = False
dev_install = False
# location of config
default_akrr_home_dir = None
akrr_home_dir = None
akrr_conf = None
akrr_conf_dir = None
akrr_log_dir = None

which_akrr = "akrr"

# top level configuration largely same as AKRR
from akrr.cfg_default import *

xd_db_user = "akrruser"
xd_db_passwd = ""

akrr_db_user = xd_db_user
akrr_db_passwd = xd_db_passwd

ak_db_user = xd_db_user
ak_db_passwd = xd_db_passwd

# administrative database user under which the installation sql script should
sql_root_name = "root"
sql_root_password = ""


def load_cfg(config_filename):
    """load configuration for reg test from file"""
    from akrr.util.yaml import yaml_load

    global yml
    yml = yaml_load(open(config_filename).read())

    exec(yml['global'], globals())


def set_default_value_for_unset_vars():
    """post process settings"""
    import os
    from .util import run_cmd_getoutput
    from akrr.util import log

    global which_akrr
    global akrr_conf
    global akrr_conf_dir
    global akrr_home_dir
    global default_akrr_home_dir
    global akrr_log_dir
    global in_source_install
    global rpm_install
    global dev_install

    if which_akrr is None or which_akrr == "akrr":
        try:
            which_akrr = run_cmd_getoutput("which akrr").strip()
        except Exception as e:
            log.critical("Can not find akrr executable")
            raise e
    if os.path.dirname(which_akrr) == "/usr/bin":
        rpm_install = True
    if os.path.dirname(which_akrr) == "/usr/local/bin":
        dev_install = True
    else:
        in_source_install = True

    # set default_akrr_home_dir
    if in_source_install:
        default_akrr_home_dir = os.path.abspath(os.path.dirname(os.path.dirname(which_akrr)))
    elif rpm_install or dev_install:
        default_akrr_home_dir = os.path.expanduser("~/akrr")

    if akrr_home_dir is None:
        akrr_home_dir = default_akrr_home_dir
    else:
        akrr_home_dir = os.path.expanduser(akrr_home_dir)

    akrr_conf_dir = os.path.join(akrr_home_dir, "etc")
    akrr_conf = os.path.join(akrr_home_dir, "etc", 'akrr.conf')
    akrr_log_dir = os.path.join(akrr_home_dir, "log")

    log.debug(
        "AKRR conf dir and log dir locations:\n"
        "    akrr_home: {}\n"
        "    akrr_conf: {}\n"
        "    akrr_conf_dir: {}\n"
        "    akrr_log_dir: {}\n"
        "".format(akrr_home_dir, akrr_conf, akrr_conf_dir, akrr_log_dir))
