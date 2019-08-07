
# Keep CLI commands setup here outside of implementation, to avoid premature cfg loading


def add_command_daemon(parent_parser):
    """
    Application Kernel Remote Runner (AKRR) daemon control command
    """
    parser = parent_parser.add_parser('daemon', description=add_command_daemon.__doc__)
    subparsers = parser.add_subparsers(title='commands')

    cli_daemon_start(subparsers)
    cli_daemon_stop(subparsers)
    cli_daemon_restart(subparsers)
    cli_daemon_check(subparsers)
    cli_daemon_checknrestart(subparsers)
    cli_daemon_monitor(subparsers)
    cli_daemon_status(subparsers)
    cli_daemon_startdeb(subparsers)


def cli_daemon_start(parent_parser):
    """launch Application Remote Runner in daemon mode"""
    parser = parent_parser.add_parser('start', description=cli_daemon_start.__doc__)

    def handler(_):
        from akrr.daemon import daemon_start
        return daemon_start()

    parser.set_defaults(func=handler)


def cli_daemon_stop(parent_parser):
    """terminate Application Remote Runner"""
    parser = parent_parser.add_parser('stop', description=cli_daemon_stop.__doc__)

    def handler(_):
        from akrr.daemon import daemon_stop
        return daemon_stop()

    parser.set_defaults(func=handler)


def cli_daemon_restart(parent_parser):
    """restart AKRR daemon"""
    parser = parent_parser.add_parser('restart', description=cli_daemon_restart.__doc__)
    parser.add_argument('-cron', action='store_true', help="for launching by cron, no output on normal operation")

    def handler(args):
        from akrr.util import log
        from akrr.daemon import get_daemon_pid, daemon_start, daemon_stop

        if args.cron is True:
            # i.e. executed by cron
            #   run same command as separate process (but without -cron)
            #   print output only if return non zero code
            import subprocess
            import sys
            import os
            argv = [sys.executable, os.path.abspath(sys.argv[0])]
            if len(sys.argv) > 0:
                for arg in sys.argv[1:]:
                    if arg != "-cron":
                        argv.append(arg)
            try:
                subprocess.check_output(argv, stderr=subprocess.STDOUT, timeout=120)
            except subprocess.CalledProcessError as e:
                if hasattr(e, 'output'):
                    print(e.output.decode("utf-8"))
        else:
            log.info("Restarting AKRR")
            try:
                if get_daemon_pid(True) is not None:
                    daemon_stop()
            except Exception as e:
                log.exception("Exception was thrown during daemon stopping")
                log.log_traceback(str(e))
            return daemon_start()

    parser.set_defaults(func=handler)


def cli_daemon_check(parent_parser):
    """Check AKRR Daemon Status, using REST API"""
    parser = parent_parser.add_parser('check', description=cli_daemon_check.__doc__)

    def handler(_):
        from akrr.util import log

        def is_api_up():
            from akrr import akrrrestclient
            request = akrrrestclient.get("/scheduled_tasks")
            if request.status_code == 200:
                return True
            else:
                log.error('Unable to successfully contact the REST API: %s: %s', request.status_code, request.text)
                return False

        log.info('Beginning check of the AKRR Rest API...')
        is_up = is_api_up()
        if is_up:
            log.info('REST API is up and running!')
        else:
            exit(1)

    parser.set_defaults(func=handler)


def cli_daemon_checknrestart(parent_parser):
    """check if AKRR daemon is up if not it will restart it"""
    parser = parent_parser.add_parser('checknrestart', description=cli_daemon_checknrestart.__doc__)
    parser.add_argument('-cron', action='store_true', help="for launching by cron, no output on normal operation")

    def handler(args):
        from akrr.daemon import daemon_check_and_start_if_needed
        if args.cron is True:
            # i.e. executed by cron
            #   run same command as separate process (but without -cron)
            #   print output only if return non zero code
            import subprocess
            import sys
            import os
            argv = [sys.executable, os.path.abspath(sys.argv[0])]
            if len(sys.argv) > 0:
                for arg in sys.argv[1:]:
                    if arg != "-cron":
                        argv.append(arg)
            try:
                subprocess.check_output(argv, stderr=subprocess.STDOUT, timeout=120)
            except subprocess.CalledProcessError as e:
                if hasattr(e, 'output'):
                    print(e.output.decode("utf-8"))
        else:
            return daemon_check_and_start_if_needed()

    parser.set_defaults(func=handler)


