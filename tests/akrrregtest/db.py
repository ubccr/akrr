from akrr.util.sql import get_con_to_db


def get_akrr_db(su=False, dict_cursor=True):
    """get access to db mod_akrr, su - superuser"""
    from . import cfg
    # def get_con_to_db(user,password,host='localhost',port=3306, db_name=None, dictCursor=True):
    con, cur = get_con_to_db(
        user=cfg.akrr_db_user if not su else cfg.sql_root_name,
        password=cfg.akrr_db_passwd if not su else cfg.sql_root_password,
        host=cfg.akrr_db_host,
        port=cfg.akrr_db_port,
        db_name=cfg.akrr_db_name if not su else None,
        dict_cursor=dict_cursor
    )
    return con, cur


def get_ak_db(su=False, dict_cursor=True):
    """get access to db mod_appkernel, su - superuser"""
    from . import cfg
    con, cur = get_con_to_db(
        host=cfg.ak_db_host,
        port=cfg.ak_db_port,
        user=cfg.ak_db_user if not su else cfg.sql_root_name,
        password=cfg.ak_db_passwd if not su else cfg.sql_root_password,
        db_name=cfg.ak_db_name if not su else None,
        dict_cursor=dict_cursor)
    return con, cur


def get_xd_db(su=False, dict_cursor=True):
    """get access to db xdmod.modw, su - superuser"""
    from . import cfg
    con, cur = get_con_to_db(
        host=cfg.xd_db_host,
        port=cfg.xd_db_port,
        user=cfg.xd_db_user if not su else cfg.sql_root_name,
        password=cfg.xd_db_passwd if not su else cfg.sql_root_password,
        db_name=cfg.xd_db_name if not su else None,
        dict_cursor=dict_cursor)
    return con, cur


def drop_db(db, cur, db_name, dry_run=False):
    """remove dbname database from db,cur connection"""
    from akrr.util import log
    cur.execute("SHOW databases")
    databases = cur.fetchall()
    if db_name in {v["Database"] for v in databases}:
        log.info("Removing %s database from %s ", db_name, str(db))
        msg = "SQL(%s): " % (str(db),)
        msg = msg + "DROP DATABASE IF EXISTS %s" % (db_name,)

        if dry_run:
            log.dry_run(msg)

        if dry_run:
            return

        # remove user
        cur.execute("DROP DATABASE IF EXISTS %s" % (db_name,))
        db.commit()
    else:
        log.info("Database %s is not present on %s ", db_name, str(db))
