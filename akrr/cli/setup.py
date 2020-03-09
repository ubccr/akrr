"""
This module contains routines for initial AKRR configuration
"""

import os
import sys
import re
import getpass
import subprocess
import string
from typing import Optional, Dict, Tuple

import MySQLdb
import MySQLdb.cursors

import akrr
from akrr.util import log
from akrr.util.sql import get_con_to_db
from akrr.util.sql import get_user_password_host_port_db
from akrr.util.sql import set_user_password_host_port_db
from akrr.util.sql import db_exist
from akrr.util.sql import cv
from akrr.util.sql import db_check_priv
from akrr.util.sql import get_db_client_host
from akrr.util.sql import create_user_if_not_exists

# Since AKRR setup is the first script to execute
# Lets check python version, proper library presence and external commands.

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

_akrr_dirs = akrr.get_akrr_dirs()
_akrr_mod_dir = _akrr_dirs['akrr_mod_dir']
_akrr_bin_dir = _akrr_dirs['akrr_bin_dir']
_in_src_install = _akrr_dirs['in_src_install']
# _akrr_home and _akrr_cfg might be later change during setup
# In the beginning it will indicate previous installation
_akrr_home: Optional[str] = _akrr_dirs["akrr_home"]
_akrr_cfg:  Optional[str] = _akrr_dirs["akrr_cfg"]


def _cursor_execute(cur, query, args=None):
    from akrr.util.sql import cursor_execute
    cursor_execute(cur, query, args=args, dry_run=akrr.dry_run)


def _make_dirs(path):
    """Recursively create directories if not in dry run mode"""
    if not akrr.dry_run:
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
        username = input('[{0}]: '.format(default_username))
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


def _read_sql_su_credentials(host: str, port: int) -> Tuple[str, str]:
    while True:
        log.log_input(
            "Please provide an administrative database user (for {}:{}) "
            "under which the installation sql script should "
            "run (This user must have privileges to create "
            "users and databases).".format(host, port))
        su_username = input("[root]: ")
        if su_username == '':
            su_username = 'root'
        log.log_input("Please provide the password for the the user which you previously entered:")
        su_password = getpass.getpass()

        try:
            get_con_to_db(su_username, su_password, host, port)
            return su_username, su_password
        except Exception as e:
            log.error("MySQL error: " + str(e))
            log.error("Entered credential is not valid. Please try again.")


def _check_and_read_su_credentials_for_dbserver(
        user: Optional[str], password: Optional[str], host: str, port: int) -> Tuple[str, str]:
    """
    Ask for administrative credential on db server
    if user and password is provided check them first
    Returns: user, password
    """
    if not user or not password:
        try:
            get_con_to_db(user, password, host, port)
            return user, password
        except Exception:
            return _read_sql_su_credentials(host, port)
    else:
        return _read_sql_su_credentials(host, port)


