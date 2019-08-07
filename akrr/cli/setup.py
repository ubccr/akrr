"""This module contains routines for initial AKRR configuration"""
import os
import sys
import inspect
import re
import getpass
import subprocess
import string

# Since AKRR setup is the first script to execute
# Lets check python version and proper library presence.
# check presence of MySQLdb
try:
    import MySQLdb
    import MySQLdb.cursors
except ImportError:
    print("""python module MySQLdb is not available. Install it!
        For example by running on
            RedHat or CentOS from EPEL:
                #instale EPEL repo information
                sudo yum install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
                #install mysqlclient-python
                sudo yum install python36-mysql
                """)
    exit(1)
except Exception as _e:
    print("""Can not import module MySQLdb!""")
    raise _e

from akrr.util import log
from akrr.util.sql import get_con_to_db
from akrr.util.sql import get_user_password_host_port_db
from akrr.util.sql import set_user_password_host_port_db
from akrr.util.sql import db_exist
from akrr.util.sql import cv
from akrr.util.sql import db_check_priv
from akrr.util.sql import get_db_client_host
from akrr.util.sql import create_user_if_not_exists

# Python version
if sys.version_info.major < 3 or sys.version_info.minor < 4:
    log.critical("Python should be of version 3.4+. This one is " + sys.version)
    exit(1)

# check openssl presence
try:
    subprocess.check_output("which openssl", shell=True)
except Exception as _e:
    log.error("""openssl program is not available. Install it!
    For example by running
    on CentOS
        sudo yum install openssl openssh-clients
    on Ubuntu:
        sudo apt-get install openssl""")
    raise _e

# AKRR configuration can be in three places
# 1) AKRR_CONF if AKRR_CONF environment variable is defined
# 2) ~/akrr/etc/akrr.conf if initiated from RPM or global python install
# 3) <path to AKRR sources>/etc/akrr.conf for in source installation

in_src_install = False

akrr_mod_dir = os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
akrr_bin_dir = None
if os.path.isfile(os.path.join(os.path.dirname(akrr_mod_dir), 'bin', 'akrr')):
    akrr_bin_dir = os.path.join(os.path.dirname(akrr_mod_dir), 'bin')
    akrr_fullpath = os.path.join(akrr_bin_dir, 'akrr')
    in_src_install = True
else:
    akrr_fullpath = inspect.stack()[-1][1]
    akrr_bin_dir = os.path.dirname(akrr_fullpath)

# determine akrr_home
akrr_cfg = os.getenv("AKRR_CONF")
if akrr_cfg is None:
    if in_src_install:
        akrr_home = os.path.dirname(akrr_mod_dir)
        akrr_cfg = os.path.join(akrr_home, 'etc', 'akrr.conf')
        log.info("In-source installation, AKRR configuration will be in " + akrr_cfg)
    else:
        akrr_home = os.path.expanduser("~/akrr")
        akrr_cfg = os.path.expanduser("~/akrr/etc/akrr.conf")
        log.info("AKRR configuration will be in " + akrr_cfg)

else:
    akrr_home = os.path.dirname(os.path.dirname(akrr_cfg))
    log.info("AKRR_CONF is set. AKRR configuration will be in " + akrr_cfg)

dry_run = False


def _cursor_execute(cur, query, args=None):
    from akrr.util.sql import cursor_execute
    cursor_execute(cur, query, args=args, dry_run=dry_run)


def _make_dirs(path):
    """Recursively create directories if not in dry run mode"""
    if not dry_run:
        log.debug("Creating directory: {}".format(path))
        os.makedirs(path)
    else:
        log.dry_run("_make_dirs({})".format(path))


def _read_username_password(
        prompt="Enter username:",
        username=None,
        password=None,
        default_username="user",
        password_on_default_user=None):
    if username is None:
        log.log_input(prompt)

    if username is None:
        username = input('[{0}] '.format(default_username))
        if username == '':
            username = default_username
    else:
        log.info("User, " + username + ", already entered.")

    if username == default_username and password is None and password_on_default_user is not None:
        password = password_on_default_user

    if password is None:
        while True:
            log.log_input("Please specify a password:")
            password = getpass.getpass()
            log.log_input("Please reenter the password:")
            password2 = getpass.getpass()
            if password == password2:
                break
            log.error("Entered passwords do not match. Please try again.")
    else:
        log.info("Password already entered.")
    return username, password


