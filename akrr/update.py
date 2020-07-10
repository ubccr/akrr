"""
Routings for AKRR update
"""
import datetime
import os
import copy
import re
import shutil
import subprocess
import pickle
import pprint
from collections import OrderedDict
from typing import Optional, Tuple
import tarfile

import akrr
from akrr.util import log
from akrr.util.sql import get_con_to_db2, cursor_execute
from akrr.akrrerror import AkrrValueException, AkrrFileNotFoundError, AkrrException
from akrr.util.sql import get_con_to_db, cursor_execute
from akrr.util import exec_files_to_dict, make_dirs
from akrr.cli.generate_tables import create_and_populate_tables, mod_akrr_create_tables_dict, \
    mod_appkernel_create_tables_dict, populate_mod_akrr_appkernels
from akrr.archive import Archive


def mod_akrr_db_compare(db_src, db_dest):
    """
    Compare mod_akrr databases
    """
    log.info("db 1: " + db_src)
    log.info("db 2: " + db_dest)
    con1, cur1 = get_con_to_db2(db_src)
    con2, cur2 = get_con_to_db2(db_dest)

    cur1.execute("show tables;")
    tables1 = [list(r.values())[0] for r in cur1.fetchall()]

    cur2.execute("show tables;")
    tables2 = [list(r.values())[0] for r in cur2.fetchall()]

    tables_all = copy.copy(tables1)
    for v in tables2:
        if v not in tables_all:
            tables_all.append(v)

    tables_common = []
    for v in tables_all:
        if (v in tables1) and (v in tables2):
            tables_common.append(v)

    log.empty_line()
    message = "Table presence\n"
    message += "%30s %10s %10s" % ("Table Name", "in tables1", "in tables2")
    for a in tables_all:
        message += "%30s %10s %10s\n" % (a, str(a in tables1), str(a in tables2))

    if len(tables_all) != len(tables_common):
        log.error("Table list is different")
    else:
        log.info("Table list is same")
    if log.verbose or len(tables_all) != len(tables_common):
        print(message)

    log.empty_line()
    log.info("Comparing tables schemas")
    all_tables_are_same = True
    for table_name in tables_common:
        log.debug("Checking table: " + table_name)
        cur1.execute("describe %s;" % table_name)
        rows = cur1.fetchall()
        table1 = {k: [dic[k] for dic in rows] for k in rows[0]}

        cur2.execute("describe %s;" % table_name)
        rows = cur2.fetchall()
        table2 = {k: [dic[k] for dic in rows] for k in rows[0]}

        fields_all = copy.copy(table1['Field'])
        for v in table2['Field']:
            if v not in fields_all:
                fields_all.append(v)

        table_is_same = True
        # {'Field': 'task_id', 'Type': 'int(11)', 'Null': 'YES', 'Key': 'UNI', 'Default': None, 'Extra': ''}
        message = "Columns in tables\n"
        message += "%30s %10s %10s %10s %20s %20s\n" % (
            "Table Name", "same", "in tables1", "in tables2", "type1", "type2")
        for field in fields_all:
            in_table1 = field in table1['Field']
            in_table2 = field in table2['Field']
            if in_table1:
                i1 = table1['Field'].index(field)
                type1 = table1['Type'][i1]
            else:
                i1 = "None"
                type1 = "None"

            if in_table2:
                i2 = table2['Field'].index(field)
                type2 = table2['Type'][i2]
            else:
                i2 = "None"
                type2 = "None"

            is_same = in_table1 and in_table2
            if is_same:
                is_same = i1 == i2
                if is_same:
                    is_same = type1 == type2
            if not is_same:
                table_is_same = False
                all_tables_are_same = False

            message += "%30s %10s %10s %10s %20s %20s\n" % (field, is_same, str(i1), str(i2), type1, type2)
        if log.verbose or table_is_same is False:
            if table_is_same is False:
                log.error(table_name + " has different schema")
            print(message)
    if all_tables_are_same:
        log.info("All tables schemas are same")
    else:
        log.error("Some tables schemas are not same")


ak_rename = {
    'xdmod.app.chem.gamess.core': 'gamess.core',
    'xdmod.app.chem.nwchem.core': 'nwchem.core',
    'xdmod.app.climate.cesm.core': 'cesm.core',
    'xdmod.app.climate.wrf.core': 'wrf.core',
    'xdmod.app.md.amber.core': 'amber.core',
    'xdmod.app.md.charmm.core': 'charmm.core',
    'xdmod.app.md.cpmd.core': 'cpmd.core',
    'xdmod.app.md.lammps.core': 'lammps.core',
    'xdmod.app.md.namd-gpu.core': 'namd-gpu.core',
    'xdmod.app.md.namd.core': 'namd.core',
    'xdmod.app.phys.quantum_espresso.core': 'quantum_espresso.core',
    'xdmod.benchmark.gpu.shoc.core': 'shoc.core',
    'xdmod.benchmark.graph.graph500.core': 'graph500.core',
    'xdmod.benchmark.hpcc.core': 'hpcc.core',
    'xdmod.benchmark.io.ior.core': 'ior.core',
    'xdmod.benchmark.io.mpi-tile-io.core': 'mpi-tile-io.core',
    'xdmod.benchmark.mpi.omb.core': 'omb.core',
    'xdmod.benchmark.npb.core': 'npb.core',
    'xdmod.benchmark.osjitter.core': 'osjitter.core',
    'xdmod.bundle.core': 'bundle.core',
    'xdmod.app.astro.enzo': 'enzo',
    'xdmod.app.chem.gamess': 'gamess',
    'xdmod.app.chem.nwchem': 'nwchem',
    'xdmod.app.md.namd': 'namd',
    'xdmod.benchmark.graph.graph500': 'graph500',
    'xdmod.benchmark.hpcc': 'hpcc',
    'xdmod.benchmark.io.ior': 'ior',
    'xdmod.benchmark.io.mdtest': 'mdtest',
    'xdmod.benchmark.io.mpi-tile-io': 'mpi-tile-io',
    'xdmod.benchmark.mpi.imb': 'imb',
    'xdmod.app.astro.enzo.node': 'enzo',
    'xdmod.app.chem.gamess.node': 'gamess',
    'xdmod.app.chem.nwchem.node': 'nwchem',
    'xdmod.app.climate.cesm': 'cesm',
    'xdmod.app.climate.wrf': 'wrf',
    'xdmod.app.md.amber': 'amber',
    'xdmod.app.md.charmm': 'charmm',
    'xdmod.app.md.cpmd': 'cpmd',
    'xdmod.app.md.lammps': 'lammps',
    'xdmod.app.md.namd-gpu': 'namd-gpu',
    'xdmod.app.md.namd.node': 'namd',
    'xdmod.app.md.namd2': 'namd2',
    'xdmod.app.phys.quantum_espresso': 'quantum_espresso',
    'xdmod.benchmark.gpu.shoc': 'shoc',
    'xdmod.benchmark.graph.graph500.node': 'graph500',
    'xdmod.benchmark.hpcc.node': 'hpcc',
    'xdmod.benchmark.io.ior.node': 'ior',
    'xdmod.benchmark.io.mpi-tile-io.node': 'mpi-tile-io',
    'xdmod.benchmark.mpi.omb': 'omb',
    'xdmod.benchmark.npb': 'npb',
    'xdmod.benchmark.osjitter': 'osjitter',
    'xdmod.bundle': 'bundle',
    'xdmod.appker.densela.blas': 'densela.blas',
    'xdmod.benchmark.hpcg': 'hpcg',
    'xdmod.benchmark.mem.stream.core': 'stream.core'
}