def cli_daemon_monitor(parent_parser):
    """monitor the activity of Application Remote Runner"""
    parser = parent_parser.add_parser('monitor', description=cli_daemon_monitor.__doc__)

    def handler(_):
        from akrr.daemon import AkrrDaemon
        sch = AkrrDaemon()
        return sch.monitor()

    parser.set_defaults(func=handler)


def cli_daemon_status(parent_parser):
    """print current status of Application Remote Runner"""
    parser = parent_parser.add_parser('status', description=cli_daemon_status.__doc__)

    def handler(_):
        from akrr.daemon import AkrrDaemon
        sch = AkrrDaemon()
        return sch.check_status()

    parser.set_defaults(func=handler)


def cli_daemon_startdeb(parent_parser):
    """launch Application Remote Runner in foreground mode"""
    parser = parent_parser.add_parser('startdeb', description=cli_daemon_startdeb.__doc__)

    parser.add_argument(
        '-th', '--max-task-handlers',
        dest='max_task_handlers',
        default=None, type=int,
        help='Overwrite max_task_handlers from configuration, if 0 tasks are executed from main thread')

    parser.add_argument(
        '-redir', '--redirect-task-processing-to-log-file',
        dest='redirect_task_processing_to_log_file',
        default=None, type=int,
        help='Overwrite redirect_task_processing_to_log_file from configuration')

    def handler(args):
        from akrr.daemon import daemon_start_in_debug_mode
        return daemon_start_in_debug_mode(
            max_task_handlers=args.max_task_handlers,
            redirect_task_processing_to_log_file=args.redirect_task_processing_to_log_file)

    parser.set_defaults(func=handler)


