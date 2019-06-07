"""Validate resource parameters and deploy app. kernel stack to remote resource"""
import sys
import io
import datetime
import time
import copy
import os
import json
import xml.etree.ElementTree
import pprint
import MySQLdb
import traceback
import requests

import akrr
import akrr.db
import akrr.util.ssh
from akrr import cfg
from akrr import akrrrestclient
from akrr.akrrerror import AkrrError
import akrr.util.log as log
import akrr.util.openstack
from akrr.util.ssh import check_dir

pp = pprint.PrettyPrinter(indent=4)

checking_frequency = 5


def make_results_summary(resource_name, app_name, completed_tasks,
                         akrr_xdmod_instanceinfo, akrr_errmsg, mega_verbose=False):
    def add_file_ref(comment, filename):
        if os.path.exists(filename):
            return comment + ": " + filename + "\n"
        else:
            return comment + ": " + "Not Present" + "\n"

    task_dir = os.path.join(cfg.completed_tasks_dir, resource_name, app_name, completed_tasks['datetime_stamp'])

    msg = ""
    msg += "status: " + str(akrr_xdmod_instanceinfo['status']) + "\n"
    if akrr_xdmod_instanceinfo['status'] == 0:
        msg += "\tstatus2: " + completed_tasks['status'] + "\n"
    msg += "status_info: " + completed_tasks['status_info'] + "\n"
    msg += 'processing message:\n'
    msg += str(akrr_xdmod_instanceinfo['message']) + "\n"
    if mega_verbose:
        msg += 'error message:\n'
        if isinstance(akrr_errmsg, dict):
            for v in ("task_id", "appstdout", "stdout", "stderr", "taskexeclog", "err_regexp_id"):
                if v in akrr_errmsg:
                    msg += v+": "+str(akrr_errmsg[v]) + "\n"

        else:
            msg += str(akrr_errmsg) + "\n"
    msg += add_file_ref("Local working directory for this task", task_dir)
    msg += 'Location of some important generated files:\n'
    msg += "\t" + add_file_ref("Batch job script", os.path.join(task_dir, 'jobfiles', app_name + ".job"))
    msg += "\t" + add_file_ref("Application kernel output", os.path.join(task_dir, 'jobfiles', 'appstdout'))
    msg += "\t" + add_file_ref("Batch job standard output", os.path.join(task_dir, 'jobfiles', 'stdout'))
    msg += "\t" + add_file_ref("Batch job standard error output", os.path.join(task_dir, 'jobfiles', 'stderr'))
    msg += "\t" + add_file_ref("XML processing results", os.path.join(task_dir, 'result.xml'))
    msg += "\t" + add_file_ref("Task execution logs", os.path.join(task_dir, 'proc', 'log'))

    return msg


def validate_resource_parameter_file(resource_name):
    """validate resource parameter file and return dictionary with resource configuration"""
    # @todo reuse  cfg.verify_resource_params
    default_resource_param_filename = os.path.join(cfg.akrr_mod_dir, "default_conf", "default.resource.conf")
    resource_param_filename = os.path.join(cfg.cfg_dir, "resources", resource_name, "resource.conf")

    log.info("Validating %s parameters from %s", resource_name, resource_param_filename)

    if not os.path.isfile(resource_param_filename):
        log.error("resource parameters file (%s) does not exist!", resource_param_filename)
        exit(1)

    # check syntax
    try:
        tmp = {}
        exec(compile(open(default_resource_param_filename).read(), default_resource_param_filename, 'exec'), tmp)
        exec(compile(open(resource_param_filename).read(), resource_param_filename, 'exec'), tmp)
    except Exception as e:
        log.critical("Can not load resource from %s.\nProbably invalid syntax.", resource_param_filename)
        raise e

    resource = None
    try:
        # now we can load akrr, parameters checking did h
        resource = cfg.find_resource_by_name(resource_name)
    except Exception as e:
            log.error(
                "Can not load resource config from %s!\n%s\n%s",
                resource_param_filename, str(e), traceback.format_exc())
            exit(1)

    log.info("Syntax of %s is correct and all necessary parameters are present.", resource_param_filename)
    log.empty_line()
    return resource


