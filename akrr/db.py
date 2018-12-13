"""DB routines"""
import MySQLdb
import MySQLdb.cursors


def get_akrr_db(dict_cursor=False):
    """
    Get connector and cursor to mod_akrr database
    """
    from akrr.cfg import akrr_db_host, akrr_db_port, akrr_db_user, akrr_db_passwd, akrr_db_name

    if dict_cursor:
        con = MySQLdb.connect(host=akrr_db_host, port=akrr_db_port, user=akrr_db_user,
                              passwd=akrr_db_passwd, db=akrr_db_name, cursorclass=MySQLdb.cursors.DictCursor)
    else:
        con = MySQLdb.connect(host=akrr_db_host, port=akrr_db_port, user=akrr_db_user,
                              passwd=akrr_db_passwd, db=akrr_db_name)
    cur = con.cursor()
    return con, cur


def get_ak_db(dict_cursor=False):
    """
    Get connector and cursor to mod_appkernel database
    """
    from akrr.cfg import ak_db_host, ak_db_port, ak_db_user, ak_db_passwd, ak_db_name

    if dict_cursor:
        con = MySQLdb.connect(host=ak_db_host, port=ak_db_port, user=ak_db_user,
                              passwd=ak_db_passwd, db=ak_db_name, cursorclass=MySQLdb.cursors.DictCursor)
    else:
        con = MySQLdb.connect(host=ak_db_host, port=ak_db_port, user=ak_db_user,
                              passwd=ak_db_passwd, db=ak_db_name)
    cur = con.cursor()
    return con, cur


def get_xd_db(dict_cursor=False):
    """
    Get connector and cursor to modw database
    """
    from akrr.cfg import xd_db_host, xd_db_port, xd_db_user, xd_db_passwd, xd_db_name

    if xd_db_host is None:
        return None, None

    if dict_cursor:
        con = MySQLdb.connect(host=xd_db_host, port=xd_db_port, user=xd_db_user,
                              passwd=xd_db_passwd, db=xd_db_name, cursorclass=MySQLdb.cursors.DictCursor)
    else:
        con = MySQLdb.connect(host=xd_db_host, port=xd_db_port, user=xd_db_user,
                              passwd=xd_db_passwd, db=xd_db_name)
    cur = con.cursor()
    return con, cur
