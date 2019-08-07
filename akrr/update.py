"""
Routings for AKRR update
"""
import copy
from akrr.util import log, get_list_from_comma_sep_values
from akrr.util.sql import get_con_to_db2, cursor_execute


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
        message += "%30s %10s %10s %10s %20s %20s\n" % ("Table Name", "same", "in tables1", "in tables2", "type1", "type2")
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
    'xdmod.benchmark.hpcg':'hpcg',
    'xdmod.benchmark.mem.stream.core':'stream.core'
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