def connect_to_resource(resource):
    """connect to resource defined in resource dictionary"""
    log.info("Validating resource accessibility. Connecting to %s.", resource['name'])
    if resource['ssh_private_key_file'] is not None and os.path.isfile(resource['ssh_private_key_file']) is False:
        log.error("Can not access ssh private key (%s)""", resource['ssh_private_key_file'])
        exit(1)

    str_io = io.StringIO()
    try:
        sys.stdout = sys.stderr = str_io
        rsh = akrr.util.ssh.ssh_resource(resource)

        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        log.info("Successfully connected to %s\n", resource['name'])
        log.empty_line()

        return rsh
    except AkrrError:
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        log.critical("Can not connect to %s\nMessage:\n%s", resource['name'], str_io.getvalue())
        exit(1)


def check_shell(rsh, resource):
    log.info("Checking if shell is BASH\n")
    msg = akrr.util.ssh.ssh_command(rsh, "echo $BASH")
    if msg.count("bash") > 0:
        log.info("Shell is BASH\n")
    else:
        log.error("Shell on headnode of %s is not BASH, change it to bash and try again.\n", resource['name'])
        exit(1)


def check_create_dirs(rsh, resource):
    log.info("Checking directory locations\n")

    d = resource['akrr_data']
    log.info("Checking: %s:%s", resource['remote_access_node'], d)
    status, msg = check_dir(rsh, d, exit_on_fail=True, try_to_create=True)
    log.info(msg)

    d = resource['appkernel_dir']
    log.info("Checking: %s:%s", resource['remote_access_node'], d)
    status, msg = check_dir(rsh, d, exit_on_fail=True, try_to_create=True)
    log.info(msg)

    d = resource['network_scratch']
    log.info("Checking: %s:%s", resource['remote_access_node'], d)
    status, msg = check_dir(rsh, d, exit_on_fail=False, try_to_create=True)

    if status is True:
        log.info(msg)
    else:
        log.warning_count += 1
        log.warning(msg)
        log.warning(
            "WARNING %d: network scratch might be have a different location on head node, "
            "so if it is by design it is ok",
            log.warning_count)

    d = resource['local_scratch']
    log.info("Checking: %s:%s", resource['remote_access_node'], d)
    status, msg = check_dir(rsh, d, exit_on_fail=False, try_to_create=False)
    if status is True:
        log.info(msg)
    else:
        log.warning_count += 1
        log.warning(msg)
        log.warning(
            "WARNING %d: local scratch might be have a different location on head node, "
            "so if it is by design it is ok",
            log.warning_count)

    log.empty_line()


