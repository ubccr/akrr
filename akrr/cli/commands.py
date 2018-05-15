
# Keep CLI commands setup here outside of implementation, to avoid premature cfg loading


def add_command_setup(parent_parser):
    """Initial AKRR Setup"""
    parser = parent_parser.add_parser('setup', description=add_command_setup.__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Dry run, print commands if possble")

    parser.add_argument(
        "--akrr-db",
        default="localhost:3306",
        help="mod_akrr database location in [user[:password]@]host[:port] format, "
             "missing values willbe asked. Default: localhost:3306")
    parser.add_argument(
        "--ak-db",
        default="localhost:3306",
        help="mod_appkernel database location. Usually same host as XDMoD's databases host. Default: localhost:3306")
    parser.add_argument(
        "--xd-db",
        default="localhost:3306",
        help="XDMoD modw database location. It is XDMoD's databases host. Default: localhost:3306")

    def setup_handler(args):
        """call routine for initial AKRR setup"""
        global dry_run
        dry_run = args.dry_run
        from .setup import AKRRSetup
        return AKRRSetup(
            akrr_db=args.akrr_db,
            ak_db=args.akrr_db,
            xd_db=args.akrr_db
        ).run()

    parser.set_defaults(func=setup_handler)


def add_command_resource(parent_parser):
    """resource manipulation"""
    parser = parent_parser.add_parser('resource', description=add_command_resource.__doc__)
    subparsers = parser.add_subparsers(title="commands for resource")

    # config
    cli_resource_add(subparsers)

    # deploy
    cli_resource_deploy(subparsers)

    # remove
    cli_resource_remove(subparsers)


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

    def handler(args):
        from .resource_remove import resource_remove
        return resource_remove(vars(args))

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

    def handler(args):
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
        '--show-batch-job', action='store_true',
        help="Generate batch job script file without actually submitting task, if dry-run is on it will only print it")

    def handler(args):
        kwargs = {k: v for k, v in vars(args).items() if k not in ['func', 'verbose']}
        from akrr.task import task_new
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
        from akrr.task import task_list
        kwargs = {k: v for k, v in vars(args).items() if k not in ['func', 'verbose']}
        if kwargs["active"] is False and kwargs["scheduled"] is False:
            # by default show both
            kwargs["active"] = True
            kwargs["scheduled"] = True
        task_list(**kwargs)

    parser.set_defaults(func=handler)