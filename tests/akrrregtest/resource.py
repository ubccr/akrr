def cli_add_command(parent_parser):
    """
    Setup (initial configuration) of AKRR.
    """
    parser = parent_parser.add_parser("resource", description=cli_add_command.__doc__)
    
    def run_it(args):
        from .util import print_important_env
        print_important_env()
        
        print("Kuku")
        
    parser.set_defaults(func=run_it)