def copy_exec_sources_and_inputs(rsh, resource):
    """Copy exec sources and inputs to remote resource"""
    log.info(
        "Preparing to copy application signature calculator,\n"
        "    app. kernel input files and \n"
        "    HPCC, IMB, IOR and Graph500 source code to remote resource\n")

    try:
        akrr.util.ssh.ssh_command(rsh, "cd %s" % resource['appkernel_dir'])
        out = akrr.util.ssh.ssh_command(rsh, "ls " + resource['appkernel_dir'])
        files_in_appker_dir = out.strip().split()

        if not ("inputs" in files_in_appker_dir or "inputs/" in files_in_appker_dir):
            log.info("Copying app. kernel input tarball to %s", resource['appkernel_dir'])
            if not akrr.dry_run:
                akrr.util.ssh.scp_to_resource(resource, cfg.appker_repo_dir + "/inputs.tar.gz", resource['appkernel_dir'])

            log.info("Unpacking app. kernel input files to %s/inputs", resource['appkernel_dir'])
            if not akrr.dry_run:
                out = akrr.util.ssh.ssh_command(rsh, "tar xvfz %s/inputs.tar.gz" % resource['appkernel_dir'])
                log.debug(out)

                out = akrr.util.ssh.ssh_command(rsh, "du -h %s/inputs" % resource['appkernel_dir'])
                log.debug(out)

                if out.count("No such file or directory") == 0:
                    log.info("App. kernel input files are in %s/inputs\n", resource['appkernel_dir'])
                else:
                    raise Exception("files are not copied!")
        else:
            log.warning_count += 1
            log.warning("WARNING %d: App. kernel inputs directory %s/inputs is present, assume they are correct.\n",
                        log.warning_count, resource['appkernel_dir'])

        if not ("execs" in files_in_appker_dir or "execs/" in files_in_appker_dir):
            log.info(
                "Copying app. kernel execs tarball to %s\n" % (resource['appkernel_dir']) +
                "It contains HPCC,IMB,IOR and Graph500 source code and app.signature calculator")
            if not akrr.dry_run:
                akrr.util.ssh.scp_to_resource(resource, cfg.appker_repo_dir + "/execs.tar.gz", resource['appkernel_dir'])
            log.info("Unpacking HPCC,IMB,IOR and Graph500 source code and app.signature calculator files to %s/execs",
                     resource['appkernel_dir'])
            if not akrr.dry_run:
                out = akrr.util.ssh.ssh_command(rsh, "tar xvfz %s/execs.tar.gz" % resource['appkernel_dir'])
                log.debug(out)

                out = akrr.util.ssh.ssh_command(rsh, "df -h %s/execs" % resource['appkernel_dir'])
                log.debug(out)

                if out.count("No such file or directory") == 0:
                    log.info("HPCC,IMB,IOR and Graph500 source code and app.signature calculator are in %s/execs\n",
                             resource['appkernel_dir'])
                else:
                    raise Exception("files are not copied!")
        else:
            log.warning_count += 1
            log.warning("WARNING %d: App. kernel executables directory %s/execs is present, assume they are correct.",
                        log.warning_count, resource['appkernel_dir'])
            log.warning("It should contain HPCC,IMB,IOR and Graph500 source code and app.signature calculator\n")

        akrr.util.ssh.ssh_command(rsh, "rm execs.tar.gz  inputs.tar.gz")
    except Exception as e:
        log.critical("Can not copy files to %s", resource['name'])
        raise e


def check_appsig(rsh, resource):
    log.info("Testing app.signature calculator on headnode\n")
    out = akrr.util.ssh.ssh_command(rsh, "%s/execs/bin/appsigcheck.sh `which md5sum`" % (resource['appkernel_dir'],))
    if out.count("===ExeBinSignature===") > 0 and out.count("MD5:") > 0:
        log.info("App.signature calculator is working on headnode\n")
    else:
        if akrr.dry_run:
            log.dry_run("App.signature calculator is not working\n")
            return
        log.error("App.signature calculator is not working\n" +
                  "See full error report below\n%s", out)
        exit(1)


def check_connection_to_rest_api():
    # get check connection
    try:
        r = akrrrestclient.get('/scheduled_tasks')
        if r.status_code != 200:
            log.error(
                "Can not get token for AKRR REST API ( %s )\nSee server response below\n%s",
                akrrrestclient.restapi_host, json.dumps(r.json(), indent=4))
            exit(1)
    except Exception as e:
        log.critical(
            "Can not connect to AKRR REST API ( %s )\nIs it running?\nSee full error report below",
            akrrrestclient.restapi_host)
        raise e


def get_test_job_lock_filename(resource, app_name="test"):
    return os.path.join(cfg.data_dir, resource["name"] + "_" + app_name + "_task.dat")


