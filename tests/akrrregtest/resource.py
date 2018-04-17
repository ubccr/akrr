def cli_add_command(parent_parser):
    """
    Setup (initial configuration) of AKRR.
    """
    parser = parent_parser.add_parser("resource", description=cli_add_command.__doc__)
    
    def runit(args):      
        from .util import print_importent_env
        print_importent_env()
        
        print("Kuku")
        
    parser.set_defaults(func=runit)
    