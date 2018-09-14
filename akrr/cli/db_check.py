import os
import sys
import inspect

#modify python_path so that we can get /src on the path
import akrr.db

cur_dir=os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
if (cur_dir+"/../../src") not in sys.path:
    sys.path.append(cur_dir+"/../../src")

from akrr.util import log
import MySQLdb

def check_rw_db(connection_func, pre_msg, post_msg):
    """
    Check that the user has the correct privileges to the database
    at the end of the connection provided by 'connection_func'. Specifically, checking
    for read / write permissions ( and create table ).

    :type connection_func function
    :type pre_msg str
    :type post_msg str

    :param connection_func: the function that will provide a (connection, cursor) tuple.
    :param pre_msg:         a message to be provided to the user before the checks begin.
    :param post_msg:        a message to be provided to the user after the checks are successful
    :return: true if the database is available / the provided user has the correct privileges.
    """
    success = False
    log.info(pre_msg)

    try:
        connection, cursor = connection_func()

        try:
            with connection:
                result = cursor.execute("CREATE TABLE CREATE_ME(`id` INT NOT NULL PRIMARY KEY, `name` VARCHAR(48));")
                success = True if result == 0 else False

                if success:
                    log.info(post_msg, success)
                else:
                    log.error(post_msg, success)

        except MySQLdb.Error as e:
            log.error('Unable to create a table w/ the provided username. %s: %s', e.args[0], e.args[1])

        connection, cursor = connection_func()
        try:
            with connection:
                cursor.execute("DROP TABLE CREATE_ME;")
        except MySQLdb.Error as e:
            log.error('Unable to drop the table created to check permissions. %s: %s', e.args[0], e.args[1])

    except MySQLdb.Error as e:
        log.error('Unable to connect to Database. %s: %s', e.args[0], e.args[1])

    return success


def check_r_db(connection_func, pre_msg, post_msg):
    """
    Check that the user has the correct privileges to the database
    at the end of the connection provided by 'connection_func'.
    Specifically checking for read permissions.

    :type connection_func function
    :type pre_msg str
    :type post_msg str

    :param connection_func: the function that will provide a (connection, cursor) tuple.
    :param pre_msg:         a message to be provided to the user before the checks begin.
    :param post_msg:        a message to be provided to the user after the checks are successful
    :return: true if the database is available / the provided user has the correct privileges.
    """
    success = False
    log.info(pre_msg)

    try:
        connection, cursor = connection_func()

        try:
            with connection:
                result = cursor.execute("SELECT COUNT(*) FROM `modw`.`resourcefact`;")
                success = True if result >= 0 else False

                if success:
                    log.info(post_msg, success)
                else:
                    log.error(post_msg, success)

        except MySQLdb.Error as e:
            log.error('Unable to select from `modw`.`resourcefact`. %s: %s', e.args[0], e.args[1])

    except MySQLdb.Error as e:
        log.error('Unable to connect to Database. %s: %s', e.args[0], e.args[1])

    return success

def db_check(mod_akrr=True,mod_appkernel=True,modw=True):
    from akrr import cfg
    
    overall_success = True

    if mod_akrr:
        akrr_ok = check_rw_db(akrr.db.get_akrr_db,
                              "Checking 'mod_akrr' Database / User privileges...",
                              "'mod_akrr' Database check complete - Status: %s")
        overall_success = overall_success and akrr_ok

    if mod_appkernel:
        app_kernel_ok = check_rw_db(akrr.db.get_ak_db,
                                    "Checking 'mod_appkernel' Database / User privileges...",
                                    "'mod_appkernel' Database check complete - Status: %s")
        overall_success = overall_success and app_kernel_ok
    
    if modw:
        xdmod_ok = check_r_db(akrr.db.get_xd_db,
                              "Checking 'modw' Database / User privileges...",
                              "'modw' Database check complete - Status: %s")
        overall_success = overall_success and xdmod_ok

    # DETERMINE: whether or not everything passed.

    if overall_success:
        log.info("All Databases / User privileges check out!")
        return True
    else:
        log.error("One or more of the required databases and their required users ran into a problem. Please take note of the previous messages, correct the issue and re-run this script.")
        return False
