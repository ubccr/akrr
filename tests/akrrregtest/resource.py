"""Execution of akrr resource config"""
from akrr import log


def resource_add(**kwargs):
    log.info("resource config: Initial resource configuration")


def cli_resource_add(parent_parser):
    """Configure new resource to AKRR"""
    parser = parent_parser.add_parser('add',
                                      description=cli_resource_config.__doc__)

    def handler(args):
        return resource_add(**vars(args))

    parser.set_defaults(func=handler)


def cli_resource(parent_parser):
    """Resource manipulation"""
    parser = parent_parser.add_parser('resource', description=cli_resource.__doc__)
    subparsers = parser.add_subparsers(title="commands for resource")

    # config
    cli_resource_add(subparsers)
