"""
A script that will provide command line access to the Application Remote Runner
functionality.

"""
from akrr.util import log

import os
import argparse


# NOTE: do not globally import akrr.cfg or other modules which invoke akrr.cfg


def tuples_to_dict(*tuples):
    """
    A helper method that only returns the tuples that have a non-None value
    """
    results = {}
    if tuples is not None:
        for i in range(0, len(tuples)):
            (key, value) = tuples[i]
            if value is not None:
                results.update({key: value})
    return results


def insert_resources(resources):
    """
    insert the provided resources (dict) into the mod_appkernel database.

    :type resources dict

    :param resources: a dict of resources that should be inserted into the
                      mod_appkernel.resource database.
    :return: void
    """
    from akrr import cfg
    
    if resources is not None and len(resources) > 0:

        parameters = tuple([(resource['name'], int(resource['id']), False) for (resource) in resources])
        resources_parameters = tuple([(resource['name'], int(resource['id'])) for (resource) in resources])

        connection, cursor = cfg.getAKDB()
        with connection:
            cursor.executemany('''
            INSERT INTO `mod_appkernel`.`resource`
            (resource, xdmod_resource_id, visible)
            VALUES(%s, %s, %s)
            ''', parameters)
            cursor.executemany('''
            INSERT INTO `mod_akrr`.`resources`
            (name, xdmod_resource_id)
            VALUES(%s, %s)
            ''', resources_parameters)


def insert_resource(resource):
    """
    Insert the provided resource (dict) into the mod_appkernel database.

    :type resource dict

    :param resource:
    :return: void
    """
    from akrr import cfg
    if resource is not None:
        name, m_id = resource
        connection, cursor = cfg.getAKDB()
        with connection:
            cursor.execute('''
            INSERT INTO `mod_appkernel`.`resource`
            (resource, xdmod_resource_id, visible)
            VALUES(%s, %s, %s)
            ''', (name, m_id, False))
            cursor.execute('''
            INSERT INTO `mod_akrr`.`resources`
            (name, xdmod_resource_id)
            VALUES(%s, %s)
            ''', (name, m_id))


def retrieve_resources():
    """
    Retrieve all resources currently present in the XDMoD database.


    :return: a dict representation of the resourcefact table ( name, id )
    """
    from akrr import cfg
    connection, cursor = cfg.getXDDB(True)
    with connection:
        cursor.execute("""
        SELECT name, id from `modw`.`resourcefact`;
        """)
        rows = cursor.fetchall()

    return rows


def retrieve_resource(resource, exact):
    """
    Retrieve the provided resource from XDMoD's database.

    :type resource str

    :param resource: the name of the resource to retrieve
    :return: a json encoded version of the record in `modw`.`resourcefact` identified by
    """
    from akrr import cfg
    if resource is None or len(resource) < 1:
        raise AssertionError('provided resource must not be empty.')

    connection, cursor = cfg.getXDDB(True)

    with connection:
        query = """
        SELECT name, id FROM `modw`.`resourcefact` AS RF WHERE RF.NAME LIKE %s
        """ if not exact else """
        SELECT name, id FROM `modw`.`resourcefact` AS RF WHERE RF.NAME = %s
        """

        parameter = (resource + "%", ) if not exact else (resource, )

        cursor.execute(query, parameter)
        rows = cursor.fetchall()

    return rows


def retrieve_task_status():
    pass


def retrieve_tasks(resource, application):
    """
    Retrieve the list of currently scheduled tasks ( resource / application pairings ) from
    mod_akrr.

    :type resource str
    :type application str

    :param resource: filter the results by the provided resource
    :param application: filter the results by the provided application
    :return: a dict representation of the mod_akrr.SCHEDULEDTASKS table
    """
    data = {
        'application': application,
        'resource': resource
    }
    from akrr import akrrrestclient

    try:
        akrrrestclient.get_token()
    except Exception:
        log.error('''
                An error occured while attempting to retrieve a token
                from the REST API.
                ''')
    try:
        result = akrrrestclient.get(
            '/scheduled_tasks',
            data=data)
        if result.status_code == 200:
            log.info('Successfully Completed Task Retrieval.\n%s', result.text)

        else:
            log.error(
                'something went wrong. %s:%s',
                result.status_code,
                result.text)
        return result
    except Exception as e:
        log.error('''
                An error occured while communicating
                with the REST API.
                %s: %s
                ''',
                  e.args[0] if len(e.args) > 0 else '',
                  e.args[1] if len(e.args) > 1 else '')


