"""Validate appkernel parameters"""

import sys
import os
import traceback
import io
import datetime
import time
import copy
import pprint
import json
import xml.etree.ElementTree as ET

import akrr.db
import akrr.util.ssh
from akrr.util import log

pp = pprint.PrettyPrinter(indent=4)


def CheckDirSimple(sh, d):
    """
    check directory existance and verify accessability
    return None,message if does not exists
    return True,message if can write there
    return False,message if can not write there
    """
    from . import cfg
    dir(sh)
    cmd = "if [ -d \"%s\" ]\n then \necho EXIST\n else echo DOESNOTEXIST\n fi" % (d)
    msg = akrr.util.ssh.ssh_command(sh, cmd)
    if msg.find("DOESNOTEXIST") >= 0:
        return None, "Directory %s:%s does not exists!" % (sh.remote_machine, d)

    cmd = "echo test > " + os.path.join(d, 'akrrtestwrite')
    # print cmd
    msg = akrr.util.ssh.ssh_command(sh, cmd)
    # print msg
    cmd = "cat " + os.path.join(d, 'akrrtestwrite')
    # print cmd
    msg = akrr.util.ssh.ssh_command(sh, cmd)
    # print msg
    if msg.strip() == "test":
        cmd = "rm " + os.path.join(d, 'akrrtestwrite')
        akrr.util.ssh.ssh_command(sh, cmd)
        return True, "Directory exist and accessible for read/write"
    else:
        return False, "Directory %s:%s is NOT accessible for read/write!" % (sh.remote_machine, d)


def CheckDir(sh, d, exitOnFail=True, tryToCreate=True):
    from . import cfg
    status, msg = CheckDirSimple(sh, d)
    if tryToCreate == True and status == None:
        log.info("Directory %s:%s does not exists, will try to create it" % (sh.remote_machine, d))
        cmd = "mkdir \"%s\"" % (d)
        akrr.util.ssh.ssh_command(sh, cmd)
        status, msg = CheckDirSimple(sh, d)
    if exitOnFail is False:
        return status, msg

    if status is None:
        log.error("Directory %s:%s does not exists!", sh.remote_machine, d)
        exit(1)
    elif status is True:
        return True, msg
    else:
        log.error("Directory %s:%s is NOT accessible for read/write!", sh.remote_machine, d)
        exit(1)