class AKRRSetup:
    """
    AKRRSetup class handles AKRR setup

    example: AKRRSetup().run(**kwargs)
    """

    default_akrr_user: str = 'akrruser'
    default_akrr_db: str = 'localhost:3306'

    def __init__(self):
        """
        Initiate class
        """
        self.generate_db_only: bool = False

        # Administrative database credential, used during this execution if needed
        self.ak_db_su_user_name: Optional[str] = None
        self.ak_db_su_user_password: Optional[str] = None
        self.akrr_db_su_user_name: Optional[str] = None
        self.akrr_db_su_user_password: Optional[str] = None
        self.xd_db_su_user_name: Optional[str] = None
        self.xd_db_su_user_password: Optional[str] = None

        # Database credential
        # user_name can be none indicating that it was not entered yet
        # password can be none indicating that it was not entered yet
        self.akrr_db_user_name: Optional[str] = None
        self.akrr_db_user_password: Optional[str] = None
        self.akrr_db_host: str = ""
        self.akrr_db_port: int = 3306
        self.akrr_db_name: str = "mod_akrr"

        self.ak_db_user_name: Optional[str] = None
        self.ak_db_user_password: Optional[str] = None
        self.ak_db_host: str = ""
        self.ak_db_port: int = 3306
        self.ak_db_name: str = "mod_appkernel"

        self.xd_db_user_name: Optional[str] = None
        self.xd_db_user_password: Optional[str] = None
        self.xd_db_host: str = ""
        self.xd_db_port: int = 3306
        self.xd_db_name: str = "modw"

        # Setup options
        self.cron_email: Optional[str] = None
        self.stand_alone: bool = False
        self.install_cron_scripts_flag: bool = True
        self.akrr_home_dir: Optional[str] = None

        # @todo update will be separate class remove it
        self.update: bool = False
        self.old_akrr_conf: Optional[str] = None
        self.old_akrr_conf_dir: Optional[Dict] = None

        # internals
        self._initial_akrr_dirs: Dict = {}
        self._akrr_dirs: Dict = {}

    def check_previous_installation(self):
        """
        check that AKRR is not already installed
        """
        if os.path.exists(_akrr_cfg):
            if self.update:
                return
            else:
                msg = "This is a fresh installation script. " + _akrr_home + \
                      " contains previous AKRR installation. Either uninstall it or see documentation on updates.\n\n"
                msg += "To uninstall AKRR manually:\n\t1)remove " + _akrr_cfg + "\n\t\trm " + _akrr_cfg + "\n"
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

    @staticmethod
    def _check_user_db_priv_on_dbserver(user: str, password: str, host: str, port: int, db_name: str, priv: str) \
            -> Tuple[bool, bool, bool]:
        """
        Check if user and database already exists and privileges are ok
        Returns: user_exists, db_exists, user_rights_are_correct
        """
        # check if user, db already there
        try:
            # connect with provided user, Exception will raise if user can not connect
            _, cur = get_con_to_db(user, password, host, port)
            client_host = get_db_client_host(cur)
            user_exists = True

            db_exists = db_exist(cur, db_name)
            if not db_exists:
                log.debug("Database %s doesn't exists on %s", db_name, host)
            user_rights_are_correct = db_check_priv(cur, db_name, priv, user, client_host)
            if not user_rights_are_correct:
                log.debug("User %s doesn't have right privilege on %s, should be %s", user, db_name, priv)
        except MySQLdb.Error:
            user_exists = False
            db_exists = False
            user_rights_are_correct = False
            log.debug("User (%s) does not exists on %s", user, host)
        return user_exists, db_exists, user_rights_are_correct

    def read_db_user_credentials(self):
        """
        Get DB access user credential
        """
        log.info("Before Installation continues we need to setup the database.")

        #######################
        # mod_akrr
        self.akrr_db_user_name, self.akrr_db_user_password = _read_username_password(
            "Please specify a database user to access mod_akrr database (Used by AKRR)"
            "(This user will be created if it does not already exist):",
            self.akrr_db_user_name, self.akrr_db_user_password, self.default_akrr_user)
        log.empty_line()

        # check if user, db already there
        user_exists, db_exists, user_rights_are_correct = AKRRSetup._check_user_db_priv_on_dbserver(
            self.akrr_db_user_name, self.akrr_db_user_password, self.akrr_db_host, self.akrr_db_port,
            self.akrr_db_name, "ALL")

        # ask for su user on this machine if needed
        if not user_exists or not db_exists or not user_rights_are_correct:
            self.akrr_db_su_user_name, self.akrr_db_su_user_password = \
                _check_and_read_su_credentials_for_dbserver(None, None, self.akrr_db_host, self.akrr_db_port)
        log.empty_line()

        #######################
        # mod_appkernel
        same_host_as_ak = self.ak_db_host == self.akrr_db_host and self.ak_db_port == self.akrr_db_port

        self.ak_db_user_name, self.ak_db_user_password = _read_username_password(
            "Please specify a database user to access mod_appkernel database "
            "(Used by XDMoD appkernel module, AKRR creates and syncronize resource and appkernel description)"
            "(This user will be created if it does not already exist):",
            self.ak_db_user_name, self.ak_db_user_password, self.akrr_db_user_name,
            self.akrr_db_user_password if same_host_as_ak else None)
        log.empty_line()

        # check if user, db already there
        user_exists, db_exists, user_rights_are_correct = AKRRSetup._check_user_db_priv_on_dbserver(
            self.ak_db_user_name, self.ak_db_user_password, self.ak_db_host, self.ak_db_port, self.ak_db_name, "ALL")

        # ask for su user on this machine
        if not user_exists or not db_exists or not user_rights_are_correct:
            self.ak_db_su_user_name, self.ak_db_su_user_password = \
                _check_and_read_su_credentials_for_dbserver(self.akrr_db_su_user_name, self.akrr_db_su_user_password,
                                                            self.ak_db_host, self.ak_db_port)
        log.empty_line()

        #######################
        # modw
        same_host_as_xd = self.xd_db_host == self.ak_db_host and self.xd_db_port == self.ak_db_port

        self.xd_db_user_name, self.xd_db_user_password = _read_username_password(
            "Please specify the user that will be connecting to the XDMoD database (modw):",
            self.xd_db_user_name, self.xd_db_user_password, self.ak_db_user_name,
            self.ak_db_user_password if same_host_as_xd else None
        )
        log.empty_line()

        # check if user, db already there
        user_exists, db_exists, user_rights_are_correct = AKRRSetup._check_user_db_priv_on_dbserver(
            self.xd_db_user_name, self.xd_db_user_password, self.xd_db_host, self.xd_db_port, self.xd_db_name, "ALL")

        # ask for su user on this machine
        if not user_exists or not db_exists or not user_rights_are_correct:
            self.xd_db_su_user_name, self.xd_db_su_user_password = \
                _check_and_read_su_credentials_for_dbserver(self.akrr_db_su_user_name, self.akrr_db_su_user_password,
                                                            self.ak_db_host, self.ak_db_port)
        log.empty_line()

    def get_akrr_db(self, su=False, dbname: Optional[str] = ""):
        """
        get connector and cursor to mod_akrr DB
        """
        return get_con_to_db(
            self.akrr_db_user_name if not su else self.akrr_db_su_user_name,
            self.akrr_db_user_password if not su else self.akrr_db_su_user_password,
            self.akrr_db_host, self.akrr_db_port,
            self.akrr_db_name if dbname == "" else dbname)

    def get_ak_db(self, su=False, dbname: Optional[str] = ""):
        """
        get connector and cursor to mod_appkernel DB
        """
        return get_con_to_db(
            self.ak_db_user_name if not su else self.ak_db_su_user_name,
            self.ak_db_user_password if not su else self.ak_db_su_user_password,
            self.ak_db_host, self.ak_db_port,
            self.ak_db_name if dbname == "" else dbname)

    def get_xd_db(self, su=False, dbname: Optional[str] = ""):
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
            if not os.path.isdir(_akrr_home):
                _make_dirs(_akrr_home)
            if not os.path.isdir(os.path.join(_akrr_home, 'etc')):
                _make_dirs(os.path.join(_akrr_home, 'etc'))
            if not os.path.isdir(os.path.join(_akrr_home, 'etc', 'resources')):
                _make_dirs(os.path.join(_akrr_home, 'etc', 'resources'))
            if not os.path.isdir(os.path.join(_akrr_home, 'etc', 'resources')):
                _make_dirs(os.path.join(_akrr_home, 'etc', 'resources'))
            if not os.path.isdir(os.path.join(_akrr_home, 'log')):
                _make_dirs(os.path.join(_akrr_home, 'log'))
            if not os.path.isdir(os.path.join(_akrr_home, 'log', 'data')):
                _make_dirs(os.path.join(_akrr_home, 'log', 'data'))
            if not os.path.isdir(os.path.join(_akrr_home, 'log', 'comptasks')):
                _make_dirs(os.path.join(_akrr_home, 'log', 'comptasks'))
            if not os.path.isdir(os.path.join(_akrr_home, 'log', 'akrrd')):
                _make_dirs(os.path.join(_akrr_home, 'log', 'akrrd'))
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

                create_user_if_not_exists(su_con, su_cur, user, password, client_host, dry_run=akrr.dry_run)
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

            if self.ak_db_su_user_name is not None:
                _create_db_user_gran_priv_if_needed(
                    self.get_ak_db, self.ak_db_user_name, self.ak_db_user_password, self.ak_db_name,
                    "ALL", True)
            if self.stand_alone:
                # add fake modw
                from akrr.cli.generate_tables import add_fake_modw
                su_con, su_cur = self.get_xd_db(True, None)
                add_fake_modw(su_con, su_cur, dry_run=akrr.dry_run)

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
                -days 3650 \
                -nodes \
                -x509 \
                -subj "/C=US/ST=Denial/L=Springfield/O=Dis/CN=localhost" \
                -keyout {akrr_cfg_dir}/server.key \
                -out {akrr_cfg_dir}/server.cert
            cp {akrr_cfg_dir}/server.key {akrr_cfg_dir}/server.pem
            cat {akrr_cfg_dir}/server.cert >> {akrr_cfg_dir}/server.pem
            """.format(akrr_cfg_dir=os.path.join(_akrr_home, 'etc'))
        if not akrr.dry_run:
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
        with open(os.path.join(_akrr_mod_dir, 'templates', 'akrr.conf'), 'r') as f:
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
        if not akrr.dry_run:
            with open(_akrr_cfg, 'w') as f:
                f.write(akrr_inp)
            log.info("Configuration is written to: {0}".format(_akrr_cfg))
        else:
            log.dry_run("New config should be written to: {}".format(_akrr_cfg))
            log.debug2(akrr_inp)

    @staticmethod
    def set_permission_on_files():
        """
        Remove access for group members and everybody for all files.
        """
        log.info(
            "Removing access for group members and everybody for all files.")
        if not akrr.dry_run:
            subprocess.check_output("""
                chmod -R g-rwx {akrr_home}
                chmod -R o-rwx {akrr_home}
                """.format(akrr_home=_akrr_home), shell=True)

    def db_check(self):
        """
        Check DB access
        """
        log.info("Checking access to DBs.")
        if akrr.dry_run:
            return

        from . import db_check
        if not db_check.db_check():
            exit(1)

    def generate_tables(self):
        """
        Create and populate AKRR tables
        """
        log.info("Creating tables and populating them with initial values.")

        from .generate_tables import create_and_populate_mod_akrr_tables, create_and_populate_mod_appkernel_tables
        from .generate_tables import copy_mod_akrr_tables

        create_and_populate_mod_akrr_tables(akrr.dry_run, not self.update)
        if self.update:
            mod_akrr = set_user_password_host_port_db(
                self.akrr_db_user_name, self.akrr_db_user_password, self.akrr_db_host,
                self.akrr_db_port, self.akrr_db_name)

            copy_mod_akrr_tables(mod_akrr)

        create_and_populate_mod_appkernel_tables(akrr.dry_run, not self.update)

    @staticmethod
    def start_daemon():
        """
        Start the daemon
        """
        log.info("Starting AKRR daemon")
        if akrr.dry_run:
            return

        akrr_cli = os.path.join(_akrr_bin_dir, 'akrr')
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
        if akrr.dry_run:
            return

        akrr_cli = os.path.join(_akrr_bin_dir, 'akrr')
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
        if akrr.dry_run:
            return

        if self.cron_email:
            mail = "MAILTO = " + self.cron_email
        else:
            mail = None
        restart = "50 23 * * * " + _akrr_bin_dir + "/akrr daemon restart -cron"
        check_and_restart = "33 * * * * " + _akrr_bin_dir + "/akrr daemon checknrestart -cron"

        try:
            crontab_content = subprocess.check_output("crontab -l", shell=True)
            crontab_content = crontab_content.decode("utf-8").splitlines(True)
        except Exception:
            log.info("Crontab does not have user's crontab yet")
            crontab_content = []

        mail_updated = False
        mail_there = False
        restart_there = False
        check_and_restart_there = False

        for i in range(len(crontab_content)):
            tmpstr = crontab_content[i]
            if len(tmpstr.strip()) > 1 and tmpstr.strip()[0] != "#":
                m = re.match(r'^MAILTO\s*=\s*(.*)', tmpstr.strip())
                if m:
                    cron_email = m.group(1)
                    cron_email = cron_email.replace('"', '')
                    mail_there = True
                    if self.cron_email != cron_email:
                        if mail:
                            crontab_content[i] = mail
                        else:
                            crontab_content[i] = "#" + crontab_content[i]
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
            crontab_content.insert(0, mail + "\n")
        if restart_there is False:
            crontab_content.append(restart + "\n")
        if check_and_restart_there is False:
            crontab_content.append(check_and_restart + "\n")

        with open(os.path.expanduser('.crontmp'), 'wt') as f:
            for tmpstr in crontab_content:
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

    def update_bashrc(self):
        """Add AKRR enviroment variables to .bashrc"""
        log.info("Updating .bashrc")

        akrr_header = '#AKRR Server Environment Variables'
        akrr_bash_content_new = []

        akrr_bash_content_new.append("\n" + akrr_header + " [Start]\n")
        if _in_src_install:
            akrr_bash_content_new.append("export PATH=\"{0}:$PATH\"\n".format(_akrr_bin_dir))
        if self._initial_akrr_dirs["akrr_home"] != self._akrr_dirs["akrr_home"]:
            # i.e. non standard AKRR home location
            akrr_bash_content_new.append("export AKRR_HOME=\"{0}\"\n".format(_akrr_home))
        akrr_bash_content_new.append(akrr_header + " [End]\n\n")

        if len(akrr_bash_content_new) > 2:
            if os.path.exists(os.path.expanduser("~/.bashrc")):
                log.info("Updating AKRR record in $HOME/.bashrc, backing to $HOME/.bashrc.akrr_back")
                if not akrr.dry_run:
                    subprocess.call("cp ~/.bashrc ~/.bashrc.akrr_back", shell=True)
                bash_content_new = []
                with open(os.path.expanduser('~/.bashrc'), 'r') as f:
                    bashcontent = f.readlines()
                    in_akrr = False
                    akrr_added = False
                    for l in bashcontent:
                        if l.count(akrr_header + ' [Start]') > 0:
                            in_akrr = True
                            if not akrr_added:
                                bash_content_new += akrr_bash_content_new
                                akrr_added = True
                        if not in_akrr:
                            bash_content_new.append(l)
                        if l.count(akrr_header + ' [End]') > 0:
                            in_akrr = False
                    if not akrr_added:
                        bash_content_new += akrr_bash_content_new
            else:
                bash_content_new = akrr_bash_content_new

            if not akrr.dry_run:
                with open(os.path.expanduser('~/.bashrc'), 'w') as f:
                    for l in bash_content_new:
                        f.write(l)
                log.info("Appended AKRR records to $HOME/.bashrc")
            else:
                log.debug("New .bashrc should be like" + "\n".join(bash_content_new))
        else:
            log.info("AKRR is in standard location, no updates to $HOME/.bashrc")

    def run(self,
            akrr_db: str = default_akrr_db,
            ak_db: str = None,
            xd_db: str = None,
            install_cron_scripts: bool = True,
            stand_alone: bool = False,
            akrr_home_dir: str = None,
            generate_db_only: bool = False,
            update: bool = False,
            old_akrr_conf_dir: str = None):
        """
        Setup or update AKRR

        Parameters
        ----------
        akrr_db: if none will use localhost:3306
        ak_db: if none will use ak_db
        xd_db: if none will use xd_db
        install_cron_scripts: install cron scripts
        stand_alone: run without XDMoD
        update: update current akrr installation
        akrr_home_dir: custom location of akrr home
        generate_db_only: only generate DB
        old_akrr_conf_dir
        generate_db_only
        """
        self.old_akrr_conf = None
        if update:
            self.read_old_akrr_conf_dir(old_akrr_conf_dir)

        # Set initial db conf
        if not update:
            # if ak_db and xd_db is not set use akrr_db
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

        self.stand_alone = stand_alone
        self.install_cron_scripts_flag = install_cron_scripts

        self.akrr_home_dir = akrr_home_dir

        self.update = update
        self.old_akrr_conf_dir = old_akrr_conf_dir
        self.generate_db_only = generate_db_only

        # check
        self.check_utils()

        # get directories layout
        global _akrr_dirs, _akrr_home, _akrr_cfg
        self._initial_akrr_dirs = _akrr_dirs
        self._akrr_dirs = akrr.get_akrr_dirs(self.akrr_home_dir)
        _akrr_dirs = self._akrr_dirs
        _akrr_home = _akrr_dirs["akrr_home"]
        _akrr_cfg = _akrr_dirs["akrr_cfg"]

        # check previous installation
        self.check_previous_installation()
        # set installation directory
        self.init_dir()

        # set environment variable in case of non standard AKRR home location
        # this will be used in child processes
        if self._initial_akrr_dirs["akrr_home"] != self._akrr_dirs["akrr_home"]:
            os.environ["AKRR_HOME"] = self._akrr_dirs["akrr_home"]

        # ask info
        self.read_db_user_credentials()

        if self.install_cron_scripts_flag and not self.generate_db_only:
            self.ask_cron_email()

        # if it is dry_run
        # all question are asked, this is dry run, so nothing else to do")
        self.init_mysql_dbs()

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

        self.update_bashrc()

        log.info("AKRR is set up and is running.")
