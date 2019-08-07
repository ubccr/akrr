"""
A script that will provide command line access to the Application Remote Runner
functionality.

"""
import argparse

from akrr.util import log


def reprocess_parsed(args):
    if not (args.resource and args.appkernel):
        log.error(
            'Please provide a resource, app')
        exit(1)
    resource = args.resource
    appkernel = args.appkernel
    time_start = args.time_start
    time_end = args.time_end
    verbose = args.verbose

    from akrr import daemon
    sch = daemon.AkrrDaemon(adding_new_tasks=True)
    sch.reprocess_completed_tasks(resource, appkernel, time_start, time_end, verbose)


def wall_time_parsed(args):
    if not args.list and not (args.resource and
                              args.appkernel and
                              args.nodes and
                              args.walltime):
        log.error(
            'Please provide a resource, app, node count and wall time.')
        exit(1)

    listing = args.list
    resource = args.resource
    app = args.appkernel
    nodes = args.nodes
    walltime = args.walltime
    comments = args.comments
    node_list = [node.strip() for node in nodes.split(',')] if ',' in nodes else list(nodes)

    for nodes in node_list:
        data = {
            'resource_params': "{'nnodes':%d}" % (int(nodes),) if nodes else "{}",
            'app_param': '{}',
            'walltime': walltime,
            'comments': comments
        }
        try:
            from akrr import akrrrestclient

            result = akrrrestclient.post(
                '/walltime/%s/%s' % (resource, app),
                data=data) if not listing else \
                akrrrestclient.get(
                    '/walltime/%s/%s' % (resource, app),
                    data=data)
            if result.status_code == 200:
                if not listing:
                    log.info('Successfully updated wall time (resource %s: application kernel: %s nodes: %d).' % (
                             resource, app, nodes))
                else:
                    log.info(
                        'Successfully queried walltime records. \n%s',
                        result.text)
            else:
                log.error('something went wrong. %s:%s',
                          result.status_code,
                          result.text)
        except Exception as e:
            import traceback
            log.error('''
            An error occured while communicating
            with the REST API.
            %s: %s
            '''.strip(),
                      e.args[0] if len(e.args) > 0 else '',
                      e.args[1] if len(e.args) > 1 else '')
            print(traceback.print_exc())


class CLI:
    """
    AKRR command line interface
    """
    def __init__(self):
        import sys

        short_log_prefix = True
        if len(sys.argv) >= 3:
            i = 1
            while i+1 < len(sys.argv):
                if sys.argv[i] == "daemon" and sys.argv[i+1] in ("start", "startdeb"):
                    short_log_prefix = False
                i = i + 1

        if short_log_prefix:
            log.basicConfig(
                level=log.INFO,
                format="[%(levelname)s] %(message)s"
            )
        else:
            log.basicConfig(
                level=log.INFO,
                format="[%(asctime)s - %(levelname)s] %(message)s"
            )

        self.root_parser = argparse.ArgumentParser(description='command line interface to AKRR')
        self.root_parser.add_argument('-v', '--verbose', action='store_true', help="turn on verbose logging")

        self.subparsers = self.root_parser.add_subparsers(title='commands')

        from .commands import add_command_daemon
        add_command_daemon(self.subparsers)

        from .commands import add_command_setup
        add_command_setup(self.subparsers)

        from .commands import add_command_resource
        add_command_resource(self.subparsers)

        from .commands import add_command_app
        add_command_app(self.subparsers)

        from .commands import add_command_task
        add_command_task(self.subparsers)

        from .commands import add_command_archive
        add_command_archive(self.subparsers)

        from .commands import add_command_update
        add_command_update(self.subparsers)

        self.verbose = False

    def process_common_args(self, cli_args):
        """
        Process arguments common for all commands. Currently only verbose.
        """
        if "verbose" in cli_args and cli_args.verbose:
            log.verbose = True
            log.basicConfig(level=log.DEBUG)
            log.getLogger().setLevel(log.DEBUG)
            self.verbose = True

    def run(self, args=None):
        """parse arguments and execute requested commands"""
        # PARSE: the command line parameters the user provided.
        cli_args = self.root_parser.parse_args(args=args)

        self.process_common_args(cli_args)

        # EXECUTE: the function provided in the '.set_defaults(func=...)'
        if hasattr(cli_args, "func"):
            return cli_args.func(cli_args)

        log.error("There is no command specified!")
        return None
