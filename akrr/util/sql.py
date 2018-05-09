"""Various utilities for SQL database handling"""


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


def get_con_to_db(user, password, host='localhost', port=3306, db_name=None, dict_cursor=True, raise_exception=True):
    import MySQLdb
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
    if not dry_run:
        cur.execute(query, args)
    else:
        from akrr import log
        if args is not None:
            if isinstance(args, dict):
                args = dict((key, cur.connection.literal(item)) for key, item in args.items())
            else:
                args = tuple(map(cur.connection.literal, args))
            query = query % args

        log.dry_run("SQL: " + query)


def create_user_if_not_exists(cur, user, password, client_host, dry_run=False):
    """Older mysql servers don't support create user if not exists directly"""
    cur.execute("SELECT * FROM mysql.user WHERE User=%s AND Host=%s", (user, client_host))
    if len(cur.fetchall()) == 0:
        # Older version of MySQL do not support CREATE USER IF NOT EXISTS
        # so need to do checking
        if password == "":
            cursor_execute(
                cur, "CREATE USER %s@%s", (user, client_host), dry_run=dry_run)
        else:
            cursor_execute(
                cur, "CREATE USER %s@%s IDENTIFIED BY %s", (user, client_host, password), dry_run=dry_run)


def drop_user_if_exists(cur, user, client_host, dry_run=False):
    """Older mysql servers don't support drop user if exists directly"""
    cur.execute("SELECT * FROM mysql.user WHERE User=%s AND Host=%s", (user, client_host))
    if len(cur.fetchall()) > 0:
        cursor_execute(
            cur, "DROP USER %s@%s", (user, client_host), dry_run=dry_run)
