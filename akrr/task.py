import io
import logging as log
import os
import sys

from akrr.util import log


def new_task(resource, appkernel, nodes, time_to_start=None, periodicity=None,
             time_window_start=None, time_window_end=None, test_run=False,
             dry_run=False, show_batch_job=False):
    """
    Handles the appropriate execution of a 'New Task' mode request
    given the provided command line arguments.
    """
    # @TODO ensure test_run propagation
    from akrr.util.time import calculate_random_start_time

    node_list = [node.strip() for node in nodes.split(',')] if ',' in nodes else list(nodes)

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
            'resource_param': "{'nnodes':%s}" % (node,)
        }

        if test_run:
            data['task_param'] = "{'test_run':True}"

        if dry_run:
            log.dry_run("Should submit following to REST API (POST to scheduled_tasks) %s" % data)

        if show_batch_job:
            generate_batch_job_for_testing(resource, appkernel, nodes, dry_run=dry_run)

        if dry_run or show_batch_job:
            continue

        try:
            from akrr import akrrrestclient

            result = akrrrestclient.post(
                '/scheduled_tasks',
                data=data)
            if result.status_code == 200:
                log.info('Successfully submitted new task')
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
