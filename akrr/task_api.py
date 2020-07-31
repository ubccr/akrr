import io
import logging as log
import os
import sys
from prettytable import PrettyTable
from collections import OrderedDict

from akrr.util import log
from akrr.util.task import pack_details, wrap_str_dict, wrap_text, get_task_list_table
from akrr.akrrerror import AkrrRestAPIException, AkrrValueException


def task_new(resource: str, appkernel: str, nodes: str, time_to_start=None, periodicity=None,
             time_window_start=None, time_window_end=None, test_run=False,
             dry_run:bool = False, gen_batch_job_only: bool = False, app_param=None, task_param=None,
             n_runs: int = 1, group_id: str = ""):
    """
    Handles the appropriate execution of a 'New Task' mode request
    given the provided command line arguments.
    """
    import pprint
    from akrr.util.time import calculate_random_start_time, get_formatted_time_to_start

    if appkernel == "all":
        import akrr.cfg
        import akrr.app
        appkernel_list = []
        resource_app_enabled = akrr.app.app_get_enabled()
        for ak in akrr.cfg.apps.keys():
            if resource not in akrr.cfg.apps[ak]['appkernel_on_resource']:
                continue
            if resource not in resource_app_enabled:
                continue
            if ak not in resource_app_enabled[resource]["apps"]:
                continue
            if "resource_app_enabled" not in resource_app_enabled[resource]["apps"][ak]:
                continue
            if not resource_app_enabled[resource]["apps"][ak]["resource_app_enabled"]:
                continue
            appkernel_list.append(ak)

        for ak in appkernel_list:
            task_new(
                resource, ak, nodes, time_to_start=time_to_start, periodicity=periodicity,
                time_window_start=time_window_start, time_window_end=time_window_end, test_run=test_run,
                dry_run=dry_run, gen_batch_job_only=gen_batch_job_only, app_param=app_param, task_param=task_param,
                n_runs=n_runs, group_id=group_id)
        return

    if nodes == "all":
        import akrr.cfg
        if appkernel not in akrr.cfg.apps:
            raise AkrrValueException("Unknown appkernel %s" % appkernel)
        if resource not in akrr.cfg.apps[appkernel]['appkernel_on_resource']:
            raise AkrrValueException("Unknown resource %s for appkernel %s" % (resource, appkernel))
        if resource not in akrr.cfg.apps[appkernel]['appkernel_on_resource']:
            raise AkrrValueException("Unknown resource %s for appkernel %s" % (resource, appkernel))
        if "num_of_nodes" in akrr.cfg.apps[appkernel]['appkernel_on_resource'][resource]:
            node_list = akrr.cfg.apps[appkernel]['appkernel_on_resource'][resource]['num_of_nodes']
        else:
            node_list = akrr.cfg.apps[appkernel]['num_of_nodes']
    else:
        node_list = [node.strip() for node in nodes.split(',')] if ',' in nodes else [nodes]

    if time_to_start is not None:
        time_to_start = get_formatted_time_to_start(time_to_start)
        if time_to_start is None:
            raise AkrrValueException("Unknown date-time format for time to start!")

    if n_runs > 1 and periodicity:
        raise AkrrValueException("n_runs larger than one can not be set with periodicity")

    for node in node_list:
        if time_window_start is not None and time_window_end is not None:
            time_to_start = calculate_random_start_time(
                time_to_start,
                periodicity,
                time_window_start,
                time_window_end)
        data = {
            'resource': resource,
            'app': appkernel,
            'time_to_start': time_to_start,
            'repeat_in': periodicity,
            'resource_param': "{'nnodes':%s}" % node
        }

        s_task_param = ""
        if test_run:
            s_task_param += "'test_run':True"
        if n_runs > 1:
            s_task_param += "" if s_task_param == "" else ","
            s_task_param += "'n_runs':%d" % n_runs
        if task_param is not None:
            s_task_param += "" if s_task_param == "" else ","
            s_task_param += task_param
        if s_task_param != "":
            data['task_param'] = "{%s}" % s_task_param

        if group_id != "":
            data['group_id'] = group_id

        if app_param is not None:
            data['app_param'] = "{%s}" % app_param

        log.debug("Trying to submit: "+pprint.pformat(data))

        if dry_run:
            log.dry_run("Should submit following to REST API (POST to scheduled_tasks) %s" % data)

        if gen_batch_job_only:
            generate_batch_job_for_testing(resource, appkernel, nodes, dry_run=dry_run)

        if dry_run or gen_batch_job_only:
            continue

        try:
            from akrr import akrrrestclient
            import json

            result = akrrrestclient.post(
                '/scheduled_tasks',
                data=data)

            if result.status_code == 200:
                data_out = json.loads(result.text)["data"]["data"]
                log.info('Successfully submitted new task. The task id is %s.' % data_out["task_id"])
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
            ''', e.args[0] if len(e.args) > 0 else '', e.args[1] if len(e.args) > 1 else '')
            raise e


def generate_batch_job_for_testing(resource, appkernel, nodes, dry_run=False):
    """
    Generate batch job script for testing purposes
    """
    from akrr import cfg
    from akrr.util.log import verbose

    resource = cfg.find_resource_by_name(resource)
    app = cfg.find_app_by_name(appkernel)

    str_io = io.StringIO()
    if not verbose:
        sys.stdout = sys.stderr = str_io

    from akrr.akrr_task import AkrrTaskHandlerAppKer
    task_handler = AkrrTaskHandlerAppKer(1, resource['name'], app['name'], "{'nnodes':%s}" % (nodes,), "{}", "{}")
    if dry_run:
        task_handler.generate_batch_job_script()
    else:
        task_handler.create_batch_job_script_and_submit_it(do_not_submit_to_queue=True)
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__

    if task_handler.status.count("ERROR") > 0:
        log.error('Batch job script was not generated see log below!')
        print(str_io.getvalue())
        log.error('Batch job script was not generated see log above!')

    job_script_full_path = os.path.join(task_handler.taskDir, "jobfiles", task_handler.JobScriptName)
    if os.path.isfile(job_script_full_path):
        fin = open(job_script_full_path, "r")
        job_script_content = fin.read()
        fin.close()

        if dry_run:
            log.info('Below is content of generated batch job script:')
            print(job_script_content)
        else:
            log.info("Local copy of batch job script is " + job_script_full_path)
            print()
            log.info(
                "Application kernel working directory on " + resource['name'] + " is " + task_handler.remoteTaskDir)
            log.info(
                "Batch job script location on " + resource['name'] + " is " + os.path.join(task_handler.remoteTaskDir,
                                                                                           task_handler.JobScriptName))
    else:
        log.error('Batch job script was not generated see messages above!')
    if dry_run:
        log.info('Removing generated files from file-system as only batch job script printing was requested')
        task_handler.delete_local_folder()


def task_list(resource=None, appkernel=None, scheduled=True, active=True):
    """
    Retrieve the list of currently scheduled tasks ( resource / application pairings ) from
    mod_akrr.

    :param resource: filter the results by the provided resource
    :param appkernel: filter the results by the provided application
    :param scheduled: show only scheduled for future execution tasks
    :param active: show only currently running tasks

    :type resource str or None
    :type appkernel str or None

    :return: None
    """
    import json
    from . import akrrrestclient

    scheduled_table_parameters = OrderedDict((
        ("Res. Param", ("resource_param", "l", lambda s: wrap_str_dict(s, width=48))),
        ("App Param", ("app_param", "l", lambda s: wrap_str_dict(s, width=48))),
        ("Task Param", ("task_param", "l", lambda s: wrap_str_dict(s, width=48))),
        ('Repeat In', ('repeat_in', "c", str))
    ))

    scheduled_table_title_key = OrderedDict((
        ("Task Id", ('task_id', "r", str)),
        ('Resource', ('resource', "l", lambda s: wrap_text(s, width=24))),
        ('App', ('app', "l", str)),
        ("Parameters", (scheduled_table_parameters, "l", pack_details)),
        ("Time to Start", ('time_to_start', "l", str)),
    ))

    active_table_details = OrderedDict((
        ('Resource', ('resource', "l", lambda s: wrap_text(s, width=48))),
        ('App', ('app', "l", str)),
        ("Resource Param", ("resource_param", "l", lambda s: wrap_str_dict(s, width=48))),
        ("App Param", ("app_param", "l", lambda s: wrap_str_dict(s, width=48))),
        ("Task Param", ("task_param", "l", lambda s: wrap_str_dict(s, width=48))),
        ("Time to Start", ('time_to_start', "l", str)),
        ('Repeat In', ('repeat_in', "c", str))))

    active_table_title_key = OrderedDict((
        ("Task Id", ('task_id', "r", str)),
        ("Details", (active_table_details, "l", pack_details)),
        ('Status', ('status', "l", lambda s: wrap_text(s, width=48))),
    ))

    log.debug("List all tasks")

    data = {}

    if resource is not None:
        data["resource"] = resource

    if appkernel is not None:
        data["app"] = appkernel

    if scheduled:
        results = akrrrestclient.get(
            '/scheduled_tasks',
            data=data
        )
        if results.status_code == 200:
            log.debug('Successfully Completed Task Retrieval.\n%s', results.text)
        else:
            if hasattr(results, "text"):
                response = json.loads(results.text)
                if "error" in response and "message" in response["error"]:
                    msg = "Message from AKRR server: "+response["error"]["message"]
                    log.error(msg)
                    raise AkrrRestAPIException(msg)
            else:
                raise AkrrRestAPIException()

        results = json.loads(results.text)['data']
        if len(results) > 0:
            table = get_task_list_table(results, scheduled_table_title_key)
            log.info('Scheduled tasks:\n' + str(table))
        else:
            log.info('There is no scheduled tasks')

    if active:
        results = akrrrestclient.get(
            '/active_tasks',
            data=data
        )

        if results.status_code == 200:
            log.debug('Successfully Completed Task Retrieval.\n%s', results.text)
        else:
            if hasattr(results, "text"):
                response = json.loads(results.text)
                if "error" in response and "message" in response["error"]:
                    msg = "Message from AKRR server: "+response["error"]["message"]
                    log.error(msg)
                    raise AkrrRestAPIException(msg)
            else:
                raise AkrrRestAPIException()

        results = json.loads(results.text)['data']

        if len(results) > 0:
            table = get_task_list_table(results, active_table_title_key)
            log.info('Active tasks:\n' + str(table))
        else:
            log.info('There is no active tasks')


def task_delete_by_task_id(task_id: int = None):
    """
    Remove task from schedule

    :param task_id:
    :return:
    """

    import re
    import json
    from akrr import akrrrestclient

    results = akrrrestclient.delete(
        '/scheduled_tasks/{}'.format(task_id)
    )

    if results.status_code == 200 and hasattr(results, "text"):
        log.debug('Message from AKRR server: %s', results.text)
        response = json.loads(results.text)
        if "data" in response and "success" in response["data"] and "message" in response["data"]:
            if response["data"]["success"]:
                log.info('Successfully deleted task with id: %s' % task_id)
            else:
                log.error('Can not deleted task with id: %s because %s' % (task_id, response["data"]["message"]))
                if re.search("is not in queue", response["data"]["message"]) is None:
                    raise AkrrRestAPIException()

        else:
            raise AkrrRestAPIException('Can not deleted task with id: %s, got following message: %s' % (task_id,
                                                                                                        results.text))
    else:
        if hasattr(results, "text"):
            msg = "Can not delete task. Message from AKRR server: " + results.text
            log.error(msg)
            raise AkrrRestAPIException(msg)
        else:
            raise AkrrRestAPIException()


def task_delete(task_id: int = None, resource: str = None, appkernel: str = None, nodes: str = None,
                group_id: str = None, all_scheduled_tasks=False, all_active_tasks=False):
    """
    Remove task from schedule

    :param task_id:
    :return:
    """
    if task_id:
        if resource or appkernel or nodes or group_id or all_scheduled_tasks or all_active_tasks:
            raise AkrrValueException("task_id can not be specified with other values")
        task_delete_by_task_id(task_id)
        return

    data = {}
    if resource or appkernel or nodes:
        if resource or appkernel or nodes or group_id or all_scheduled_tasks or all_active_tasks:
            raise AkrrValueException("resource/appkernel/nodes can not be specified with other values")
        if resource:
            data["resource"] = resource
        if appkernel:
            appkernel_list = [ak.strip() for ak in appkernel.split(',')] if ',' in appkernel else [appkernel]
            data["appkernel"] = appkernel_list
        if nodes:
            node_list = [int(node.strip()) for node in nodes.split(',')] if ',' in nodes else [int(nodes)]
            data["nodes"] = node_list

    if group_id:
        data["group_id"] = group_id

    if all_scheduled_tasks:
        if all_active_tasks:
            raise AkrrValueException("all_scheduled_tasks can not be specified with other values")
        data["all_scheduled_tasks"] = all_scheduled_tasks

    if all_active_tasks:
        data["all_active_tasks"] = all_active_tasks

    try:
        from akrr import akrrrestclient
        import json

        result = akrrrestclient.post(
            '/scheduler/no_new_tasks',
            data=data)
        result = akrrrestclient.post(
            '/scheduler/no_active_tasks_check',
            data=data)


        if result.status_code == 200:
            #data_out = json.loads(result.text)["data"]["data"]
            log.info('Successfully deleted tasks.')
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
        ''', e.args[0] if len(e.args) > 0 else '', e.args[1] if len(e.args) > 1 else '')
        raise e
