
# Keep CLI commands setup here outside of implementation, to avoid premature cfg loading


def add_command_setup(parent_parser):
    """Initial AKRR Setup"""
    parser = parent_parser.add_parser('setup',
                                      description=add_command_setup.__doc__)
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
    parser = parent_parser.add_parser('add',
                                      description=cli_resource_add.__doc__)

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