def rename_appkernels_mod_akrr(mod_akrr: str, dry_run: bool = False) -> None:
    """
    Rename appkernels from long to short format in mod_akrr db
    """
    update_akrr_xdmod_instanceinfo = True
    update_completed_tasks = True
    update_app_kernels = True
    update_app_kernels_list = True
    update_scheduled_tasks = True

    con_akrr, cur_akrr = get_con_to_db2(mod_akrr)

    if update_akrr_xdmod_instanceinfo:
        log.info("Updating akrr_xdmod_instanceinfo")
        for old, new in ak_rename.items():
            log.debug("update akrr_xdmod_instanceinfo: %s -> %s" % (new, old))
            cursor_execute(
                cur_akrr,
                "update akrr_xdmod_instanceinfo set reporter=%s where reporter=%s",
                (new, old), dry_run)
        if not dry_run:
            con_akrr.commit()
        cursor_execute(
            cur_akrr,
            "update akrr_xdmod_instanceinfo "
            "set reporternickname=CONCAT(reporter,'.',REGEXP_SUBSTR(reporternickname,'[0-9]+$'))",
            None, dry_run)
        if not dry_run:
            con_akrr.commit()

    if update_completed_tasks:
        log.info("Updating completed_tasks")
        for old, new in ak_rename.items():
            log.debug("update completed_tasks: %s -> %s" % (new, old))
            cursor_execute(
                cur_akrr,
                "update completed_tasks set app=%s where app=%s", (new, old), dry_run)
        if not dry_run:
            con_akrr.commit()

        cursor_execute(
            cur_akrr,
            "update completed_tasks set app=CONCAT(app,'.core') where resource_param like '%ncpus%'",
            None, dry_run)
        if not dry_run:
            con_akrr.commit()

    if update_app_kernels:
        log.info("Updating app_kernels")
        for old, new in ak_rename.items():
            log.debug("update app_kernels: %s -> %s" % (new, old))
            cursor_execute(
                cur_akrr,
                "update app_kernels set name=%s where name=%s", (new, old), dry_run)
        if not dry_run:
            con_akrr.commit()

    if update_app_kernels_list:
        log.info("Updating app_kernels list")
        from akrr.cli.generate_tables import populate_mod_akrr_appkernels
        populate_mod_akrr_appkernels(con_akrr, cur_akrr, dry_run)

    if update_scheduled_tasks:
        log.info("Updating scheduled_tasks")
        for old, new in ak_rename.items():
            log.debug("update scheduled_tasks: %s -> %s" % (new, old))
            cursor_execute(
                cur_akrr,
                "update scheduled_tasks set app=%s where app=%s", (new, old), dry_run)


def find_old_akrr_home_and_cfg(old_akrr_home: str = None) -> Tuple[str, str]:
    """
    Find akrr home and cfg file; check that they exist.
    Raises error if they do not exist.
    Return home and cfg paths
    """
    if old_akrr_home is None:
        if "AKRR_HOME" in os.environ:
            old_akrr_home = os.environ["AKRR_HOME"]
            log.debug2("Found AKRR home in %s", old_akrr_home)

    if old_akrr_home:
        old_akrr_home = os.path.abspath(os.path.expanduser(old_akrr_home))

    if old_akrr_home is None:
        msg = "Can not find old AKRR home directory specify AKRR_HOME environment variables"
        log.error(msg)
        raise AkrrValueException(msg)
    if not os.path.isdir(old_akrr_home):
        msg = "AKRR home is not found (%s is not directory or do not exists)" % old_akrr_home
        log.error(msg)
        raise AkrrFileNotFoundError(msg)

    # locate config
    old_akrr_cfg_file1 = os.path.join(old_akrr_home, "cfg", "akrr.inp.py")
    old_akrr_cfg_file2 = os.path.join(old_akrr_home, "etc", "akrr.conf")
    if os.path.isfile(old_akrr_cfg_file2):
        old_akrr_cfg_file = old_akrr_cfg_file2
    elif os.path.isfile(old_akrr_cfg_file1):
        old_akrr_cfg_file = old_akrr_cfg_file1
    else:
        msg = "AKRR config file not found (was looking for %s or %s" % (old_akrr_cfg_file2, old_akrr_cfg_file1)
        log.error(msg)
        raise AkrrFileNotFoundError(msg)

    log.debug2("Found AKRR config is %s", old_akrr_cfg_file)

    return old_akrr_home, old_akrr_cfg_file