def check_if_test_job_already_submitted(resource, app_name="test"):
    """check if the test job is already submitted, return task id if it is submitted"""
    task_id = None
    test_job_lock_filename = get_test_job_lock_filename(resource, app_name)
    if os.path.isfile(test_job_lock_filename):
        fin = open(test_job_lock_filename, "r")
        task_id = int(fin.readline())
        fin.close()

        r = akrrrestclient.get('/tasks/' + str(task_id))
        if r.status_code != 200:
            task_id = None
        else:
            log.warning_count += 1
            log.warning("\nWARNING %d: Seems this is rerun of this script, will monitor task with task_id = %d ",
                        log.warning_count, task_id)
            log.warning("To submit new task delete %s\n", test_job_lock_filename)

        # check how old is it
    return task_id


def submit_test_job(resource, app_name="test", nodes=2):
    # submit test job
    r = None
    try:
        payload = {'resource': resource['name'],
                   'app': app_name,
                   'resource_param': "{'nnodes':%d}" % nodes,
                   'task_param': "{'test_run':True}"
                   }
        r = akrrrestclient.post('/scheduled_tasks', data=payload)
        if r.status_code != 200:
            log.error(
                "Can not submit task through AKRR REST API ( %s )\nSee server response below\n%s\n",
                akrrrestclient.restapi_host, json.dumps(r.json(), indent=4))
            exit(1)
        task_id = r.json()['data']['data']['task_id']
    except Exception as e:
        if r is not None:
            log.critical(
                "Can not submit task through AKRR REST API ( %s )\n"
                "Is it still running?\nSee full error report below\n%s",
                akrrrestclient.restapi_host, r.json())
        else:
            log.critical(
                "Can not submit task through AKRR REST API ( %s )\n"
                "Is it still running?\n",
                akrrrestclient.restapi_host)
        raise e

    # write file with task_id
    test_job_lock_filename = get_test_job_lock_filename(resource, app_name)
    with open(test_job_lock_filename, "w") as fout:
        print(task_id, file=fout)

    log.info("\nSubmitted test job to AKRR, task_id is %d\n", task_id)
    return task_id


def monitor_test_job(task_id):
    """monitor the job progress, wait till job is done """
    completed_tasks = None
    akrr_xdmod_instance_info = None
    akrr_errmsg = None

    msg_body_prev = ""

    bad_cycles = 0
    while True:
        t = datetime.datetime.now()

        r = akrrrestclient.get('/tasks/' + str(task_id))

        response_json = r.json()

        if r.status_code == 200:
            response_json = r.json()

            msg_body = "Test status:\n"

            if response_json["data"]["queue"] == "scheduled_tasks":
                msg_body += "Task is in scheduled_tasks queue.\n"
                msg_body += "It schedule to be started on " + response_json["data"]["data"]['time_to_start'] + "\n"
            elif response_json["data"]["queue"] == "active_tasks":
                msg_body += "Task is in active_tasks queue.\n"
                msg_body += "Status: " + str(response_json["data"]["data"]['status']) + "\n"
                msg_body += "Status info:\n" + str(response_json["data"]["data"]['status_info']) + "\n"
            elif response_json["data"]["queue"] == "completed_tasks":
                msg_body += "Task is completed!\n"
                completed_tasks = r.json()['data']['data']['completed_tasks']
                akrr_xdmod_instance_info = r.json()['data']['data']['akrr_xdmod_instanceinfo']
                akrr_errmsg = r.json()['data']['data'].get('akrr_errmsg', "None")
                if log.verbose:
                    msg_body += "completed_tasks table entry:\n" + pp.pformat(completed_tasks) + "\n"
                    msg_body += "akrr_xdmod_instanceinfo table entry:\n" + pp.pformat(akrr_xdmod_instance_info) + "\n"
                    msg_body += 'output parsing results:\n' + akrr_xdmod_instance_info['body'] + "\n"
                else:
                    msg_body += "\tstatus: " + str(akrr_xdmod_instance_info['status']) + "\n"
                    if akrr_xdmod_instance_info['status'] == 0:
                        msg_body += "\tstatus2: " + completed_tasks['status'] + "\n"
                    msg_body += "\tstatus_info: " + completed_tasks['status_info'] + "\n"
            else:
                msg_body += r.text + "\n"

            tail_msg = "time: " + t.strftime("%Y-%m-%d %H:%M:%S")

            if msg_body != msg_body_prev:
                print("\n\n" + msg_body)
                print(tail_msg, end=' ')
                sys.stdout.flush()
            else:
                print("\r" + tail_msg, end=' ')
                sys.stdout.flush()

            msg_body_prev = copy.deepcopy(msg_body)

            if response_json["data"]["queue"] == "completed_tasks":
                break
        else:
            bad_cycles += 1
            if bad_cycles > 3:
                log.error("Something wrong, REST API said: %s", response_json)
                break

        # try to update:
        try:
            payload = {'next_check_time': ''}
            akrrrestclient.put('/active_tasks/' + str(task_id), data=payload)
        except Exception as e:
            bad_cycles += 1
            if bad_cycles > 10:
                log.error("Something wrong with REST API")
                raise e

        time.sleep(checking_frequency)
    print("\n\n")
    return completed_tasks, akrr_xdmod_instance_info, akrr_errmsg


