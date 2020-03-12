"""DB routines"""
from akrr.util.sql import get_con_to_db


def get_akrr_db(dict_cursor=False):
    """
    Get connector and cursor to mod_akrr database
    """
    from akrr.cfg import akrr_db_host, akrr_db_port, akrr_db_user, akrr_db_passwd, akrr_db_name

    return get_con_to_db(
        user=akrr_db_user, password=akrr_db_passwd, host=akrr_db_host, port=akrr_db_port,
        db_name=akrr_db_name, dict_cursor=dict_cursor)


def get_ak_db(dict_cursor=False):
    """
    Get connector and cursor to mod_appkernel database
    """
    from akrr.cfg import ak_db_host, ak_db_port, ak_db_user, ak_db_passwd, ak_db_name

    return get_con_to_db(
        user=ak_db_user, password=ak_db_passwd, host=ak_db_host, port=ak_db_port,
        db_name=ak_db_name, dict_cursor=dict_cursor)


def get_xd_db(dict_cursor=False):
    """
    Get connector and cursor to modw database
    """
    from akrr.cfg import xd_db_host, xd_db_port, xd_db_user, xd_db_passwd, xd_db_name

    if xd_db_host is None:
        return None, None

    return get_con_to_db(
        user=xd_db_user, password=xd_db_passwd, host=xd_db_host, port=xd_db_port,
        db_name=xd_db_name, dict_cursor=dict_cursor)