class UpdateAKRR:
    """
    Class for updating old AKRR
    """

    def __init__(self, old_akrr_home: str = None):
        """
        Parameters
        ----------
        old_akrr_cfg - old AKRR Config path, if None will try to locate based on environment variables
        """
        self.akrr_db = {
            "mod_akrr": {'list': {'con': None, 'cur': None}, 'dict': {'con': None, 'cur': None}},
            "mod_appkernel": {'list': {'con': None, 'cur': None}, 'dict': {'con': None, 'cur': None}},
        }
        self.task_id_max = 0  # type: int
        self.cron_email = ""  # type: str

        # find akrr home if needed
        self.old_akrr_home, self.old_akrr_cfg_file = find_old_akrr_home_and_cfg(old_akrr_home)
        self.old_akrr_cfg_dir = os.path.dirname(self.old_akrr_cfg_file)

        # read cfg
        self.old_cfg = self._read_config(self.old_akrr_cfg_file)

        # set db credential for automatic access
        self.db_cred = {
            "mod_appkernel": {
                'db_host': self.old_cfg['ak_db_host'],
                'db_name': self.old_cfg['ak_db_name'],
                'db_passwd': self.old_cfg['ak_db_passwd'],
                'db_port': self.old_cfg['ak_db_port'],
                'db_user': self.old_cfg['ak_db_user']},
            "mod_akrr": {
                'db_host': self.old_cfg['akrr_db_host'],
                'db_name': self.old_cfg['akrr_db_name'],
                'db_passwd': self.old_cfg['akrr_db_passwd'],
                'db_port': self.old_cfg['akrr_db_port'],
                'db_user': self.old_cfg['akrr_db_user']}
        }

    @staticmethod
    def _read_config(old_akrr_cfg_file: str) -> dict:
        """
        Read old AKRR config from old_akrr_cfg_file.
        """
        log.info("Reading old AKRR config from %s.", old_akrr_cfg_file)
        old_cfg = exec_files_to_dict(old_akrr_cfg_file)

        # make absolute paths from relative
        old_cfg_dir = os.path.dirname(old_akrr_cfg_file)
        if not os.path.isabs(old_cfg['data_dir']):
            old_cfg['data_dir'] = os.path.abspath(os.path.join(old_cfg_dir, old_cfg['data_dir']))
        if not os.path.isabs(old_cfg['completed_tasks_dir']):
            old_cfg['completed_tasks_dir'] = os.path.abspath(os.path.join(old_cfg_dir, old_cfg['completed_tasks_dir']))

        log.debug2("AKRR config (%s) content: \n%s", old_akrr_cfg_file, pprint.pformat(old_cfg, indent=4))
        return old_cfg

    def remove_old_akrr_from_crontab(self):
        """
        Remove old akrr checkers/re-launchers from crontab so that it would not start unexpectedly
        """
        from tempfile import mkstemp
        log.info("Removing old akrr checkers/re-launchers from crontab.")
        try:
            crontab_content = subprocess.check_output("crontab -l", shell=True)
            crontab_content = crontab_content.decode("utf-8").splitlines(False)
            log.debug2("Old crontab:\n" + "\n".join(crontab_content))
        except Exception:
            log.info("Crontab does not have user's crontab yet")
            return True

        old_akrr_home_env = os.environ['AKRR_HOME'] if 'AKRR_HOME' in os.environ else None

        crontab_content_new = []
        for crontab_line in crontab_content:
            if crontab_line == "#AKRR" or crontab_line == "##AKRR" or crontab_line == "## AKRR":
                continue
            fields = crontab_line.strip().split()
            if len(fields) > 0:
                # AKRR 1.0
                if os.path.abspath(fields[-1]) == os.path.join(self.old_akrr_home, "bin", "restart.sh"):
                    continue
                if os.path.abspath(fields[-1]) == os.path.join(self.old_akrr_home, "bin", "checknrestart.sh"):
                    continue
                if old_akrr_home_env:
                    if os.path.abspath(fields[-1]) == os.path.join(old_akrr_home_env, "bin", "restart.sh"):
                        continue
                    if os.path.abspath(fields[-1]) == os.path.join(old_akrr_home_env, "bin", "checknrestart.sh"):
                        continue
                # AKRR 2.0
                if re.search(r"akrr\s+daemon\s+(restart|checknrestart)", crontab_line):
                    continue
                if re.search(r"akrr\s+archive", crontab_line):
                    continue
            if len(crontab_line.strip()) > 6 and crontab_line.strip()[:6].upper() == 'MAILTO':
                fields = crontab_line.strip().split("=")
                self.cron_email = fields[1].strip('\'"')

            crontab_content_new.append(crontab_line)

        tmp_cronfile_fd, tmp_cronfile = mkstemp(prefix="crontmp", dir=os.path.expanduser('~'), text=True)
        if not akrr.dry_run:
            with open(tmp_cronfile_fd, 'wt') as f:
                for tmp_str in crontab_content_new:
                    f.write(tmp_str + "\n")
            subprocess.call("crontab " + tmp_cronfile, shell=True)
            os.remove(tmp_cronfile)
            log.info("Crontab updated.")
        else:
            log.dry_run("For removing old AKRR should update crontab to:\n" + "\n".join(crontab_content_new))

    def shut_down_old_akrr(self):
        """
        Shut down old AKRR
        """
        log.info("Shutting down old akrr daemon.")
        import akrr.util.daemon
        akrr_pid = akrr.util.daemon.get_daemon_pid(os.path.join(self.old_cfg['data_dir'], 'akrr.pid'),
                                                   delete_pid_file_if_daemon_down=True)
        if akrr_pid is None:
            log.info("AKRR daemon is already down.")
            return
        if akrr.dry_run:
            log.dry_run("Should stop AKRR daemon here.")
            return

        if not akrr.util.daemon.daemon_stop(akrr_pid):
            msg = "Can not stop old daemon please kill it manually!"
            log.error(msg)
            raise AkrrException(msg)

    def rename_old_akrr_home(self):
        pass

    def get_akrr_db_con(self, db_name: str, dict_cursor=False):
        cursor_type = 'dict' if dict_cursor else 'list'
        if self.akrr_db[db_name][cursor_type]['con'] is None or self.akrr_db[db_name][cursor_type]['cur'] is None:
            self.akrr_db[db_name][cursor_type]['con'], self.akrr_db[db_name][cursor_type]['cur'] = get_con_to_db(
                user=self.db_cred[db_name]["db_user"], password=self.db_cred[db_name]["db_passwd"],
                host=self.db_cred[db_name]["db_host"], port=self.db_cred[db_name]["db_port"],
                db_name=self.db_cred[db_name]["db_name"],
                dict_cursor=dict_cursor, raise_exception=True)
        return self.akrr_db[db_name][cursor_type]['con'], self.akrr_db[db_name][cursor_type]['cur']

    def get_old_akrr_db_con(self, dict_cursor=False):
        return self.get_akrr_db_con("mod_akrr", dict_cursor=dict_cursor)


def convert_appname(iapp: int, row, ireporternickname: int = None):
    is_tuple = False
    if isinstance(row, tuple):
        row = list(row)
        is_tuple = True

    if row[iapp] in ak_rename:
        row[iapp] = ak_rename[row[iapp]]

    if ireporternickname is not None:
        # xdmod.app.md.namd2.128 -> (xdmod.app.md.namd2, 128)
        m = re.match(r"^(.*)\.([0-9]+)$", row[ireporternickname])
        if m and m.group(1) in ak_rename:
            row[ireporternickname] = ak_rename[m.group(1)] + "." + m.group(2)

    if is_tuple:
        return tuple(row)
    else:
        return row


