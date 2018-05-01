import os
import sys
import subprocess
import shutil

from akrr import log

from . import cfg

from .cfg import dry_run

from .db import get_akrr_db, get_ak_db, get_xd_db, drop_db


def _get_akrr_pids():
    akrr_daemon_pids = []

    try:
        output = subprocess.check_output(
            """ ps --no-headers -U $USER -o "uname,pid,ppid,cmd"|grep -P 'akrr daemon'|grep -v "grep" """,
            shell=True)

        for l in output.splitlines():
            akrr_daemon_pids.append(l.decode("utf-8").split()[1])
    except subprocess.CalledProcessError:
        pass
    if len(akrr_daemon_pids) > 0:
        return akrr_daemon_pids
    else:
        return None


def _stop_akrr():
    akrr_daemon_pids = _get_akrr_pids()
    if akrr_daemon_pids is None:
        log.info("AKRR daemon is not running.")
        return

    log.info("AKRR daemon is running, trying to stop it.")

    try:
        if os.path.exists(os.path.join(cfg.which_akrr)):
            cmd = "{} {} daemon stop".format(sys.executable, cfg.which_akrr)
            if not dry_run:
                subprocess.check_output(
                    cmd, shell=True, timeout=60)
            else:
                log.dry_run("should execute: " + cmd)
    except subprocess.CalledProcessError:
        pass

    akrr_daemon_pids = _get_akrr_pids()
    if akrr_daemon_pids is None:
        return

    try:
        for pid in akrr_daemon_pids:
            cmd = "kill -9 {}".format(pid)
            if not dry_run:
                subprocess.check_output(
                    cmd, shell=True, timeout=60)
            else:
                log.dry_run("should execute: " + cmd)
    except subprocess.CalledProcessError:
        pass

    akrr_daemon_pids = _get_akrr_pids()
    if akrr_daemon_pids is None:
        return

    if dry_run:
        log.dry_run("at this point AKRR daemon should be stopped")
        return

    raise Exception("was not able to stop AKRR daemon")


def _remove_user():
    """remove user from dbs"""
    dbs = get_akrr_db(su=True), get_ak_db(su=True), get_xd_db(su=True)
    users = cfg.akrr_db_user, cfg.ak_db_user, cfg.xd_db_user

    for user, (db, cur) in zip(users, dbs):
        # see if user exists
        cur.execute("SELECT * FROM mysql.user WHERE user = %s", (user,))

        records = cur.fetchall()

        for rec in records:
            log.info("Removing %s@%s from %s ", rec["User"], rec["Host"], str(db))
            msg = "DRY RUN:\n" if dry_run else ""
            msg = msg + "SQL(%s): " % (str(db),)
            msg = msg + "DROP USER %s@%s" % (rec["User"], rec["Host"])

            if dry_run:
                log.info(msg)
            else:
                log.dry_run(msg)

            if dry_run:
                continue

            # remove user
            cur.execute("DROP USER %s@%s", (rec["User"], rec["Host"]))
            db.commit()
        if len(records) == 0:
            log.info("There is no user with name %s on %s ", user, str(db))
    for db, cur in dbs:
        cur.close()
        db.close()


def _remove_akrr_db():
    """remove mod_akrr"""
    drop_db(*get_akrr_db(su=True), db_name=cfg.akrr_db_name, dry_run=dry_run)


def _remove_ak_db():
    """remove mod_appkernel"""
    drop_db(*get_ak_db(su=True), db_name=cfg.ak_db_name, dry_run=dry_run)


def _remove_modw_db():
    """remove mod_appkernel"""
    drop_db(*get_xd_db(su=True), db_name=cfg.xd_db_name, dry_run=dry_run)


def _remove_dir(path):
    if os.path.exists(path):
        log.info("Deleting " + path)
        if not dry_run:
            shutil.rmtree(path)
    else:
        log.info("Directory " + path + " doesn't exists.")


def _remove_conf_dir():
    """remove mod_appkernel"""
    if cfg.akrr_conf_dir is None:
        log.warning("akrr_conf_dir is None")
        return
    _remove_dir(cfg.akrr_conf_dir)


def _remove_log_dir():
    """remove mod_appkernel"""
    if cfg.akrr_log_dir is None:
        log.warning("akrr_log_dir is None")
        return
    _remove_dir(cfg.akrr_log_dir)


def _remove_from_bashrc():
    """remove from bashrc"""
    bashrc = os.path.expanduser('~/.bashrc')
    if not os.path.exists(bashrc):
        log.info("~/.bashrc file doesn't exists.")
        return

    any_akrr_section = False

    for akrrHeader in ['#AKRR Enviromental Varables', '#AKRR Server Environment Variables']:
        akrr_present = False
        with open(os.path.expanduser('~/.bashrc'), 'r') as f:
            bashrc_content = f.readlines()
            for l in bashrc_content:
                if l.count(akrrHeader + ' [Start]') > 0:
                    akrr_present = True
        if akrr_present:
            any_akrr_section = True
            log.info("AKRR Section present in ~/.bashrc. Cleaning ~/.bashrc.")
            if not dry_run:
                with open(os.path.expanduser('~/.bashrc'), 'w') as f:
                    in_akrr = False
                    for l in bashrc_content:
                        if l.count(akrrHeader + ' [Start]') > 0:
                            in_akrr = True
                        if not in_akrr:
                            f.write(l)
                        if l.count(akrrHeader + ' [End]') > 0:
                            in_akrr = False
    if not any_akrr_section:
        log.info("AKRR Section doesn't present in ~/.bashrc.")


