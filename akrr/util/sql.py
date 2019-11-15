"""
Various utilities for SQL database handling
"""
from akrr.util import log
from typing import Tuple, Dict, Union, Optional


class Database:
    """
    @todo should we use it?
    """
    def __init__(self,
                 user: str = None,
                 password: str = None,
                 host: str = None,
                 port: int = None,
                 database: str = None):
        self.user: Optional[str] = user
        self.password: Optional[str] = password
        self.host: Optional[str] = host
        self.port: Optional[int] = port
        self.database: Optional[str] = database


def get_user_password_host_port(user_password_host_port, default_port=3306, return_dict=False):
    """
    return user,password,host,port tuple from [user[:password]@]host[:port] format.
    user and host can not contain @ or : symbols, password can.
    port should be integer.
    """
    user = None
    password = None
    port = default_port

    if user_password_host_port.count("@"):
        user_password = user_password_host_port[:user_password_host_port.rfind("@")]
        host_port = user_password_host_port[user_password_host_port.rfind("@") + 1:]
    else:
        user_password = None
        host_port = user_password_host_port

    if user_password is not None:
        if user_password.count(":") > 0:
            user = user_password[:user_password.find(":")]
            password = user_password[user_password.find(":") + 1:]
        else:
            user = user_password

        if user == "":
            user = None

    if host_port.count(":") > 0:
        host, port = host_port.split(":")
        port = int(port)
    else:
        host = host_port

    if return_dict:
        return {
            "user": user, "password": password, "host": host, "port": port
        }

    return user, password, host, port


def get_user_password_host_port_db(user_password_host_port_db: str,
                                   default_port: int =3306,
                                   default_database: str = None,
                                   return_dict: bool = False) -> Union[Dict, Tuple]:
    """
    return user,password,host,port,db tuple from [user[:password]@]host[:port][:/database] format.
    user and host can not contain @ or : symbols, password can.
    port should be integer.
    """
    if user_password_host_port_db.count("@"):
        user_password = user_password_host_port_db[:user_password_host_port_db.rfind("@")]
        host_port_db = user_password_host_port_db[user_password_host_port_db.rfind("@") + 1:]
    else:
        user_password = None
        host_port_db = user_password_host_port_db

    if user_password is not None:
        if user_password.count(":") > 0:
            user = user_password[:user_password.find(":")]
            password = user_password[user_password.find(":") + 1:]
        else:
            user = user_password
            password = None

        if user == "":
            user = None
    else:
        user = None
        password = None

    if host_port_db.count(":/") > 0:
        host_port = host_port_db[:host_port_db.rfind(":/")]
        db = host_port_db[host_port_db.rfind(":/") + 2:]
    else:
        host_port = host_port_db
        db = default_database

    if host_port.count(":") > 0:
        host, port = host_port.split(":")
        port = int(port)
    else:
        host = host_port
        port = default_port

    if return_dict:
        return {
            "user": user, "password": password, "host": host, "port": port, "database": db
        }

    return user, password, host, port, db


def set_user_password_host_port_db(user, password, host, port, db):
    """
        return [user[:password]@]host[:port][:/database] format.
    """
    user_password_host_port_db = host
    if port is not None:
        user_password_host_port_db += ":"+str(port)
    if db is not None:
        user_password_host_port_db += ":/" + str(db)
    if user is not None or password is not None:
        user_password_host_port_db = "@" + user_password_host_port_db
        if password is not None:
            user_password_host_port_db = ":" + str(password) + user_password_host_port_db
        if user is not None:
            user_password_host_port_db = str(user) + user_password_host_port_db
    return user_password_host_port_db


def get_con_to_db(user: str, password: str, host: str = 'localhost', port: int = 3306, db_name: str = None,
                  dict_cursor: bool = True, raise_exception: bool = True):
    import MySQLdb.cursors

    kwarg = {
        "host": host,
        "port": port,
        "user": user,
        "passwd": password
    }
    if db_name is not None:
        kwarg["db"] = db_name
    if dict_cursor:
        kwarg["cursorclass"] = MySQLdb.cursors.DictCursor

    try:
        con = MySQLdb.connect(**kwarg)
        cur = con.cursor()
    except MySQLdb.Error as e:
        if raise_exception:
            raise e
        else:
            return None, None

    return con, cur


def get_con_to_db2(user_password_host_port_db, dict_cursor=True, raise_exception=True):
    user, password, host, port, db_name = get_user_password_host_port_db(user_password_host_port_db)
    return get_con_to_db(user, password, host=host, port=port, db_name=db_name, dict_cursor=dict_cursor,
                         raise_exception=raise_exception)