class UpdateDataBase:
    """
    Class for updating old AKRR Database 1.0 to early 2.0 to 2.0
    """
    convert_mod_akrr_db = OrderedDict((
        # active_tasks - just drop it
        (
            "ak_on_nodes",
            {
                "select_cols_old":
                    "resource_id, node_id, task_id, collected, status"
            }
        ), (
            "akrr_default_walltime_limit", {
                "name_old": "akrr_default_walllimit",
                "select_cols_old":
                    "id, resource, app, walllimit,      resource_param, app_param, last_update, comments",
                "populate_cols_new":
                    "id, resource, app, walltime_limit, resource_param, app_param, last_update, comments",
                "convert": lambda row: convert_appname(2, row)
            }
        ), (
            "akrr_errmsg", {
                "select_cols_old":
                    "task_id, err_regexp_id, appstdout, stderr, stdout, taskexeclog",
            }
        ), (
            "akrr_err_regexp", {
                "select_cols_old":
                    "id, active, resource, app, reg_exp, reg_exp_opt, source, err_msg, description",
                "convert": lambda row: convert_appname(3, row)
            }
        ), (
            "akrr_internal_failure_codes", {
                "select_cols_old":
                    "id, description",
            }
        ), (
            "akrr_resource_maintenance", {
                "select_cols_old":
                    "id, resource, start, end, comment",
            }
        ), (
            "akrr_task_errors", {
                "name_old": "akrr_taks_errors",
                "select_cols_old":
                    "task_id, err_reg_exp_id"
            }
        ), (
            "akrr_xdmod_instanceinfo", {
                "select_cols_old":
                    "instance_id, collected, committed, resource, executionhost, reporter, reporternickname,\n"
                    "status, message, stderr, body, memory, cputime, walltime, job_id, internal_failure, nodes,\n"
                    "ncores, nnodes",
                "convert": lambda row: convert_appname(5, row, ireporternickname=6)
            }
        ), (
            "completed_tasks", {
                "name_old": "COMPLETEDTASKS",
                "select_cols_old":
                    "task_id, time_finished, status, statusinfo, time_to_start, datetimestamp, time_activated,\n"
                    "time_submitted_to_queue, repeat_in, resource, app, resource_param, app_param, task_param,\n"
                    "group_id, FatalErrorsCount, FailsToSubmitToTheQueue, parent_task_id",
                "populate_cols_new":
                    "task_id, time_finished, status, status_info, time_to_start, datetime_stamp, time_activated,\n"
                    "time_submitted_to_queue, repeat_in, resource, app, resource_param, app_param, task_param,\n"
                    "group_id, fatal_errors_count, fails_to_submit_to_the_queue, parent_task_id",
                "convert": lambda row: convert_appname(10, row)
            }
        ), (
            "nodes", {
                "select_cols_old":
                    "node_id, resource_id, name",
            }
        ), (
            "scheduled_tasks", {
                "name_old": "SCHEDULEDTASKS",
                "select_cols_old":
                    "task_id, time_to_start, repeat_in, resource, app, resource_param, app_param, task_param,\n"
                    "group_id, parent_task_id",
                "convert": lambda row: convert_appname(4, row)
            }
        ), (
            "resources", {
                "select_cols_old":
                    "id, xdmod_resource_id, name, enabled",
            }
        ), (
            "app_kernels", {
                "select_cols_old":
                    "id, name, enabled, nodes_list",
                "convert": lambda row: convert_appname(1, row)
            }
        ), (
            "resource_app_kernels", {
                "select_cols_old":
                    "id, resource_id, app_kernel_id, enabled"
            }
        )
    ))
    tables_to_drop = OrderedDict((
        ("mod_akrr",
         {'tables': [
             'ACTIVETASKS', 'active_tasks', 'ak_on_nodes', 'akrr_default_walllimit', 'akrr_default_walltime_limit',
             'akrr_errmsg',
             'akrr_err_regexp', 'akrr_internal_failure_codes', 'akrr_resource_maintenance',
             'akrr_taks_errors', 'akrr_xdmod_instanceinfo', 'COMPLETEDTASKS', 'completed_tasks', 'nodes',
             'SCHEDULEDTASKS', "scheduled_tasks", 'resources', 'app_kernels', 'resource_app_kernels'],
             'views': ['akrr_erran', 'akrr_erran2', 'akrr_err_distribution_alltime']}),
        ("mod_appkernel",
         {'tables':
              ['a_data', 'a_data2', 'app_kernel_def', 'app_kernel', 'metric', 'parameter', 'resource',
               'ak_has_metric', 'ak_has_parameter', 'ak_instance', 'ak_instance_debug',
               'ak_supremme_metrics', 'a_tree', 'a_tree2', 'control_set', 'ingester_log', 'log_id_seq',
               'log_table', 'metric_attribute', 'metric_data', 'parameter_data', 'report',
               'sumpremm_metrics', 'control_region_def', 'control_regions'],
          'views': ['v_ak_metrics', 'v_ak_parameters', 'v_tree_debug']
          })
    ))

    def __init__(self, uppdate_akrr: UpdateAKRR):
        self.uppdate_akrr = uppdate_akrr

    def get_akrr_db_con(self, db_name: str, dict_cursor=False):
        return self.uppdate_akrr.get_akrr_db_con(db_name, dict_cursor=dict_cursor)

    def get_old_akrr_db_con(self, dict_cursor=False):
        return self.uppdate_akrr.get_akrr_db_con("mod_akrr", dict_cursor=dict_cursor)

    def get_old_ak_db_con(self, dict_cursor=False):
        return self.uppdate_akrr.get_akrr_db_con("mod_appkernel", dict_cursor=dict_cursor)

    def _get_table_pkl_name(self, db_name, table_name):
        """
        Get pickeled filename for table dump
        """
        return os.path.join(self.uppdate_akrr.old_cfg['data_dir'], "%s__%s.pkl" % (db_name, table_name))

    def _update_db_save_old_db(self):
        """
        Save old tables
        """
        log.info("Saving old tables ...")
        akrr_con, akrr_cur = self.get_old_akrr_db_con()
        cursor_execute(akrr_cur, "show tables")
        tables = tuple((r[0] for r in akrr_cur.fetchall()))
        nrecs = 128

        for name_new, table_info in self.convert_mod_akrr_db.items():
            if table_info["select_cols_old"] is None:
                continue

            name_old = name_new if "name_old" not in table_info else table_info['name_old']
            name_to_use = name_new if name_new in tables else name_old
            if name_to_use not in tables:
                raise akrr.akrrerror.AkrrError("Can not find table %s" % name_to_use)

            cursor_execute(akrr_cur, "show columns from %s" % name_to_use)
            columns = ",".join(tuple((r[0] for r in akrr_cur.fetchall())))
            if columns == table_info["select_cols_old"].replace(" ", "").replace("\n", ""):
                # old format
                columns = table_info["select_cols_old"]
            elif "populate_cols_new" in table_info and \
                    columns == table_info["populate_cols_new"].replace(" ", "").replace("\n", ""):
                # new format
                columns = table_info["populate_cols_new"]
            else:
                log.warning("Unknown format probably development version, will try anyway")

            log.debug("Saving: mod_akrr.%s" % name_to_use)
            cursor_execute(akrr_cur, "SELECT %s \nFROM %s" % (columns, name_to_use))

            with open(self._get_table_pkl_name("mod_akrr", name_new), "wb") as fout:
                while True:
                    rows = akrr_cur.fetchmany(nrecs)
                    if not rows:
                        break
                    pickle.dump(rows, fout)

        # find current task_id_max
        self.task_id_max = 0
        if "COMPLETEDTASKS" in tables:
            task_id_tables = ("COMPLETEDTASKS", "SCHEDULEDTASKS", "ACTIVETASKS")
        else:
            task_id_tables = ("completed_tasks", "scheduled_tasks", "active_tasks")
        for table in task_id_tables:
            print(table)
            akrr_cur.execute("SELECT max(task_id) FROM %s" % table)
            rows = akrr_cur.fetchall()
            if len(rows) > 0 and len(rows[0]) > 0 and rows[0][0] is not None:
                if rows[0][0] > self.task_id_max:
                    self.task_id_max = rows[0][0]

        # save mod_appkernel
        ak_con, ak_cur = self.get_old_ak_db_con()
        cursor_execute(ak_cur, "show tables")
        tables = tuple((r[0] for r in ak_cur.fetchall()))

        for name in self.tables_to_drop['mod_appkernel']['tables']:
            if name not in tables:
                continue
            cursor_execute(ak_cur, "show columns from %s" % name)
            columns = ",".join(tuple((r[0] for r in ak_cur.fetchall())))
            log.debug("Saving: mod_appkernel.%s" % name)
            cursor_execute(ak_cur, "SELECT %s \nFROM %s" % (columns, name))

            with open(self._get_table_pkl_name("mod_appkernel", name), "wb") as fout:
                while True:
                    rows = ak_cur.fetchmany(nrecs)
                    if not rows:
                        break
                    pickle.dump(rows, fout)
        log.info("\t\tDone")

    def _update_db_drop_old_tables(self):
        """
        drop old tables
        """
        log.info("Dropping old tables ...")
        for db_name, tables_and_views in self.tables_to_drop.items():
            con, cur = self.get_akrr_db_con(db_name)
            tables_and_views['views'].reverse()
            for name_old in tables_and_views['views']:
                log.debug("Dropping: %s.%s" % (db_name, name_old))
                if not akrr.dry_run:
                    cur.execute("DROP VIEW IF EXISTS %s" % name_old)

            tables_and_views['tables'].reverse()
            for name_old in tables_and_views['tables']:
                log.debug("Dropping: %s.%s" % (db_name, name_old))
                if not akrr.dry_run:
                    cur.execute("DROP TABLE IF EXISTS %s" % name_old)
            con.commit()
        log.info("\t\tDone")

    def _update_db_create_new(self):
        """
        create new tables
        """
        log.info("Creating new tables ...")
        akrr_con, akrr_cur = self.get_old_akrr_db_con()
        ak_con, ak_cur = self.get_old_ak_db_con()
        for con, cur, db_name, create_tables_dict in (
                (akrr_con, akrr_cur, "mod_akrr", mod_akrr_create_tables_dict),
                (ak_con, ak_cur, "mod_appkernel", mod_appkernel_create_tables_dict)):
            create_and_populate_tables(
                create_tables_dict,
                tuple(),
                "Creating %s tables/views ...",
                "%s tables and views created.",
                None, connection=con, cursor=cur,
                drop_if_needed=True, dry_run=akrr.dry_run
            )
        log.info("\t\tDone")

    def _update_db_populate_new_db(self):
        """
        Populate new tables
        """
        log.info("Populating new tables ...")
        akrr_con, akrr_cur = self.get_old_akrr_db_con()
        akrr_con_dict, akrr_cur_dict = self.get_old_akrr_db_con(dict_cursor=True)

        # scheduled_tasks
        for table_name, table_info in self.convert_mod_akrr_db.items():
            if "populate_cols_new" in table_info:
                populate_col_new = table_info["populate_cols_new"]
            else:
                populate_col_new = table_info['select_cols_old']

            values_in = ", ".join(["%s"] * (populate_col_new.count(",") + 1))
            log.debug("Populating: mod_akrr.%s" % table_name)
            with open(self._get_table_pkl_name("mod_akrr", table_name), "rb") as fin:
                while True:
                    try:
                        rows = pickle.load(fin)
                    except EOFError:
                        break
                    for row in rows:
                        if "convert" in table_info:
                            row = table_info["convert"](row)
                        if not akrr.dry_run:
                            akrr_cur.execute(
                                "INSERT INTO %s\n(%s)\nVALUES(%s)" % (table_name, populate_col_new, values_in), row)
                akrr_con.commit()

        # update auto increment
        if self.task_id_max > 0:
            cursor_execute(akrr_cur, "ALTER TABLE scheduled_tasks AUTO_INCREMENT=%s" % (self.task_id_max + 1))
            akrr_con.commit()

        # correct some values
        cursor_execute(akrr_cur,
                       "update completed_tasks set app=CONCAT(app,'.core') where resource_param like '%ncpus%'")
        akrr_con.commit()

        # add new records if needed
        populate_mod_akrr_appkernels(akrr_con_dict, akrr_cur_dict, dry_run=akrr.dry_run)

        # load mod_appkernel
        ak_con, ak_cur = self.get_old_ak_db_con()
        tables_to_load = self.tables_to_drop['mod_appkernel']['tables']
        tables_to_load.reverse()
        for table_name in tables_to_load:
            table_pkl_name = self._get_table_pkl_name("mod_appkernel", table_name)
            if not os.path.isfile(table_pkl_name):
                log.debug("Table %s was not saved (might not present in previous version)", table_name)
                continue
            log.debug("Populating: mod_appkernel.%s" % table_name)

            cursor_execute(ak_cur, "show columns from %s" % table_name)
            columns = ",".join(tuple((r[0] for r in ak_cur.fetchall())))

            values_in = ", ".join(["%s"] * (columns.count(",") + 1))

            with open(table_pkl_name, "rb") as fin:
                while True:
                    try:
                        rows = pickle.load(fin)
                    except EOFError:
                        break
                    for row in rows:
                        if not akrr.dry_run:
                            ak_cur.execute(
                                "INSERT INTO %s\n(%s)\nVALUES(%s)" % (table_name, columns, values_in), row)
                ak_con.commit()
        # update mod_appkernel
        self._rename_appkernels_mod_appkernel()
        log.info("\t\tDone")

    def _rename_appkernels_mod_appkernel(self) -> None:
        """
        Rename appkernels from long to short format in mod_appkernel db
        """
        dry_run = akrr.dry_run
        update_app_kernel_def = True
        update_app_kernel = True
        update_app_kernel_def_list = True

        con_appkernel, cur_appkernel = self.get_akrr_db_con("mod_appkernel", dict_cursor=True)

        log.info("Updating mod_appkernel")
        if update_app_kernel_def:
            log.info("Updating app_kernel_def")
            for old, new in ak_rename.items():
                log.debug("update app_kernel_def: %s -> %s" % (new, old))
                cursor_execute(
                    cur_appkernel,
                    "update app_kernel_def set ak_base_name=%s where ak_base_name=%s", (new, old), dry_run)
            if not dry_run:
                con_appkernel.commit()

        if update_app_kernel:
            log.info("Updating app_kernel")
            for old, new in ak_rename.items():
                log.debug("update app_kernel: %s -> %s" % (new, old))
                cursor_execute(
                    cur_appkernel,
                    "update app_kernel set name=%s where name=%s", (new, old), dry_run)
            if not dry_run:
                con_appkernel.commit()

        if update_app_kernel_def_list:
            log.info("Updating mod_appkernel.app_kernel_def")
            from akrr.cli.generate_tables import populate_mod_appkernel_app_kernel_def
            populate_mod_appkernel_app_kernel_def(con_appkernel, cur_appkernel, dry_run)

    def _prepare_db_convertion(self):
        """helper function to prepare convertion statements"""
        akrr_con, akrr_cur = self.get_old_akrr_db_con()

        new_old_table = OrderedDict([
            ('active_tasks', 'ACTIVETASKS'),
            ('ak_on_nodes', 'ak_on_nodes'),
            ('akrr_default_walltime_limit', 'akrr_default_walllimit'),
            ('akrr_errmsg', 'akrr_errmsg'),
            ('akrr_err_regexp', 'akrr_err_regexp'),
            ('akrr_internal_failure_codes', 'akrr_internal_failure_codes'),
            ('akrr_resource_maintenance', 'akrr_resource_maintenance'),
            ('akrr_taks_errors', 'akrr_taks_errors'),
            ('akrr_xdmod_instanceinfo', 'akrr_xdmod_instanceinfo'),
            ('completed_tasks', 'COMPLETEDTASKS'),
            ('nodes', 'nodes'),
            ('scheduled_tasks', 'SCHEDULEDTASKS'),
            ('resources', 'resources'),
            ('app_kernels', 'app_kernels'),
            ('resource_app_kernels', 'resource_app_kernels'),
            # ('akrr_erran', 'akrr_erran'),
            # ('akrr_erran2', 'akrr_erran2'),
            # ('akrr_err_distribution_alltime', 'akrr_err_distribution_alltime')
        ])

        old_cols = {}
        for name_new, name_old in new_old_table.items():
            log.debug("SHOW COLUMNS FROM mod_akrr.%s" % name_old)
            akrr_cur.execute("SHOW COLUMNS FROM mod_akrr.%s" % name_old)
            rows = akrr_cur.fetchall()
            cols = ", ".join([r[0] for r in rows])
            old_cols[name_old] = cols

        for name_old in ('akrr_erran', 'akrr_erran2', 'akrr_err_distribution_alltime'):
            akrr_cur.execute("DROP VIEW IF EXISTS %s" % name_old)

        for name_new, name_old in new_old_table.items():
            akrr_cur.execute("DROP TABLE IF EXISTS %s" % name_old)
        akrr_con.commit()

        create_and_populate_tables(
            mod_akrr_create_tables_dict, tuple(),
            "Creating mod_akrr Tables / Views...", "mod_akrr Tables / Views Created!",
            None, connection=akrr_con, cursor=akrr_cur, drop_if_needed=True, dry_run=False
        )
        akrr_con.commit()

        new_cols = {}
        for name_new, name_old in new_old_table.items():
            log.debug("SHOW COLUMNS FROM mod_akrr.%s" % name_new)
            akrr_cur.execute("SHOW COLUMNS FROM mod_akrr.%s" % name_new)
            rows = akrr_cur.fetchall()
            cols = ", ".join([r[0] for r in rows])
            new_cols[name_new] = [cols, ",".join(["%s"] * len(rows))]

        for name_new, name_old in new_old_table.items():
            print("""    (
        "%s",
        {
            "name_new": "%s",
            "name_old": "%s",
            "select_cols_old":
                "SELECT %s\\n"
                "FROM %s",
            "drop_old": True,
            "create_new": mod_akrr_create_tables_dict['%s'],
            "populate_cols_new":
                "INSERT INTO %s\\n" 
                "      (%s)\\n"
                "VALUES(%s)",
        }
    ),""" % (name_new, name_new, name_old, old_cols[name_old], name_old, name_new, name_new,
             new_cols[name_new][0], new_cols[name_new][1]))

    def update(self, skip_saving_db_for_update=False):
        if not skip_saving_db_for_update:
            self._update_db_save_old_db()
        self._update_db_drop_old_tables()
        self._update_db_create_new()
        self._update_db_populate_new_db()


