import logging as log
import argparse

import akrrregtest
from _ast import arg

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
        #self.root_parser.add_argument("--in-src", action="store_true", help="install akrr in source")
        #self.root_parser.add_argument("--akrr-conf", help="location of feture AKRR_CONF")

        self.subparsers = self.root_parser.add_subparsers(title="commands")
        
        self.add_command_build()
        self.add_command_install()
        self.add_command_setup()
        self.add_command_remove()
    
    def process_common_args(self,cli_args):
        from . import cfg
        
        if "cfg" in cli_args:
            cfg.loadCfg(cli_args.cfg)
        
        if "verbose" in cli_args and cli_args.verbose:
            log.basicConfig(level=log.DEBUG)
            log.getLogger().setLevel(log.DEBUG)
        
        if "dry_run" in cli_args and cli_args.dry_run:
            cfg.dry_run=cli_args.dry_run
        
        cfg.set_default_value_for_unset_vars()
    
    def add_command_remove(self):
        """remove AKRR installation"""
        parser = self.subparsers.add_parser("remove", description=self.add_command_setup.__doc__)
        
        parser.add_argument("-a","--all", action="store_true", help="remove everything except sources")
        parser.add_argument("--db-all", action="store_true", help="remove from DB all AKRR related entities.")
        parser.add_argument("--db-akrr", action="store_true", help="remove from DB mod_akrr")
        parser.add_argument("--db-appkernel", action="store_true", help="remove from DB mod_appkernel")
        parser.add_argument("--db-user", action="store_true", help="remove user from DBs.")
        parser.add_argument("--conf-dir", action="store_true", help="remove conf directory")
        parser.add_argument("--log-dir", action="store_true", help="remove log directory")
        parser.add_argument("--bashrc", action="store_true", help="remove akrr from bashrc")
        parser.add_argument("--crontab", action="store_true", help="remove akrr from crontab")
        parser.add_argument("--crontab-remove-mailto", action="store_true", help="remove mail to from crontab records")
        
        def runit(args):
            if args.db_all:
                args.db_akrr=True
                args.db_appkernel=True
                args.db_user=True
            if args.all:
                args.db_akrr=True
                args.db_appkernel=True
                args.db_user=True
                args.conf_dir=True
                args.log_dir=True
                args.bashrc=True
                args.crontab=True
                args.crontab_remove_mailto=True
            
            kwarg=vars(args)
            #remove not needed keys
            kwarg.pop("func")
            kwarg.pop("cfg")
            kwarg.pop("dry_run")
            kwarg.pop("verbose")
            
            kwarg.pop("db_all")
            kwarg.pop("all")
            
            
            from .util import print_importent_env
            print_importent_env()
            print(kwarg)
            
            from .remove import remove
            remove(**kwarg)
            
        parser.set_defaults(func=runit)
        
        
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
        """
        parser = self.subparsers.add_parser("setup", description=self.add_command_setup.__doc__)
        
        def runit(args):
            if args.akrr_conf!=None and args.in_src==True:
                msg="Can not specify --in-src and --akrr-conf at the same time"
                log.critical(msg)
                exit(1)
                #raise Exception(msg)
            log.warning("add_command_setup is not implemented")
            
            print(args)
            from .util import print_importent_env
            print_importent_env()
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
        
        
    