def _read_sql_su_credentials(host, port):
    while True:
        log.log_input(
            "Please provide an administrative database user (for {}:{}) "
            "under which the installation sql script should "
            "run (This user must have privileges to create "
            "users and databases).".format(host, port))
        su_username = input("Username: ")
        log.log_input("Please provide the password for the the user which you previously entered:")
        su_password = getpass.getpass()

        try:
            get_con_to_db(su_username, su_password, host, port)
            return su_username, su_password
        except Exception as e:
            log.error("MySQL error: " + str(e))
            log.error("Entered credential is not valid. Please try again.")


class AKRRSetup:
    """
    AKRRSetup class handles AKRR setup
    """
    default_akrr_user = 'akrruser'

    def __init__(
            self,
            akrr_db=None,
            ak_db=None,
            xd_db=None,
            install_cron_scripts=True,
            stand_alone=False,
            update=False,
            old_akrr_conf_dir=None,
            generate_db_only=False):
        """
        Setup or update AKRR

        Parameters
        ----------
        akrr_db - if none will use localhost:3306
        ak_db - if none will use ak_db
        xd_db - if none will use xd_db
        install_cron_scripts
        stand_alone
        update - update current akrr installation
        old_akrr_conf_dir
        generate_db_only
        """
        self.old_akrr_conf = None
        if update:
            self.read_old_akrr_conf_dir(old_akrr_conf_dir)

        # Set initial db conf
        if not update:
            if akrr_db is None:
                # i.e. not set, use default
                akrr_db = "localhost:3306"
            if ak_db is None:
                ak_db = akrr_db
            if xd_db is None:
                xd_db = akrr_db
        else:
            if akrr_db is None:
                # i.e. not set, use default
                akrr_db = set_user_password_host_port_db(
                    self.old_akrr_conf['akrr_db_user'], self.old_akrr_conf['akrr_db_passwd'],
                    self.old_akrr_conf['akrr_db_host'], self.old_akrr_conf['akrr_db_port'],
                    None)
            if ak_db is None:
                ak_db = set_user_password_host_port_db(
                    self.old_akrr_conf['akrr_db_user'], self.old_akrr_conf['akrr_db_passwd'],
                    self.old_akrr_conf['akrr_db_host'], self.old_akrr_conf['akrr_db_port'],
                    self.old_akrr_conf['akrr_db_name'])
            if xd_db is None:
                xd_db = set_user_password_host_port_db(
                    self.old_akrr_conf['akrr_db_user'], self.old_akrr_conf['akrr_db_passwd'],
                    self.old_akrr_conf['akrr_db_host'], self.old_akrr_conf['akrr_db_port'],
                    self.old_akrr_conf['akrr_db_name'])

        # Get db details
        self.akrr_db_user_name, \
            self.akrr_db_user_password, \
            self.akrr_db_host, \
            self.akrr_db_port, \
            self.akrr_db_name = get_user_password_host_port_db(akrr_db, default_database="mod_akrr")

        self.ak_db_user_name, \
            self.ak_db_user_password, \
            self.ak_db_host, \
            self.ak_db_port, \
            self.ak_db_name = get_user_password_host_port_db(ak_db, default_database="mod_appkernel")

        self.xd_db_user_name, \
            self.xd_db_user_password, \
            self.xd_db_host, \
            self.xd_db_port, \
            self.xd_db_name = get_user_password_host_port_db(xd_db, default_database="modw")

        # su will remain None if akrr user and db already exists and user has proper rights
        self.ak_db_su_user_name = None
        self.ak_db_su_user_password = None
        self.akrr_db_su_user_name = None
        self.akrr_db_su_user_password = None
        self.xd_db_su_user_name = None
        self.xd_db_su_user_password = None

        self.cron_email = None
        self.stand_alone = stand_alone
        self.install_cron_scripts_flag = install_cron_scripts

        self.update = update

        self.old_akrr_conf_dir = old_akrr_conf_dir
        self.generate_db_only = generate_db_only

    def check_previous_installation(self):
        """
        check that AKRR is not already installed
        """
        if os.path.exists(akrr_cfg):
            if self.update:
                return
            else:
                msg = "This is a fresh installation script. " + akrr_home + \
                      " contains previous AKRR installation. Either uninstall it or see documentation on updates.\n\n"
                msg += "To uninstall AKRR manually:\n\t1)remove " + akrr_cfg + "\n\t\trm " + akrr_cfg + "\n"
                msg += "\t2) (optionally for totally fresh start) drop mod_akrr and mod_appkernel database\n"
                msg += "\t\tDROP DATABASE mod_appkernel;\n"
                msg += "\t\tDROP DATABASE mod_akrr;\n\n"

                log.error(msg)
                exit(1)

    @staticmethod
    def check_utils():
        """
        check that ssh and openssl already installed
        """
        from distutils.spawn import find_executable

        errmsg = ""
        if not find_executable('ssh'):
            errmsg += "Can not find ssh in PATH, please install it.\n"
        if not find_executable('openssl'):
            errmsg += "Can not find openssl in PATH, please install it.\n"

        if errmsg != "":
            log.error(errmsg)
            exit(1)

    def read_db_user_credentials(self):
        """
        Get DB access user credential
        """
        # mod_akrr
        log.info("Before Installation continues we need to setup the database.")

        self.akrr_db_user_name, self.akrr_db_user_password = _read_username_password(
            "Please specify a database user to access mod_akrr database (Used by AKRR)"
            "(This user will be created if it does not already exist):",
            self.akrr_db_user_name,
            self.akrr_db_user_password,
            self.default_akrr_user)
        log.empty_line()

        # check if user, db already there
        db_exists = False
        user_rights_are_correct = False
        try:
            # connect with provided user, Exception will raise if user can not connect
            _, cur = get_con_to_db(self.akrr_db_user_name, self.akrr_db_user_password, self.akrr_db_host,
                                   self.akrr_db_port)
            client_host = get_db_client_host(cur)
            user_exists = True

            db_exists = db_exist(cur, self.akrr_db_name)
            if not db_exists:
                log.debug("Database {} doesn't exists on {}".format(self.akrr_db_name, self.akrr_db_host))
            user_rights_are_correct = db_check_priv(cur, self.akrr_db_name, "ALL", self.akrr_db_user_name, client_host)
            if not user_rights_are_correct:
                log.debug(
                    "User {} doesn't have right privilege on {}, should be ALL".format(
                        self.akrr_db_user_name, self.akrr_db_name))
        except MySQLdb.Error:
            user_exists = False
            log.debug("User ({}) does not exists on {}".format(self.akrr_db_user_name, self.akrr_db_host))

        # ask for su user on this machine if needed
        if not user_exists or not db_exists or not user_rights_are_correct:
            self.akrr_db_su_user_name, \
                self.akrr_db_su_user_password = _read_sql_su_credentials(self.akrr_db_host, self.akrr_db_port)
        log.empty_line()
        ###
        # mod_appkernel
        same_host_as_ak = self.ak_db_host == self.akrr_db_host and self.ak_db_port == self.akrr_db_port

        self.ak_db_user_name, self.ak_db_user_password = _read_username_password(
            "Please specify a database user to access mod_appkernel database "
            "(Used by XDMoD appkernel module, AKRR creates and syncronize resource and appkernel description)"
            "(This user will be created if it does not already exist):",
            self.ak_db_user_name,
            self.ak_db_user_password,
            self.akrr_db_user_name,
            self.akrr_db_user_password if same_host_as_ak else None
        )
        log.empty_line()

        # ask for su user on this machine
        db_exists = False
        user_rights_are_correct = False
        try:
            _, cur = get_con_to_db(self.ak_db_user_name, self.ak_db_user_password, self.ak_db_host, self.ak_db_port)
            client_host = get_db_client_host(cur)
            user_exists = True

            db_exists = db_exist(cur, self.ak_db_name)
            if not db_exists:
                log.debug("Database {} doesn't exists on {}".format(self.ak_db_name, self.ak_db_host))
            user_rights_are_correct = db_check_priv(cur, self.ak_db_name, "ALL", self.ak_db_user_name, client_host)
            if not user_rights_are_correct:
                log.debug(
                    "User {} doesn't have right privelege on {}, should be ALL".format(
                        self.ak_db_user_name, self.ak_db_name))
        except Exception:
            user_exists = False
            log.debug("User ({}) does not exists on {}".format(self.akrr_db_user_name, self.akrr_db_host))

        if not user_exists or not db_exists or not user_rights_are_correct:
            self.ak_db_su_user_name = self.akrr_db_su_user_name
            self.ak_db_su_user_password = self.akrr_db_su_user_password
            try:
                get_con_to_db(self.ak_db_su_user_name, self.ak_db_su_user_password, self.ak_db_host, self.ak_db_port)
            except Exception:
                self.ak_db_su_user_name, \
                    self.ak_db_su_user_password = _read_sql_su_credentials(self.ak_db_host, self.ak_db_port)
        log.empty_line()

        ##
        # modw
        same_host_as_xd = self.xd_db_host == self.ak_db_host and self.xd_db_port == self.ak_db_port

        self.xd_db_user_name, self.xd_db_user_password = _read_username_password(
            "Please specify the user that will be connecting to the XDMoD database (modw):",
            self.xd_db_user_name,
            self.xd_db_user_password,
            self.ak_db_user_name,
            self.ak_db_user_password if same_host_as_xd else None
        )
        log.empty_line()

        # ask for su user on this machine
        db_exists = False
        user_rights_are_correct = False
        try:

            _, cur = get_con_to_db(self.xd_db_user_name, self.xd_db_user_password, self.xd_db_host, self.xd_db_port)
            client_host = get_db_client_host(cur)
            user_exists = True

            db_exists = db_exist(cur, "modw")
            if not db_exists:
                log.debug("Database {} doesn't exists on {}".format(self.xd_db_name, self.xd_db_host))
            user_rights_are_correct = db_check_priv(cur, self.xd_db_name, "SELECT", self.xd_db_user_name, client_host)
            if not user_rights_are_correct:
                log.debug(
                    "User {} doesn't have right privelege on {}, should be at least SELECT".format(
                        self.xd_db_user_name, self.xd_db_name))
        except Exception:
            user_exists = False
            log.debug("User ({}) does not exists on {}".format(self.xd_db_user_name, self.xd_db_host))

        if not user_exists or not db_exists or not user_rights_are_correct:
            self.xd_db_su_user_name = self.ak_db_su_user_name
            self.xd_db_su_user_password = self.ak_db_su_user_password
            try:
                get_con_to_db(self.xd_db_su_user_name, self.xd_db_su_user_password, self.xd_db_host, self.xd_db_port)
            except Exception:
                self.ak_db_su_user_name, \
                    self.ak_db_su_user_password = _read_sql_su_credentials(self.xd_db_host, self.xd_db_port)
        log.empty_line()

    def get_akrr_db(self, su=False, dbname=""):
        """
        get connector and cursor to mod_akrr DB
        """
        return get_con_to_db(
            self.akrr_db_user_name if not su else self.akrr_db_su_user_name,
            self.akrr_db_user_password if not su else self.akrr_db_su_user_password,
            self.akrr_db_host, self.akrr_db_port,
            self.akrr_db_name if dbname == "" else dbname)

    def get_ak_db(self, su=False, dbname=""):
        """
        get connector and cursor to mod_appkernel DB
        """
        return get_con_to_db(
            self.ak_db_user_name if not su else self.ak_db_su_user_name,
            self.ak_db_user_password if not su else self.ak_db_su_user_password,
            self.ak_db_host, self.ak_db_port,
            self.ak_db_name if dbname == "" else dbname)

    def get_xd_db(self, su=False, dbname=""):
        """
        get connector and cursor to XDMoD's modw DB
        """
        return get_con_to_db(
            self.xd_db_user_name if not su else self.xd_db_su_user_name,
            self.xd_db_user_password if not su else self.xd_db_su_user_password,
            self.xd_db_host, self.xd_db_port,
            self.xd_db_name if dbname == "" else dbname)

    @staticmethod
    def get_random_password():
        """
        Pseudo-random password generator
        """
        length = 16
        chars = string.ascii_letters + string.digits
        # + '@#$%^&*'
        password = ""
        while len(password) < length:
            i = os.urandom(1)
            if ord(i) > (255 / len(chars)) * len(chars):
                continue
            password += chars[ord(i) % len(chars)]
        return password

    @staticmethod
    def init_dir():
        """
        Make directories for configuration and logging
        """
        try:
            log.info("Creating directories structure.")
            if not os.path.isdir(akrr_home):
                _make_dirs(akrr_home)
            if not os.path.isdir(os.path.join(akrr_home, 'etc')):
                _make_dirs(os.path.join(akrr_home, 'etc'))
            if not os.path.isdir(os.path.join(akrr_home, 'etc', 'resources')):
                _make_dirs(os.path.join(akrr_home, 'etc', 'resources'))
            if not os.path.isdir(os.path.join(akrr_home, 'etc', 'resources')):
                _make_dirs(os.path.join(akrr_home, 'etc', 'resources'))
            if not os.path.isdir(os.path.join(akrr_home, 'log')):
                _make_dirs(os.path.join(akrr_home, 'log'))
            if not os.path.isdir(os.path.join(akrr_home, 'log', 'data')):
                _make_dirs(os.path.join(akrr_home, 'log', 'data'))
            if not os.path.isdir(os.path.join(akrr_home, 'log', 'comptasks')):
                _make_dirs(os.path.join(akrr_home, 'log', 'comptasks'))
            if not os.path.isdir(os.path.join(akrr_home, 'log', 'akrrd')):
                _make_dirs(os.path.join(akrr_home, 'log', 'akrrd'))
        except Exception as e:
            log.error("Can not create directories: " + str(e))
            exit(1)

    def init_mysql_dbs(self):
        """
        Create AKRR database and access user, set the user access rights
        """
        try:
            def _create_db_user_gran_priv_if_needed(con_fun, user, password, db, priv, create):
                """
                Helping function to create db and user
                """
                if create:
                    log.info("Creating %s and user to access it" % (db,))
                else:
                    log.info("Setting user to access %s" % (db,))
                su_con, su_cur = con_fun(True, None)
                client_host = get_db_client_host(su_cur)

                if create:
                    _cursor_execute(su_cur, "CREATE DATABASE IF NOT EXISTS %s" % (cv(db),))

                create_user_if_not_exists(su_cur, user, password, client_host, dry_run=dry_run)
                _cursor_execute(su_cur, "GRANT " + cv(priv) + " ON " + cv(db) + ".* TO %s@%s", (user, client_host))

                su_con.commit()

            # During self.read_db_creds db and user was checked and
            # if they do not exist or not good enough super user credentials
            # was asked so if they not None that means that
            # either user or db or user priv needed to be set
            if self.akrr_db_su_user_name is not None:
                _create_db_user_gran_priv_if_needed(
                    self.get_akrr_db, self.akrr_db_user_name, self.akrr_db_user_password, self.akrr_db_name,
                    "ALL", True)
            if not self.stand_alone:
                if self.ak_db_su_user_name is not None:
                    _create_db_user_gran_priv_if_needed(
                        self.get_ak_db, self.ak_db_user_name, self.ak_db_user_password, self.ak_db_name,
                        "ALL", True)
                if self.xd_db_su_user_name is not None:
                    _create_db_user_gran_priv_if_needed(
                        self.get_xd_db, self.xd_db_user_name, self.xd_db_user_password, self.xd_db_name,
                        "SELECT", False)

        except Exception as e:
            import traceback
            traceback.print_exc()
            log.error("Can not execute the sql setup script: " + str(e))
            exit(1)

    @staticmethod
    def generate_self_signed_certificate():
        """
        Generate self signed certificate for AKRR Rest API
        """
        log.info("Generating self-signed certificate for REST-API")

        cmd = """
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
            """.format(akrr_cfg_dir=os.path.join(akrr_home, 'etc'))
        if not dry_run:
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
            log.debug(output.decode("utf-8"))
            log.info("    new self-signed certificate have been generated")
        else:
            log.dry_run("run command: " + cmd)

    def generate_settings_file(self):
        """
        Generate configuration (akrr.conf) file
        """
        log.info("Generating configuration file ...")
        with open(os.path.join(akrr_mod_dir, 'templates', 'akrr.conf'), 'r') as f:
            akrr_inp_template = f.read()
        restapi_rw_password = self.get_random_password()
        restapi_ro_password = self.get_random_password()
        var = {
            'akrr_db_host': '"%s"' % self.akrr_db_host,
            'akrr_db_port': '%s' % str(self.akrr_db_port),
            'akrr_db_user_name': '"%s"' % self.akrr_db_user_name,
            'akrr_db_user_password': '"%s"' % self.akrr_db_user_password,
            'akrr_db_name': '"%s"' % self.akrr_db_name,
            'ak_db_name': '"%s"' % self.ak_db_name,
            'xd_db_name': '"%s"' % self.xd_db_name,
            'restapi_rw_password': restapi_rw_password,
            'restapi_ro_password': restapi_ro_password
        }
        if self.akrr_db_host == self.ak_db_host and self.akrr_db_port == self.ak_db_port and \
                self.akrr_db_user_name == self.ak_db_user_name and \
                self.akrr_db_user_password == self.ak_db_user_password:
            var.update({
                'ak_db_host': 'akrr_db_host',
                'ak_db_port': 'akrr_db_port',
                'ak_db_user_name': 'akrr_db_user',
                'ak_db_user_password': 'akrr_db_passwd'
            })
        else:
            var.update({
                'ak_db_host': '"%s"' % self.ak_db_host,
                'ak_db_port': '%s' % str(self.ak_db_port),
                'ak_db_user_name': '"%s"' % self.ak_db_user_name,
                'ak_db_user_password': '"%s"' % self.ak_db_user_password
            })

        if self.xd_db_host == self.akrr_db_host and self.xd_db_port == self.akrr_db_port and \
                self.xd_db_user_name == self.akrr_db_user_name and \
                self.xd_db_user_password == self.akrr_db_user_password:
            var.update({
                'xd_db_host': 'akrr_db_host',
                'xd_db_port': 'akrr_db_port',
                'xd_db_user_name': 'akrr_db_user',
                'xd_db_user_password': 'akrr_db_passwd',

            })
        elif self.xd_db_host == self.ak_db_host and self.xd_db_port == self.ak_db_port and \
                self.xd_db_user_name == self.ak_db_user_name and \
                self.xd_db_user_password == self.ak_db_user_password:
            var.update({
                'xd_db_host': 'ak_db_host',
                'xd_db_port': 'ak_db_port',
                'xd_db_user_name': 'ak_db_user',
                'xd_db_user_password': 'ak_db_passwd',
            })
        else:
            var.update({
                'xd_db_host': '"%s"' % self.xd_db_host,
                'xd_db_port': '%s' % str(self.xd_db_port),
                'xd_db_user_name': '"%s"' % self.xd_db_user_name,
                'xd_db_user_password': '"%s"' % self.xd_db_user_password,
            })

        akrr_inp = akrr_inp_template.format(**var)
        if not dry_run:
            with open(akrr_cfg, 'w') as f:
                f.write(akrr_inp)
            log.info("Configuration is written to: {0}".format(akrr_cfg))
        else:
            log.dry_run("New config should be written to: {}".format(akrr_cfg))
            log.debug2(akrr_inp)

    @staticmethod
    def set_permission_on_files():
        """
        Remove access for group members and everybody for all files.
        """
        log.info(
            "Removing access for group members and everybody for all files.")
        if not dry_run:
            subprocess.check_output("""
                chmod -R g-rwx {akrr_home}
                chmod -R o-rwx {akrr_home}
                """.format(akrr_home=akrr_home), shell=True)

    def db_check(self):
        """
        Check DB access
        """
        log.info("Checking access to DBs.")
        if dry_run:
            return

        from . import db_check
        if not db_check.db_check(mod_appkernel=not self.stand_alone, modw=not self.stand_alone):
            exit(1)

    def generate_tables(self):
        """
        Create and populate AKRR tables
        """
        log.info("Creating tables and populating them with initial values.")

        from .generate_tables import create_and_populate_mod_akrr_tables, create_and_populate_mod_appkernel_tables
        from .generate_tables import copy_mod_akrr_tables

        create_and_populate_mod_akrr_tables(dry_run, not self.update)
        if self.update:
            mod_akrr = set_user_password_host_port_db(
                self.akrr_db_user_name, self.akrr_db_user_password, self.akrr_db_host,
                self.akrr_db_port, self.akrr_db_name)

            copy_mod_akrr_tables(mod_akrr)

        if not self.stand_alone:
            create_and_populate_mod_appkernel_tables(dry_run, not self.update)

    @staticmethod
    def start_daemon():
        """
        Start the daemon
        """
        log.info("Starting AKRR daemon")
        if dry_run:
            return

        akrr_cli = os.path.join(akrr_bin_dir, 'akrr')
        status = subprocess.call(akrr_cli + " daemon start", shell=True)

        if status != 0:
            log.critical("AKRR daemon didn't start.")
            exit(status)

    @staticmethod
    def check_daemon():
        """
        Check that the daemon is running
        """
        log.info("Checking that AKRR daemon is running")
        if dry_run:
            return

        akrr_cli = os.path.join(akrr_bin_dir, 'akrr')
        status = subprocess.call(akrr_cli + " daemon check", shell=True)
        if status != 0:
            exit(status)

    def ask_cron_email(self):
        """
        ask for cron e-mail.
        """
        try:
            crontan_content = subprocess.check_output("crontab -l", shell=True)
            crontan_content = crontan_content.decode("utf-8").splitlines(True)
        except Exception:
            # probably no crontab was setup yet
            crontan_content = []
        for l in crontan_content:
            if len(l.strip()) > 1 and l.strip()[0] != "#":
                m = re.match(r'^MAILTO\s*=\s*(.*)', l.strip())
                if m:
                    self.cron_email = m.group(1)
                    self.cron_email = self.cron_email.replace('"', '')
        if self.cron_email is None:
            log.log_input("Please enter the e-mail where cron will send messages (leave empty to opt out):")
            self.cron_email = input()
        else:
            log.log_input("Please enter the e-mail where cron will send messages:")
            cron_email = input('[{0}] '.format(self.cron_email))
            if cron_email != "":
                self.cron_email = cron_email
        if self.cron_email == "":
            self.cron_email = None

    def install_cron_scripts(self):
        """
        Install cron scripts.
        """
        log.info("Installing cron entries")
        if dry_run:
            return

        if self.cron_email:
            mail = "MAILTO = " + self.cron_email
        else:
            mail = None
        restart = "50 23 * * * " + akrr_bin_dir + "/akrr daemon restart -cron"
        check_and_restart = "33 * * * * " + akrr_bin_dir + "/akrr daemon checknrestart -cron"

        try:
            crontan_content = subprocess.check_output("crontab -l", shell=True)
            crontan_content = crontan_content.decode("utf-8").splitlines(True)
        except Exception:
            log.info("Crontab does not have user's crontab yet")
            crontan_content = []

        mail_updated = False
        mail_there = False
        restart_there = False
        check_and_restart_there = False

        for i in range(len(crontan_content)):
            tmpstr = crontan_content[i]
            if len(tmpstr.strip()) > 1 and tmpstr.strip()[0] != "#":
                m = re.match(r'^MAILTO\s*=\s*(.*)', tmpstr.strip())
                if m:
                    cron_email = m.group(1)
                    cron_email = cron_email.replace('"', '')
                    mail_there = True
                    if self.cron_email != cron_email:
                        if mail:
                            crontan_content[i] = mail
                        else:
                            crontan_content[i] = "#" + crontan_content[i]
                        mail_updated = True
                if tmpstr.count("akrr") and tmpstr.count("daemon") and tmpstr.count("restart") > 0:
                    restart_there = True
                if tmpstr.count("akrr") and tmpstr.count("daemon") and tmpstr.count("checknrestart") > 0:
                    check_and_restart_there = True
        if mail_updated:
            log.info("Cron's MAILTO was updated")
        if ((self.cron_email is not None and mail_there) or (
                self.cron_email is None and mail_there is False)) and restart_there and check_and_restart_there \
                and mail_updated is False:
            log.warning("All AKRR crond entries found. No modifications necessary.")
            return
        if self.cron_email is not None and mail_there is False:
            crontan_content.insert(0, mail + "\n")
        if restart_there is False:
            crontan_content.append(restart + "\n")
        if check_and_restart_there is False:
            crontan_content.append(check_and_restart + "\n")

        with open(os.path.expanduser('.crontmp'), 'w') as f:
            for tmpstr in crontan_content:
                f.write(tmpstr)
        subprocess.call("crontab .crontmp", shell=True)
        os.remove(".crontmp")
        log.info("Cron Scripts Processed!")

    def read_old_akrr_conf_dir(self, old_akrr_conf_dir):
        """Read old AKRR configuration file"""

        if not os.path.isdir(old_akrr_conf_dir):
            log.error("Directory with old AKRR configuration do not exist: " + old_akrr_conf_dir)
            exit(1)

        old_akrr_conf_file = os.path.join(old_akrr_conf_dir, "akrr.conf")
        if not os.path.isfile(old_akrr_conf_file):
            log.error("File with old AKRR configuration do not exist: " + old_akrr_conf_file)
            exit(1)

        from akrr.util import exec_files_to_dict
        log.info("Reading old AKRR configuration from: " + old_akrr_conf_file)
        self.old_akrr_conf = exec_files_to_dict(old_akrr_conf_file)

    @staticmethod
    def update_bashrc():
        """Add AKRR enviroment variables to .bashrc"""
        log.info("Updating .bashrc")

        bash_content_new = []
        akrr_header = '#AKRR Server Environment Variables'
        if os.path.exists(os.path.expanduser("~/.bashrc")):
            log.info("Updating AKRR record in $HOME/.bashrc, backing to $HOME/.bashrc_akrrbak")
            if not dry_run:
                subprocess.call("cp ~/.bashrc ~/.bashrcakrr", shell=True)
            with open(os.path.expanduser('~/.bashrc'), 'r') as f:
                bashcontent = f.readlines()
                in_akrr = False
                for l in bashcontent:
                    if l.count(akrr_header + ' [Start]') > 0:
                        in_akrr = True
                    if not in_akrr:
                        bash_content_new.append(l)
                    if l.count(akrr_header + ' [End]') > 0:
                        in_akrr = False
        bash_content_new.append("\n" + akrr_header + " [Start]\n")
        bash_content_new.append("export PATH=\"{0}/bin:$PATH\"\n".format(akrr_home))
        bash_content_new.append(akrr_header + " [End]\n\n")
        if not dry_run:
            with open(os.path.expanduser('~/.bashrc'), 'w') as f:
                for l in bash_content_new:
                    f.write(l)
            log.info("Appended AKRR records to $HOME/.bashrc")
        else:
            log.debug("New .bashrc should be like" + "\n".join(bash_content_new))

    def run(self):
        # check
        self.check_utils()
        self.check_previous_installation()

        # ask info
        self.read_db_user_credentials()

        if self.install_cron_scripts_flag and not self.generate_db_only:
            self.ask_cron_email()

        # if it is dry_run
        # all question are asked, this is dry run, so nothing else to do")

        self.init_mysql_dbs()

        self.init_dir()
        self.generate_self_signed_certificate()
        if not self.update:
            self.generate_settings_file()
        self.set_permission_on_files()
        self.db_check()

        self.generate_tables()

        if self.generate_db_only:
            log.info("AKRR DB Generated")
            return

        self.start_daemon()
        self.check_daemon()
        if self.install_cron_scripts_flag:
            self.install_cron_scripts()

        if in_src_install:
            self.update_bashrc()

        log.info("AKRR is set up and is running.")