class UpdateResourceAppConfigs:
    def __init__(self, update_akrr: UpdateAKRR):
        self.update_akrr = update_akrr
        self.old_cfg = self.update_akrr.old_cfg

    def get_resource_dir(self, resource_name: str) -> Tuple[str, str, str, str]:
        """
        Return tuple with old and new directory name for resource
        """
        import akrr
        cfg_dir = akrr.get_akrr_dirs()['cfg_dir']
        resource_dir_old = os.path.join(self.update_akrr.old_akrr_cfg_dir, "resources", resource_name)
        resource_dir = os.path.join(cfg_dir, "resources", resource_name)
        resource_cfg_filename_old1 = os.path.join(resource_dir_old, 'resource.inp.py')
        resource_cfg_filename_old2 = os.path.join(resource_dir_old, 'resource.conf')
        resource_cfg_filename_old = resource_cfg_filename_old1 if os.path.isfile(resource_cfg_filename_old1) else \
            resource_cfg_filename_old2
        resource_cfg_filename = os.path.join(resource_dir, 'resource.conf')
        return resource_dir_old, resource_dir, resource_cfg_filename_old, resource_cfg_filename

    @staticmethod
    def config_rename_var(config_text: str,
                          current_vars: dict,
                          renamed_vars: Tuple[Tuple[str, str]] = None,
                          renamed_template_vars: Tuple[Tuple[str, str]] = None) -> str:
        """
        Rename var names
        """
        # replace old variables with new
        log.debug2("Replacing old variables with new")
        if renamed_vars is not None:
            for old_key, new_key in renamed_vars:
                if old_key in current_vars:
                    config_text, nsub = re.subn(r"^(\s*)" + old_key + r"\s*=\s*", "\\1" + new_key + " = ",
                                                config_text, flags=re.MULTILINE)
                    if nsub == 0:
                        log.warning("Was not able to substitute %s to %s, update it manually!", old_key, new_key)
                    if nsub == 1:
                        log.debug2("    %s -> %s", old_key, new_key)
                    if nsub > 1:
                        log.warning("Too many substitution (%d) for %s to %s conversion. Check the outcome!",
                                    nsub, old_key, new_key)
        # update variables in templates
        if renamed_template_vars is not None:
            log.debug2("Replacing variables in templates")
            config_text = config_text.replace('{{', 'LeFtyCurlyBrackets')
            config_text = config_text.replace('}}', 'RiGhTyCurlyBrackets')

            for old_key, new_key in renamed_template_vars:
                config_text, nsub = re.subn(r'{' + old_key + r"}", "{" + new_key + "}",
                                            config_text, flags=re.MULTILINE)
                if nsub > 0:
                    log.debug2("    %s -> %s %d times", old_key, new_key, nsub)

            config_text = config_text.replace('LeFtyCurlyBrackets', '{{')
            config_text = config_text.replace('RiGhTyCurlyBrackets', '}}')
        return config_text

    def update_app(self, resource_name: str, app_name: str) -> str:
        """
        Update app kernel config, return hints on what to do next.
        """
        from akrr.cfg_util import load_app_default, load_app_on_resource, load_resource, \
            resource_renamed_parameters, app_renamed_parameters

        # get old and new app name
        app_name_old = app_name
        app_name = ak_rename[app_name_old] if app_name_old in ak_rename else app_name
        if app_name == app_name_old:
            log.info("Processing: resource: %s, app kernel: %s ", resource_name, app_name)
        else:
            log.info("Processing: resource: %s, app kernel: rename %s to %s",
                     resource_name, app_name_old, app_name)

        hints_to_do_next = "# Test appkernel execution on resource:\n" + \
                           "akrr app validate -n 2 -r %s -a %s\n" % (resource_name, app_name)

        resource_dir_old, resource_dir, resource_cfg_filename_old, resource_cfg_filename = \
            self.get_resource_dir(resource_name)
        app_cfg_filename_old1 = os.path.join(resource_dir_old, app_name_old + '.app.inp.py')
        app_cfg_filename_old2 = os.path.join(resource_dir_old, app_name_old + '.app.conf')
        app_cfg_filename_old = app_cfg_filename_old1 if os.path.isfile(app_cfg_filename_old1) else \
            app_cfg_filename_old2
        app_cfg_filename = os.path.join(resource_dir, app_name + '.app.conf')
        log.info("Old app kernel config file: %s", app_cfg_filename_old)

        if not os.path.isfile(app_cfg_filename_old):
            log.error("Can not find %s! Will skip it.", app_cfg_filename_old)
            return "# [ERROR] Can not find %s! Will skip it.\n" % app_cfg_filename_old

        try:
            resource_old = load_resource(resource_name, resource_cfg_filename=resource_cfg_filename_old, validate=False)
            app_default = load_app_default(app_name)
            app = load_app_on_resource(app_name, resource_name, resource_old, app_default,
                                       app_on_resource_cfg_filename=app_cfg_filename_old, validate=False)
        except Exception as e:  # pylint: disable=broad-except
            log.exception("Exception occurred during resource and app loading:" + str(e))
            return "# [ERROR] old configs for %s on %s has errors, can not convert it\n" % (app_name, resource_name)

        config_text = open(app_cfg_filename_old, "rt").read()
        config_text = self.config_rename_var(
            config_text, app, resource_renamed_parameters + app_renamed_parameters,
            resource_renamed_parameters + app_renamed_parameters)

        log.info("Writing updated app config file to %s", app_cfg_filename)
        if not akrr.dry_run:
            with open(app_cfg_filename, "wt") as fout:
                fout.write(config_text)
        else:
            log.dry_run("New config file:\n" + config_text)

        # Try to load new file
        log.info("Loading updated app kernel config")
        try:
            if not akrr.dry_run:
                resource_old = load_resource(resource_name, resource_cfg_filename=resource_cfg_filename, validate=False)
                app_default = load_app_default(app_name)
                app = load_app_on_resource(app_name, resource_name, resource_old, app_default,
                                           app_on_resource_cfg_filename=app_cfg_filename, validate=False)
        except Exception as e:  # pylint: disable=broad-except
            log.exception("Exception occurred during updated resources loading:" + str(e) +
                          "\nYou'll need to maniaully fix it!")
            return "# [ERROR] Converted config for " + resource_name + \
                   "contain errors fix them first and deploy/test\n" + hints_to_do_next
        return hints_to_do_next

    def update_resource(self, resource_name: str) -> str:
        """
        Update resource configuration, return hints on what to do next.
        """
        from akrr.cli.setup import make_dirs
        from akrr.cfg_util import load_resource, resource_renamed_parameters, app_renamed_parameters

        hints_to_do_next = "# Deploy new utils on resource and check it is working properly:\n" + \
                           "akrr resource deploy -r %s\n" % resource_name

        log.info("Processing: %s", resource_name)

        resource_dir_old, resource_dir, resource_cfg_filename_old, resource_cfg_filename = \
            self.get_resource_dir(resource_name)
        # make resource dir if needed
        if not os.path.isdir(resource_dir):
            make_dirs(resource_dir)

        log.info("Old resource config file: %s", resource_cfg_filename_old)

        if not os.path.isfile(resource_cfg_filename_old):
            log.error("Can not find %s! Will skip it.", resource_cfg_filename_old)
            return "# [ERROR] Can not find %s! Will skip it.\n" % resource_cfg_filename_old

        try:
            resource_old = load_resource(
                resource_name, resource_cfg_filename=resource_cfg_filename_old, validate=False)
        except Exception as e:  # pylint: disable=broad-except
            log.exception("Exception occurred during resources loading:" + str(e))
            return "# [ERROR] old configs for %s has errors, can not convert it\n" % resource_name

        config_text = open(resource_cfg_filename_old, "rt").read()
        config_text = self.config_rename_var(
            config_text, resource_old, resource_renamed_parameters + app_renamed_parameters,
            resource_renamed_parameters + app_renamed_parameters)

        log.info("Writing updated resource config file to %s", resource_cfg_filename)
        if not akrr.dry_run:
            with open(resource_cfg_filename, "wt") as fout:
                fout.write(config_text)
        else:
            log.dry_run("New config file:\n" + config_text)

        # Try to load new file
        if not akrr.dry_run:
            log.info("Loading updated resource config")
            try:
                resource = load_resource(resource_name, resource_cfg_filename=resource_cfg_filename)
            except Exception as e:  # pylint: disable=broad-except
                log.exception("Exception occurred during updated resources loading:" + str(e) +
                              "\nYou'll need to maniaully fix it!")
                return "# [ERROR] Converted config for " + resource_name + \
                       "contain errors fix them first and deploy/test\n" + hints_to_do_next
        return hints_to_do_next

    def update(self) -> str:
        hints_to_do_next = ""
        # get resources
        for resource_name in os.listdir(os.path.join(self.update_akrr.old_akrr_cfg_dir, "resources")):
            if resource_name in ['notactive', 'templates']:
                continue

            hints_to_do_next += self.update_resource(resource_name)
            # Update apps
            resource_dir_old, _, _, _ = self.get_resource_dir(resource_name)
            for filename in os.listdir(resource_dir_old):
                if filename.endswith(".app.inp.py"):
                    app_name = re.sub(r'\.app\.inp\.py$', '', filename)
                    hints_to_do_next += self.update_app(resource_name, app_name)
                if filename.endswith(".app.conf"):
                    app_name = re.sub(r'\.app\.conf$', '', filename)
                    hints_to_do_next += self.update_app(resource_name, app_name)
        return hints_to_do_next