def analyse_test_job_results(task_id, resource, app_name="test"):
    """analysing the output"""
    log.info("Test job is completed analyzing output\n")
    test_job_lock_filename = get_test_job_lock_filename(resource, app_name)
    r = akrrrestclient.get('/tasks/%d' % task_id)

    if r.status_code != 200:
        log.error("Can not get information about task\nSee full error report below\nAKRR server response:\n%s\n",
                  r.text)
        exit(1)

    completed_tasks = r.json()['data']['data']['completed_tasks']
    akrr_xdmod_instance_info = r.json()['data']['data']['akrr_xdmod_instanceinfo']
    akrr_errmsg = r.json()['data']['data'].get('akrr_errmsg', "None")

    results_summary = make_results_summary(
        resource['name'], app_name, completed_tasks, akrr_xdmod_instance_info, akrr_errmsg)

    if completed_tasks['status'].count("ERROR") > 0:
        # execution was not successful
        if completed_tasks['status'].count("ERROR Can not created batch job script and submit it to remote queue") > 0:
            log.error(
                "Can not created batch job script and/or submit it to remote queue\nSee full error report below\n%s",
                results_summary)
        else:
            log.error("Status: %s\nSee full error report below\n%s", completed_tasks['status'], results_summary)
        os.remove(test_job_lock_filename)
        exit(1)

    if akrr_xdmod_instance_info['status'] == 0:
        # execution was not successful
        log.error("Task execution was not successful\nSee full error report below\n%s", results_summary)
        os.remove(test_job_lock_filename)
        exit(1)

    # see what is in report
    elm_perf = xml.etree.ElementTree.fromstring(akrr_xdmod_instance_info['body'])
    elm_parameters = elm_perf.find('benchmark').find('parameters')
    elm_statistics = elm_perf.find('benchmark').find('statistics')

    parameters = {'RunEnv:Nodes': '',
                  'App:ExeBinSignature': ''
                  }
    statistics = {'Wall Clock Time': '0.0',
                  'Network scratch directory exists': '0',
                  'Network scratch directory accessible': '0',
                  'App kernel input exists': '0',
                  'Task working directory accessible': '0',
                  'local scratch directory accessible': '0',
                  'local scratch directory exists': '0',
                  'App kernel executable exists': '0',
                  'Task working directory exists': '0',
                  'Shell is BASH': '0'
                  }

    for elm in list(elm_parameters):
        variable = elm.findtext('ID')
        if variable is not None:
            variable = variable.strip()
        value = elm.findtext('value')
        if value is not None:
            value = value.strip()
        units = elm.findtext('units')
        if units is not None:
            units = units.strip()

        if variable == 'App:ExeBinSignature' or variable == 'RunEnv:Nodes':
            value = os.popen('echo "%s"|base64 -d|gzip -d' % (value,)).read()

        log.debug2("parameter: {} = {} {}".format(variable, value, units))
        parameters[variable] = value

    for elm in list(elm_statistics):
        variable = elm.findtext('ID')
        if variable is not None:
            variable = variable.strip()
        value = elm.findtext('value')
        if value is not None:
            value = value.strip()
        units = elm.findtext('units')
        if units is not None:
            units = units.strip()

        statistics[variable] = value
        log.debug2("statistic: {} = {} {}".format(variable, value, units))

    files_exists = [
        'Network scratch directory exists',
        'App kernel input exists',
        'local scratch directory exists',
        'App kernel executable exists',
        'Task working directory exists']
    dirs_access = [
        'Network scratch directory accessible',
        'Task working directory accessible',
        'local scratch directory accessible']

    if statistics['Shell is BASH'] == '0':
        log.error("Shell on compute nodes of %s is not BASH, change it to bash and try again.\n", resource['name'])
        log.error_count += 1
    for file_exists in files_exists:
        if statistics[file_exists] == '0':
            log.error(file_exists.replace('exists', 'does not exist'))
            log.error_count += 1
    for dirAccess in dirs_access:
        if statistics[dirAccess] == '0':
            log.error(dirAccess.replace('accessible', 'is not accessible'))
            log.error_count += 1

    if parameters['App:ExeBinSignature'] == '':
        log.error(
            "Application signature calculator is not working, you might need to recompile it."
            "see application output for more hints")
        log.error_count += 1

    if resource['batch_scheduler'].lower() != "openstack":
        # test the nodes, log to headnode and ping them
        if parameters['RunEnv:Nodes'] == '':
            log.error("Nodes are not detected, check batch_job_template and setup of AKRR_NODELIST variable")
            log.error_count += 1

        nodes = parameters['RunEnv:Nodes'].split()

        requested_nodes = eval(completed_tasks['resource_param'])['nnodes']

        str_io = io.StringIO()
        try:
            sys.stdout = sys.stderr = str_io
            rsh = akrr.util.ssh.ssh_resource(resource)

            number_of_unknown_hosts = 0
            for node in set(nodes):
                log.debug2(node)
                out = akrr.util.ssh.ssh_command(rsh, "ping -c 1 %s" % node)
                if out.count("unknown host") > 0:
                    number_of_unknown_hosts += 1

            rsh.close(force=True)
            del rsh

            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

            if number_of_unknown_hosts > 0:
                log.error("ERROR %d: Can not ping compute nodes from head node\n" % (log.error_count + 1) +
                          "Nodes on which test job was executed detected as " + parameters['RunEnv:Nodes'] + "\n" +
                          "If these names does not have sense check batch_job_template and setup of AKRR_NODELIST "
                          "variable in resource configuration file")
                log.error_count += 1
        except Exception as e:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            log.critical("Can not connect to %s\nProbably invalid credential, see full error report:\n%s",
                         resource['name'], str_io.getvalue())
            raise e

        # check ppn count
        if requested_nodes * resource['ppn'] != len(nodes):
            log.error(
                "ERROR {}: Number of requested processes (processes per node * nodes) "
                "do not match actual processes executed"
                "Either\n"
                "    AKRR_NODELIST variable is set incorrectly\n"
                "Or\n"
                "    processes per node (PPN) is wrong\n".format(log.error_count + 1))
            log.error_count += 1
    log.info("\nTest kernel execution summary:\n%s", results_summary)
    log.info("\nThe output looks good.\n")


