"""
A script that will provide command line access to the Application Remote Runner
functionality.

"""
from util import logging as log
import akrr
import akrrrestclient
import random
import datetime
import os
import sys
import cStringIO
import inspect

try:
    import argparse
except:
    #add argparse directory to path and try again
    curdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    argparsedir=os.path.abspath(os.path.join(curdir,"..","3rd_party","argparse-1.3.0"))
    if argparsedir not in sys.path:sys.path.append(argparsedir)
    import argparse

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
    if resources is not None and len(resources) > 0:

        parameters = tuple([(resource['name'], int(resource['id']), False) for (resource) in resources])
        resources_parameters = tuple([(resource['name'], int(resource['id'])) for (resource) in resources])

        connection, cursor = akrr.getAKDB()
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
    if resource is not None:
        name, id = resource
        connection, cursor = akrr.getAKDB()
        with connection:
            cursor.execute('''
            INSERT INTO `mod_appkernel`.`resource`
            (resource, xdmod_resource_id, visible)
            VALUES(%s, %s, %s)
            ''', (name, id, False))
            cursor.execute('''
            INSERT INTO `mod_akrr`.`resources`
            (name, xdmod_resource_id)
            VALUES(%s, %s)
            ''', (name, id))


def retrieve_resources():
    """
    Retrieve all resources currently present in the XDMoD database.


    :return: a dict representation of the resourcefact table ( name, id )
    """
    connection, cursor = akrr.getXDDB(True)
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
    if resource is None or len(resource) < 1:
        raise AssertionError('provided resource must not be empty.')

    connection, cursor = akrr.getXDDB(True)

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

    try:
        akrrrestclient.get_token()
    except StandardError:
        log.error('''
                An error occured while attempting to retrieve a token
                from the REST API.
                ''')
    try:
        result = akrrrestclient.get(
            '/scheduled_tasks',
            data=data)
        if result.status_code == 200:
            log.info('Successfully Completed Task Retrieval.\n{0}', result.text)

        else:
            log.error(
                'something went wrong. {0}:{1}',
                result.status_code,
                result.text)
        return result
    except StandardError, e:
        log.error('''
                An error occured while communicating
                with the REST API.
                {0}: {1}
                ''',
                  e.args[0] if len(e.args) > 0 else '',
                  e.args[1] if len(e.args) > 1 else '')


def to_time(time):
    """
    Converts a string of the format: HH:MI to a datetime.time object. Returns None if the string
    fails validation.

    :type time str

    :param time:
    :return: a datetime.time representation of the provided time string. None if it fails validation.
    """
    if time and isinstance(time, str) and len(time) > 0:
        parts = time.split(':')
        if len(parts) >= 2:
            hours = int(parts[0].strip())
            minutes = int(parts[1].strip())
            return datetime.time(hours, minutes)


def to_datetime(time):
    """
    converts the provided datetime.time into a datetime.datetime object.

    :type time datetime.time

    :param time: that is to be converted into datetime.time object.
    :return: datetime.datetime object representation of the provided 'time' parameter
    """
    if time and isinstance(time, datetime.time):
        return datetime.datetime.now().replace(hour=time.hour, minute=time.minute, second=0, microsecond=0)