def query_parsed(args):
    """
    Handles the appropriate execution of a 'Query' mode request given
    the provided command line arguments.
    """
    dry_run = args.dryrun
    verbose = args.verbose
    resource = args.resource
    exact = args.exact

    def handle_results(results, dry_run):
        if dry_run:
            log.info("Would have inserted the following:")
            [log.info("Id: {0:<9}Name: {1}".format(r['id'], r['name'])) for r in results]
        else:
            log.info("Inserting the following:")
            [log.info("Id: {0:<9}Name: {1}".format(r['id'], r['name'])) for r in results]
            insert_resources(results)

    if verbose:
        log.info("Retrieving requested resource(s)...")

    if not resource:
        results = retrieve_resources()
        handle_results(results, dry_run)
    else:
        results = retrieve_resource(resource, exact)
        handle_results(results, dry_run)

    if verbose:
        log.info("Requested Operation Completed")


def list_parsed(args):
    """
    Handles the appropriate execution of a 'List' mode request given
    the provided command line arguments.
    """

    verbose = args.verbose
    resource = args.resource
    application = args.application
    status = args.status

    if verbose:
        log.info("Attempting to complete the requested Operation: ")

    if status:
        results = {}
        pass
    else:
        results = retrieve_tasks(resource, application)
        if results:
            log.info('Retrieved the following: ')
            [log.info("[{:<8}] Resource: {:<15} App:{:<24}".format(r['task_id'],  r['resource'], r['app'])) for r in results]
        else:
            log.warning('No records returned.')

    if verbose:
        log.info("Requested Operation Completed")


def on_parsed(args):
    """
    Handles the appropriate execution of an 'On' mode request given
    the provided command line arguments.
    """
    data = {
        'application': args.application if args.application else ''
    }
    
    try:
        from akrr import akrrrestclient
        
        result = akrrrestclient.put(
            '/resources/{0}/on'.format(args.resource),
            data=data)
        if result.status_code == 200:
            message = 'Successfully enabled {0} -> {1}.\n{2}' if args.application and args.resource \
                else 'Successfully enabled all applications on {0}.\n{1}'
            parameters = (args.application, args.resource, result.text) if args.application and args.resource \
                else (args.resource, result.text)
            log.info(message.format(*parameters))
        else:
            log.error(
                'something went wrong.%s:%s',
                result.status_code,
                result.text)
    except Exception as e:
        log.error('''
            An error occured while communicating
            with the REST API.
            %s: %s
            ''',
                  e.args[0] if len(e.args) > 0 else '',
                  e.args[1] if len(e.args) > 1 else '')


def off_parsed(args):
    """
    Handles the appropriate execution of an 'Off' mode request given
    the provided command line arguments.
    """
    data = {
        'application': args.application if args.application else ''
    }

    try:
        from akrr import akrrrestclient
        
        result = akrrrestclient.put(
            '/resources/{0}/off'.format(args.resource),
            data=data)

        if result.status_code == 200:
            message = 'Successfully disabled {0} -> {1}.\n{2}' if args.application and args.resource \
                else 'Successfully disabled all applications on {0}.\n{1}'
            parameters = (args.application, args.resource, result.text) if args.application and args.resource \
                else (args.resource, result.text)
            log.info(message.format(*parameters))
        else:
            log.error(
                'something went wrong. %s:%s',
                result.status_code,
                result.text)
    except Exception as e:
        log.error('''
            An error occured while communicating
            with the REST API.
            %s: %s
            ''',
                  e.args[0] if len(e.args) > 0 else '',
                  e.args[1] if len(e.args) > 1 else '')

def reprocess_parsed(args):
    if not (args.resource and args.appkernel):
        log.error(
            'Please provide a resource, app')
        exit(1)
    resource=args.resource
    appkernel=args.appkernel
    time_start=args.time_start
    time_end=args.time_end
    verbose=args.verbose
    
    from akrr import akrrscheduler
    sch=akrrscheduler.akrrScheduler(AddingNewTasks=True)
    sch.reprocessCompletedTasks(resource, appkernel, time_start, time_end, verbose)
    
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
            'app_param':'{}',
            'walltime': walltime,
            'comments':comments
        }
        try:
            from akrr import akrrrestclient
            
            result = akrrrestclient.post(
                '/walltime/%s/%s'%(resource,app),
                data=data) if not listing else \
                akrrrestclient.get(
                    '/walltime/%s/%s'%(resource,app),
                    data=data)
            if result.status_code == 200:
                if not listing:
                    log.info('Successfully updated wall time (resource %s: application kernel: %s nodes: %d).'%(resource,app,nodes))
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