def run_test_job(resource, app_name="test", nodes=2):
    log.info("Will send test job to queue, wait till it executed and will analyze the output")
    log.debug("Will use AKRR REST API at {}".format(akrrrestclient.restapi_host))

    check_connection_to_rest_api()

    if akrr.dry_run:
        return

    task_id = check_if_test_job_already_submitted(resource, app_name)

    if task_id is None:
        task_id = submit_test_job(resource, app_name, nodes)

    monitor_test_job(task_id)
    analyse_test_job_results(task_id, resource, app_name)

    os.remove(get_test_job_lock_filename(resource, app_name))


def append_to_bashrc(resource):
    # append environment variables to .bashrc
    log.info("\nAdding AKRR enviroment variables to resource's .bashrc!\n")
    if akrr.dry_run:
        return

    str_io = io.StringIO()
    try:
        sys.stdout = sys.stderr = str_io
        rsh = akrr.util.ssh.ssh_resource(resource)
        akrr_header = 'AKRR Remote Resource Environment Variables'

        out = akrr.util.ssh.ssh_command(
            rsh,
            '''if [ -e $HOME/.bashrc ]
then
   if [[ `grep "\#''' + akrr_header + ''' \[Start\]" $HOME/.bashrc` == *"''' + akrr_header + ''' [Start]"* ]]
   then
       echo "Updating AKRR record in $HOME/.bashrc, backing to $HOME/.bashrc_akrrbak"
       cp $HOME/.bashrc $HOME/.bashrc_akrrbak
       head -n "$(( $(grep -n '\#''' + akrr_header + ''' \[Start\]' $HOME/.bashrc_akrrbak | head -n 1 | cut -d ":" -f 1) - 1 ))" $HOME/.bashrc_akrrbak > $HOME/.bashrc
       tail -n "+$(( $(grep -n '\#''' + akrr_header + ''' \[End\]' $HOME/.bashrc_akrrbak | head -n 1 | cut -d ":" -f 1) + 1 ))" $HOME/.bashrc_akrrbak  >> $HOME/.bashrc
   fi
fi''')
        log.debug(out)
        cmds = (
            '''echo "Appending AKRR records to $HOME/.bashrc"''',
            '''echo "#''' + akrr_header + ''' [Start]" >> $HOME/.bashrc''',
            '''echo "export AKRR_NETWORK_SCRATCH=\\"''' + resource['network_scratch'] + '''\\"" >> $HOME/.bashrc''',
            '''echo "export AKRR_LOCAL_SCRATCH=\\"''' + resource['local_scratch'] + '''\\"" >> $HOME/.bashrc''',
            '''echo "export AKRR_APPKER_DIR=\\"''' + resource['appkernel_dir'] + '''\\"" >> $HOME/.bashrc''',
            '''echo "export AKRR_AKRR_DIR=\\"''' + resource['akrr_data'] + '''\\"" >> $HOME/.bashrc''',
            '''echo "#''' + akrr_header + ''' [End]" >> $HOME/.bashrc''',
            '''echo "Appending AKRR records to $HOME/.bashrc"'''
        )
        for cmd in cmds:
            out = akrr.util.ssh.ssh_command(rsh, cmd)
            log.debug(out)
        rsh.close(force=True)
        del rsh


        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
    except Exception as e:
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        log.critical("Can not connect to %s\nProbably invalid credential, see full error report:\n%s",
                     resource['name'], str_io.getvalue())
        raise e


