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
    def __init__(self):
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

        self.verbose = False

    def process_common_args(self, cli_args):
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
        return

        parser = argparse.ArgumentParser(description='command line interface to AKRR')
        parser.add_argument('-v', '--verbose', action='store_true', help="turn on verbose logging")

        subparsers = parser.add_subparsers()

        query_parser = subparsers.add_parser('query',
                                             description='Query XDMoD for a list of available resource and update the AKRR database.')
        query_parser.add_argument('-d', '--dryrun', action='store_true',
                                  help='Only display data. Do not update the database.')
        query_parser.add_argument('-v', '--verbose', action='store_true',
                                  help='Increase the level of output verbosity.')
        query_parser.add_argument('-r', '--resource', help='Only query / update for the provided resource.')
        query_parser.add_argument('-e', '--exact', action='store_true',
                                  help='Only useful if a resource has been provided. Will only consider exact matches.')
        query_parser.set_defaults(func=query_parsed)

        on_parser = subparsers.add_parser('on',
                                          description='Enable a specific application kernel or all application kernels for a given resource.')
        on_parser.add_argument('-a', '--application', help='Enable a particular application on the provided resource')
        on_parser.add_argument('resource', help='The resource on which to perform the enabling of application kernels.')
        on_parser.set_defaults(func=on_parsed)

        off_parser = subparsers.add_parser('off',
                                           description='Disable a specific application kernel or all application kernels for a given resource.')
        off_parser.add_argument('-a', '--application', help='Disable a particular application on the provided resource')
        off_parser.add_argument('resource',
                                help='The resource on which to perform the disabling of application kernels.')
        off_parser.set_defaults(func=off_parsed)

        wall_time_parser = subparsers.add_parser('walltime',
                                                 description='''Update or insert a new wall time limit for the tasks
                                                 matching the specified parameters.
                                                 ''')
        wall_time_parser.add_argument('-r',
                                      '--resource',
                                      help='''Specify the resource filter that the new wall time should
                                      be applied to
                                      ''')
        wall_time_parser.add_argument('-a',
                                      '--appkernel',
                                      help='''Specify the application filter that the wall time should
                                      be applied to.
                                      ''')
        wall_time_parser.add_argument('-n',
                                      '--nodes',
                                      help='''Specify the number of nodes filter that the wall time should
                                      be applied to.
                                      ''')
        wall_time_parser.add_argument('-w',
                                      '--walltime',
                                      help='''Specify the wall time value that should be used during
                                      update or insert operation.
                                      ''')
        wall_time_parser.add_argument('-c',
                                      '--comments',
                                      help='''Comments''')
        wall_time_parser.add_argument('-l',
                                      '--list',
                                      action='store_true',
                                      help='''List the wall time records that have been entered already. Providing
                                      this switch allows the resource (-r), appkernel (-a), nodes (-n) and walltime
                                      (-w) arguments to become optional. When provided they with 'list' they will
                                      filter the records to be returned.
                                      ''')

        wall_time_parser.set_defaults(func=wall_time_parsed)

        reprocess = subparsers.add_parser('reprocess',
                                          description='Reparce the output from previously executed tasks')
        reprocess.add_argument('-r', '--resource', help='resource for update')
        reprocess.add_argument('-a', '--appkernel', help='application kernel for update')
        reprocess.add_argument('-t0', '--time_start', help='Start time for update')
        reprocess.add_argument('-t1', '--time_end', help='End time for update')
        reprocess.add_argument('-v', '--verbose', action='store_true', help='Increase the level of output verbosity.')
        reprocess.set_defaults(func=reprocess_parsed)


if __name__ == '__main__':
    CLI().run()