def check_daemon(args):
    from akrr import cfg
    from requests.auth import HTTPBasicAuth
    import requests

    restapi_host = cfg.restapi_host
    if cfg.restapi_host!= "":
        restapi_host=cfg.restapi_host
    #set full address
    api_url = 'https://' + restapi_host +':' + str(cfg.restapi_port) + cfg.restapi_apiroot
    ssl_cert = cfg.restapi_certfile
    ssl_verify = ssl_cert
    
    def populate_token():
        request = requests.get(api_url + "/token", auth=HTTPBasicAuth(cfg.restapi_rw_username, cfg.restapi_rw_password), verify=ssl_verify, cert=ssl_cert)
        if request.status_code == 200:
            token = request.json()['data']['token']
            return token
        else:
            log.error('Something went wrong when attempting to contact the REST API.')
            return None
    
    
    def is_api_up(token):
        request = requests.get(api_url + "/scheduled_tasks", auth=(token, ""), verify=ssl_verify, cert=ssl_cert)
        if request.status_code == 200:
            return True
        else:
            log.error('Unable to successfully contact the REST API: %s: %s', request.status_code, request.text)
            return False

    log.info('Beginning check of the AKRR Rest API...')
    # Holds the user token returned by the auth request.
    token = populate_token()
    if token !=None:
        is_up = is_api_up(token)
        if is_up:
            log.info('REST API is up and running!')
        else:
            exit(1)
    else:
        log.error('Unable to retrieve authentication token.')
        exit(1)
    

def app_add_handler(args):
    import akrr.app_add
    return akrr.app_add.app_add(args.resource,args.appkernel,verbose=args.verbose)


def app_validate_handler(args):
    import akrr.app_validate
    return akrr.app_validate.app_validate(args.resource,args.appkernel,args.nnodes,verbose=args.verbose)


def daemon_handler(args):
    """AKRR daemon handler"""
    log.debug(args)
    if args.action == 'check':
        return check_daemon(args)

    from akrr import cfg

    if args.cron and args.action in ['checknrestart', 'restart']:
        args.append = True
        args.output_file = os.path.join(cfg.data_dir, 'checknrestart')

    import akrr.akrrscheduler

    if args.action == "startdeb":
        akrr.debug = True

        if args.max_task_handlers is not None:
            cfg.max_task_handlers = args.max_task_handlers
        if args.redirect_task_processing_to_log_file is not None:
            cfg.redirect_task_processing_to_log_file = args.redirect_task_processing_to_log_file > 0

    return akrr.akrrscheduler.akrrd_main2(args.action, args.append, args.output_file)
    

