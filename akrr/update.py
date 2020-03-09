"""
Routings for AKRR update
"""
import os
import copy
import re
import subprocess
import pickle
import pprint
from collections import OrderedDict
from typing import Optional

from akrr.util import log
from akrr.util.sql import get_con_to_db2, cursor_execute
from akrr.akrrerror import AkrrValueException, AkrrFileNotFoundError, AkrrException
from akrr.util.sql import get_con_to_db
from akrr.util import exec_files_to_dict
from akrr.cli.generate_tables import create_and_populate_tables, mod_akrr_create_tables_dict


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


def rename_appkernels(mod_akrr: str, mod_appkernel: str, dry_run: bool = False) -> None:
    """
    Rename appkernels from long to short format
    """
    rename_appkernels_mod_akrr(mod_akrr, dry_run)
    rename_appkernels_mod_appkernel(mod_appkernel, dry_run)


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


def rename_appkernels_mod_appkernel(mod_appkernel: str, dry_run: bool = False) -> None:
    """
    Rename appkernels from long to short format in mod_appkernel db
    """
    update_app_kernel_def = True
    update_app_kernel = True
    update_app_kernel_def_list = True

    con_appkernel, cur_appkernel = get_con_to_db2(mod_appkernel)

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


_convert_mod_akrr_db = OrderedDict((
    (
        "active_tasks",
        {
            "name_new": "active_tasks",
            "name_old": "ACTIVETASKS",
            "select_old": None,
            "drop_old": True,
            "create_new": mod_akrr_create_tables_dict['active_tasks'],
            "populate_new": None,
        }
    ),
    (
        "ak_on_nodes",
        {
            "name_new": "ak_on_nodes",
            "name_old": "ak_on_nodes",
            "select_old":
                "SELECT resource_id, node_id, task_id, collected, status\n"
                "FROM ak_on_nodes",
            "drop_old": True,
            "create_new": mod_akrr_create_tables_dict['ak_on_nodes'],
            "populate_new":
                "INSERT INTO ak_on_nodes\n"
                "      (resource_id, node_id, task_id, collected, status)\n"
                "VALUES(%s,%s,%s,%s,%s)",
        }
    ),
    (
        "akrr_default_walltime_limit",
        {
            "name_new": "akrr_default_walltime_limit",
            "name_old": "akrr_default_walllimit",
            "select_old":
                "SELECT id, resource, app, walllimit,      resource_param, app_param, last_update, comments\n"
                "FROM akrr_default_walllimit",
            "drop_old": True,
            "create_new": mod_akrr_create_tables_dict['akrr_default_walltime_limit'],
            "populate_new":
                "INSERT INTO akrr_default_walltime_limit\n"
                "      (id, resource, app, walltime_limit, resource_param, app_param, last_update, comments)\n"
                "VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
            "convert": lambda row: convert_appname(2, row)
        }
    ),
    (
        "akrr_errmsg",
        {
            "name_new": "akrr_errmsg",
            "name_old": "akrr_errmsg",
            "select_old":
                "SELECT task_id, err_regexp_id, appstdout, stderr, stdout, taskexeclog\n"
                "FROM akrr_errmsg",
            "drop_old": True,
            "create_new": mod_akrr_create_tables_dict['akrr_errmsg'],
            "populate_new":
                "INSERT INTO akrr_errmsg\n"
                "      (task_id, err_regexp_id, appstdout, stderr, stdout, taskexeclog)\n"
                "VALUES(%s,%s,%s,%s,%s,%s)",
        }
    ),
    (
        "akrr_err_regexp",
        {
            "name_new": "akrr_err_regexp",
            "name_old": "akrr_err_regexp",
            "select_old":
                "SELECT id, active, resource, app, reg_exp, reg_exp_opt, source, err_msg, description\n"
                "FROM akrr_err_regexp",
            "drop_old": True,
            "create_new": mod_akrr_create_tables_dict['akrr_err_regexp'],
            "populate_new":
                "INSERT INTO akrr_err_regexp\n"
                "      (id, active, resource, app, reg_exp, reg_exp_opt, source, err_msg, description)\n"
                "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            "convert": lambda row: convert_appname(3, row)
        }
    ),
    (
        "akrr_internal_failure_codes",
        {
            "name_new": "akrr_internal_failure_codes",
            "name_old": "akrr_internal_failure_codes",
            "select_old":
                "SELECT id, description\n"
                "FROM akrr_internal_failure_codes",
            "drop_old": True,
            "create_new": mod_akrr_create_tables_dict['akrr_internal_failure_codes'],
            "populate_new":
                "INSERT INTO akrr_internal_failure_codes\n"
                "      (id, description)\n"
                "VALUES(%s,%s)",
        }
    ),
    (
        "akrr_resource_maintenance",
        {
            "name_new": "akrr_resource_maintenance",
            "name_old": "akrr_resource_maintenance",
            "select_old":
                "SELECT id, resource, start, end, comment\n"
                "FROM akrr_resource_maintenance",
            "drop_old": True,
            "create_new": mod_akrr_create_tables_dict['akrr_resource_maintenance'],
            "populate_new":
                "INSERT INTO akrr_resource_maintenance\n"
                "      (id, resource, start, end, comment)\n"
                "VALUES(%s,%s,%s,%s,%s)",
        }
    ),
    (
        "akrr_task_errors",
        {
            "name_new": "akrr_task_errors",
            "name_old": "akrr_taks_errors",
            "select_old":
                "SELECT task_id, err_reg_exp_id\n"
                "FROM akrr_taks_errors",
            "drop_old": True,
            "create_new": mod_akrr_create_tables_dict['akrr_task_errors'],
            "populate_new":
                "INSERT INTO akrr_task_errors\n"
                "      (task_id, err_reg_exp_id)\n"
                "VALUES(%s,%s)",
        }
    ),
    (
        "akrr_xdmod_instanceinfo",
        {
            "name_new": "akrr_xdmod_instanceinfo",
            "name_old": "akrr_xdmod_instanceinfo",
            "select_old":
                "SELECT instance_id, collected, committed, resource, executionhost, reporter, reporternickname,\n"
                "       status, message, stderr, body, memory, cputime, walltime, job_id, internal_failure, nodes,\n"
                "       ncores, nnodes\n"
                "FROM akrr_xdmod_instanceinfo",
            "drop_old": True,
            "create_new": mod_akrr_create_tables_dict['akrr_xdmod_instanceinfo'],
            "populate_new":
                "INSERT INTO akrr_xdmod_instanceinfo\n"
                "      (instance_id, collected, committed, resource, executionhost, reporter, reporternickname, \n"
                "       status, message, stderr, body, memory, cputime, walltime, job_id, internal_failure, nodes,\n"
                "       ncores, nnodes)\n"
                "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            "convert": lambda row: convert_appname(5, row, ireporternickname=6)
        }
    ),
    (
        "completed_tasks",
        {
            "name_new": "completed_tasks",
            "name_old": "COMPLETEDTASKS",
            "select_old":
                "SELECT task_id, time_finished, status, statusinfo, time_to_start, datetimestamp, time_activated,\n"
                "       time_submitted_to_queue, repeat_in, resource, app, resource_param, app_param, task_param,\n"
                "       group_id, FatalErrorsCount, FailsToSubmitToTheQueue, parent_task_id\n"
                "FROM COMPLETEDTASKS",
            "drop_old": True,
            "create_new": mod_akrr_create_tables_dict['completed_tasks'],
            "populate_new":
                "INSERT INTO completed_tasks\n"
                "      (task_id, time_finished, status, status_info, time_to_start, datetime_stamp, time_activated,\n"
                "       time_submitted_to_queue, repeat_in, resource, app, resource_param, app_param, task_param,\n"
                "       group_id, fatal_errors_count, fails_to_submit_to_the_queue, parent_task_id)\n"
                "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            "convert": lambda row: convert_appname(10, row)
        }
    ),
    (
        "nodes",
        {
            "name_new": "nodes",
            "name_old": "nodes",
            "select_old":
                "SELECT node_id, resource_id, name\n"
                "FROM nodes",
            "drop_old": True,
            "create_new": mod_akrr_create_tables_dict['nodes'],
            "populate_new":
                "INSERT INTO nodes\n"
                "      (node_id, resource_id, name)\n"
                "VALUES(%s,%s,%s)",
        }
    ),
    (
        "scheduled_tasks",
        {
            "name_new": "scheduled_tasks",
            "name_old": "SCHEDULEDTASKS",
            "select_old":
                "SELECT task_id, time_to_start, repeat_in, resource, app, resource_param, app_param, task_param,\n"
                "       group_id, parent_task_id\n"
                "FROM SCHEDULEDTASKS",
            "drop_old": True,
            "create_new": mod_akrr_create_tables_dict['scheduled_tasks'],
            "populate_new":
                "INSERT INTO scheduled_tasks\n"
                "      (task_id, time_to_start, repeat_in, resource, app, resource_param, app_param, task_param,\n"
                "       group_id, parent_task_id)\n"
                "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            "convert": lambda row: convert_appname(4, row)
        }
    ),
    (
        "resources",
        {
            "name_new": "resources",
            "name_old": "resources",
            "select_old":
                "SELECT id, xdmod_resource_id, name, enabled\n"
                "FROM resources",
            "drop_old": True,
            "create_new": mod_akrr_create_tables_dict['resources'],
            "populate_new":
                "INSERT INTO resources\n"
                "      (id, xdmod_resource_id, name, enabled)\n"
                "VALUES(%s,%s,%s,%s)",
        }
    ),
    (
        "app_kernels",
        {
            "name_new": "app_kernels",
            "name_old": "app_kernels",
            "select_old":
                "SELECT id, name, enabled, nodes_list\n"
                "FROM app_kernels",
            "drop_old": True,
            "create_new": mod_akrr_create_tables_dict['app_kernels'],
            "populate_new":
                "INSERT INTO app_kernels\n"
                "      (id, name, enabled, nodes_list)\n"
                "VALUES(%s,%s,%s,%s)",
            "convert": lambda row: convert_appname(1, row)
        }
    ),
    (
        "resource_app_kernels",
        {
            "name_new": "resource_app_kernels",
            "name_old": "resource_app_kernels",
            "select_old":
                "SELECT id, resource_id, app_kernel_id, enabled\n"
                "FROM resource_app_kernels",
            "drop_old": True,
            "create_new": mod_akrr_create_tables_dict['resource_app_kernels'],
            "populate_new":
                "INSERT INTO resource_app_kernels\n"
                "      (id, resource_id, app_kernel_id, enabled)\n"
                "VALUES(%s,%s,%s,%s)",
        }
    )
))