def _remove_from_crontab(remove_mailto=False):
    """remove from cron"""

    try:

        crontab_content = subprocess.check_output("crontab -l", shell=True)
    except subprocess.CalledProcessError:
        log.error("Can not run crontab -l")
        return

    new_crontab = False
    crontab_content = crontab_content.decode("utf-8").splitlines(True)

    with open(os.path.expanduser('.crontmp'), 'w') as f:
        for l in crontab_content:
            not_akrr = True
            if l.count('akrr') > 0 and (l.count('checknrestart.sh') > 0 or l.count('restart.sh') > 0):
                not_akrr = False
            if remove_mailto and l.count('MAILTO') > 0:
                not_akrr = False
            if not_akrr:
                f.write(l)
            else:
                new_crontab = True
    if new_crontab:
        log.info("AKRR Section present in crontab. Cleaning crontab.")
        try:
            if not dry_run:
                output = subprocess.check_output("crontab .crontmp", shell=True).decode("utf-8")
                log.debug(output)
            else:
                log.info("DRY RUN: should run `crontab .crontmp`. .crontmp:" + open(".crontmp", "rt").read())
        except subprocess.CalledProcessError:
            log.error("Can not run crontab .crontmp")
        os.remove(".crontmp")
    else:
        log.info("There was no AKRR records detected in crontab list")


def remove(
        db_akrr=False, db_appkernel=False, db_modw=False, db_user=False,
        conf_dir=False, log_dir=False,
        bashrc=False,
        crontab=False, crontab_remove_mailto=False,
        **kwargs):
    log.debug(
        "Removal options for removal:\n"
        "    db_akrr: {}\n"
        "    db_appkernel: {}\n"
        "    db_modw: {}\n"
        "    db_user: {}\n"
        "    conf_dir: {}\n"
        "    log_dir: {}\n"
        "    bashrc: {}\n"
        "    crontab: {} , crontab_remove_mailto: {}\n"
        "".format(
            db_akrr, db_appkernel, db_modw, db_user, conf_dir, log_dir, bashrc, crontab, crontab_remove_mailto)
    )
    _stop_akrr()

    log.debug2("Unused keyword arguments: {}".format(kwargs))

    if db_user:
        _remove_user()
    if db_akrr:
        _remove_akrr_db()
    if db_appkernel:
        _remove_ak_db()
    if db_modw:
        _remove_modw_db()
    if conf_dir:
        _remove_conf_dir()
    if log_dir:
        _remove_log_dir()
    if bashrc:
        _remove_from_bashrc()
    if crontab:
        _remove_from_crontab(crontab_remove_mailto)


def cli_add_command(parent_parser):
    """remove AKRR installation"""
    parser = parent_parser.add_parser("remove", description=cli_add_command.__doc__)

    parser.add_argument("-a", "--all", action="store_true", help="remove everything except sources and modw")
    parser.add_argument("--db-all", action="store_true", help="remove from DB all AKRR related entities (except modw).")
    parser.add_argument("--db-akrr", action="store_true", help="remove from DB mod_akrr")
    parser.add_argument("--db-appkernel", action="store_true", help="remove from DB mod_appkernel")
    parser.add_argument("--db-user", action="store_true", help="remove user from DBs.")
    parser.add_argument("--db-modw", action="store_true", help="remove from DB modw")
    parser.add_argument("--conf-dir", action="store_true", help="remove conf directory")
    parser.add_argument("--log-dir", action="store_true", help="remove log directory")
    parser.add_argument("--bashrc", action="store_true", help="remove akrr from bashrc")
    parser.add_argument("--crontab", action="store_true", help="remove akrr from crontab")
    parser.add_argument("--crontab-remove-mailto", action="store_true", help="remove mail to from crontab records")

    def run_it(args):
        if args.db_all:
            args.db_akrr = True
            args.db_appkernel = True
            args.db_user = True
        if args.all:
            args.db_akrr = True
            args.db_appkernel = True
            args.db_user = True
            args.conf_dir = True
            args.log_dir = True
            args.bashrc = True
            args.crontab = True
            args.crontab_remove_mailto = True

        kwarg = vars(args)
        # remove not needed keys
        kwarg.pop("func")
        kwarg.pop("cfg")
        kwarg.pop("dry_run")
        kwarg.pop("verbose")

        kwarg.pop("db_all")
        kwarg.pop("all")

        from .util import print_important_env
        print_important_env()

        remove(**kwarg)

    parser.set_defaults(func=run_it)