def app_validate(resource, appkernel, nnodes):
    from akrr.util.log import verbose
    resource_name = resource
    app_name = appkernel

    errorCount = 0
    warningCount = 0

    log.info("Validating " + app_name + " application kernel installation on " + resource_name)

    from akrr import get_akrr_dirs

    akrr_dirs = get_akrr_dirs()

    default_resource_param_filename = os.path.abspath(os.path.join(akrr_dirs['default_dir'], "default.resource.conf"))
    resource_param_filename = os.path.abspath(
        os.path.join(akrr_dirs['cfg_dir'], "resources", resource_name, "resource.conf"))

    default_app_param_filename = os.path.abspath(os.path.join(akrr_dirs['default_dir'], "default.app.conf"))
    app_ker_param_filename = os.path.abspath(os.path.join(akrr_dirs['default_dir'], app_name + ".app.conf"))
    ###############################################################################################
    # validating resource parameter file

    log.info("#" * 80)
    log.info("Validating %s parameters from %s" % (resource_name, resource_param_filename))

    if not os.path.isfile(resource_param_filename):
        log.error("resource parameters file (%s) do not exists!" % (resource_param_filename,))
        exit(1)

    # check syntax
    try:
        tmp = {}
        exec(compile(open(default_resource_param_filename).read(), default_resource_param_filename, 'exec'), tmp)
        exec(compile(open(resource_param_filename).read(), resource_param_filename, 'exec'), tmp)
    except Exception:
        log.exception("Can not load resource from """ + resource_param_filename + "\n" +
                      "Probably invalid syntax.")
        exit(1)
    # check syntax
    try:
        tmp = {}
        exec(compile(open(default_app_param_filename).read(), default_app_param_filename, 'exec'), tmp)
        exec(compile(open(app_ker_param_filename).read(), app_ker_param_filename, 'exec'), tmp)
    except Exception:
        log.exception("Can not load application kernel from """ + app_ker_param_filename + "\n" +
                      "Probably invalid syntax")
        exit(1)

    # now we can load akrr
    from . import cfg
    from . import akrrrestclient
    from .cli.resource_deploy import  make_results_summary

    resource = cfg.find_resource_by_name(resource_name)
    log.info("Syntax of %s is correct and all necessary parameters are present." % resource_param_filename)

    app = cfg.find_app_by_name(app_name)
    # check the presence of runScript[resource]
    # if resource_name not in app['runScript'] and 'default' not in app['runScript']:
    #    logerr("Can not load application kernel from """+app_ker_param_filename+"\n"+
    #           "runScript['%s'] is not set"%(resource_name,))
    #    exit(1)
    log.info("Syntax of %s is correct and all necessary parameters are present." % app_ker_param_filename)

    # check if AK is in DB
    if True:
        # add entry to mod_appkernel.resource
        dbAK, curAK = akrr.db.get_ak_db(True)

        curAK.execute('''SELECT * FROM app_kernel_def WHERE ak_base_name=%s''', (app_name,))
        ak_in_AKDB = curAK.fetchall()
        if len(ak_in_AKDB) == 0:
            curAK.execute('''INSERT INTO app_kernel_def (name,ak_base_name,processor_unit,enabled, description, visible)
                        VALUES(%s,%s,'node',0,%s,0);''',
                          (app_name, app_name, app_name))
            dbAK.commit()
        curAK.execute('''SELECT * FROM app_kernel_def WHERE ak_base_name=%s''', (app_name,))
        ak_in_AKDB = curAK.fetchall()[0]
        # add entry to mod_akrr.resource
        db, cur = akrr.db.get_akrr_db(True)

        cur.execute('''SELECT * FROM app_kernels WHERE name=%s''', (app_name,))
        ak_in_DB = cur.fetchall()
        if len(ak_in_DB) == 0:
            cur.execute('''INSERT INTO app_kernels (id,name,enabled,nodes_list)
                        VALUES(%s,%s,0,'1,2,4,8');''',
                        (ak_in_AKDB['ak_def_id'], app_name))
            db.commit()

    ###############################################################################################
    # connect to resource
    log.info("#" * 80)
    log.info("Validating resource accessibility. Connecting to %s." % (resource['name']))
    if resource['ssh_private_key_file'] != None and os.path.isfile(resource['ssh_private_key_file']) == False:
        log.error("Can not access ssh private key (%s)""" % (resource['ssh_private_key_file'],))
        exit(1)

    str_io = io.StringIO()
    try:
        sys.stdout = sys.stderr = str_io
        rsh = akrr.util.ssh.ssh_resource(resource)

        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
    except Exception as e:
        msg2 = str_io.getvalue()
        msg2 += "\n" + traceback.format_exc()
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        log.error("Can not connect to """ + resource['name'] + "\n" +
                  "Probably invalid credential, see full error report below", msg2)
        exit(1)
    print("=" * 80)
    log.info("Successfully connected to %s\n\n" % (resource['name']))

    ###############################################################################################
    log.info("Checking directory locations\n")

    d = resource['akrr_data']
    log.info("Checking: %s:%s" % (resource['remoteAccessNode'], d))
    status, msg = CheckDir(rsh, d, exitOnFail=True, tryToCreate=True)
    log.info(msg + "\n")

    d = resource['appKerDir']
    log.info("Checking: %s:%s" % (resource['remoteAccessNode'], d))
    status, msg = CheckDir(rsh, d, exitOnFail=True, tryToCreate=True)
    log.info(msg + "\n")

    d = resource['networkScratch']
    log.info("Checking: %s:%s" % (resource['remoteAccessNode'], d))
    status, msg = CheckDir(rsh, d, exitOnFail=False, tryToCreate=False)
    if status == True:
        log.info(msg)
    else:
        log.warning(msg)
        log.warning(
            "WARNING %d: network scratch might be have a different location on head node, so if it is by design it is ok" % (
                        warningCount + 1))
        warningCount += 1
    log.info("")

    d = resource['local_scratch']
    log.info("Checking: %s:%s" % (resource['remoteAccessNode'], d))
    status, msg = CheckDir(rsh, d, exitOnFail=False, tryToCreate=False)
    if status == True:
        log.info(msg)
    else:
        log.warning(msg)
        log.warning(
            "WARNING %d: local scratch might be have a different location on head node, so if it is by design it is ok" % (
                        warningCount + 1))
        warningCount += 1
    log.info("")

    # close connection we don't need it any more
    rsh.close(force=True)
    del rsh
    ###############################################################################################
    # send test job to queue

    log.info("#" * 80)
    log.info("Will send test job to queue, wait till it executed and will analyze the output")

    print("Will use AKRR REST API at", akrrrestclient.restapi_host)
    # get check connection
    try:
        r = akrrrestclient.get('/scheduled_tasks')
        if r.status_code != 200:
            log.error("Can not get token for AKRR REST API ( """ + akrrrestclient.restapi_host + " )\n" +
                      "See server response below", json.dumps(r.json(), indent=4))
            exit(1)
    except Exception as e:
        log.error("Can not connect to AKRR REST API ( """ + akrrrestclient.restapi_host + " )\n" +
                  "Is it running?\n" +
                  "See full error report below", traceback.format_exc())
        exit(1)

    # check if the test job is already submitted
    task_id = None
    test_job_lock_filename = os.path.join(cfg.data_dir, resource_name + "_" + app_name + "_test_task.dat")
    if os.path.isfile(test_job_lock_filename):
        fin = open(test_job_lock_filename, "r")
        task_id = int(fin.readline())
        fin.close()

        r = akrrrestclient.get('/tasks/' + str(task_id))
        if r.status_code != 200:
            task_id = None
        else:
            log.warning("\nWARNING %d: Seems this is rerun of this script, will monitor task with task_id = " % (
                        warningCount + 1) + str(task_id))
            log.warning("To submit new task delete " + test_job_lock_filename + "\n")
            warningCount += 1
        # check how old is it
    # submit test job
    if task_id == None:
        try:
            payload = {'resource': resource_name,
                       'app': app_name,
                       'resource_param': "{'nnodes':%d}" % nnodes,
                       'task_param': "{'test_run':True}"
                       }
            r = akrrrestclient.post('/scheduled_tasks', data=payload)
            if r.status_code != 200:
                log.error("Can not submit task through AKRR REST API ( """ + akrrrestclient.restapi_host + " )\n" +
                          "See server response below", json.dumps(r.json(), indent=4))
                exit(1)
            task_id = r.json()['data']['data']['task_id']
        except Exception as e:
            log.error("Can not submit task through AKRR REST API ( """ + akrrrestclient.restapi_host + " )\n" +
                      "Is it still running?\n" +
                      "See full error report below", traceback.format_exc())
            exit(1)
        # write file with tast_id
        fout = open(os.path.join(test_job_lock_filename), "w")
        print(task_id, file=fout)
        fout.close()
        log.info("\nSubmitted test job to AKRR, task_id is " + str(task_id) + "\n")
    # now wait till job is done
    msg_body0 = ""
    msg_body = ""

    # response_json0={}
    # response_json=r.json()
    while True:
        t = datetime.datetime.now()
        # try:
        r = akrrrestclient.get('/tasks/' + str(task_id))

        response_json = r.json()
        if r.status_code == 200:
            response_json = r.json()

            msg_body = "=" * 80
            msg_body += "\nTast status:\n"

            if response_json["data"]["queue"] == "scheduled_tasks":
                msg_body += "Task is in scheduled_tasks queue.\n"
                msg_body += "It schedule to be started on" + response_json["data"]["data"]['time_to_start'] + "\n"
            elif response_json["data"]["queue"] == "active_tasks":
                msg_body += "Task is in active_tasks queue.\n"
                msg_body += "Status: " + str(response_json["data"]["data"]['status']) + "\n"
                msg_body += "Status info:\n" + str(response_json["data"]["data"]['statusinfo']) + "\n"
            elif response_json["data"]["queue"] == "completed_tasks":
                msg_body += "Task is completed!\n"
                completed_tasks = r.json()['data']['data']['completed_tasks']
                akrr_xdmod_instanceinfo = r.json()['data']['data']['akrr_xdmod_instanceinfo']
                akrr_errmsg = r.json()['data']['data']['akrr_errmsg']
                if verbose:
                    msg_body += "completed_tasks table entry:\n" + pp.pformat(completed_tasks) + "\n"
                    msg_body += "akrr_xdmod_instanceinfo table entry:\n" + pp.pformat(akrr_xdmod_instanceinfo) + "\n"
                    msg_body += 'output parsing results:\n' + akrr_xdmod_instanceinfo['body'] + "\n"
                else:
                    msg_body += "\tstatus: " + str(akrr_xdmod_instanceinfo['status']) + "\n"
                    if akrr_xdmod_instanceinfo['status'] == 0:
                        msg_body += "\tstatus2: " + completed_tasks['status'] + "\n"
                    msg_body += "\tstatusinfo: " + completed_tasks['statusinfo'] + "\n"
            else:
                msg_body += r.text + "\n"

            tail_msg = "time: " + t.strftime("%Y-%m-%d %H:%M:%S")

            if msg_body != msg_body0:
                print("\n\n" + msg_body)
                print(tail_msg, end=' ')
                sys.stdout.flush()
            else:
                print("\r" + tail_msg, end=' ')
                sys.stdout.flush()

            msg_body0 = copy.deepcopy(msg_body)

            if response_json["data"]["queue"] == "completed_tasks":
                break
        # try to update:
        try:
            payload = {'next_check_time': ''}
            r = akrrrestclient.put('/active_tasks/' + str(task_id), data=payload)
        except:
            pass
        time.sleep(5)
    ###############################################################################################
    # analysing the output
    log.info("Test job is completed analyzing output\n")
    r = akrrrestclient.get('/tasks/' + str(task_id))
    if r.status_code != 200:
        log.error("Can not get information about task\n" +
                  "See full error report below",
                  "AKRR server response:\n" + r.text)
        exit(1)
    completed_tasks = r.json()['data']['data']['completed_tasks']
    akrr_xdmod_instanceinfo = r.json()['data']['data']['akrr_xdmod_instanceinfo']
    akrr_errmsg = r.json()['data']['data']['akrr_errmsg']

    results_summary = make_results_summary(
        resource_name, app_name, completed_tasks, akrr_xdmod_instanceinfo, akrr_errmsg)
    # execution was not successful
    if completed_tasks['status'].count("ERROR") > 0:
        if completed_tasks['status'].count("ERROR Can not created batch job script and submit it to remote queue") > 0:
            log.error("Can not created batch job script and/or submit it to remote queue\n" +
                      "See full error report below",
                      results_summary)
            os.remove(test_job_lock_filename)
            exit(1)
        else:
            log.error(completed_tasks['status'] + "\n" +
                      "See full error report below",
                      results_summary)
            os.remove(test_job_lock_filename)
            exit(1)

    # execution was not successful
    if akrr_xdmod_instanceinfo['status'] == 0:
        log.error("Task execution was not successful\n" +
                  "See full error report below:\n" +
                  results_summary)
        os.remove(test_job_lock_filename)
        exit(1)
    # see what is in report
    elm_perf = ET.fromstring(akrr_xdmod_instanceinfo['body'])
    elm_parameters = elm_perf.find('benchmark').find('parameters')
    elm_statistics = elm_perf.find('benchmark').find('statistics')

    log.info("\nTest kernel execution summary:")
    print(results_summary)
    print()
    # log.info("\nThe output looks good.\n")
    if (errorCount == 0):
        # enabling resource for execution
        log.info("\nEnabling %s on %s for execution\n" % (app_name, resource_name))
        try:
            result = akrrrestclient.put(
                '/resources/%s/on' % (resource_name,),
                data={'application': app_name})
            if result.status_code == 200:
                log.info("Successfully enabled %s on %s" % (app_name, resource_name))
            else:
                if result != None:
                    log.error("Can not turn-on %s on %s" % (app_name, resource_name), result.text)
                else:
                    log.error("Can not turn-on %s on %s" % (app_name, resource_name))
                exit(1)
            if True:
                # add entry to mod_appkernel.resource
                dbAK, curAK = akrr.db.get_ak_db(True)

                curAK.execute('''SELECT * FROM app_kernel_def WHERE ak_base_name=%s''', (app_name,))
                ak_in_AKDB = curAK.fetchall()
                if len(ak_in_AKDB) == 0:
                    curAK.execute('''INSERT INTO app_kernel_def (name,ak_base_name,processor_unit,enabled, description, visible)
                                VALUES(%s,%s,'node',0,%s,0);''',
                                  (app_name, app_name, app_name))
                    dbAK.commit()
                curAK.execute('''UPDATE app_kernel_def SET enabled=1,visible=1  WHERE ak_base_name=%s''', (app_name,))
                dbAK.commit()
                # add entry to mod_akrr.resource
                db, cur = akrr.db.get_akrr_db(True)

                cur.execute('''SELECT * FROM app_kernels WHERE name=%s''', (app_name,))
                ak_in_DB = cur.fetchall()
                if len(ak_in_DB) == 0:
                    cur.execute('''INSERT INTO app_kernels (id,name,enabled,nodes_list)
                                VALUES(%s,%s,0,'1,2,4,8');''',
                                (ak_in_AKDB['ak_def_id'], app_name))
                    db.commit()
                cur.execute('''UPDATE app_kernels SET enabled=1  WHERE name=%s''', (app_name,))
                db.commit()
        except:
            log.exception("Can not turn-on %s on %s", app_name, resource_name)
            exit(1)

    if (errorCount > 0):
        log.error("There are %d errors, fix them.", errorCount)
    if (warningCount > 0):
        log.warning(
            "\nThere are %d warnings.\nif warnings have sense (highlighted in yellow), you can move to next step!\n" %
            warningCount)
    if errorCount == 0 and warningCount == 0:
        log.info("\nDONE, you can move to next step!\n")
    os.remove(test_job_lock_filename)
