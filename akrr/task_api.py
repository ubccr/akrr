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


def task_delete_selection(resource: str = None, appkernel: str = None, nodes: str = None, group_id: str = None,
                          active_tasks=False, scheduled_tasks=False):
    """
    delete tasks from schedule
    """
    from akrr import akrrrestclient
    import json

    from akrr.db import get_akrr_db
    from akrr.daemon import delete_task
    import time

    if not (resource or appkernel or nodes or group_id):
        raise AkrrValueException("Something out of resource/appkernel/nodes/group id should be set!")

    db, cur = get_akrr_db(dict_cursor=True)

    # ask scheduler not to start new tasks
    if akrrrestclient.post('/scheduler/no_new_tasks').status_code != 200:
        raise AkrrRestAPIException("Can not post scheduler/no_new_tasks")

    if active_tasks:
        if akrrrestclient.post('/scheduler/no_active_tasks_check').status_code != 200:
            raise AkrrRestAPIException("Can not post scheduler/no_active_tasks_check")
        # Now we need to wait till scheduler will be done checking active tasks
        while True:
            sql = "SELECT task_id FROM active_tasks WHERE task_lock > 0"
            log.debug(sql)
            cur.execute(sql)
            n_active_checking_task = len(cur.fetchall())
            if n_active_checking_task==0:
                break
            log.info("There are %d task which daemon is working on, waiting for it to finish.")
            time.sleep(5)
        # now daemon is not working on any tasks

    # now we can work with db
    where = []
    if resource:
        where.append("resource='%s'", resource)
    if appkernel:
        appkernel_list = ["'" + ak.strip() + "'" for ak in appkernel.split(',')] if ',' in appkernel else [appkernel]
        where.append("app IN (" + ",".join(appkernel_list) + ")")
    if group_id:
        where.append("group_id='%s'", group_id)

    active_tasks_ids = []

    if nodes:
        node_list = [int(node.strip()) for node in nodes.split(',')] if ',' in nodes else [int(nodes)]
        for node in node_list:
            where_node = where + ["resource_param LIKE \"%'nnodes':%d%\"" % node]
            if scheduled_tasks:
                sql = "DELETE FROM scheduled_tasks WHERE " + " AND ".join(where_node)
                log.debug(sql)
                cur.execute(sql)
            if active_tasks:
                sql = "SELECT task_id FROM active_tasks WHERE " + " AND ".join(where_node)
                log.debug(sql)
                cur.execute(sql)
                active_tasks_ids += [int(t['task_id']) for t in cur.fetchall()]
    else:
        if scheduled_tasks:
            sql = "DELETE FROM scheduled_tasks WHERE " + " AND ".join(where)
            log.debug(sql)
            cur.execute(sql)
        if active_tasks:
                sql = "SELECT task_id FROM active_tasks WHERE " + " AND ".join(where_node)
                log.debug(sql)
                cur.execute(sql)
                active_tasks_ids += [int(t['task_id']) for t in cur.fetchall()]

    if active_tasks:
        if len(active_tasks_ids)==0:
            log.info("No active tasks to delete")
        else:
            for task_id in active_tasks_ids:
                log.info("Deleting task_id %d", task_id)
                delete_task(task_id, remove_from_scheduled_queue=False, remove_from_active_queue=True,
                                remove_derived_task=False)

    if scheduled_tasks or active_tasks:
        db.commit()

    # ask scheduler can start new tasks now
    if akrrrestclient.post('/scheduler/new_tasks_on').status_code != 200:
        raise AkrrRestAPIException("Can not post scheduler/new_tasks_on")

    log.info("Done")


def task_delete(task_id: int = None, resource: str = None, appkernel: str = None, nodes: str = None,
                group_id: str = None, active_tasks=False, scheduled_tasks=False):
    """
    Remove task from schedule

    :param task_id:
    :return:
    """
    if task_id:
        if resource or appkernel or nodes or group_id:
            raise AkrrValueException("task_id can not be specified with other values")
        if active_tasks:
            from akrr.daemon import delete_task
            delete_task(task_id, remove_from_scheduled_queue=False, remove_from_active_queue=True,
                        remove_derived_task=False)
        else:
            task_delete_by_task_id(task_id)
        return

    if resource or appkernel or nodes or group_id:
        task_delete_selection(resource=resource, appkernel=appkernel, nodes=nodes, group_id=group_id,
                              active_tasks=active_tasks, scheduled_tasks=scheduled_tasks)
        return

    log.error("task delete: no option were specified!")