def add_command_setup(parent_parser):
    """Initial AKRR Setup"""
    parser = parent_parser.add_parser('setup', description=add_command_setup.__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Dry run, print commands if possible")

    parser.add_argument(
        "--akrr-db",
        help="mod_akrr2 database location in [user[:password]@]host[:port] format, "
             "missing values will be asked. Default: localhost:3306")
    parser.add_argument(
        "--ak-db",
        help="mod_appkernel database location. Usually same host as XDMoD's databases host. Default: same as akrr")
    parser.add_argument(
        "--xd-db",
        help="XDMoD modw database location. It is XDMoD's databases host. Default: same as akrr")
    parser.add_argument(
        '--stand-alone', action='store_true',
        help="install stand alone AKRR, fake modw db will be installed, normally modw comes with XDMoD.")

    def setup_handler(args):
        """call routine for initial AKRR setup"""
        global dry_run
        dry_run = args.dry_run
        from .setup import AKRRSetup
        return AKRRSetup(
            akrr_db=args.akrr_db,
            ak_db=args.ak_db,
            xd_db=args.xd_db,
            stand_alone=args.stand_alone
        ).run()

    parser.set_defaults(func=setup_handler)


def add_command_setup_update(parent_parser):
    """Update AKRR"""
    # @todo should be option to setup
    parser = parent_parser.add_parser('update', description=add_command_setup.__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Dry run, print commands if possble")

    parser.add_argument(
        "--old-akrr-conf-dir",
        required=True,
        help="location of old AKRR configuration directory")
    parser.add_argument(
        "--akrr-db",
        help="mod_akrr database location in [user[:password]@]host[:port] format, "
             "missing values will be asked. Default: localhost:3306")
    parser.add_argument(
        "--ak-db",
        help="mod_appkernel database location. Usually same host as XDMoD's databases host. Default: same as akrr")
    parser.add_argument(
        "--xd-db",
        help="XDMoD modw database location. It is XDMoD's databases host. Default: same as akrr")
    parser.add_argument(
        '--generate-db-only', action='store_true', help="only generate db")
    parser.add_argument(
        '--stand-alone', action='store_true',
        help="install stand alone akrr, fake modw db (normally comes with XDMoD) will be installed")

    def update_handler(args):
        """call routine for initial AKRR setup"""
        global dry_run
        dry_run = args.dry_run
        from .setup import AKRRSetup
        return AKRRSetup(
            akrr_db=args.akrr_db,
            ak_db=args.ak_db,
            xd_db=args.xd_db,
            update=True,
            stand_alone=args.stand_alone,
            generate_db_only=args.generate_db_only,
            old_akrr_conf_dir=args.old_akrr_conf_dir
        ).run()

    parser.set_defaults(func=update_handler)


def add_command_resource(parent_parser):
    """resource manipulation"""
    parser = parent_parser.add_parser('resource', description=add_command_resource.__doc__)
    subparsers = parser.add_subparsers(title="commands for resource")

    # config
    cli_resource_add(subparsers)

    # deploy
    cli_resource_deploy(subparsers)

    # list
    cli_resource_list(subparsers)

    # remove
    # cli_resource_remove(subparsers)


def cli_resource_add(parent_parser):
    """configure new resource to AKRR"""
    parser = parent_parser.add_parser('add', description=cli_resource_add.__doc__)

    parser.add_argument(
        '--dry-run', action='store_true', help="Dry Run, just show the changes without doing them")
    parser.add_argument(
        '--minimalistic', action='store_true',
        help="Minimize questions number, configuration files will be edited manually")
    parser.add_argument(
        '--no-ping', action='store_true', help="do not run ping to test headnode name")

    def handler(args):
        from .resource_add import resource_add
        return resource_add(args)

    parser.set_defaults(func=handler)


def cli_resource_deploy(parent_parser):
    """deploy input files and scripts to resource"""
    parser = parent_parser.add_parser('deploy',
                                      description=cli_resource_deploy.__doc__)
    parser.add_argument(
        '-r', '--resource', required=True, help="name of resource for validation and deployment'")
    parser.add_argument('-a', '--appkernel', default="test",
                        help='Specify which application kernel to use as probe.'
                             ' Default is test, special appkernel for deployment')
    parser.add_argument('-n', '--nodes', type=int, default=2,
                        help='Specify how many nodes the new task should be setup with. Default=2')
    parser.add_argument(
        '-cf', '--checking-frequency', default=5.0, type=float, help="checking frequency of test job, default is 5 sec")

    parser.add_argument(
        '--dry-run', action='store_true', help="Dry Run, just show the changes without doing them")

    def resource_deploy_handler(args):
        from .resource_deploy import resource_deploy
        return resource_deploy(args)

    parser.set_defaults(func=resource_deploy_handler)


def cli_resource_remove(parent_parser):
    """remove input files and scripts to resource and working directories"""
    parser = parent_parser.add_parser('remove',
                                      description=cli_resource_remove.__doc__)
    parser.add_argument(
        '-r', '--resource', required=True, help="name of resource for validation and deployment'")

    def handler(_):
        raise NotImplementedError()
        # from .resource_remove import resource_remove
        # return resource_remove(vars(args))

    parser.set_defaults(func=handler)


def cli_resource_list(parent_parser):
    """list all resource"""
    parser = parent_parser.add_parser('list', description=cli_app_list.__doc__)

    def handler(_):
        from akrr.util import log
        from akrr import cfg

        log.info("Resource:\n    "+"\n    ".join(list(cfg.resources.keys())))

    parser.set_defaults(func=handler)


def add_command_app(parent_parser):
    """application manipulation"""
    parser = parent_parser.add_parser('app', description=add_command_resource.__doc__)
    subparsers = parser.add_subparsers(title="commands for appkernels")

    cli_app_add(subparsers)
    cli_app_validate(subparsers)
    cli_app_list(subparsers)


def cli_app_add(parent_parser):
    """configure new app on resource to AKRR"""
    parser = parent_parser.add_parser('add',
                                      description=cli_app_add.__doc__)

    parser.add_argument(
        '-r', '--resource', required=True, help="name of resource")
    parser.add_argument(
        '-a', '--appkernel', required=True, help="name of app kernel")
    parser.add_argument(
        '--dry-run', action='store_true', help="Dry Run, just show the changes without doing them")

    def handler(args):
        from akrr.app import app_add
        app_add(args.resource, args.appkernel, args.dry_run)

    parser.set_defaults(func=handler)


def cli_app_validate(parent_parser):
    """validate that app can run on resource"""
    parser = parent_parser.add_parser('validate',
                                      description=cli_app_validate.__doc__)

    parser.add_argument(
        '-r', '--resource', required=True, help="name of resource")
    parser.add_argument(
        '-a', '--appkernel', required=True, help="name of app kernel")
    parser.add_argument(
        '-n', '--nodes', required=True, help='Specify how many nodes the new task should be setup with.')

    def handler(args):
        from akrr.app_validate import app_validate
        app_validate(args.resource, args.appkernel, int(args.nodes))

    parser.set_defaults(func=handler)


def cli_app_list(parent_parser):
    """list all appkernels"""
    parser = parent_parser.add_parser('list', description=cli_app_list.__doc__)

    def handler(_):
        from akrr.util import log
        from akrr.app import app_list
        log.info("Appkernels:\n"+"\n    ".join(app_list()))

    parser.set_defaults(func=handler)


def add_command_task(parent_parser):
    """tasks manipulation"""
    parser = parent_parser.add_parser('task', description=add_command_task.__doc__)
    subparsers = parser.add_subparsers(title="commands for tasks")

    cli_task_new(subparsers)
    cli_task_list(subparsers)
    cli_task_delete(subparsers)


def cli_task_new(parent_parser):
    """Create new task"""
    parser = parent_parser.add_parser('new', description=cli_task_new.__doc__)

    parser.add_argument(
        '-r', '--resource', required=True, help="name of resource")
    parser.add_argument(
        '-a', '--appkernel', required=True, help="name of app kernel")
    parser.add_argument(
        '-n', '--nodes', required=True, help='Specify how many nodes the new task should be setup with.')
    parser.add_argument(
        '-s', '--time-to-start',
        help='Specify what time the newly created task should start. If it is not specified then start now.')
    parser.add_argument(
        '-t0', '--time-window-start', help='Specify the time at which the random distribution begins')
    parser.add_argument(
        '-t1', '--time-window-end', help='Specify the time at which the random distribution ends')
    parser.add_argument(
        '-p', '--periodicity', help='Specify the amount of time that should elapse between executions.')
    parser.add_argument(
        '-test-run', '--test-run', action='store_true',
        help='Run appkernel on resource even if it is not validated yet.')
    parser.add_argument(
        '--dry-run', action='store_true', help="Dry Run, just show the changes without doing them")
    parser.add_argument(
        '--gen-batch-job-only', action='store_true',
        help="Generate batch job script file without actually submitting task, if dry-run is on it will only print it")

    def handler(args):
        kwargs = {k: v for k, v in vars(args).items() if k not in ['func', 'verbose']}
        from akrr.task_api import task_new
        task_new(**kwargs)

    parser.set_defaults(func=handler)


def cli_task_list(parent_parser):
    """list all tasks"""
    parser = parent_parser.add_parser('list', description=cli_task_list.__doc__)

    parser.add_argument(
        '-r', '--resource', help="filter by resource")
    parser.add_argument(
        '-a', '--appkernel', help="filter by app kernel")
    parser.add_argument(
        '-scheduled', '--scheduled', action='store_true', help="show only scheduled for future execution tasks")
    parser.add_argument(
        '-active', '--active', action='store_true', help="show only currently running tasks")

    def handler(args):
        from akrr.task_api import task_list
        kwargs = {k: v for k, v in vars(args).items() if k not in ['func', 'verbose']}
        if kwargs["active"] is False and kwargs["scheduled"] is False:
            # by default show both
            kwargs["active"] = True
            kwargs["scheduled"] = True
        task_list(**kwargs)

    parser.set_defaults(func=handler)


def cli_task_delete(parent_parser):
    """Remove task from schedule"""
    parser = parent_parser.add_parser('delete', description=cli_task_list.__doc__)

    parser.add_argument(
        '-t', '--task-id', required=True, type=int, help="task id")

    def handler(args):
        from akrr.task_api import task_delete
        task_delete(args.task_id)

    parser.set_defaults(func=handler)


def cli_enable(parent_parser):
    """enable resource, app or specific app on a particular resource"""
    parser = parent_parser.add_parser('enable',
                                      description=cli_app_add.__doc__)

    parser.add_argument(
        '-r', '--resource', required=True, help="name of resource")
    parser.add_argument(
        '-a', '--appkernel', required=True, help="name of app kernel")
    parser.add_argument(
        '--dry-run', action='store_true', help="Dry Run, just show the changes without doing them")

    def handler(args):
        from akrr.app import resource_app_enable
        resource_app_enable(args.resource, args.appkernel, args.dry_run)

    parser.set_defaults(func=handler)


def add_command_archive(parent_parser):
    """AK runs output, logs, pickels and batch jobs script manipulation"""
    parser = parent_parser.add_parser('archive',  description=add_command_archive.__doc__)
    subparsers = parser.add_subparsers(title="commands for archive")
    #parser.add_argument(
    #    '-udl', '--update-dir-layout', action='store_true', help="update dir layout")

    cli_archive_remove_state_dumps(subparsers)
    cli_archive_remove_tasks_workdir(subparsers)
    cli_archive_update_layout(subparsers)


def cli_archive_remove_state_dumps(parent_parser):
    """remove state dumps"""
    parser = parent_parser.add_parser(
        'remove-tasks-state-dumps', description=cli_archive_remove_state_dumps.__doc__)

    parser.add_argument(
        '--days', required=True, type=int, help="do operations for tasks older than `--days`")
    parser.add_argument(
        '-r', '--resource', help="comma separated names of resources")
    parser.add_argument(
        '-a', '--appkernel', help="comma separated names of app kernels")
    parser.add_argument('--comp-task-dir', help="complete tasks directory")
    parser.add_argument('-d', '--dry-run', action='store_true', help="dry run")

    def handler(args):
        from akrr.archive import Archive
        Archive(args.dry_run, args.comp_task_dir).remove_tasks_state_dumps(
            args.days, args.resource, args.appkernel)

    parser.set_defaults(func=handler)


def cli_archive_remove_tasks_workdir(parent_parser):
    """remove task workdir, normally it should not be copied to AKRR at all."""
    parser = parent_parser.add_parser(
        'remove-tasks-workdir', description=cli_archive_remove_state_dumps.__doc__)

    parser.add_argument(
        '--days', required=True, type=int, help="do operations for tasks older than `--days`")
    parser.add_argument(
        '-r', '--resource', help="comma separated names of resources")
    parser.add_argument(
        '-a', '--appkernel', help="comma separated names of app kernels")
    parser.add_argument('--comp-task-dir', help="complete tasks directory")
    parser.add_argument('-d', '--dry-run', action='store_true', help="dry run")

    def handler(args):
        from akrr.archive import Archive
        Archive(args.dry_run, args.comp_task_dir).remove_tasks_workdir(
            args.days, args.resource, args.appkernel)

    parser.set_defaults(func=handler)


def cli_archive_update_layout(parent_parser):
    """update resource/appkernel/task to resource/appkernel/year/month/task layout"""
    parser = parent_parser.add_parser(
        'update-layout', description=cli_archive_update_layout.__doc__)

    parser.add_argument(
        '-r', '--resource', help="comma separated names of resources")
    parser.add_argument(
        '-a', '--appkernel', help="comma separated names of app kernels")
    parser.add_argument('--comp-task-dir', help="complete tasks directory")
    parser.add_argument('-d', '--dry-run', action='store_true', help="dry run")

    def handler(args):
        from akrr.archive import Archive
        Archive(args.dry_run, args.comp_task_dir).update_layout(
            args.resource, args.appkernel)

    parser.set_defaults(func=handler)


def add_command_update(parent_parser):
    """AKRR update routings"""
    parser = parent_parser.add_parser('update',  description=add_command_archive.__doc__)
    subparsers = parser.add_subparsers(title="commands for update")
    #parser.add_argument(
    #    '-udl', '--update-dir-layout', action='store_true', help="update dir layout")

    cli_update_db_compare(subparsers)
    cli_update_rename_appkernels(subparsers)


def cli_update_db_compare(parent_parser):
    """Copy mod_akrr database"""
    parser = parent_parser.add_parser(
        'db-compare', description=cli_archive_remove_state_dumps.__doc__)
    parser.add_argument(
        "--src",
        help="mod_akrr source database location in [user[:password]@]host[:port][:/db_name] format, "
             "missing values will be asked. Default: akrruser:@localhost:3306:/mod_akrr")
    parser.add_argument(
        "--dest",
        help="mod_akrr database location in [user[:password]@]host[:port][:/db_name] format, "
             "missing values will be asked. Default: akrruser:@localhost:3306:/mod_akrr")
    parser.add_argument(
        '-r', '--resource', help="comma separated names of resources to copy")
    parser.add_argument('-d', '--dry-run', action='store_true', help="dry run")

    def handler(args):
        from akrr.update import mod_akrr_db_compare
        mod_akrr_db_compare(args.src, args.dest)

    parser.set_defaults(func=handler)


def cli_update_rename_appkernels(parent_parser):
    """Rename appkernels from long to short format"""
    parser = parent_parser.add_parser(
        'rename-appkernels', description=cli_archive_remove_state_dumps.__doc__)
    parser.add_argument(
        "--mod-akrr", default='akrruser:@localhost:3306:/mod_akrr',
        help="mod_akrr source database location in [user[:password]@]host[:port][:/db_name] format, "
             "missing values will be asked. Default: akrruser:@localhost:3306:/mod_akrr")
    parser.add_argument(
        "--mod-appkernel", default='akrruser:@localhost:3306:/mod_appkernel',
        help="mod_appkernel database location in [user[:password]@]host[:port][:/db_name] format, "
             "missing values will be asked. Default: akrruser:@localhost:3306:/mod_appkernel")
    parser.add_argument('-d', '--dry-run', action='store_true', help="dry run")

    def handler(args):
        from akrr.update import rename_appkernels
        rename_appkernels(args.mod_akrr, args.mod_appkernel, args.dry_run)

    parser.set_defaults(func=handler)
