

def cli_add_command(parent_parser): 
    """resource manipulation"""
    parser = parent_parser.add_parser('resource', description=cli_add_command.__doc__)
    subparsers = parser.add_subparsers(title="commands for resource")
    
    #config
    from .resource_config import cli_resource_config
    cli_resource_config(subparsers)

    #deploy
    from .resource_deploy import cli_resource_deploy
    cli_resource_deploy(subparsers)