class CLI:
    def __init__(self):
        log.basicConfig(
            level=log.INFO,
            format="[%(asctime)s - %(levelname)s] %(message)s"
        )
        
        self.root_parser = argparse.ArgumentParser(description='command line interface to AKRR')
        self.root_parser.add_argument('-v', '--verbose', action='store_true', help="turn on verbose logging")
        
        self.subparsers = self.root_parser.add_subparsers(title='commands')
        
        self.add_command_daemon()
        
        from .commands import add_command_setup
        add_command_setup(self.subparsers)
        
        from .commands import add_command_resource
        add_command_resource(self.subparsers)

        from .commands import add_command_app
        add_command_app(self.subparsers)

        from .commands import add_command_task
        add_command_task(self.subparsers)
    
    def add_command_daemon(self): 
        """set up daemon command"""
        parser = self.subparsers.add_parser('daemon',description="""Application Kernel Remote Runner (AKRR) daemon launcher.
        Without arguments will launch AKRR in command line mode, i.e. stdout is to terminal
        """)
        parser.add_argument('-o', '--output-file', help="redirect stdout and stderr to file")
        parser.add_argument('-a', '--append', action='store_true', help="append stdout and stderr to file rather then overwrite")
        parser.add_argument('-cron', action='store_true', help="set defaults for launching by cron")
        
        subparsers = parser.add_subparsers(title='commands',dest='action');
        subparsers.add_parser('start', help='launch Application Remote Runner in daemon mode')
        subparsers.add_parser('stop', help='terminate Application Remote Runner')
        subparsers.add_parser('restart', help='restart AKRR daemon')
        subparsers.add_parser('check', help='Check AKRR Daemon Status')
        subparsers.add_parser('checknrestart', help='check if AKRR daemon is up if not it will restart it')
        subparsers.add_parser('monitor', help='monitor the activity of Application Remote Runner')
        subparsers.add_parser('status', help='print current status of Application Remote Runner')
        startdeb_parsers=subparsers.add_parser('startdeb', help='launch Application Remote Runner in foreground mode')
        startdeb_parsers.add_argument(
            '-th', '--max-task-handlers',
            dest='max_task_handlers',
            default=None,type=int,
            help='Overwrite max_task_handlers from configuration, if 0 tasks are executed from main thread')
        startdeb_parsers.add_argument(
            '-redir', '--redirect-task-processing-to-log-file',
            dest='redirect_task_processing_to_log_file',
            default=None,type=int,
            help='Overwrite redirect_task_processing_to_log_file from configuration')

        parser.set_defaults(func=daemon_handler)

    def process_common_args(self, cli_args):
        if "verbose" in cli_args and cli_args.verbose:
            log.verbose = True
            log.basicConfig(level=log.DEBUG)
            log.getLogger().setLevel(log.DEBUG)

    def run(self, args=None):
        """parse arguments and execute requested commands"""
        # PARSE: the command line parameters the user provided.
        cli_args = self.root_parser.parse_args(args=args)
        
        self.process_common_args(cli_args)
    
        # EXECUTE: the function provided in the '.set_defaults(func=...)'
        if hasattr(cli_args, "func"):
            cli_args.func(cli_args)
        else:
            log.error("There is no command specified!")
        
        return
        
        parser = argparse.ArgumentParser(description='command line interface to AKRR')
        parser.add_argument('-v', '--verbose', action='store_true', help="turn on verbose logging")
        
        subparsers = parser.add_subparsers()
    
        query_parser = subparsers.add_parser('query',
                                             description='Query XDMoD for a list of available resource and update the AKRR database.')
        query_parser.add_argument('-d', '--dryrun', action='store_true',
                                  help='Only display data. Do not update the database.')
        query_parser.add_argument('-v', '--verbose', action='store_true', help='Increase the level of output verbosity.')
        query_parser.add_argument('-r', '--resource', help='Only query / update for the provided resource.')
        query_parser.add_argument('-e', '--exact', action='store_true',
                                  help='Only useful if a resource has been provided. Will only consider exact matches.')
        query_parser.set_defaults(func=query_parsed)
    
        list_parser = subparsers.add_parser('list',
                                            description='By default lists all resources and their application kernels.')
        list_parser.add_argument('-v', '--verbose', action='store_true', help='Increase the level of output verbosity.')
        list_parser.add_argument('-r', '--resource', help='Only list information about the provided resource')
        list_parser.add_argument('-a', '--application', help='Only list information about the provided application kernel.')
        list_parser.add_argument('-s', '--status', action='store_true',
                                 help='Retrieve the status of the resources and application kernels.')
        list_parser.set_defaults(func=list_parsed)
    
        on_parser = subparsers.add_parser('on',
                                          description='Enable a specific application kernel or all application kernels for a given resource.')
        on_parser.add_argument('-a', '--application', help='Enable a particular application on the provided resource')
        on_parser.add_argument('resource', help='The resource on which to perform the enabling of application kernels.')
        on_parser.set_defaults(func=on_parsed)
    
        off_parser = subparsers.add_parser('off',
                                           description='Disable a specific application kernel or all application kernels for a given resource.')
        off_parser.add_argument('-a', '--application', help='Disable a particular application on the provided resource')
        off_parser.add_argument('resource', help='The resource on which to perform the disabling of application kernels.')
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
        
        #new appkernel
        app_parser = subparsers.add_parser('app',
            description='appkernel on resource manipulation')
        app_subparsers = app_parser.add_subparsers()
        app_add_parser = app_subparsers.add_parser('add',
            description='add new appkernel to resource')
        app_add_parser.add_argument('resource', help="name of resource to where appkernel is added'")
        app_add_parser.add_argument('appkernel', help="name of appkernel to add'")
        app_add_parser.set_defaults(func=app_add_handler)
        
        app_validate_parser = app_subparsers.add_parser('validate',
            description='Validation of app kernel installation on resource')
        app_validate_parser.add_argument('-n', '--nnodes', default=2,type=int, help="number of nodes (default: 2)")
        app_validate_parser.add_argument('resource', help="name of resource for validation and deployment'")
        app_validate_parser.add_argument('appkernel', help="name of resource for validation and deployment'")
        app_validate_parser.set_defaults(func=app_validate_handler)

    
if __name__ == '__main__':
    CLI().run()