class UpdateAKRR:
    """
    Class for updating old AKRR
    """

    def __init__(self, old_akrr_home: str = None, yes_to_all: bool = False):
        """
        Parameters
        ----------
        old_akrr_cfg - old AKRR Config path, if None will try to locate based on environment variables
        """
        self.old_akrr_home = old_akrr_home  # type: Optional[str]
        self.old_akrr_cfg_file = None  # type: Optional[str]
        self.yes_to_all = yes_to_all  # type: bool
        self.akrr_con = None
        self.akrr_cur = None
        self.task_id_max = 0  # type: int

        # find akrr home if needed
        if self.old_akrr_home is None:
            if "AKRR_HOME" in os.environ:
                self.old_akrr_home = os.environ["AKRR_HOME"]
                log.debug2("Found AKRR home in %s", self.old_akrr_home)

        if self.old_akrr_home is None:
            msg = "Can not find old AKRR home directory specify AKRR_HOME environment variables"
            log.error(msg)
            raise AkrrValueException(msg)
        if not os.path.isdir(self.old_akrr_home):
            msg = "AKRR home is not found (%s is not directory or do not exists)" % self.old_akrr_home
            log.error(msg)
            raise AkrrFileNotFoundError(msg)

        self.old_akrr_home = os.path.abspath(os.path.expanduser(self.old_akrr_home))

        # locate config
        self.old_akrr_cfg_file = os.path.join(self.old_akrr_home, "cfg", "akrr.inp.py")
        if not os.path.isfile(self.old_akrr_cfg_file):
            msg = "AKRR config file not found (was looking for %s)" % self.old_akrr_cfg_file
            log.error(msg)
            raise AkrrFileNotFoundError(msg)

        log.debug2("Found AKRR config is %s", self.old_akrr_cfg_file)

        # read cfg
        self.old_cfg = self._read_config(self.old_akrr_cfg_file)

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
        except Exception:
            log.info("Crontab does not have user's crontab yet")
            return True

        crontab_content_new = []
        for crontab_line in crontab_content:
            if crontab_line == "#AKRR" or crontab_line == "##AKRR" or crontab_line == "## AKRR":
                continue
            fields = crontab_line.strip().split()
            if len(fields) > 0:
                if os.path.abspath(fields[-1]) == os.path.join(self.old_akrr_home, "bin", "restart.sh"):
                    continue
                if os.path.abspath(fields[-1]) == os.path.join(self.old_akrr_home, "bin", "checknrestart.sh"):
                    continue

            crontab_content_new.append(crontab_line)

        tmp_cronfile_fd, tmp_cronfile = mkstemp(prefix="crontmp", dir=os.path.expanduser('~'), text=True)
        with open(tmp_cronfile_fd, 'wt') as f:
            for tmp_str in crontab_content_new:
                f.write(tmp_str + "\n")
        subprocess.call("crontab " + tmp_cronfile, shell=True)
        os.remove(tmp_cronfile)
        log.info("Crontab updated.")

    def shut_down_old_akrr(self):
        """
        Shut down old AKRR
        """
        log.info("Shutting down old akrr daemon.")
        import akrr.util.daemon
        if not akrr.util.daemon.daemon_stop(akrr.util.daemon.get_daemon_pid(
                os.path.join(self.old_cfg['data_dir'], 'akrr.pid'), delete_pid_file_if_daemon_down=True)):
            msg = "Can not stop old daemon please kill it manually!"
            log.error(msg)
            raise AkrrException(msg)

    def rename_old_akrr_home(self):
        pass

    def get_old_akrr_db_con(self):
        if self.akrr_con is None or self.akrr_cur is None:
            self.akrr_con, self.akrr_cur = get_con_to_db(
                user=self.old_cfg["ak_db_user"], password=self.old_cfg["ak_db_passwd"],
                host=self.old_cfg["akrr_db_host"], port=self.old_cfg["ak_db_port"],
                db_name=self.old_cfg["akrr_db_name"],
                dict_cursor=False, raise_exception=True)
        return self.akrr_con, self.akrr_cur

    def _get_table_pkl_name(self, db_name, table_name):
        """
        Get pickeled filename for table dump
        """
        return os.path.join(self.old_cfg['data_dir'], "%s__%s.pkl" % (db_name, table_name))

    def _update_db_save_old_db(self):
        """
        Save old tables
        """
        akrr_con, akrr_cur = self.get_old_akrr_db_con()

        for table_ref, table_info in _convert_mod_akrr_db.items():
            if table_info['select_old'] is None:
                continue
            log.debug("Saving: mod_akrr.%s" % table_info['name_old'])
            akrr_cur.execute(table_info['select_old'])

            with open(self._get_table_pkl_name("mod_akrr", table_info['name_new']), "wb") as fout:
                while True:
                    rows = akrr_cur.fetchmany(4)
                    if not rows:
                        break
                    pickle.dump(rows, fout)

        # find current task_id_max
        self.task_id_max = 0
        for table in ("COMPLETEDTASKS", "SCHEDULEDTASKS", "ACTIVETASKS"):
            akrr_cur.execute("SELECT max(task_id) FROM %s" % table)
            rows = akrr_cur.fetchall()
            if len(rows) > 0 and len(rows[0]) > 0:
                if rows[0][0] > self.task_id_max:
                    self.task_id_max = rows[0][0]

    def _update_db_drop_old_tables(self):
        """
        drop old tables
        """
        akrr_con, akrr_cur = self.get_old_akrr_db_con()
        for name_old in ('akrr_erran', 'akrr_erran2', 'akrr_err_distribution_alltime'):
            log.debug("Dropping: mod_akrr.%s" % name_old)
            akrr_cur.execute("DROP VIEW IF EXISTS %s" % name_old)

        for table_ref, table_info in _convert_mod_akrr_db.items():
            if table_info['drop_old']:
                akrr_cur.execute("DROP TABLE IF EXISTS %s" % table_info['name_old'])
                log.debug("Dropping: mod_akrr.%s" % table_info['name_old'])
        akrr_con.commit()

    def _update_db_create_new(self):
        """
        create new tables
        """
        akrr_con, akrr_cur = self.get_old_akrr_db_con()
        for table_ref, table_info in _convert_mod_akrr_db.items():
            create_and_populate_tables(
                ((table_info['name_new'], table_info['create_new']),),
                tuple(),
                "Creating mod_akrr.%s Tables ..." % table_info['name_new'],
                "mod_akrr.%s table created." % table_info['name_new'],
                None,
                connection=akrr_con, cursor=akrr_cur,
                drop_if_needed=True,
                dry_run=False
            )
        for name_new in ('akrr_erran', 'akrr_erran2', 'akrr_err_distribution_alltime'):
            create_and_populate_tables(
                ((name_new, mod_akrr_create_tables_dict[name_new]),),
                tuple(),
                "Creating mod_akrr.%s Tables ..." % name_new,
                "mod_akrr.%s table created." % name_new,
                None,
                connection=akrr_con, cursor=akrr_cur,
                drop_if_needed=True,
                dry_run=False
            )

    def _update_db_populate_new_db(self):
        """
        Populate new tables
        """
        akrr_con, akrr_cur = self.get_old_akrr_db_con()

        # scheduled_tasks
        for table_ref, table_info in _convert_mod_akrr_db.items():
            if table_info['populate_new'] is None:
                continue
            log.debug("Populating: mod_akrr.%s" % table_info['name_new'])
            with open(self._get_table_pkl_name("mod_akrr", table_info['name_new']), "rb") as fin:
                while True:
                    try:
                        rows = pickle.load(fin)
                    except EOFError:
                        break
                    for row in rows:
                        if "convert" in table_info:
                            row = table_info["convert"](row)
                        akrr_cur.execute(table_info['populate_new'], row)
                akrr_con.commit()

        # update auto increment
        if self.task_id_max > 0:
            akrr_cur.execute("ALTER TABLE scheduled_tasks AUTO_INCREMENT=%s" % (self.task_id_max + 1))
            akrr_con.commit()

        # correct some values
        akrr_cur.execute("update completed_tasks set app=CONCAT(app,'.core') where resource_param like '%ncpus%'")
        akrr_con.commit()

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
            tuple(mod_akrr_create_tables_dict.items()), tuple(),
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
            new_cols[name_new] = [cols, ",".join(["%s"]*len(rows))]

        for name_new, name_old in new_old_table.items():
            print("""    (
        "%s",
        {
            "name_new": "%s",
            "name_old": "%s",
            "select_old":
                "SELECT %s\\n"
                "FROM %s",
            "drop_old": True,
            "create_new": mod_akrr_create_tables_dict['%s'],
            "populate_new":
                "INSERT INTO %s\\n" 
                "      (%s)\\n"
                "VALUES(%s)",
        }
    ),""" % (name_new, name_new, name_old, old_cols[name_old], name_old, name_new, name_new,
             new_cols[name_new][0], new_cols[name_new][1]))

    def update_db(self):
        self._update_db_save_old_db()
        self._update_db_drop_old_tables()
        self._update_db_create_new()
        self._update_db_populate_new_db()

    def run(self):
        """
        Do update
        """
        self.remove_old_akrr_from_crontab()
        self.shut_down_old_akrr()
        self.update_db()