class UpdateCompletedDirs:
    def __init__(self, old_completed_task_dir, completed_task_dir):
        self.old_completed_task_dir = old_completed_task_dir
        self.completed_task_dir = completed_task_dir
        self.days_to_archive_task = datetime.timedelta(days=90)

    def _check_completed_task_dir(self):
        """
        if old and new completed task dir are the same rename old one
        """
        if self.old_completed_task_dir == self.completed_task_dir:
            old_completed_task_dir = self.old_completed_task_dir + '.bak'
            i = 1
            while not os.path.exists(old_completed_task_dir):
                i += 1
                old_completed_task_dir = self.old_completed_task_dir + '.bak%d' % i
            log.info("Renamed old complete task dir %s to %s.", self.old_completed_task_dir, old_completed_task_dir)
            self.old_completed_task_dir = old_completed_task_dir

    def _get_app_name(self, app_old):
        """
        Get new app name
        """
        return app_old if app_old not in ak_rename else ak_rename[app_old]


    def _get_resource_dir(self, resource):
        """
        Return resource old and new dir, return None, None if old dir do not exists
        """
        resource_old_dir = os.path.join(self.old_completed_task_dir, resource)
        resource_dir = os.path.join(self.completed_task_dir, resource)
        if not os.path.isdir(resource_old_dir):
            return None, None
        return resource_old_dir, resource_dir

    def _get_resource_app_dir(self, resource, app_old):
        """
        Get resource app dir
        """
        resource_old_dir, resource_dir = self._get_resource_dir(resource)
        if not resource_old_dir:
            return None, None

        app = self._get_app_name(app_old)
        app_old_dir = os.path.join(resource_old_dir, app_old)
        app_dir = os.path.join(resource_dir, app)

        if not os.path.isdir(app_old_dir):
            return None, None
        return app_old_dir, app_dir

    def _copy_task_v1(self, resource, app_old, task_time_stamp):
        """
        Copy logs with old layout
        """
        app = self._get_app_name(app_old)
        app_old_dir, app_dir = self._get_resource_app_dir(resource, app_old)
        if not app_old_dir:
            return
        task_old_dir = os.path.join(app_old_dir, task_time_stamp)
        if not os.path.isdir(task_old_dir):
            return

        datetime_stamp_split = task_time_stamp.split(".")
        if len(datetime_stamp_split) > 3:
            year = datetime_stamp_split[0]
            month = datetime_stamp_split[1]
            day = datetime_stamp_split[2]
        else:
            # unknown format just copy
            task_parent_dir = os.path.join(app_old_dir, task_time_stamp)
            task_dir = os.path.join(app_dir, task_time_stamp)
            if not akrr.dry_run:
                shutil.copytree(task_parent_dir, task_dir)
            return

        task_dir = os.path.join(app_dir, year, month, task_time_stamp)
        if not akrr.dry_run:
            # move only logs and app output
            make_dirs(task_dir, verbose=False)
            filename_old = os.path.join(task_old_dir, 'result.xml')
            filename = os.path.join(task_dir, 'result.xml')

            if os.path.isfile(filename_old):
                shutil.copyfile(filename_old, filename)

            filename_old = os.path.join(task_old_dir, 'proc', 'log')
            filename = os.path.join(task_dir, 'proc', 'log')

            if os.path.isfile(filename_old):
                make_dirs(os.path.join(task_dir, 'proc'), verbose=False)
                shutil.copyfile(filename_old, filename)

            jobfiles_old_dir = os.path.join(task_old_dir, 'jobfiles')
            jobfiles_dir = os.path.join(task_dir, 'jobfiles')
            if os.path.isdir(jobfiles_old_dir):
                make_dirs(jobfiles_dir, verbose=False)
                for filename in ('appstdout', 'gen.info', 'job.id', 'stderr', 'stdout'):
                    filename_old = os.path.join(jobfiles_old_dir, filename)
                    filename = os.path.join(jobfiles_dir, filename)
                    if os.path.isfile(filename_old):
                        shutil.copyfile(filename_old, filename)

                batch_job_file_old = os.path.join(jobfiles_old_dir, app_old + ".job")
                batch_job_file = os.path.join(jobfiles_dir, app + ".job")
                if os.path.isfile(batch_job_file_old):
                    shutil.copyfile(batch_job_file_old, batch_job_file)
        # Archive completed tasks to save space and file counts
        # zip task dir after 90 days
        if datetime.date.today() - datetime.date(int(year), int(month), int(day)) > self.days_to_archive_task:
            out = tarfile.open(task_dir + '.tar.gz', mode='w|gz')
            out.add(task_dir, task_time_stamp)
            out.close()
            shutil.rmtree(task_dir)

    def run(self):
        self._check_completed_task_dir()
        # Moving old complete tasks logs
        log.info("Moving old complete tasks logs from %s to %s", self.old_completed_task_dir, self.completed_task_dir)
        for resource in os.listdir(self.old_completed_task_dir):
            resource_old_dir, resource_dir = self._get_resource_dir(resource)
            if not resource_old_dir:
                continue
            log.info("\tMoving %s resource", resource)
            for app_old in os.listdir(resource_old_dir):
                app = self._get_app_name(app_old)
                app_old_dir, app_dir = self._get_resource_app_dir(resource, app_old)
                if not app_old_dir:
                    continue

                tasks = [f for f in os.listdir(app_old_dir) if os.path.isdir(os.path.join(app_old_dir, f))]
                if len(tasks) == 0:
                    log.info("\t\tNo completed tasks in %s", app_old)
                    continue

                if app_old == app:
                    log.info("\t\tMoving %s", app)
                else:
                    log.info("\t\tMoving %s -> %s", app_old, app)

                if tasks[0].isdigit():
                    # 2.0 format just copy
                    for year in tasks:
                        year_old_dir = os.path.join(app_old_dir, year)
                        year_dir = os.path.join(app_dir, year)
                        if not akrr.dry_run:
                            shutil.copytree(year_old_dir, year_dir)
                else:
                    # 1.0 format
                    for task_time_stamp in tasks:
                        self._copy_task_v1(resource, app_old, task_time_stamp)
        # Archive completed tasks to save space and file counts
        # zip task dir after 90 days
        # zip month dir after half a year
        Archive(comp_task_dir=self.completed_task_dir).archive_tasks_by_months(months_old=6)
        Archive(comp_task_dir=self.completed_task_dir).archive_tasks(days_old=90)