def enable_resource_for_execution(resource):
    """populate mod_appkernel database and allow execution of jobs on this resource"""
    if akrr.dry_run:
        return
    resource_name = resource['name']
    try:
        con_ak, cur_ak = akrr.db.get_ak_db(True)

        cur_ak.execute('''SELECT * FROM resource WHERE nickname=%s''', (resource_name,))
        resource_in_ak_db = cur_ak.fetchall()
        if len(resource_in_ak_db) == 0:
            log.warning("There is no record of %s in mod_appkernel.resource will add one.", resource_name)
            cur_ak.execute('''INSERT INTO resource (resource,nickname,description,enabled,visible)
                        VALUES(%s,%s,%s,0,0);''',
                           (resource['name'], resource['name'], resource['info']))
            con_ak.commit()

            cur_ak.execute('''SELECT * FROM resource WHERE nickname=%s''', (resource_name,))
            resource_in_ak_db = cur_ak.fetchall()
        resource_in_ak_db = resource_in_ak_db[0]
        # enable and make visible
        cur_ak.execute('''UPDATE resource
                        SET enabled=1,visible=1
                        WHERE resource_id=%s;''',
                       (resource_in_ak_db['resource_id'],))
        con_ak.commit()
        log.info("Enabled %s in mod_appkernel.resource for tasks execution and made it visible to XDMoD UI.",
                 resource_name)
    except MySQLdb.Error:
        log.error(
            "Can not connect to AK DB\n"
            "Probably invalid credential")

    # enabling resource for execution
    try:
        r = akrrrestclient.put('/resources/' + resource_name + '/on')
        if r.status_code == 200:
            log.info('Successfully enabled ' + resource_name)
        else:
            log.error(
                "Can not enable resource through AKRR REST API ( %s )\nSee server response below\n%s",
                akrrrestclient.restapi_host, json.dumps(r.json(), indent=4))
    except requests.RequestException:
        log.error(
            "Can not enable resource through AKRR REST API ( %s )\n"
            "Is it still running?\n",
            akrrrestclient.restapi_host)


