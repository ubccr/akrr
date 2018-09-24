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

from akrr.util import log

from .util import get_bash

from . import cfg

# Setup empty string means default

# empty string means that when asked user accept default value
# None means that there is no expectation that this value will be asked


akrr_db_user_name = ""
akrr_db_user_password = ""
akrr_db_host = None
akrr_db_port = None
akrr_db_name = None

akrr_db_su_user_name = "root"
akrr_db_su_user_password = ""

ak_db_user_name = ""
ak_db_user_password = None
ak_db_host = None
ak_db_port = None
ak_db_name = None

ak_db_su_user_name = None
ak_db_su_user_password = None

xd_db_user_name = ""
xd_db_user_password = None
xd_db_host = None
xd_db_port = None
xd_db_name = None

xd_db_su_user_name = None
xd_db_su_user_password = None

cron_email = ""

# add fake modw database with simple resource table
add_fake_modw = False

testMismatchingPassword = False
testInvalidAdministrativeDatabaseUser = False

dry_run_flag = ""

fast_timeout = 3


def _cursor_execute(cur, query, args=None):
    from akrr.util.sql import cursor_execute
    cursor_execute(cur, query, args=args, dry_run=cfg.dry_run)


def _send_user_password(bash, expect, user, password,
                        test_mismatching_password=True):
    bash.expectSendline(expect, user, timeout=fast_timeout)

    bash.justExpect("\n")

    if password is None:
        return

    if test_mismatching_password:
        log.info("Entering not matching password")
        bash.expectSendline(
            r'.*INPUT.* Please specify a password.*\n',
            'password', timeout=fast_timeout)
        bash.expectSendline(
            r'.*INPUT.* Please reenter the password.*\n',
            'not_matching_password', timeout=fast_timeout)
        bash.justExpect(
            r'.*ERROR.* Entered passwords do not match. Please try again.', timeout=fast_timeout)
        log.info("\nEntering matching password")
    bash.expectSendline(
        r'.*INPUT.* Please specify a password.*\n',
        password, timeout=fast_timeout)
    bash.expectSendline(
        r'.*INPUT.* Please reenter the password.*\n',
        password, timeout=fast_timeout)


def _send_su_user_password(bash, user, password):
    if user is None:
        return
    # set AKRR database root user
    if testInvalidAdministrativeDatabaseUser:
        log.info("Entering invalid administrative database user")
        bash.expectSendline(
            r'.*INPUT.* Please provide an administrative database user.*\nUsername:',
            "invalid", timeout=fast_timeout)
        bash.expectSendline(
            r'.*INPUT.* Please provide the password.*\n',
            "invalid", timeout=fast_timeout)
        bash.justExpect(
            r'.*ERROR.* Entered credential is not valid. Please try again.', timeout=fast_timeout)
        log.info("\nEntering valid administrative database user")

    bash.expectSendline(
        r'.*INPUT.* Please provide an administrative database user.*\nUsername:',
        user, timeout=fast_timeout)
    bash.expectSendline(
        r'.*INPUT.* Please provide the password.*\n',
        password, timeout=fast_timeout)


def _config_setup():
    if cfg.which_akrr is None:
        log.critical("Can not find akrr. It should be in PATH or set in conf.")
        exit(1)

    # set config
    globals().update(cfg.yml["setup"])

    if cfg.dry_run:
        global dry_run_flag
        dry_run_flag = " --dry-run "


def _add_fake_modw():
    log.info("Creating minimal modw database required for AKRR functioning if needed")
    create_db = True
    create_table = True
    populate_table = True

    import MySQLdb
    from .db import get_xd_db
    con, cur = get_xd_db(su=True)

    from akrr.util.sql import db_exist

    if db_exist(cur, "modw"):
        create_db = False
        log.info("modw exists")
        try:
            cur.execute("SELECT * FROM modw.resourcefact")
            cur.fetchall()
            create_table = False
            log.info("modw.resourcefact exists")

            cur.execute("SELECT * FROM modw.resourcefact WHERE code='Alpha' OR code='Bravo'")
            rs = cur.fetchall()
            if len(rs) == 2:
                populate_table = False
                log.info("modw.resourcefact contains Alpha and Bravo")
        except MySQLdb.Error:
            log.debug2("Either modw.resourcefact  does not exist or unexpected values")

    if create_db:
        _cursor_execute(cur, "CREATE DATABASE IF NOT EXISTS modw")

    if create_table:
        _cursor_execute(cur, """
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

    if populate_table:
        _cursor_execute(
            cur,
            "INSERT INTO modw.resourcefact (" +
            "id, resourcetype_id, organization_id, name, code, description, " +
            "    start_date, start_date_ts, end_date, end_date_ts) " +
            "VALUES (10, 1, 35, 'alpha', 'Alpha', null, " +
            "    '2010-01-01 00:00:00.0', 1262322000, null, null);")
        _cursor_execute(
            cur,
            "INSERT INTO modw.resourcefact (" +
            "id, resourcetype_id, organization_id, name, code, description," +
            "    start_date, start_date_ts, end_date, end_date_ts) " +
            "VALUES (11, 1, 35, 'bravo', 'Bravo', null, " +
            "    '2010-01-01 00:00:00.0', 1262322000, null, null); ")
    con.commit()
    cur.close()
    con.close()

def setup():
    if add_fake_modw:
        _add_fake_modw()
    # start bash shell
    bash = get_bash()
    bash.output = ""
    bash.timeoutMessage = 'Unexpected behavior of prep.sh (premature EOF or TIMEOUT)'

    bash.runcmd('which python3', printOutput=True)
    bash.runcmd('which ' + cfg.which_akrr, printOutput=True)

    # start akrr setup
    bash.startcmd(cfg.which_akrr + " setup " + dry_run_flag)

    # set database user for AKRR
    _send_user_password(
        bash,
        r'Please specify a database user to access mod_akrr database.*\n\[\S+\]',
        akrr_db_user_name, akrr_db_user_password
    )
    _send_su_user_password(bash, akrr_db_su_user_name, akrr_db_su_user_password)

    # bAK database:
    _send_user_password(
        bash,
        r'Please specify a database user to access mod_appkernel database.*\n\[\S+\]',
        ak_db_user_name, ak_db_user_password
    )
    _send_su_user_password(bash, ak_db_su_user_name, ak_db_su_user_password)

    # XD database:
    _send_user_password(
        bash,
        r'Please specify the user that will be connecting to the XDMoD database.*\n\[\S+\]',
        ak_db_user_name, ak_db_user_password
    )
    _send_su_user_password(bash, ak_db_su_user_name, ak_db_su_user_password)

    bash.expectSendline(r'.*INPUT.* Please enter the e-mail where cron will send messages.*\n',
                        "" if cron_email is None else cron_email)
    # wait for prompt
    bash.justExpect(bash.prompt, timeout=60)

    log.info(bash.output)

    if bash.output.count("AKRR is set up and is running.") == 0:

        log.critical("AKRR was not set up")
        exit(1)
    else:
        log.info("AKRR is set up and is running.")
    return


def cli_add_command(parent_parser):
    """
    Setup (initial configuration) of AKRR.
    """
    parser = parent_parser.add_parser("setup", description=cli_add_command.__doc__)

    def run_it(_):
        from .util import print_important_env
        print_important_env()

        log.info("AKRR Setup")

        _config_setup()
        setup()

    parser.set_defaults(func=run_it)
