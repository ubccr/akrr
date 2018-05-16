import io
import logging as log
import os
import sys

from akrr.util import log

from akrr.akrrerror import AkrrRestAPIException, AkrrValueException


def task_new(resource, appkernel, nodes, time_to_start=None, periodicity=None,
             time_window_start=None, time_window_end=None, test_run=False,
             dry_run=False, show_batch_job=False):
    """
    Handles the appropriate execution of a 'New Task' mode request
    given the provided command line arguments.
    """
    import pprint
    from akrr.util.time import calculate_random_start_time, get_formatted_time_to_start

    node_list = [node.strip() for node in nodes.split(',')] if ',' in nodes else list(nodes)

    if time_to_start is not None:
        time_to_start = get_formatted_time_to_start(time_to_start)
        if time_to_start is None:
            raise AkrrValueException("Unknown date-time format for time to start!")

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

        if test_run:
            data['task_param'] = "{'test_run':True}"

        log.debug("Trying to submit: "+pprint.pformat(data))

        if dry_run:
            log.dry_run("Should submit following to REST API (POST to scheduled_tasks) %s" % data)

        if show_batch_job:
            generate_batch_job_for_testing(resource, appkernel, nodes, dry_run=dry_run)

        if dry_run or show_batch_job:
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
    from akrr import cfg
    from akrr.util.log import verbose

    resource = cfg.FindResourceByName(resource)
    app = cfg.FindAppByName(appkernel)

    str_io = io.StringIO()
    if not verbose:
        sys.stdout = sys.stderr = str_io

    from akrr.akrrtaskappker import akrrTaskHandlerAppKer
    task_handler = akrrTaskHandlerAppKer(1, resource['name'], app['name'], "{'nnodes':%s}" % (nodes,), "{}", "{}")
    if dry_run:
        task_handler.GenerateBatchJobScript()
    else:
        task_handler.CreateBatchJobScriptAndSubmitIt(doNotSubmitToQueue=True)
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
        task_handler.DeleteLocalFolder()


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
            msg = 'Scheduled tasks:\n'
            msg = msg + "%10s%16s%32s%8s%20s%20s\n" % ('task_id', 'resource', 'app', 'nnodes',
                                                       'time_to_start', 'repeat_in')

            for r in results:
                if r is None:
                    r = {}
                nodes = eval(r.get('resource_param', "{}")).get("nnodes", "NA")
                msg = msg + "%10s%16s%32s%8s%20s%20s\n" % (
                    r.get('task_id', "NA"), r.get('resource', "NA"), r.get('app', "NA"), nodes,
                    r.get('time_to_start', "NA"), r.get('repeat_in', "NA"))
            log.info(msg)
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
            msg = 'Active tasks:\n'
            msg = msg + "%10s%16s%32s%8s%20s%20s%22s\n" % ('task_id', 'resource', 'app', 'nnodes',
                                                           'time_to_start', 'repeat_in', 'status')

            for r in results:
                if r is None:
                    r = {}
                nodes = eval(r.get('resource_param', "{}")).get("nnodes", "NA")

                if r.get('status', "NA") is None:
                    status = "NA"
                else:
                    status = r.get('status', "NA")
                msg = msg + "%10s%16s%32s%8s%20s%20s%22s\n" % (
                    r.get('task_id', "NA"), r.get('resource', "NA"), r.get('app', "NA"), nodes,
                    r.get('time_to_start', "NA"), r.get('repeat_in', "NA"), status[:19])
            log.info(msg)
        else:
            log.info('There is no active tasks')


def task_delete(task_id):
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
            msg = "Can not delete task. Message from AKRR server: "+results.text
            log.error(msg)
            raise AkrrRestAPIException(msg)
        else:
            raise AkrrRestAPIException()