def resource_deploy(args):
    global checking_frequency

    resource_name = args.resource

    if 'dry_run' in args:
        akrr.dry_run = args.dry_run
    else:
        akrr.dry_run = False

    if "checking_frequency" in args:
        checking_frequency = args.checking_frequency

    if "appkernel" in args:
        app_name = args.appkernel
    else:
        app_name = "test"

    if "nodes" in args:
        nodes = int(args.nodes)
    else:
        nodes = 2

    log.error_count = 0
    log.warning_count = 0

    # validate resource configuration and get config
    resource = validate_resource_parameter_file(resource_name)

    # connect to resource
    if resource['batch_scheduler'].lower() == "openstack":
        # Start instance if it is cloud
        openstack_server = akrr.util.openstack.OpenStackServer(resource=resource)
        resource['openstack_server'] = openstack_server
        openstack_server.create()
        resource['remote_access_node'] = openstack_server.ip
    rsh = connect_to_resource(resource)

    # do tests
    check_shell(rsh, resource)
    check_create_dirs(rsh, resource)

    # deploy inputs and sources
    copy_exec_sources_and_inputs(rsh, resource)

    # check that app.signature calculator on headnode
    check_appsig(rsh, resource)

    # close connection we don't need it any more
    rsh.close(force=True)
    del rsh
    if resource['batch_scheduler'].lower() == "openstack":
        # delete instance if it is cloud
        akrr.util.openstack.OpenStackServer(resource=resource)
        resource['openstack_server'].delete()
        resource['remote_access_node'] = None

    # run test job to queue
    run_test_job(resource, app_name, nodes)

    if resource['batch_scheduler'].lower() == "openstack":
        # Start instance if it is cloud
        openstack_server = akrr.util.openstack.OpenStackServer(resource=resource)
        resource['openstack_server'] = openstack_server
        openstack_server.create()
        resource['remote_access_node'] = openstack_server.ip

    if log.error_count == 0:
        append_to_bashrc(resource)
        enable_resource_for_execution(resource)

    if resource['batch_scheduler'].lower() == "openstack":
        # delete instance if it is cloud
        akrr.util.openstack.OpenStackServer(resource=resource)
        resource['openstack_server'].delete()
        resource['remote_access_node'] = None

    log.empty_line()

    log.info("Result:")
    if log.error_count > 0:
        log.error("There are %d errors, fix them.", log.error_count)

    if log.warning_count > 0:
        log.warning("There are %d warnings.\nif warnings have sense you can move to next step!\n", log.warning_count)
    if log.error_count == 0 and log.warning_count == 0:
        log.info("\nDONE, you can move to next step!\n")
