import os
from akrr.util import log
import argparse


class CLI:
    def __init__(self):
        log.basicConfig(
            level=log.INFO,
            format="[%(asctime)s -ART- %(levelname)s] %(message)s"
        )

        self.root_parser = argparse.ArgumentParser(description="command line interface to AKRR regression tests")
        self.root_parser.add_argument("-v", "--verbose", action="store_true", help="turn on verbose logging")
        self.root_parser.add_argument("-vv", "--very-verbose", action="store_true", help="turn on very verbose logging")
        self.root_parser.add_argument("-cfg", "--cfg", default="akrrregtest.conf",
                                      help="configuration for the test, default: akrrregtest.conf")
        self.root_parser.add_argument("--dry-run", action="store_true", help="Dry run, print commands if possble")
        self.root_parser.add_argument("--which-akrr", help="Path to akrr to use, default is akrr, i.e. find from PATH")

        self.subparsers = self.root_parser.add_subparsers(title="commands")

        self.add_command_build()
        self.add_command_install()

        from .setup import cli_add_command as add_command_setup
        add_command_setup(self.subparsers)

        from .remove import cli_add_command as add_command_remove
        add_command_remove(self.subparsers)

        from .resource import cli_resource
        cli_resource(self.subparsers)

    @staticmethod
    def process_common_args(cli_args):
        from . import cfg

        if "cfg" in cli_args:
            cfg.load_cfg(cli_args.cfg)

        if "verbose" in cli_args and cli_args.verbose:
            log.basicConfig(level=log.DEBUG)
            log.getLogger().setLevel(log.DEBUG)
            cfg.verbose = True

        if "very_verbose" in cli_args and cli_args.very_verbose:
            log.basicConfig(level=1)
            log.getLogger().setLevel(1)

        if "dry_run" in cli_args and cli_args.dry_run:
            cfg.dry_run = cli_args.dry_run
        if "which_akrr" in cli_args and cli_args.which_akrr is not None:
            cfg.which_akrr = cli_args.which_akrr
            if cfg.which_akrr != "akrr" and not os.path.exists(cfg.which_akrr):
                log.critical("Path to akrr is incorrect. Can not find " + cfg.which_akrr)

        cfg.set_default_value_for_unset_vars()

    def add_command_build(self):
        """commands for create redistributive, like rpm or else"""
        parser = self.subparsers.add_parser("build",
                                            description="create redistributive, like rpm or else")

        def run_it(_):
            log.warning("add_command_build is not implemented")

        parser.set_defaults(func=run_it)

    def add_command_install(self):
        """commands for do installation"""
        parser = self.subparsers.add_parser("build",
                                            description="install code")

        def run_it(_):
            log.warning("add_command_install is not implemented")

        parser.set_defaults(func=run_it)

    def run(self):
        """execute what asked in command line"""
        log.info("AKRR Regression Tests")
        cli_args = self.root_parser.parse_args()

        self.process_common_args(cli_args)

        if hasattr(cli_args, "func"):
            cli_args.func(cli_args)
        else:
            log.error("There is no command specified!")
