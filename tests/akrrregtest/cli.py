import logging as log
import argparse

import akrrregtest

class cli:
    def __init__(self):
        log.basicConfig(
            level=log.INFO,
            format="[%(asctime)s - %(levelname)s] %(message)s"
        )
        
        self.root_parser = argparse.ArgumentParser(description="command line interface to AKRR regression tests")
        self.root_parser.add_argument("-v", "--verbose", action="store_true", help="turn on verbose logging")
        self.root_parser.add_argument("-cfg", "--cfg", default="akrrregtest.conf", help="configuration for the test, default: akrrregtest.conf")
        self.root_parser.add_argument("--dry-run", action="store_true", help="Dry run, print commands if possble")
        self.subparsers = self.root_parser.add_subparsers(title="commands")
        
        self.add_command_build()
        self.add_command_install()
        self.add_command_setup()
    
    def process_common_args(self,cli_args):
        if "verbose" in cli_args and cli_args.verbose:
            log.basicConfig(level=log.DEBUG)
            log.getLogger().setLevel(log.DEBUG)
        
        if "cfg" in cli_args:
            pass
        
        if "dry_run" in cli_args and cli_args.dry_run:
            akrrregtest.dry_run=cli_args.dry_run
    
    def add_command_build(self): 
        """commands for create redistributive, like rpm or else"""
        parser = self.subparsers.add_parser("build",
            description="create redistributive, like rpm or else")
        
        def runit(args):
            log.warning("add_command_build is not implemented")
        parser.set_defaults(func=runit)
        
    def add_command_install(self): 
        """commands for do installation"""
        parser = self.subparsers.add_parser("build",
            description="install code")
        
        def runit(args):
            log.warning("add_command_install is not implemented")
        parser.set_defaults(func=runit)
        
    def add_command_setup(self):
        """
        Setup (initial configuration) of AKRR.
        
        By default performs setup in akrr config in default location i.e. $HOME/akrr.
        
        Options --in-src and --akrr-conf change that behaviour.
        
        In all cases akrr command line interface will be taken from $PATH
        """
        parser = self.subparsers.add_parser("setup", description=self.add_command_setup.__doc__)
        
        parser.add_argument("--in-src", action="store_true", help="install akrr in source")
        parser.add_argument("--akrr-conf", help="location of feture AKRR_CONF")
        
        def runit(args):
            if args.akrr_conf!=None and args.in_src==True:
                msg="Can not specify --in-src and --akrr-conf at the same time"
                log.critical(msg)
                exit(1)
                #raise Exception(msg)
            log.warning("add_command_setup is not implemented")
            print(args)
        parser.set_defaults(func=runit)
    
    def run(self):
        """execute what asked in command line"""
        log.info("AKRR Regression Tests")
        cli_args = self.root_parser.parse_args()
        
        self.process_common_args(cli_args)
        
        if hasattr(cli_args, "func"):
            cli_args.func(cli_args)
        else:
            log.error("There is no command specified!")
        
        
    