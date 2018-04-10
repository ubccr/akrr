
def get_db(dictCursor=True,user=None,passwd=None,host='localhost',port=3306,db='mod_akrr'):
    import MySQLdb
    import MySQLdb.cursors
    if dictCursor:
        db = MySQLdb.connect(host=host, port=port, user=user,
                             passwd=passwd, db=db,
                             cursorclass=MySQLdb.cursors.DictCursor)
    else:
        db = MySQLdb.connect(host=host, port=port, user=user,
                             passwd=passwd, db=db)
    cur = db.cursor()
    return db, cur

def get_akrr_db(dictCursor=True,su=False):
    "get access to db mod_akrr, su - superuser"
    from . import cfg
    db,cur=get_db(
        dictCursor=dictCursor,
        host   = cfg.akrr_db_host, 
        port   = cfg.akrr_db_port, 
        user   = cfg.akrr_db_user   if not su else cfg.sql_root_name, 
        passwd = cfg.akrr_db_passwd if not su else cfg.sql_root_password, 
        db     = cfg.akrr_db_name   if not su else "mysql")
    return db,cur

def get_ak_db(dictCursor=True,su=False):
    "get access to db mod_appkernel, su - superuser"
    from . import cfg
    db,cur=get_db(
        dictCursor=dictCursor,
        host   = cfg.ak_db_host, 
        port   = cfg.ak_db_port, 
        user   = cfg.ak_db_user   if not su else cfg.sql_root_name, 
        passwd = cfg.ak_db_passwd if not su else cfg.sql_root_password, 
        db     = cfg.ak_db_name   if not su else "mysql")
    return db,cur

def get_xd_db(dictCursor=True,su=False):
    "get access to db xdmod.modw, su - superuser"
    from . import cfg
    db,cur=get_db(
        dictCursor=dictCursor,
        host   = cfg.xd_db_host, 
        port   = cfg.xd_db_port, 
        user   = cfg.xd_db_user   if not su else cfg.sql_root_name, 
        passwd = cfg.xd_db_passwd if not su else cfg.sql_root_password, 
        db     = cfg.xd_db_name if not su else "mysql")
    return db,cur