def calculate_random_start_time(start_time, periodicity, time_start, time_end):
    """
    Calculate a new, random start time based on the provided parameters.

    :type start_time str
    :type periodicity str
    :type time_start str
    :type time_end str

    :param start_time  a string in the format 'YYYY-MM-DD HH24:MI:SS'
    :param periodicity a string in the format ''
    :param time_start  a string in the format 'HH24:MI'
    :param time_end    a string in the format 'HH24:MI'

    :return a new datetime.datetime with a randomized day / time constrained by
            the provided periodicity and time_start / time_end
    """
    time_to_start = akrr.getDatatimeTimeToStart(start_time).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0)
    repeat_in = akrr.getTimeDeltaRepeatIn(periodicity)

    if time_to_start and repeat_in:
        spans_multiple_days = repeat_in.days > 1
        if spans_multiple_days:
            chosen_day = random.randint(0, repeat_in.days)

            chosen_start_time = to_time(time_start)
            chosen_end_time = to_time(time_end)
            chosen_start_datetime = to_datetime(chosen_start_time)
            chosen_end_datetime = to_datetime(chosen_end_time)

            difference = chosen_end_datetime - chosen_start_datetime
            lower_bound = chosen_start_datetime - datetime.datetime.now().replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0)

            chosen_time = random.randint(
                lower_bound.seconds,
                difference.seconds + repeat_in.seconds)
            chosen_datetime = time_to_start + datetime.timedelta(
                days=chosen_day,
                seconds=chosen_time)
            return chosen_datetime.strftime('%Y-%m-%d %H:%M:%S')
        else:
            chosen_start_time = to_time(time_start)
            chosen_end_time = to_time(time_end)
            chosen_start_datetime = to_datetime(chosen_start_time)
            chosen_end_datetime = to_datetime(chosen_end_time)

            difference = chosen_end_datetime - chosen_start_datetime

            chosen_time = random.randint(
                chosen_start_time.second,
                difference.seconds)
            chosen_datetime = time_to_start + datetime.timedelta(
                seconds=chosen_time)
            return chosen_datetime.strftime('%Y-%m-%d %H:%M:%S')

    return start_time


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
            [log.info("Id: {0:<9}Name: {1}", r['id'], r['name']) for r in results]
        else:
            log.info("Inserting the following:")
            [log.info("Id: {0:<9}Name: {1}", r['id'], r['name']) for r in results]
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
            [log.info("[{:<8}] Resource: {:<15} App:{:<24}",r['task_id'],  r['resource'], r['app']) for r in results]
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
        result = akrrrestclient.put(
            '/resources/{0}/on'.format(args.resource),
            data=data)
        if result.status_code == 200:
            message = 'Successfully enabled {0} -> {1}.\n{2}' if args.application and args.resource \
                else 'Successfully enabled all applications on {0}.\n{1}'
            parameters = (args.application, args.resource, result.text) if args.application and args.resource \
                else (args.resource, result.text)
            log.info(message, *parameters)
        else:
            log.error(
                'something went wrong. {0}:{1}',
                result.status_code,
                result.text)
    except StandardError, e:
        log.error('''
            An error occured while communicating
            with the REST API.
            {0}: {1}
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
        result = akrrrestclient.put(
            '/resources/{0}/off'.format(args.resource),
            data=data)

        if result.status_code == 200:
            message = 'Successfully disabled {0} -> {1}.\n{2}' if args.application and args.resource \
                else 'Successfully disabled all applications on {0}.\n{1}'
            parameters = (args.application, args.resource, result.text) if args.application and args.resource \
                else (args.resource, result.text)
            log.info(message, *parameters)
        else:
            log.error(
                'something went wrong. {0}:{1}',
                result.status_code,
                result.text)
    except StandardError, e:
        log.error('''
            An error occured while communicating
            with the REST API.
            {0}: {1}
            ''',
                  e.args[0] if len(e.args) > 0 else '',
                  e.args[1] if len(e.args) > 1 else '')


def new_task_parsed(args):
    """
    Handles the appropriate execution of a 'New Task' mode request
    given the provided command line arguments.
    """
    if not (args.resource and
            args.appkernel and
            args.nodes):
        parser.error(
            'Please provide a resource, application and node count.')
        exit(1)
    resource = args.resource
    app = args.appkernel
    time_to_start=args.start_time
    time_start = args.time_start# if args.time_start else '01:00'
    time_end = args.time_end# if args.time_end else '05:00'
    repeat_in = args.periodicity
    nodes = args.nodes
    node_list = [node.strip() for node in nodes.split(',')] if ',' in nodes else list(nodes)

    for node in node_list:
        if time_start!=None and time_end!=None:
            time_to_start = calculate_random_start_time(
                args.start_time,
                repeat_in,
                time_start,
                time_end)
        data = {
            'resource': resource,
            'app': app,
            'time_to_start': time_to_start,
            'repeat_in': repeat_in,
            'resource_param': "{'nnodes':%s}" % (node,)
        }
        try:
            result = akrrrestclient.post(
                '/scheduled_tasks',
                data=data)
            if result.status_code == 200:
                log.info('Successfully submitted new task')
            else:
                log.error(
                    'something went wrong. {0}:{1}',
                    result.status_code,
                    result.text)
        except StandardError, e:
            log.error('''
            An error occured while communicating
            with the REST API.
            {0}: {1}
            ''',
                      e.args[0] if len(e.args) > 0 else '',
                      e.args[1] if len(e.args) > 1 else '')


def wall_time_parsed(args):

    if not args.list and not (args.resource and
                              args.appkernel and
                              args.nodes and
                              args.walltime):
        parser.error(
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
                        'Successfully queried walltime records. \n{0}',
                        result.text)
            else:
                log.error('something went wrong. {0}:{1}',
                          result.status_code,
                          result.text)
        except StandardError, e:
            import traceback
            log.error('''
            An error occured while communicating
            with the REST API.
            {0}: {1}
            '''.strip(),
                      e.args[0] if len(e.args) > 0 else '',
                      e.args[1] if len(e.args) > 1 else '')
            print traceback.print_exc()

def batch_job_parsed(args):
    if not (args.resource and
          args.appkernel and
          args.nodes):
        parser.error(
            'Please provide a resource, application kernel and node count.')
        exit(1)
    resource = akrr.FindResourceByName(args.resource)
    app = akrr.FindAppByName(args.appkernel)
    nodes = args.nodes
    print_only=args.print_only
    verbose=args.verbose

    str_io=cStringIO.StringIO()
    if not verbose:
        sys.stdout = sys.stderr = str_io
    from akrrtaskappker import akrrTaskHandlerAppKer
    taskHandler=akrrTaskHandlerAppKer(1,resource['name'],app['name'],"{'nnodes':%s}" % (nodes,),"{}","{}")
    if print_only:
        taskHandler.GenerateBatchJobScript()
    else:
        taskHandler.CreateBatchJobScriptAndSubmitIt(doNotSubmitToQueue=True)
    sys.stdout=sys.__stdout__
    sys.stderr=sys.__stderr__

    if taskHandler.status.count("ERROR")>0:
        log.error('Batch job script was not generated see log below!')
        print str_io.getvalue()
        log.error('Batch job script was not generated see log above!')


    jobScriptFullPath=os.path.join(taskHandler.taskDir,"jobfiles",taskHandler.JobScriptName)
    if os.path.isfile(jobScriptFullPath):
        fin=open(jobScriptFullPath,"r")
        jobScriptContent=fin.read()
        fin.close()

        if print_only:
            log.info('Below is content of generated batch job script:')
            print jobScriptContent
        else:
            log.info("Local copy of batch job script is "+jobScriptFullPath)
            print
            log.info("Application kernel working directory on "+resource['name']+" is "+taskHandler.remoteTaskDir)
            log.info("Batch job script location on "+resource['name']+" is "+os.path.join(taskHandler.remoteTaskDir,taskHandler.JobScriptName))
    else:
        log.error('Batch job script was not generated see messages above!')
    if print_only:
        log.info('Removing generated files from file-system as only batch job script printing was requested')
        taskHandler.DeleteLocalFolder()
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
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

    new_parser = subparsers.add_parser('new_task',
                                       description='Create a new task given the specified parameters')
    new_parser.add_argument('-r', '--resource', help='Specify the resource that the new task should be created for.')
    new_parser.add_argument('-a', '--appkernel', help='Specify which application kernel to use for the new task.')
    new_parser.add_argument('-n', '--nodes', help='Specify how many nodes the new task should be setup with.')
    new_parser.add_argument('-s', '--start_time', help='Specify what time the newly created task should start.')
    new_parser.add_argument('-t0', '--time_start', help='Specify the time at which the random distribution begins')
    new_parser.add_argument('-t1', '--time_end', help='Specify the time at which the random distribution ends')
    new_parser.add_argument('-p', '--periodicity', help='Specify the amount of time that should elapse between executions.')
    new_parser.set_defaults(func=new_task_parsed)

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

    batch_job_parser = subparsers.add_parser('batch_job',
                                  description='batch job script generation for debug purposes')
    batch_job_parser.add_argument('-r', '--resource', help='Specify the resource that the batch job script should be created for.')
    batch_job_parser.add_argument('-a', '--appkernel', help='Specify which application kernel to use for the batch job script.')
    batch_job_parser.add_argument('-n', '--nodes', help='Specify how many nodes the batch job script should be setup with.')
    batch_job_parser.add_argument('-p', '--print-only',action='store_true',
                                   help='Print generated batch job script')
    batch_job_parser.add_argument('-v', '--verbose', action='store_true', help='Increase the level of output verbosity.')
    batch_job_parser.set_defaults(func=batch_job_parsed)

    # PARSE: the command line parameters the user provided.
    cli_args = parser.parse_args()

    # EXECUTE: the function provided in the '.set_defaults(func=...)'
    cli_args.func(cli_args)