def db_exist(cur, name):
    """return True if db exists"""
    cur.execute("SHOW databases LIKE %s", (name,))
    r = cur.fetchall()
    return len(r) > 0


def _db_check_priv__identify_priv(db_to_check, priv_to_check, priv_list):
    """
    internal function for db_check_priv,
    check that priv_to_check (ALL or SELECT) are set for db_to_check database in priv_list
    returned by SHOW GRANTS query
    """
    import re
    for priv_entry in priv_list:
        m = re.match(r"GRANT (.+) ON (\S+) TO ", priv_entry)
        if m:
            priv = m.group(1)
            db_table = m.group(2)
            db = db_table[:db_table.find(".")].strip("\"'`")
            table = db_table[db_table.find(".") + 1:].strip("\"'`")

            if table == "*" and (db == "*" or db == db_to_check):
                if priv_to_check[:3] == "ALL" and priv[:3] == "ALL":
                    return True
                if priv_to_check == "SELECT":
                    if priv[:3] == "ALL":
                        return True
                    if priv == "SELECT":
                        return True
    return False


def get_db_client_host(cur):
    cur.execute("SELECT USER() as user")
    client_host = cur.fetchall()[0]['user'].split("@")[1]
    return client_host


def db_check_priv(cur, db_to_check, priv_to_check, user=None, host=None):
    """
    Checking that user has priveleges on database, so far can only do 
    "ALL [PRIVILEGES]" and SELECT
    """

    cur.execute("SHOW databases LIKE %s", (db_to_check,))
    rs = cur.fetchall()
    db_exists = len(rs) > 0

    if user is not None:
        if host is None:
            cur.execute("SELECT USER() as user")
            host = cur.fetchall()[0]['user'].split("@")[1]
        cur.execute("SHOW GRANTS FOR %s@%s", (user, host))
    else:
        cur.execute("SHOW GRANTS FOR CURRENT_USER()")

    priv_list = [x[tuple(x.keys())[0]] for x in cur.fetchall()]

    priv_correct = _db_check_priv__identify_priv(db_to_check, priv_to_check, priv_list)

    if priv_to_check == "SELECT":
        if db_exists:
            return priv_correct

        return False

    if priv_to_check[:3] == "ALL":
        if db_exists:
            return priv_correct

        return _db_check_priv__identify_priv("*", priv_to_check, priv_list)

    raise Exception("Can not handle this type of previlege:{}".format(priv_to_check))


def cv(value):
    """check that value do not has escapes and other potentially harm"""
    if value.count(";") or value.count("'") or value.count('"') or value.count('`') > 0:
        raise Exception("Bad value")
    return value


def cursor_execute(cur, query, args=None, dry_run=False):
    """Execute database affecting command if not in dry run mode"""
    if log.verbose or dry_run:
        if args is not None:
            if isinstance(args, dict):
                args_filled = dict((key, cur.connection.literal(item)) for key, item in args.items())
            else:
                args_filled = tuple(map(cur.connection.literal, args))
            query_filled = query % args_filled
        else:
            query_filled = query
        if dry_run:
            log.dry_run("SQL: " + query_filled)
        else:
            log.debug("SQL: " + query_filled)
    if not dry_run:
        cur.execute(query, args)


def create_user_if_not_exists(con, cur, user, password, client_host, dry_run=False):
    """Older mysql servers don't support create user if not exists directly"""
    cur.execute("SELECT * FROM mysql.user WHERE User=%s AND Host=%s", (user, client_host))
    if len(cur.fetchall()) == 0:
        # Older version of MySQL do not support CREATE USER IF NOT EXISTS
        # so need to do checking
        if password == "":
            cursor_execute(cur, "CREATE USER %s@%s", (user, client_host), dry_run=dry_run)
            con.commit()
        else:
            cursor_execute(cur, "CREATE USER %s@%s IDENTIFIED BY %s", (user, client_host, password), dry_run=dry_run)
            con.commit()


def drop_user_if_exists(cur, user, client_host, dry_run=False):
    """Older mysql servers don't support drop user if exists directly"""
    cur.execute("SELECT * FROM mysql.user WHERE User=%s AND Host=%s", (user, client_host))
    if len(cur.fetchall()) > 0:
        cursor_execute(
            cur, "DROP USER %s@%s", (user, client_host), dry_run=dry_run)
