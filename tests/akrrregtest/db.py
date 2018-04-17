

from akrr.util.sql import get_con_to_db


def get_akrr_db(su=False,dictCursor=True):
    "get access to db mod_akrr, su - superuser"
    from . import cfg
    #def get_con_to_db(user,password,host='localhost',port=3306, db_name=None, dictCursor=True):
    db,cur=get_con_to_db(
        user   = cfg.akrr_db_user   if not su else cfg.sql_root_name, 
        password = cfg.akrr_db_passwd if not su else cfg.sql_root_password,
        host   = cfg.akrr_db_host, 
        port   = cfg.akrr_db_port, 
        db_name     = cfg.akrr_db_name   if not su else None,
        dictCursor=dictCursor
        )
    return db,cur

def get_ak_db(su=False,dictCursor=True):
    "get access to db mod_appkernel, su - superuser"
    from . import cfg
    db,cur=get_con_to_db(
        host   = cfg.ak_db_host, 
        port   = cfg.ak_db_port, 
        user   = cfg.ak_db_user   if not su else cfg.sql_root_name, 
        password = cfg.ak_db_passwd if not su else cfg.sql_root_password, 
        db_name     = cfg.ak_db_name   if not su else None,
        dictCursor=dictCursor)
    return db,cur

def get_xd_db(su=False,dictCursor=True):
    "get access to db xdmod.modw, su - superuser"
    from . import cfg
    db,cur=get_con_to_db(
        host   = cfg.xd_db_host, 
        port   = cfg.xd_db_port, 
        user   = cfg.xd_db_user   if not su else cfg.sql_root_name, 
        password = cfg.xd_db_passwd if not su else cfg.sql_root_password, 
        db_name     = cfg.xd_db_name if not su else None,
        dictCursor=dictCursor)
    return db,cur

def drop_db(db,cur,dbname,dry_run=False):
    "remove dbname database from db,cur connection"
    from . import log
    cur.execute("SHOW databases")
    databases=cur.fetchall()
    if dbname in {v["Database"] for v in databases}:
        log.info("Removing %s database from %s ",dbname,str(db))
        msg="SQL(%s): "%(str(db),)
        msg=msg+"DROP DATABASE IF EXISTS %s"%(dbname,)
        
        if dry_run:log.dry_run(msg)
                    
        if dry_run: return
        
        #remove user
        cur.execute("DROP DATABASE IF EXISTS %s"%(dbname,))
        db.commit()
    else:
        log.info("Database %s is not present on %s ",dbname,str(db))
        