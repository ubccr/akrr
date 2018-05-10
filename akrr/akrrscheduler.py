from . import cfg
from . import akrrtask

import time
import os

import sys
import datetime
import re
import multiprocessing
import signal
import traceback
import copy
import subprocess
import socket

from .appkernelsparsers.akrrappkeroutputparser import AppKerOutputParser

from .akrrerror import AkrrError

# from .util import logging as log

import logging as log

akrrscheduler = None

import argparse


class akrrScheduler:
    def __init__(self, AddingNewTasks=False):
        # rest api process
        self.restapi_proc = None
        # load Scheduled Tasks DB
        self.dbCon, self.dbCur = cfg.getDB()

        # Sanitizing
        if not AddingNewTasks:
            self.dbCur.execute('''UPDATE ACTIVETASKS
                    SET task_lock=0
                    WHERE task_lock>0 ;''')
            self.dbCon.commit()
        #
        self.maxTaskHandlers = cfg.max_task_handlers
        self.max_wall_time_for_task_handlers = cfg.max_wall_time_for_task_handlers
        self.Workers = []
        self.Results = {}
        self.ResultsQueue = multiprocessing.Queue()
        self.repeat_after_forcible_termination = cfg.repeat_after_forcible_termination
        #    self.FatalErrorsForTask={}
        self.max_fatal_errors_for_task = cfg.max_fatal_errors_for_task

    def __del__(self):
        if self.dbCon != None:
            self.dbCon.commit()
            if self.dbCur != None:
                self.dbCur.close()
            self.dbCon.close()
        if self.restapi_proc != None:
            self.restapi_proc.terminate()
        # if self.dbCon!=None:
        #    self.dbCon.commit()
        #    if self.dbCur!=None:
        #        self.dbCur.close()
        #    self.dbCon.close()

    def AddFatalErrorsForTaskCount(self, task_id, count=1):
        self.dbCur.execute('''SELECT FatalErrorsCount FROM ACTIVETASKS
            WHERE task_id=%s ;''', (task_id,))
        FatalErrorsCount = self.dbCur.fetchall()[0][0]
        FatalErrorsCount += count
        self.dbCur.execute('''UPDATE ACTIVETASKS
            SET FatalErrorsCount=%s
            WHERE task_id=%s ;''', (FatalErrorsCount, task_id))
        self.dbCon.commit()

    #    if self.FatalErrorsForTask.has_key(task_id):
    #        self.FatalErrorsForTask[task_id]+=count
    #    else:
    #        self.FatalErrorsForTask[task_id]=count
    def runScheduledTasks(self):
        timenow = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        # Get all tasks which should be started
        #         self.dbCur.execute('''SELECT task_id, time_to_start, repeat_in, resource, app, resource_param, app_param, task_param, group_id, parent_task_id,
        #                 r.enabled as resource_enabled, a.enabled as app_kernel_enabled, ra.enabled as resource_app_kernel_enabled
        #             FROM mod_akrr.SCHEDULEDTASKS AS s
        #             INNER JOIN resources AS r
        #             ON s.resource = r.name
        #             INNER JOIN app_kernels AS a
        #             ON s.app = a.name
        #             INNER JOIN resource_app_kernels AS ra
        #             ON ra.resource_id = r.id AND ra.app_kernel_id=a.id
        #             WHERE s.time_to_start<=%s
        #               AND r.enabled=1 AND a.enabled=1 AND ra.enabled=1
        #             ORDER BY s.time_to_start ASC''',(timenow,))
        # get list of resource from db
        self.dbCur.execute('''SELECT id, name, enabled FROM resources''')
        raw = self.dbCur.fetchall()
        resource_enabled = {}
        for r in raw:
            resource_enabled[r[1]] = r[2]

        self.dbCur.execute('''SELECT id, name, enabled FROM app_kernels''')
        raw = self.dbCur.fetchall()
        appkernel_enabled = {}
        for r in raw:
            appkernel_enabled[r[1]] = r[2]

        self.dbCur.execute('''SELECT task_id, time_to_start, repeat_in, resource, app, resource_param, app_param, task_param, group_id, parent_task_id
            FROM mod_akrr.SCHEDULEDTASKS AS s
            WHERE s.time_to_start<=%s
            ORDER BY s.time_to_start ASC''', (timenow,))
        tasksToActivate = self.dbCur.fetchall()
        for row in tasksToActivate:
            (task_id, time_to_start, repeat_in, resource, app, resource_param, app_param, task_param, group_id,
             parent_task_id) = row

            taskParam = eval(task_param)
            if taskParam.get('test_run', False) == False:
                if resource_enabled.get(resource, 0) == 0 or appkernel_enabled.get(app, 0) == 0:
                    continue

            print("\n>>> " + timenow + " " + ">" * 96)

            TaskActivated = False
            TaskHandler = None
            StartTaskExecution = True
            # Commit all what was pushed before but not commited
            # so we can rollback if something will go wrong
            self.dbCon.commit()
            self.dbCon.commit()
            try:
                log.info(
                    "Activating Task\n" +
                    "Task Number: %s\n\t" % task_id +
                    "Start time: %s\n\t" % time_to_start +
                    "Repeating period: %s\n\t" % repeat_in +
                    "Resource: %s\n\t" % resource +
                    "Resource parameters: %s\n\t" % resource_param +
                    "Application kernel: %s\n\t" % app +
                    "Application kernel parameters: %s\n\t" % app_param +
                    "Task parameters: %s\n\t" % task_param +
                    "Parent task id: %s" % parent_task_id)

                if cfg.FindResourceByName(resource).get('active', True) == False:
                    raise AkrrError("%s is marked as inactive in AKRR" % (self.resourceName))

                # Check If resource is on maintenance
                self.dbCur.execute('''SELECT * FROM akrr_resource_maintenance
                    WHERE (resource="*" OR resource=%s OR resource LIKE %s OR resource LIKE %s OR resource LIKE %s)
                    AND start<=%s AND %s<=end;''', (resource, resource, resource, resource, timenow, timenow))
                raws = self.dbCur.fetchall()
                if len(raws) > 0:
                    StartTaskExecution = False
                    log.warning("Resource (%s) is under maintenance:" % resource)
                    for raw in raws:
                        log.warning(raw)
                    if repeat_in != None:
                        log.warning("This app. kernel is scheduled for repeat run, thus will skip this run")
                    else:
                        log.warning("Will postpone the execution by one day")
                        self.dbCur.execute('''UPDATE SCHEDULEDTASKS
                            SET time_to_start=%s
                            WHERE task_id=%s ;''', (time_to_start + datetime.timedelta(days=1), task_id))

                # self.dbCon.commit()

                # if a bundle task send subtask to  SCHEDULEDTASKS
                if app.count("bundle") > 0:
                    taskParam = eval(task_param)
                    if 'AppKers' in taskParam:
                        for subtask_app in taskParam['AppKers']:
                            subtask_task_param = "{'masterTaskID':%d}" % (task_id,)
                            self.addTask(time_to_start, None, resource, subtask_app, resource_param, app_param,
                                         subtask_task_param, group_id, parent_task_id)

                if StartTaskExecution:
                    TaskHandler = akrrtask.akrrGetNewTaskHandler(task_id, resource, app, resource_param, app_param,
                                                                 task_param)
                    akrrtask.akrrDumpTaskHandler(TaskHandler)
                    next_check_time = (datetime.datetime.today() + datetime.timedelta(minutes=1)).strftime(
                        "%Y-%m-%d %H:%M:%S")
                    # First we'll copy it to ActiveTasks
                    self.dbCur.execute('''INSERT INTO ACTIVETASKS (task_id,next_check_time,datetimestamp,time_activated,time_to_start,repeat_in,resource,app,resource_param,app_param,task_lock,task_param,group_id,parent_task_id)
                        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,0,%s,%s,%s);''',
                                       (task_id, next_check_time, TaskHandler.timeStamp,
                                        datetime.datetime.strptime(TaskHandler.timeStamp,
                                                                   "%Y.%m.%d.%H.%M.%S.%f").strftime(
                                            "%Y-%m-%d %H:%M:%S"),
                                        time_to_start, repeat_in, resource, app, resource_param, app_param, task_param,
                                        group_id, parent_task_id))
                    # Sanity check on repeat
                    if repeat_in != None:
                        match = re.match(r'(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)', repeat_in, 0)
                        if not match:
                            log.error("Unknown repeat_in format, will set it to None")
                            repeat_in = None
                        else:
                            g = match.group(1, 2, 3, 4, 5, 6)
                            tao = (int(g[0]), int(g[1]), int(g[2]), int(g[3]), int(g[4]), int(g[5]))
                            if tao[0] == 0 and tao[1] == 0 and tao[2] == 0 and tao[3] == 0 and tao[4] == 0 and tao[
                                5] == 0:
                                log.error("repeat_in is zero will set it to None")
                                repeat_in = None

                    # Schedule next
                    if repeat_in != None:
                        match = re.match(r'(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)', repeat_in, 0)
                        g = match.group(1, 2, 3, 4, 5, 6)
                        tao = (int(g[0]), int(g[1]), int(g[2]), int(g[3]), int(g[4]), int(g[5]))
                        match = re.match(r'(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)',
                                         time_to_start.strftime("%Y-%m-%d %H:%M:%S"), 0)
                        g = match.group(1, 2, 3, 4, 5, 6)
                        t0 = (int(g[0]), int(g[1]), int(g[2]), int(g[3]), int(g[4]), int(g[5]))

                        at0 = datetime.datetime(*t0)
                        adt = datetime.timedelta(tao[2], tao[5], 0, 0, tao[4], tao[3])
                        current_time = datetime.datetime.now()

                        at1 = at0 + adt
                        # schedule task only for the future
                        while at1 < current_time:
                            at1 += adt

                        if tao[0] != 0 or tao[1] != 0:
                            y = at1.year + tao[0]
                            m = at1.month + tao[1]
                            if m > 12:
                                y += 1
                                m -= 12
                            at1 = at1.replace(year=y, month=m)
                        nexttime = at1.strftime("%Y-%m-%d %H:%M:%S")
                        log.info("Schedule another task for %s" % nexttime)
                        self.addTask(nexttime, repeat_in, resource, app, resource_param, app_param, task_param,
                                     group_id, parent_task_id)
                        # self.dbCon.commit()
                if self.bRunScheduledTasks == False:
                    # means that the termination signal was send while this function is already running
                    raise IOError("Can not activate task because got a massage to postpone activation")
                TaskActivated = True
            except Exception:
                log.exception("Can not submit job to active tasks, for some reason.")
                self.dbCon.rollback()
                self.dbCon.rollback()
                if TaskHandler != None:
                    TaskHandler.DeleteLocalFolder()
            del TaskHandler
            if TaskActivated == True:
                # Now commit the changes
                self.dbCon.commit()
                if repeat_in != None:
                    self.dbCon.commit()
                # Now we need to delete it from ScheduledTasks
                self.dbCur.execute('''DELETE FROM SCHEDULEDTASKS
                    WHERE task_id=%s;''', (task_id,))
                self.dbCon.commit()

            print("<" * 120)

    def runActiveTasks_StartTheStep(self):
        """For task with expired next_check_time and currently not handled
        start a proccess to handle it"""

        def StartTheStep(resourceName, appName, timeStamp, ResultsQueue, FatalErrorsCount=0, FailsToSubmitToTheQueue=0):
            try:
                # Redirect logging
                taskDir = akrrtask.GetLocalTaskDir(resourceName, appName, timeStamp)
                if cfg.redirect_task_processing_to_log_file:
                    akrrtask.RedirectStdoutToLog(os.path.join(taskDir, 'proc', 'log'))

                # Do the task
                th = akrrtask.akrrGetTaskHandler(resourceName, appName, timeStamp)

                th.FatalErrorsCount = FatalErrorsCount
                th.FailsToSubmitToTheQueue = FailsToSubmitToTheQueue

                repeatein = th.ToDoNext()

                if th.IsStateChanged():
                    akrrtask.akrrDumpTaskHandler(th)
                # else:
                #    if hasattr(th, "FailsToSubmitToTheQueue"):
                #        th.LastPickledState-=1
                #        akrrtask.akrrDumpTaskHandler(th)

                pid = os.getpid()
                ResultsQueue.put({
                    'pid': pid,
                    "status": th.status,
                    "statusinfo": th.statusinfo,
                    "repeatein": repeatein,
                    "FatalErrorsCount": th.FatalErrorsCount,
                    "FailsToSubmitToTheQueue": th.FailsToSubmitToTheQueue,
                })

                # Redirect logging back
                if cfg.redirect_task_processing_to_log_file:
                    akrrtask.RedirectStdoutBack()

                return 0
            except Exception:
                log.exception("Exception was thrown during StartTheStep")
                if akrrtask.log_file != None:
                    akrrtask.RedirectStdoutBack()
                return 1

        timenow = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        # Get all tasks which should be started
        self.dbCur.execute('''SELECT task_id,resource,app,datetimestamp,FatalErrorsCount,FailsToSubmitToTheQueue FROM ACTIVETASKS
            WHERE next_check_time<=%s AND task_lock=0
            ORDER BY next_check_time ASC ;''', (timenow,))
        tasksToCheck = self.dbCur.fetchall()

        iTasksSend = 0
        for row in tasksToCheck:
            if self.maxTaskHandlers == 0:
                # Executing task by main thread
                (task_id, resourceName, appName, timeStamp, FatalErrorsCount, FailsToSubmitToTheQueue) = row
                log.info("Working on:\n\t%s" % (akrrtask.GetLocalTaskDir(resourceName, appName, timeStamp)))

                class fakeProcess:
                    def __init__(self):
                        self.exitcode = 0

                    def join(self, t):
                        return

                    def is_alive(self):
                        return False

                self.Workers.append({
                    "task_id": task_id,
                    "pid": os.getpid(),
                    "timestarted": datetime.datetime.today(),
                    "process": fakeProcess(),
                })

                StartTheStep(resourceName, appName, timeStamp, self.ResultsQueue, 0, FailsToSubmitToTheQueue)
                self.dbCon.commit()

            if len(self.Workers) >= self.maxTaskHandlers:
                # all workers are busy skipping the
                return

            (task_id, resourceName, appName, timeStamp, FatalErrorsCount, FailsToSubmitToTheQueue) = row
            log.info("Working on:\n\t%s" % (akrrtask.GetLocalTaskDir(resourceName, appName, timeStamp)))
            try:
                p = multiprocessing.Process(target=StartTheStep, args=(
                resourceName, appName, timeStamp, self.ResultsQueue, 0, FailsToSubmitToTheQueue))
                p.start()
                pid = p.pid
                self.dbCur.execute('''UPDATE ACTIVETASKS
                    SET task_lock=%s
                    WHERE task_id=%s ;''', (pid, task_id))

                self.Workers.append({
                    "task_id": task_id,
                    "pid": pid,
                    "timestarted": datetime.datetime.today(),
                    "process": p,
                })

                iTasksSend += 1
            except Exception:
                log.exception("Exception occurred during process start for next step execution")
                self.AddFatalErrorsForTaskCount(task_id)
                # raise

        if iTasksSend > 0:
            self.dbCon.commit()
            # print StartTheStep(resourceName,appName,timeStamp)
            # print "Back"

            # print "\n>>> "+timenow+" "+">"*96
            # print "<"*120

    def runActiveTasks_CheckTheStep(self):
        """
        """
        timenow = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        # Get all tasks which should be started

        iP = 0
        Ninit = len(self.Workers)
        N = len(self.Workers)
        if N == 0:
            return

        while iP < N:
            p = self.Workers[iP]['process']
            task_id = self.Workers[iP]['task_id']
            pid = self.Workers[iP]['pid']

            self.dbCur.execute('''SELECT FatalErrorsCount,FailsToSubmitToTheQueue FROM ACTIVETASKS
                WHERE task_id=%s;''', (task_id,))
            (FatalErrorsCount, FailsToSubmitToTheQueue) = self.dbCur.fetchall()[0]

            while not self.ResultsQueue.empty():
                r = self.ResultsQueue.get()
                self.Results[r['pid']] = r

            p.join(0.5)

            if p.is_alive():
                dt = datetime.datetime.today() - self.Workers[iP]['timestarted']
                if dt > self.max_wall_time_for_task_handlers:
                    p.terminate()  # will handle it next round
                iP += 1
                continue

            status = "None"
            statusinfo = "None"
            repeatein = None
            if p.exitcode == -signal.SIGTERM:  # process the case when process was terminated
                dt = datetime.datetime.today() - self.Workers[iP]['timestarted']
                if dt > self.max_wall_time_for_task_handlers:  # 1) exceed the max time (the process, not the real task on remote machine)
                    status = "Task handler process was terminated."
                    statusinfo = "The task handler process was terminated probably due to overtime."
                    repeatein = self.repeat_after_forcible_termination
                    FatalErrorsCount += 1
                else:  # 2) the process was killed by system or by user
                    status = "Task handler process was terminated."
                    statusinfo = "The task handler process was terminated externally."
                    repeatein = self.repeat_after_forcible_termination
                    FatalErrorsCount += 1
            else:  # process normal exit of process
                # Process the results
                while not self.ResultsQueue.empty():  # organized results in dict with pid keys
                    r = self.ResultsQueue.get()
                    self.Results[r['pid']] = r
                if pid not in self.Results:  # process finished abnormally
                    log.error(
                        "the process was finished but results was not sent."
                        "\n\tat this point treat it as forcibly terminated"
                    )
                    status = "Task handler process was terminated."
                    statusinfo = "the process was finished but results was not sent. At this point treat it as forcibly terminated"
                    repeatein = self.repeat_after_forcible_termination
                    FatalErrorsCount += 1
                else:
                    r = self.Results[pid]
                    status = copy.deepcopy(r['status'])
                    statusinfo = copy.deepcopy(r['statusinfo'])
                    repeatein = copy.deepcopy(r['repeatein'])
                    FatalErrorsCount += r['FatalErrorsCount']
                    FailsToSubmitToTheQueue = r['FailsToSubmitToTheQueue']
                    del self.Results[pid]

            timenow = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
            if FatalErrorsCount > self.max_fatal_errors_for_task:  # if too much errors terminate the execution
                repeatein = None
                status = status + " Number of errors exceeded allowed maximum and task was terminated."
                self.dbCon.commit()
                self.dbCon.commit()
                self.dbCur.execute('''SELECT resource,app,datetimestamp
                    FROM ACTIVETASKS
                    WHERE task_id=%s;''', (task_id,))
                (resource, app, datetimestamp) = self.dbCur.fetchone()
                th = akrrtask.akrrGetTaskHandler(resource, app, datetimestamp)
                th.status = "Error: Number of errors exceeded allowed maximum and task was terminated." + th.status
                th.ReportFormat = "Error"
                th.ProccessResults()
                if th.PushToDB() != None:
                    log.error("Can not push to DB")
                akrrtask.akrrDumpTaskHandler(th)
                status = copy.deepcopy(th.status)
                statusinfo = copy.deepcopy(th.statusinfo)
                del th

            # Read log

            # Update error counters on DB
            self.dbCur.execute('''UPDATE ACTIVETASKS
                SET FatalErrorsCount=%s,FailsToSubmitToTheQueue=%s
                WHERE task_id=%s ;''', (FatalErrorsCount, FailsToSubmitToTheQueue, task_id))
            self.dbCon.commit()
            # update DB
            if status == "Done" or repeatein == None:
                # we need to remove it from ACTIVETASKS and add to COMPLETEDTASKS
                resource = None
                app = None
                datetimestamp = None
                try:
                    self.dbCon.commit()
                    self.dbCon.commit()
                    self.dbCur.execute('''SELECT statusupdatetime,status,statusinfo,time_to_start,repeat_in,resource,app,datetimestamp,time_activated,
                            time_submitted_to_queue,resource_param,app_param,task_param,group_id,FatalErrorsCount,FailsToSubmitToTheQueue,
                            parent_task_id 
                        FROM ACTIVETASKS
                        WHERE task_id=%s;''', (task_id,))
                    (statusupdatetime, status_prev, statusinfo_prev, time_to_start, repeat_in, resource, app,
                     datetimestamp, time_activated, time_submitted_to_queue, resource_param, app_param, task_param,
                     group_id, FatalErrorsCount, FailsToSubmitToTheQueue, parent_task_id) = self.dbCur.fetchone()

                    self.dbCur.execute('''INSERT INTO COMPLETEDTASKS
                    (task_id,time_finished,status,statusinfo,time_to_start,repeat_in,resource,app,datetimestamp,time_activated,time_submitted_to_queue,resource_param,app_param,task_param,group_id,FatalErrorsCount,FailsToSubmitToTheQueue,parent_task_id)
                    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);''',
                                       (task_id, statusupdatetime, status, statusinfo, time_to_start, repeat_in,
                                        resource, app, datetimestamp, time_activated, time_submitted_to_queue,
                                        resource_param, app_param, task_param, group_id, FatalErrorsCount,
                                        FailsToSubmitToTheQueue, parent_task_id))
                    self.dbCur.execute('''DELETE FROM ACTIVETASKS
                        WHERE task_id=%s;''', (task_id,))
                except Exception:
                    log.exception(
                        "Exception occurred during moving task record from ACTIVETASKS to COMPLETEDTASKS table")
                    self.dbCon.rollback()
                    self.dbCon.rollback()

                    FatalErrorsCount += 1
                    self.dbCur.execute('''UPDATE ACTIVETASKS
                        SET task_lock=0,FatalErrorsCount=%s
                        WHERE task_id=%s ;''', (FatalErrorsCount, task_id))

                self.dbCon.commit()
                self.dbCon.commit()

                # now the last thing moving the directory
                taskdir = os.path.join(cfg.data_dir, resource, app, datetimestamp)
                comptasksdir = os.path.join(cfg.completed_tasks_dir, resource, app)
                log.info(
                    "Task is completed. Moving its' working directory\n" +
                    "\tfrom %s" % (taskdir) + "\n"
                                              "\tto %s" % (os.path.join(comptasksdir, datetimestamp))
                )
                import shutil
                shutil.move(taskdir, comptasksdir)
                # clean error list
                # if self.FatalErrorsForTask.has_key(task_id):
                #    del self.FatalErrorsForTask[task_id]

            else:
                # we need to resubmit and update
                nextround = datetime.datetime.today() + repeatein
                nextround = nextround.strftime("%Y-%m-%d %H:%M:%S")
                self.dbCur.execute('''UPDATE ACTIVETASKS
                    SET task_lock=0, status=%s,statusinfo=%s,next_check_time=%s,statusupdatetime=%s
                    WHERE task_id=%s ;''', (status, statusinfo, nextround, timenow, task_id))
                self.dbCon.commit()
            # remove worker from list

            self.Workers.pop(iP)
            N = len(self.Workers)
        if Ninit != len(self.Workers):
            self.dbCon.commit()

    def run(self):
        self.bRunScheduledTasks = True
        self.bRunActiveTasks_StartTheStep = True
        self.bRunActiveTasks_CheckTheStep = True
        self.LastOpSignal = "Run"

        if os.path.isfile(os.path.join(cfg.data_dir, "akrr.pid")):
            raise IOError("""File %s exists meaning that another AKRR Scheduler
            process is already working with this directory.
            or the previous one had exited incorrectly.""" % (os.path.join(cfg.data_dir, "akrr.pid")))

        log.info("AKRR Scheduler PID is %s." % os.getpid())

        with open(os.path.join(cfg.data_dir, "akrr.pid"), "wt") as fout:
            fout.write("%s\n" % os.getpid())
        fout.close()

        # set signal handling
        def SEGTERMHandler(signum, stack):
            log.info("Received termination signal. Actual signal is %s." % signum)
            log.info("Going to clean up ...")
            self.bRunScheduledTasks = False
            self.bRunActiveTasks_StartTheStep = False
            self.bRunActiveTasks_CheckTheStep = True
            self.LastOpSignal = "SEGTERM"

        def NoNewTasks(signum, stack):
            log.info("Activation of new tasks is postponed.")
            self.bRunScheduledTasks = False
            self.bRunActiveTasks_StartTheStep = False
            self.bRunActiveTasks_CheckTheStep = True
            self.LastOpSignal = "Run"

        def NewTasksOn(signum, stack):
            log.info("Activation of new tasks is allowed.")
            self.bRunScheduledTasks = True
            self.bRunActiveTasks_StartTheStep = True
            self.bRunActiveTasks_CheckTheStep = True
            self.LastOpSignal = "Run"

        signal.signal(signal.SIGTERM, SEGTERMHandler)
        signal.signal(signal.SIGINT, SEGTERMHandler)
        signal.signal(signal.SIGUSR1, NoNewTasks)
        signal.signal(signal.SIGUSR2, NewTasksOn)

        # start rest api
        from . import akrrrestapi
        log.info("Starting REST-API Service")
        self.proc_queue_to_master = multiprocessing.Queue(1)
        self.proc_queue_from_master = multiprocessing.Queue(1)
        self.restapi_proc = multiprocessing.Process(target=akrrrestapi.start_rest_api,
                                                    args=(self.proc_queue_to_master, self.proc_queue_from_master))
        self.restapi_proc.start()

        # go to the loop
        self.runLoop()

        # reset signal
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        if os.path.isfile(os.path.join(cfg.data_dir, "akrr.pid")):
            os.remove(os.path.join(cfg.data_dir, "akrr.pid"))

    def runUpdateExternalDB(self):
        # @todo is it happence in task now?
        return None
        try:
            self.dbCur.execute('''SELECT task_id,statusupdatetime,status,statusinfo,time_to_start,repeat_in,resource,app,datetimestamp,resource_param,app_param,task_param,group_id 
                        FROM ACTIVETASKS;''')

            db, cur = cfg.getExportDB()
            change = False

            for row in self.dbCur.fetchall():
                (task_id, statusupdatetime, status_prev, statusinfo_prev, time_to_start, repeat_in, resource, app,
                 datetimestamp, resource_param, app_param, task_param, group_id) = row

            if change:
                db.commit()
            cur.close()
            del db

        except Exception:
            log.exception("Exception occurred during runUpdateExternalDB")

    def checkDBandReconnect(self):
        """check the db connection and reconnect"""
        attemptsToReconnect = 0
        while True:
            dbConnected = False
            try:
                self.dbCur.execute('''SELECT * FROM  `resources`  ''')
                self.dbCur.fetchall()
                dbConnected = True
            except Exception as e:
                log.exception("Exception occurred during DB connection checking.")

            if dbConnected:
                return True

            if attemptsToReconnect > 3 * 360:
                log.error("Have tried %d to reconnect to DB and failed" % attemptsToReconnect)
                raise e

            if attemptsToReconnect > 0:
                log.warning(
                    "Have tried %d to reconnect to DB and failed. Will wait for 10 sec and tried again\n" % attemptsToReconnect)
                time.sleep(10)

            log.info("Trying to reconnect to DB.")
            self.dbCon, self.dbCur = cfg.getDB()
            attemptsToReconnect += 1

    def runLoop(self):
        log.info("#" * 100)
        log.info("Got into the running loop on " + datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"))
        log.info("#" * 100 + "\n")
        numBigFails = 0
        while True:
            try:
                self.checkDBandReconnect()

                if self.bRunScheduledTasks:
                    self.runScheduledTasks()
                if self.bRunActiveTasks_StartTheStep:
                    self.runActiveTasks_StartTheStep()
                if self.bRunActiveTasks_CheckTheStep:
                    self.runActiveTasks_CheckTheStep()

                self.runUpdateExternalDB()

                self.runREST_API_requests()

                if self.LastOpSignal == "SEGTERM":
                    log.info("Trying to shut down REST API...")
                    if self.restapi_proc.is_alive():
                        self.restapi_proc.terminate()
                    if self.restapi_proc.is_alive():
                        log.info("REST API PID %s", self.restapi_proc.pid)
                        os.kill(self.restapi_proc.pid, signal.SIGKILL)
                    if len(self.Workers) == 0 and self.restapi_proc.is_alive() == False:
                        log.info(
                            "There is no active proccesses handling the task"
                            "REST API is down"
                            "Safely exiting from the loop"
                        )
                        log.info("#" * 100)
                        log.info("# Got out of loop on " + datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"))
                        log.info("#" * 100 + "\n")
                        return
                    time.sleep(0.05)
                else:
                    time.sleep(cfg.scheduled_tasks_loop_sleep_time)
            except Exception:
                log.exception("Exception occurred in main loop!")
                numBigFails += 1;
                time.sleep(10)
                if numBigFails > 360:
                    log.error("Too many errors! Shutting down the daemon!")
                    if self.restapi_proc.is_alive():
                        self.restapi_proc.terminate()
                    if self.restapi_proc.is_alive():
                        log.debug("REST API PID", self.restapi_proc.pid)
                        os.kill(self.restapi_proc.pid, signal.SIGKILL)
                    for w in self.Workers:
                        if w['p'].is_alive():
                            w['p'].terminate()
                        if w['p'].is_alive():
                            os.kill(w['p'].pid, signal.SIGKILL)
                    exit(1)

    def runREST_API_requests(self):
        """execute REST API requests which can not be handled without interaptions"""
        if self.restapi_proc == None:
            return

        if self.proc_queue_to_master.empty():
            return

        request = self.proc_queue_to_master.get()

        log.info(request)
        log.info(list(globals().keys()))
        try:
            if request['fun'] in globals():
                globals()[request['fun']](*(request['args']), **(request['kargs']))
                response = {
                    "success": True,
                    "message": None
                }
            else:
                raise Exception("Unimplemented method")
        except Exception as e:
            response = {
                "success": False,
                "message": str(e)
            }
            log.exception()
        self.proc_queue_from_master.put(response)

    def monitor(self):
        while True:
            sys.stdout.write("\x1b[J\x1b[2J\x1b[H")
            sys.stdout.flush()

            pid = akrrGetPIDofServer()
            if pid == None:
                print("AKRR Server is down")
            else:
                print("AKRR Server is up and it's PID is %d" % (pid))

            print("Scheduled Tasks (%s) :" % (str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"))))
            self.dbCur.execute('''SELECT * FROM SCHEDULEDTASKS ORDER BY time_to_start ASC;''')
            tasks = self.dbCur.fetchall()
            for row in tasks:
                print(row)
            print("Active Tasks (%s) :" % (str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"))))
            # self.dbCur.execute('''SELECT * FROM ACTIVETASKS ORDER BY next_check_time,time_to_start ASC;''')

            self.dbCur.execute('''SELECT task_id,resource,app,datetimestamp,next_check_time,task_lock,status,statusinfo,statusupdatetime
                FROM ACTIVETASKS
                ORDER BY next_check_time,time_to_start ASC;''')
            tasks = self.dbCur.fetchall()
            for row in tasks:
                print(row)

            print("Completed Tasks (%s) :" % (str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"))))
            # self.dbCur.execute('''SELECT * FROM ACTIVETASKS ORDER BY next_check_time,time_to_start ASC;''')

            self.dbCur.execute('''SELECT task_id,resource,app,datetimestamp,resource_param,app_param,status,statusinfo,time_finished
                FROM COMPLETEDTASKS
                ORDER BY time_finished DESC;''')

            tasks = self.dbCur.fetchall()
            for row in tasks[:3]:
                print(row)
            time.sleep(1)

    def status(self):
        """like monitor only print once"""
        pid = akrrGetPIDofServer()
        if pid == None:
            print("AKRR Server is down")
        else:
            print("AKRR Server is up and it's PID is %d" % (pid))

        print("Scheduled Tasks (%s) :" % (str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"))))
        self.dbCur.execute('''SELECT * FROM SCHEDULEDTASKS ORDER BY time_to_start ASC;''')
        tasks = self.dbCur.fetchall()
        for row in tasks:
            print(row)
        print("Active Tasks (%s) :" % (str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"))))
        # self.dbCur.execute('''SELECT * FROM ACTIVETASKS ORDER BY next_check_time,time_to_start ASC;''')

        self.dbCur.execute('''SELECT task_id,resource,app,datetimestamp,next_check_time,task_lock,status,statusinfo,statusupdatetime
            FROM ACTIVETASKS
            ORDER BY task_id;''')  # next_check_time,time_to_start ASC;''')
        tasks = self.dbCur.fetchall()
        for row in tasks:
            (task_id, resource, app, datetimestamp, next_check_time, task_lock, status, statusinfo,
             statusupdatetime) = row
            print("-" * 120)
            print("%-10d %-14s %-40s %-25s %-20s %6d" % (
            task_id, resource, app, datetimestamp, next_check_time, task_lock))
            print("\t%s" % (datetimestamp), status)
            print(statusinfo)

        print("Completed Tasks (%s) :" % (str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"))))
        # self.dbCur.execute('''SELECT * FROM ACTIVETASKS ORDER BY next_check_time,time_to_start ASC;''')

        self.dbCur.execute('''SELECT task_id,resource,app,datetimestamp,resource_param,app_param,status,statusinfo,time_finished
            FROM COMPLETEDTASKS
            ORDER BY time_finished DESC;''')

        tasks = self.dbCur.fetchall()
        for row in tasks[:3]:
            print(row)

        # Tasks completed with errors
        self.dbCur.execute('''SELECT task_id,time_finished,status, statusinfo,time_to_start,datetimestamp,repeat_in,resource,app,resource_param,app_param,task_param,group_id
            FROM COMPLETEDTASKS
            ORDER BY time_finished  DESC LIMIT 5;''')
        tasks = self.dbCur.fetchall()
        if len(tasks) == 0:
            print("\nThere were no tasks completed with errors.")
        else:
            print("\nTasks completed with errors (last %d):" % (len(tasks)))
            for row in tasks:
                (task_id, time_finished, status, statusinfo, time_to_start, datetimestamp, repeat_in, resource, app,
                 resource_param, app_param, task_param, group_id) = row
                if re.match("ERROR:", status, re.M):
                    TaskDir = akrrtask.GetLocalTaskDir(resource, app, datetimestamp, False)
                    print("Done with errors: %s %5d %s\n" % (time_finished, task_id, TaskDir), resource_param,
                          app_param, task_param, group_id, "\n", status, "\n", statusinfo)

    def reprocessCompletedTasks(self, resource, appkernel, time_start, time_end, Verbose=False):
        """reprocess the output from Completed task one more time with hope that new task handlers have a better implementation of error handling"""

        print(
            """Reprocess the output from Completed task one more time with hope that new task handlers have a better implementation of error handling""")
        print("Current time: %s" % (str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"))))
        print("Resource:", resource)
        print("Application kernel:", appkernel)
        if time_start != None and time_end != None:
            print("Time frame: from ", time_start, "till", time_end)
        if time_start == None and time_end != None:
            print("Time frame: till", time_end)
        if time_start != None and time_end == None:
            print("Time frame: from ", time_start)

        sqlquote = "SELECT task_id,time_finished,status, statusinfo,time_to_start,datetimestamp,repeat_in,resource,app,resource_param,app_param,task_param,group_id\n"
        sqlquote += "FROM COMPLETEDTASKS\n"
        cond = []
        if resource != None:
            cond.append("resource LIKE \"" + resource + "\"\n")
        if appkernel != None:
            cond.append("app LIKE \"" + appkernel + "\"\n")
        if time_start != None:
            cond.append("time_finished >= \"" + time_start + "\"\n")
        if time_end != None:
            cond.append("time_finished <= \"" + time_end + "\"\n")
        if len(cond) > 0:
            sqlquote += "WHERE\n" + " AND ".join(cond)
        sqlquote += "ORDER BY task_id ASC;"

        self.dbCur.execute(sqlquote)

        tasks = self.dbCur.fetchall()

        db, cur = cfg.getExportDB()
        if Verbose: print("#" * 120)
        for row in tasks:
            (task_id, time_finished, status, statusinfo, time_to_start, datetimestamp, repeat_in, resource, app,
             resource_param, app_param, task_param, group_id) = row
            TaskDir = akrrtask.GetLocalTaskDir(resource, app, datetimestamp, False)
            if Verbose:
                print("task_id:  %-10d     started:      %s    finished: %s    group_id: %s" % (
                task_id, time_to_start, time_finished, group_id))
                print("resource: %-14s application: %-40s timestamp: %s" % (resource, app, datetimestamp))
                print("resource_param: %s    app_param: %s    task_param: %s    " % (
                resource_param, app_param, task_param))
                print("TaskDir:", TaskDir)
                print("-" * 120)
                print("status: %s" % (status))
                # print "statusinfo:"
                # print statusinfo
                print("=" * 120)

            # Get All States
            ths = []

            procTaskDir = os.path.join(TaskDir, 'proc')
            thsFNs = []
            for f in os.listdir(procTaskDir):
                if re.match("(\d+).st", f, 0) != None:
                    thsFNs.append(f)
            thsFNs = sorted(thsFNs)
            for thFN in thsFNs:
                picklefilename = os.path.join(procTaskDir, thFN)
                th = akrrtask.akrrGetTaskHandlerFromPkl(picklefilename)
                th.statefilename = thFN
                th.SetDirNames(cfg.completed_tasks_dir)

                ths.append(th)
            ths[-1].ProccessResults(Verbose)
            ths[-1].PushToDBRaw(cur, task_id, time_finished, Verbose)
            # akrrtask.akrrDumpTaskHandler(ths[-1])
            if re.match("ERROR:", ths[-1].status, re.M):
                print("Done with errors:", TaskDir, ths[-1].status)
            if ths[-1].status != status or ths[-1].statusinfo != statusinfo:
                print("status changed")
                print(status)
                print(ths[-1].status)
                self.dbCur.execute('''UPDATE COMPLETEDTASKS
                    SET status=%s,statusinfo=%s
                    WHERE task_id=%s ;''', (ths[-1].status, ths[-1].statusinfo, task_id))
                self.dbCon.commit()
            if Verbose and 0:
                print("States history:")
                print("-" * 120)
                for th in ths:
                    print(th.statefilename)
                    print(th.status)
                    print(th.statusinfo)
                    print("-" * 120)
            if Verbose:
                print("#" * 120)
        db.commit()
        cur.close()
        print("Reprocessing complete")
        # return

    def reprocess2(self, Verbose=True):
        """reprocess the output from Completed task one more time with hope that new task handlers have a better implementation of error handling"""

        print(
            """Reprocess the output from Completed task one more time with hope that new task handlers have a better implementation of error handling""")
        print("Time: %s" % (str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"))))

        self.dbCur.execute('''SELECT task_id,time_finished,status, statusinfo,time_to_start,datetimestamp,repeat_in,resource,app,resource_param,app_param,task_param,group_id
            FROM COMPLETEDTASKS
            where time_finished > "2013-11-31"
            ORDER BY task_id DESC;''')

        tasks = self.dbCur.fetchall()

        self.dbCur.execute("TRUNCATE TABLE  akrr_errmsg")

        if Verbose: print("#" * 120)
        for row in tasks:
            (task_id, time_finished, status, statusinfo, time_to_start, datetimestamp, repeat_in, resource, app,
             resource_param, app_param, task_param, group_id) = row
            TaskDir = None
            try:
                TaskDir = akrrtask.GetLocalTaskDir(resource, app, datetimestamp, False)
            except:
                pass

            if Verbose:
                print("task_id:  %-10d     started:      %s    finished: %s    group_id: %s" % (
                task_id, time_to_start, time_finished, group_id))
                print("resource: %-14s application: %-40s timestamp: %s" % (resource, app, datetimestamp))
                print("resource_param: %s    app_param: %s    task_param: %s    " % (
                resource_param, app_param, task_param))
                print("TaskDir:", TaskDir)
                print("-" * 120)
                print("status: %s" % (status))
                print("statusinfo:")
                print(statusinfo)
                print("=" * 120)

            appstdoutFileContent = None
            stdoutFileContent = None
            stderrFileContent = None

            if TaskDir != None:
                # Get All States
                ths = []

                import pickle
                procTaskDir = os.path.join(TaskDir, 'proc')
                thsFNs = []
                for f in os.listdir(procTaskDir):
                    if re.match("(\d+).st", f, 0) != None:
                        thsFNs.append(f)
                thsFNs = sorted(thsFNs)
                thFN = thsFNs[-1]

                picklefilename = os.path.join(procTaskDir, thFN)
                th = akrrtask.akrrGetTaskHandlerFromPkl(picklefilename)
                th.statefilename = thFN
                th.SetDirNames(cfg.completed_tasks_dir)

                resultFile = os.path.join(th.taskDir, "result.xml")
                jobfilesDir = os.path.join(th.taskDir, "jobfiles")
                (batchJobDir, stdoutFile, stderrFile, appstdoutFile, taskexeclogFile) = th.GetResultFiles()

                if appstdoutFile != None:
                    fin = open(appstdoutFile, "r")
                    appstdoutFileContent = fin.read()
                    fin.close()
                else:
                    appstdoutFileContent = "Does Not Present"
                if stdoutFile != None:
                    fin = open(stdoutFile, "r")
                    stdoutFileContent = fin.read()
                    fin.close()
                else:
                    stdoutFileContent = "Does Not Present"
                if stderrFile != None:
                    fin = open(stderrFile, "r")
                    stderrFileContent = fin.read()
                    fin.close()
                else:
                    stderrFileContent = "Does Not Present"
                if taskexeclogFile != None:
                    fin = open(taskexeclogFile, "r")
                    taskexeclogFileContent = fin.read()
                    fin.close()
                else:
                    taskexeclogFileContent = "Does Not Present"

                self.dbCur.execute("""SELECT * FROM akrr_errmsg WHERE task_id=%s""", (task_id,))
                raw = self.dbCur.fetchall()
                if 1:
                    if len(raw) == 0:
                        self.dbCur.execute("""INSERT INTO akrr_errmsg
    (task_id,appstdout,stderr,stdout,taskexeclog)
    VALUES (%s,%s,%s,%s,%s)""",
                                           (task_id, appstdoutFileContent, stderrFileContent, stdoutFileContent,
                                            taskexeclogFileContent))
                    else:
                        self.dbCur.execute("""UPDATE akrr_errmsg
    SET appstdout=%s,stderr=%s,stdout=%s,taskexeclog=%
    WHERE task_id=%s""",
                                           (appstdoutFileContent, stderrFileContent, stdoutFileContent,
                                            taskexeclogFileContent, task_id))
                self.dbCon.commit()

                #
                if 0:
                    jobfilesDir = os.path.join(th.taskDir, "jobfiles")
                    batchJobDir = None
                    stdoutFile = None
                    stderrFile = None
                    appstdoutFile = None
                    resultFile = os.path.join(th.taskDir, "result.xml")

                    if hasattr(th, 'ReportFormat'):  # i.e. fatal error and the last one is already in status/statusinfo
                        if th.ReportFormat == "Error":
                            print("Error")

                    for d in os.listdir(jobfilesDir):
                        if re.match("batchJob", d):
                            if batchJobDir == None:
                                batchJobDir = os.path.join(jobfilesDir, d)
                            else:
                                raise IOError("Error: found multiple batchJob* Directories although it should be one")
                    if batchJobDir != None:
                        for f in os.listdir(batchJobDir):
                            if re.match("sub.*\.stdout", f):
                                if stdoutFile == None:
                                    stdoutFile = os.path.join(batchJobDir, f)
                                else:
                                    raise IOError("Error: found multiple sub*.stdout files although it should be one")
                            if re.match("sub.*\.stderr", f):
                                if stderrFile == None:
                                    stderrFile = os.path.join(batchJobDir, f)
                                else:
                                    raise IOError("Error: found multiple sub*.stderr files although it should be one")
                            if re.match("sub.*\.appstdout", f):
                                if appstdoutFile == None:
                                    appstdoutFile = os.path.join(batchJobDir, f)
                                else:
                                    raise IOError(
                                        "Error: found multiple sub*.appstdout files although it should be one")
                    else:
                        batchJobDir = jobfilesDir
                        for f in os.listdir(jobfilesDir):
                            if re.match("stdout", f):
                                if stdoutFile == None:
                                    stdoutFile = os.path.join(jobfilesDir, f)
                                else:
                                    raise IOError("Error: found multiple sub*.stdout files although it should be one")
                            if re.match("stderr", f):
                                if stderrFile == None:
                                    stderrFile = os.path.join(jobfilesDir, f)
                                else:
                                    raise IOError("Error: found multiple sub*.stderr files although it should be one")
                            if re.match("appstdout", f):
                                if appstdoutFile == None:
                                    appstdoutFile = os.path.join(jobfilesDir, f)
                                else:
                                    raise IOError(
                                        "Error: found multiple sub*.appstdout files although it should be one")
                    completed = None
                    try:
                        import xml.etree.ElementTree as ET
                        tree = ET.parse(resultFile)
                        root = tree.getroot()

                        t = root.find('exitStatus').find('completed').text

                        if t.upper() == "TRUE":
                            completed = True
                        else:
                            completed = False

                        if completed:
                            root.find('body').find('performance').find('benchmark').find('statistics')
                        self.status = "Task was completed successfully."
                        self.statusinfo = "Done"
                    except:
                        completed = None

                    if 1:  # completed==None:
                        print(appstdoutFile, stdoutFile, stderrFile)
                        if appstdoutFile != None:
                            fin = open(appstdoutFile, "r")
                            appstdoutFileContent = fin.read()
                            fin.close()
                        else:
                            appstdoutFileContent = "Does Not Present"
                        if stdoutFile != None:
                            fin = open(stdoutFile, "r")
                            stdoutFileContent = fin.read()
                            fin.close()
                        else:
                            stdoutFileContent = "Does Not Present"
                        if stderrFile != None:
                            fin = open(stderrFile, "r")
                            stderrFileContent = fin.read()
                            fin.close()
                        else:
                            stderrFileContent = "Does Not Present"
                self.dbCur.execute("""SELECT * FROM akrr_errmsg WHERE task_id=%s""", (task_id,))
                raw = self.dbCur.fetchall()
                if 0:
                    if len(raw) == 0:
                        self.dbCur.execute("""INSERT INTO akrr_errmsg
    (task_id,appstdout,stderr,stdout)
    VALUES (%s,%s,%s,%s)""",
                                           (task_id, appstdoutFileContent, stderrFileContent, stdoutFileContent))
                    else:
                        self.dbCur.execute("""UPDATE akrr_errmsg
    SET appstdout=%s,stderr=%s,stdout=s
    WHERE task_id=%s""",
                                           (appstdoutFileContent, stderrFileContent, stdoutFileContent, task_id))
                self.dbCon.commit()
                # if batchJobDir==None or stdoutFile==None or stderrFile==None:
                #    raise IOError("Error: standard files is not present among job-files copied from remote resource.")

                # else:
                #    print
                # th.task_id=task_id
                # th.TimeJobPossiblyCompleted=datetime.datetime.strptime(time_finished,"%Y-%m-%d %H:%M:%S")

                if 0:
                    th.LastPickledState -= 1
                    akrrtask.akrrDumpTaskHandler(th)
            # return

    def reprocess_add_nodes(self, Verbose=True):
        """reprocess_add_nodes"""

        print(
            """Reprocess the output from Completed task one more time with hope that new task handlers have a better implementation of error handling""")
        print("Time: %s" % (str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"))))

        self.dbCur.execute('''SELECT task_id,time_finished,status, statusinfo,time_to_start,datetimestamp,repeat_in,resource,app,resource_param,app_param,task_param,group_id
            FROM COMPLETEDTASKS
            ORDER BY task_id DESC;''')

        tasks = self.dbCur.fetchall()

        pass
        if Verbose: print("#" * 120)
        for row in tasks:
            (task_id, time_finished, status, statusinfo, time_to_start, datetimestamp, repeat_in, resource, app,
             resource_param, app_param, task_param, group_id) = row
            TaskDir = None
            try:
                TaskDir = akrrtask.GetLocalTaskDir(resource, app, datetimestamp, False)
            except:
                pass

            if Verbose:
                print("task_id:  %-10d     started:      %s    finished: %s    group_id: %s" % (
                task_id, time_to_start, time_finished, group_id))
                print("resource: %-14s application: %-40s timestamp: %s" % (resource, app, datetimestamp))
                print("resource_param: %s    app_param: %s    task_param: %s    " % (
                resource_param, app_param, task_param))
                print("TaskDir:", TaskDir)
                print("-" * 120)
                print("status: %s" % (status))
                print("statusinfo:")
                print(statusinfo)
                print("-" * 120)

            appstdoutFileContent = None
            stdoutFileContent = None
            stderrFileContent = None

            if TaskDir != None:
                # Get All States
                ths = []

                import pickle
                procTaskDir = os.path.join(TaskDir, 'proc')
                thsFNs = []
                for f in os.listdir(procTaskDir):
                    if re.match("(\d+).st", f, 0) != None:
                        thsFNs.append(f)
                thsFNs = sorted(thsFNs)
                thFN = thsFNs[-1]

                picklefilename = os.path.join(procTaskDir, thFN)
                th = akrrtask.akrrGetTaskHandlerFromPkl(picklefilename)
                th.statefilename = thFN
                th.SetDirNames(cfg.completed_tasks_dir)

                resultFile = os.path.join(th.taskDir, "result.xml")
                jobfilesDir = os.path.join(th.taskDir, "jobfiles")
                (batchJobDir, stdoutFile, stderrFile, appstdoutFile, taskexeclogFile) = th.GetResultFiles()

                if appstdoutFile != None:
                    fin = open(appstdoutFile, "r")
                    appstdoutFileContent = fin.read()
                    fin.close()
                else:
                    appstdoutFileContent = "Does Not Present"
                if stdoutFile != None:
                    fin = open(stdoutFile, "r")
                    stdoutFileContent = fin.read()
                    fin.close()
                else:
                    stdoutFileContent = "Does Not Present"
                if stderrFile != None:
                    fin = open(stderrFile, "r")
                    stderrFileContent = fin.read()
                    fin.close()
                else:
                    stderrFileContent = "Does Not Present"
                if taskexeclogFile != None:
                    fin = open(taskexeclogFile, "r")
                    taskexeclogFileContent = fin.read()
                    fin.close()
                else:
                    taskexeclogFileContent = "Does Not Present"
                nodes = None
                nodesFileName = os.path.join(jobfilesDir, "gen.info")

                if (os.path.isfile(nodesFileName)):
                    parser = AppKerOutputParser()
                    parser.parseCommonParsAndStats(geninfo=nodesFileName)
                    if hasattr(parser, 'geninfo') and 'nodeList' in parser.geninfo:
                        nodesList = parser.geninfo['nodeList'].split()
                        nodes = ";"
                        for line in nodesList:
                            line = line.strip()
                            nodes += "%s;" % (line)
                        if len(nodes.strip().strip(';')) == 0:
                            nodes = None
                # print nodesFileName

                # print "*"*112
                if nodes != None:
                    if Verbose:
                        print("UPDATING nodes:", nodes)
                        print("=" * 120)
                    self.dbCur.execute("""UPDATE akrr_xdmod_instanceinfo
                        SET nodes=%s
                        WHERE instance_id=%s""",
                                       (nodes, task_id))

    def erran_task(self, task_id, resource, app):
        # Get applicable reg_exp
        print(task_id, resource, app)

        # Get appstdout,stderr,stdout
        self.dbCur.execute('''SELECT appstdout,stderr,stdout
            FROM akrr_errmsg
            WHERE task_id=%s;''', (task_id))

        rows = self.dbCur.fetchall()

        OutputFromRemoteHostIsPresent = False
        appstdout, stderr, stdout = (None, None, None)
        if len(rows) > 0:
            OutputFromRemoteHostIsPresent = True
            appstdout, stderr, stdout = rows[0]

        # Get akrr_statusinfo and  akrr_status
        self.dbCur.execute('''SELECT status,statusinfo
            FROM COMPLETEDTASKS
            WHERE task_id=%s;''', (task_id,))
        rows = self.dbCur.fetchall()
        akrr_status, akrr_statusinfo = (None, None)
        if len(rows) > 0:
            akrr_status, akrr_statusinfo = rows[0]

        # Get reg_exps
        self.dbCur.execute('''SELECT id,reg_exp,reg_exp_opt,source
            FROM akrr_err_regexp
            WHERE active=1 AND (resource="*" OR resource=%s OR resource LIKE %s OR resource LIKE %s OR resource LIKE %s)
            ORDER BY id ASC;''',
                           (resource, resource + ',%', "%," + resource + ',%', '%,' + resource))
        raw = self.dbCur.fetchall()

        # strings where to look for match
        strings_to_comp = [
            ['appstdout', appstdout],
            ['stderr', stderr],
            ['stdout', stdout],
            ['akrr_statusinfo', akrr_statusinfo],
            ['akrr_status', akrr_status],
        ]
        # apply reg. exp.
        rslt = None
        for reg_exp_id, reg_exp, reg_exp_opt, source in raw:
            rslt_found_in = None
            source = source.split(',')
            for stc_name, stc in strings_to_comp:
                if (source == "*" or source.count(stc_name) > 0) and stc != None:
                    rslt = re.search(reg_exp, stc, eval(reg_exp_opt))
                    if rslt != None:
                        rslt_found_in = stc_name
                        break
            if rslt != None:
                rslt = [rslt, stc_name, reg_exp_id, reg_exp, reg_exp_opt]
                break
        # push results to db
        if rslt != None:
            regres, stc_name, reg_exp_id, reg_exp, reg_exp_opt = rslt
            print("\treg_exp_id=", reg_exp_id)
            print("\treg_exp=", reg_exp)
            print("\tfound_in=", stc_name)
            self.dbCur.execute('''UPDATE  akrr_errmsg
            SET err_regexp_id=%s
            WHERE task_id=%s;''', (reg_exp_id, task_id))
        else:
            print("\tUnknown Error")
            self.dbCur.execute('''UPDATE  akrr_errmsg
            SET err_regexp_id=%s
            WHERE task_id=%s;''', (1000, task_id))
        self.dbCon.commit()

    def erran(self, dataFrom, dataTo, Verbose=True):
        """reprocess the output from Completed task one more time with hope that new task handlers have a better implementation of error handling"""

        print("""Reprocess the output from Completed task""")
        print("Time: %s" % (str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"))))

        print("Analysing period:", dataFrom, dataTo)
        self.dbCur.execute('''SELECT instance_id,resource,reporter
            FROM akrr_xdmod_instanceinfo
            WHERE status=0 AND collected >= %s AND collected < %s
            ORDER BY collected ASC;''', (dataFrom, dataTo))

        tasks = self.dbCur.fetchall()
        print("Total number of task to process:", len(tasks))
        for raw in tasks:
            task_id, resource, app = raw
            self.erran_task(task_id, resource, app)
        print("Done")

    def addTaskNR(self, time_to_start, repeat_in, resource, app, resource_param="{}", app_param="{}", task_param="{}",
                  group_id="None", parent_task_id=None):
        try:
            return self.addTask(time_to_start, repeat_in, resource, app, resource_param, app_param, task_param,
                                group_id, parent_task_id)
        except Exception:
            log.exception("Exception occurred during addTaskNR")
            return None

    def addTask(self, time_to_start, repeat_in, resource, app, resource_param, app_param, task_param, group_id,
                parent_task_id, only_checking=False):
        """Check the format and add task to schedule"""
        log.info(">" * 100)
        log.info("Adding new task")

        # determine timeToStart
        timeToStart = None
        if time_to_start == None or time_to_start == "":  # i.e. start now
            timeToStart = datetime.datetime.today()

        if timeToStart == None:
            if isinstance(time_to_start, datetime.datetime):
                timeToStart = copy.deepcopy(time_to_start)

        if timeToStart == None:
            iform = 0
            datetimeformats = ["%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%y-%m-%d %H:%M:%S", "%y-%m-%d %H:%M"]
            while not (timeToStart != None or iform >= len(datetimeformats)):
                try:
                    timeToStart = datetime.datetime.strptime(time_to_start, datetimeformats[iform])
                except:
                    iform += 1
        if timeToStart == None:
            iform = 0
            datetimeformats = ["%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"]
            while not (timeToStart != None or iform >= len(datetimeformats)):
                try:
                    timeToStart = datetime.datetime.strptime(
                        datetime.datetime.today().strftime("%Y-%m-%d ") + time_to_start, datetimeformats[iform])
                except:
                    iform += 1
        if timeToStart == None:
            raise IOError("Incorrect data-time format")
        # timeToStart=datetime.datetime.strptime(time_to_start,"%Y-%m-%d %H:%M:%S")
        # determine repeatIn
        repeatInFin = None
        if repeat_in != None:
            repeatInFin = cfg.get_formatted_repeat_in(repeat_in)
            if repeatInFin == None:
                raise IOError("Incorrect data-time format for repeating period")
            # check the repeat values
            match = re.match(r'(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)', repeatInFin, 0)
            g = match.group(1, 2, 3, 4, 5, 6)
            tao = (int(g[0]), int(g[1]), int(g[2]), int(g[3]), int(g[4]), int(g[5]))
            datetime.timedelta(tao[2], tao[3], tao[4], tao[5])
            if tao[0] != 0 or tao[1] != 0:
                if tao[2] != 0 or tao[3] != 0 or tao[4] != 0 or tao[5] != 0:
                    raise IOError(
                        "If repeating period is calendar months or years then increment in day/hours/mins/secs should be zero.")

        # check if resource exists
        cfg.FindResourceByName(resource)
        # check if app exists
        cfg.FindAppByName(app)
        # determine repeatIn
        log.info(
            "New task:\n\t" +
            "Starting time: %s\n\t" % timeToStart.strftime("%Y-%m-%d %H:%M:%S") +
            "Repeating period: %s\n\t" % repeatInFin +
            "Resource: %s\n\t" % resource +
            "Resource parameters: %s\n\t" % resource_param +
            "Application kernel: %s\n\t" % app +
            "Application kernel parameters: %s\n\t" % app_param +
            "Task parameters: %s\n" % task_param
        )
        task_id = None
        if not only_checking:
            self.dbCur.execute('''INSERT INTO SCHEDULEDTASKS (time_to_start,repeat_in,resource,app,resource_param,app_param,task_param,group_id,parent_task_id)
                    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)''', (
            timeToStart.strftime("%Y-%m-%d %H:%M:%S"), repeatInFin, resource, app, resource_param, app_param,
            task_param, group_id, parent_task_id))
            task_id = self.dbCur.lastrowid
            # self.dbCon.insert_id()
            self.dbCon.commit()
            if parent_task_id == None:
                self.dbCur.execute("""UPDATE SCHEDULEDTASKS
                        SET parent_task_id=%s
                        WHERE task_id=%s""",
                                   (task_id, task_id))
                self.dbCon.commit()
            #                 self.dbCur.execute('''SELECT task_id,parent_task_id FROM SCHEDULEDTASKS WHERE parent_task_id is NULL''')
        #                 rows=self.dbCur.fetchall()
        #                 for row in rows:
        #                     (m_task_id,m_parent_task_id)=row;
        #                     self.dbCur.execute("""UPDATE SCHEDULEDTASKS
        #                         SET parent_task_id=%s
        #                         WHERE task_id=%s""",
        #                         (m_task_id,m_task_id))
        #                 self.dbCon.commit()
        log.info("task id: %s", task_id)
        log.info("<" * 120)
        return task_id


def akrrValidateTaskVariableValue(k, v):
    """validate value of task variable, reformat if needed/possible
    raise error if value is incorrect
    return value or reformated value"""
    if k == "repeat_in":
        if v == None:
            # i.e. no repetition
            return None
        v = v.strip().strip('"').strip("'")
        v = cfg.get_formatted_repeat_in(v)
        if v != None:
            match = re.match(r'(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)', v, 0)
            if not match:
                raise IOError('Unknown format for repeat_in')
            else:
                g = match.group(1, 2, 3, 4, 5, 6)
                tao = (int(g[0]), int(g[1]), int(g[2]), int(g[3]), int(g[4]), int(g[5]))
                if g[0] == 0 and g[1] == 0 and g[2] == 0 and g[3] == 0 and g[4] == 0 and g[5] == 0:
                    return None
        if v == None:
            raise IOError('Unknown format for repeat_in')
    if k == "time_to_start":
        v = v.strip().strip('"').strip("'")
        v = cfg.get_formatted_time_to_start(v)
        if v == None:
            raise IOError('Unknown format for time_to_start')

    if k == 'task_param' or k == 'resource_param' or k == 'app_param':
        try:
            v2 = eval(v)
        except Exception:
            raise IOError('Unknown format for ' + k)
        if not isinstance(v2, dict):
            raise IOError('Unknown format for ' + k + '. Must be dict.')

    if k == 'resource_param':
        v2 = eval(v)
        print(v2['nnodes'], isinstance(v2['nnodes'], int))
        if 'nnodes' not in v2:
            raise IOError('nnodes must be present in ' + k)
        if not isinstance(v2['nnodes'], int):
            raise IOError("incorrect format for resource_param['nnodes'] must be integer")
    if k == "resource":
        try:
            cfg.FindResourceByName(v)
        except Exception:
            log.exception("Exception occurred during resource record searching.")
            raise IOError('Unknown resource: ' + v)
    if k == "app":
        try:
            cfg.FindAppByName(v)
        except Exception:
            log.exception("Exception occurred during app kernel; record searching.")
            raise IOError('Unknown application kernel: ' + v)
    if k == "next_check_time":
        v = v.strip().strip('"').strip("'")
        v = cfg.get_formatted_time_to_start(v)
        if v == None:
            raise IOError('Unknown format for next_check_time')
    return v


# task manipulation
def akrrDeleteTask(task_id, removeFromScheduledQueue=True, removeFromActiveQueue=True, removeDerivedTask=True):
    """
    remove the task from AKRR server
    
    removeFromScheduledQueue=True and removeFromActiveQueue=False and removeDerivedTask=False
    remove only from scheduled queue
    
    removeFromScheduledQueue=False and removeFromActiveQueue=True and removeDerivedTask=False
    remove only from active queue
    
    removeFromScheduledQueue=True and removeFromActiveQueue=True and removeDerivedTask=False
    remove from scheduled or active queue
    
    removeFromScheduledQueue=True and removeFromActiveQueue=True and removeDerivedTask=True
    remove this and all derivative tasks from scheduled or active queue
    """
    db, cur = cfg.getDB(True)
    cur.execute('''SELECT * FROM SCHEDULEDTASKS
            WHERE task_id=%s''', (task_id,))
    possible_task = cur.fetchall()

    scheduled_task = None
    active_task = None
    complete_task = None

    if len(possible_task) == 1:
        # task still in scheduled_tasks queue
        scheduled_task = possible_task[0]
    else:
        # task might be in active_tasks queue
        cur.execute('''SELECT * FROM ACTIVETASKS
            WHERE task_id=%s''', (task_id,))
        possible_task = cur.fetchall()

        if len(possible_task) == 1:
            active_task = possible_task[0]
        else:
            # task might be complete_tasks
            cur.execute('''SELECT * FROM COMPLETEDTASKS
                WHERE task_id=%s''', (task_id,))
            possible_task = cur.fetchall()
            if len(possible_task) == 1:
                complete_task = possible_task[0]
            else:
                raise IOError("""Task %d is not in queue""" % (task_id))

    if removeFromScheduledQueue == True and scheduled_task != None:
        cur.execute('''DELETE FROM SCHEDULEDTASKS
                WHERE task_id=%s;''', (task_id,))
        db.commit()

    if removeFromActiveQueue == True and active_task != None:
        print("Trying to remove task from ACTIVETASKS")
        t0 = datetime.datetime.now()
        while active_task['task_lock'] != 0:
            # i.e. one of child process is working on this task, will wait till it finished
            if akrrscheduler != None:
                # i.e. it is master
                akrrscheduler.runActiveTasks_CheckTheStep()

            cur.execute('''SELECT * FROM ACTIVETASKS
                WHERE task_id=%s''', (task_id,))
            active_task = cur.fetchone()
            if t0 - datetime.datetime.now() > datetime.timedelta(seconds=120):
                raise Exception("child proccess handling subtask for too long")

        CanBeSafelyRemoved = False
        # get task handler
        th = akrrtask.akrrGetTaskHandler(active_task['resource'], active_task['app'], active_task['datetimestamp'])

        CanBeSafelyRemoved = th.Terminate()

        if CanBeSafelyRemoved:
            print("The task can be safely removed")
            # remove from DB
            cur.execute('''DELETE FROM ACTIVETASKS
                WHERE task_id=%s;''', (task_id,))
            db.commit()
            # remove from local disk
            th.DeleteRemoteFolder()
            th.DeleteLocalFolder()
        else:
            raise Exception("Task can NOT be remove safely. Unimplemented status:" + active_task['status'])

    if removeDerivedTask == True:
        # find derived tasks
        task = scheduled_task
        if task == None:
            task = active_task
        if task == None:
            task = complete_task
        if task['parent_task_id'] != None:
            task_id = task['task_id']
            parent_task_id = task['parent_task_id']
            tasks_to_delete = []

            if removeFromScheduledQueue == True:
                cur.execute('''SELECT * FROM SCHEDULEDTASKS
                    WHERE parent_task_id=%s''', (task_id,))
                possible_tasks = cur.fetchall()

                for possible_task in possible_tasks:
                    if possible_task['task_id'] > task_id:
                        tasks_to_delete.append(possible_task['task_id'])

            if removeFromActiveQueue == True:
                cur.execute('''SELECT * FROM ACTIVETASKS
                    WHERE parent_task_id=%s''', (task_id,))
                possible_tasks = cur.fetchall()

                for possible_task in possible_tasks:
                    if possible_task['task_id'] > task_id:
                        tasks_to_delete.append(possible_task['task_id'])

            for task_to_delete in tasks_to_delete:
                akrrDeleteTask(task_to_delete, removeFromScheduledQueue=removeFromScheduledQueue,
                               removeFromActiveQueue=removeFromActiveQueue, removeDerivedTask=False)

    cur.close()
    db.close()
    return


def akrrUpdateTaskParameters(task_id, new_param, updateDerivedTask=True):
    """
    update task parameters
    """
    print("Akrr Update Task Parameters: %r" % (task_id,))

    db, cur = cfg.getDB(True)
    cur.execute('''SELECT * FROM SCHEDULEDTASKS
            WHERE task_id=%s''', (task_id,))
    possible_task = cur.fetchall()

    scheduled_task = None
    active_task = None
    complete_task = None

    print("Length of Possible Tasks: %r" % (len(possible_task),))
    if len(possible_task) == 1:
        # task still in scheduled_tasks queue
        scheduled_task = possible_task[0]
    else:
        # task might be in active_tasks queue
        cur.execute('''SELECT * FROM ACTIVETASKS
            WHERE task_id=%s''', (task_id,))
        possible_task = cur.fetchall()

        if len(possible_task) == 1:
            active_task = possible_task[0]
        else:
            # task might be complete_tasks
            cur.execute('''SELECT * FROM COMPLETEDTASKS
                WHERE task_id=%s''', (task_id,))
            possible_task = cur.fetchall()
            if len(possible_task) == 1:
                complete_task = possible_task[0]
            else:
                raise IOError("""Task %d is not in queue""" % (task_id))

    if scheduled_task != None:
        possible_keys_to_change = list(scheduled_task.keys())
        possible_keys_to_change.remove('task_id')
        possible_keys_to_change.remove('parent_task_id')
        possible_keys_to_change.remove('app')
        possible_keys_to_change.remove('resource')

        print("Scheduled Task Keys: %r" % (list(scheduled_task.keys()),))
        print("Possible Keys: %r" % (possible_keys_to_change,))
        print("New Params: %r " % (new_param,))
        # pack mysql update
        update_set_var = []
        update_set_value = []
        for k in new_param:
            if k in possible_keys_to_change:
                update_set_var.append(k + "=%s")
                update_set_value.append(akrrValidateTaskVariableValue(k, new_param[k]))
            else:
                raise IOError('Can not update %s' % (k,))

        update_set_value.append(scheduled_task['task_id'])

        if len(update_set_var) > 0:
            # update the db
            cur.execute('UPDATE SCHEDULEDTASKS SET ' + ", ".join(update_set_var) + " WHERE task_id=%s",
                        tuple(update_set_value))
            db.commit()
    else:
        if updateDerivedTask == False:
            raise IOError('Can not update task because it left scheduled_task queue')

    if updateDerivedTask == True and scheduled_task == None:
        # find derived tasks
        task = scheduled_task
        if task == None:
            task = active_task
        if task == None:
            task = complete_task
        print(task)

        if task['parent_task_id'] != None:
            task_id = task['task_id']
            parent_task_id = task['parent_task_id']
            tasks_to_update = []

            cur.execute('''SELECT * FROM SCHEDULEDTASKS
                WHERE parent_task_id=%s''', (task_id,))
            possible_tasks = cur.fetchall()

            for possible_task in possible_tasks:
                if possible_task['task_id'] > task_id:
                    tasks_to_update.append(possible_task)

            for task_to_update in tasks_to_update:
                # new_param2={}
                # for k,v in new_param.iteritems():
                #    new_param2[k]=v

                # if "time_to_start" in new_param:

                akrrUpdateTaskParameters(task_to_update['task_id'], new_param, updateDerivedTask=False)
        else:
            raise IOError('Can not update task because it left scheduled_task queue')

    cur.close()
    db.close()
    return


def akrrGetPIDofServer(bDeletePIDFileIfPIDdoesNotExist=False):
    """Return the PID of AKRR server"""
    pid = None
    if os.path.isfile(os.path.join(cfg.data_dir, "akrr.pid")):
        # print "Read process pid from",os.path.join(akrr.data_dir,"akrr.pid")

        fin = open(os.path.join(cfg.data_dir, "akrr.pid"), "r")
        l = fin.readlines()
        pid = int(l[0])
        fin.close()

        # Check For the existence of a unix pid
        try:
            os.kill(pid, 0)
            # print "/proc/%d/cmdline"%(pid)
            fin = open("/proc/%d/cmdline" % (pid), 'r')
            cmd = fin.read()
            fin.close()

            if cmd.count('akrr') and cmd.count('daemon') and cmd.count('start'):
                return pid
        except Exception:
            pass
    if pid != None:
        # if here means that previous session was crushed
        if bDeletePIDFileIfPIDdoesNotExist:
            log.warning("""WARNING:File %s exists meaning that another AKRR Scheduler
            process is already working with this directory.
            or the previous one had exited incorrectly.""" % (os.path.join(cfg.data_dir, "akrr.pid")))
            os.remove(os.path.join(cfg.data_dir, "akrr.pid"))
            return None
        else:
            raise IOError("""File %s exists meaning that another AKRR Scheduler
            process is already working with this directory.
            or the previous one had exited incorrectly.""" % (os.path.join(cfg.data_dir, "akrr.pid")))

    return pid


redirected_filename = None
this_stdout = None
this_stderr = None


def akrrServerStart():
    """Start AKRR server"""
    # check if AKRR already up
    pid = akrrGetPIDofServer(bDeletePIDFileIfPIDdoesNotExist=True)
    if pid != None:
        raise IOError("Can not start AKRR server because another instance is already running.")
    # check if something already listening on REST API port
    restapi_host = 'localhost'
    if cfg.restapi_host != "":
        restapi_host = cfg.restapi_host
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((restapi_host, cfg.restapi_port))
    if result == 0:
        raise IOError(
            "Can not start AKRR server because another servise listening on %s:%d!" % (restapi_host, cfg.restapi_port))

    def kill_child_processes(parent_pid, sig=signal.SIGTERM):
        ps_command = subprocess.Popen("ps -o pid --ppid %d --noheaders" % parent_pid, shell=True,
                                      stdout=subprocess.PIPE)
        ps_output = ps_command.stdout.read()
        retcode = ps_command.wait()
        assert retcode == 0, "ps command returned %d" % retcode
        for pid_str in ps_output.split("\n")[:-1]:
            os.kill(int(pid_str), sig)

    # make dir for logs and check the biggest number
    if not os.path.isdir(cfg.data_dir):
        raise IOError("Directory %s does not exist or is not directory." % (cfg.data_dir))
    if not os.path.isdir(os.path.join(cfg.data_dir, "srv")):
        log.info("Directory %s does not exist, creating it." % (os.path.join(cfg.data_dir, "srv")))
        os.mkdir(os.path.join(cfg.data_dir, "srv"))
    logname = os.path.join(cfg.data_dir, "srv", datetime.datetime.today().strftime("%Y.%m.%d_%H.%M.%f") + ".log")
    while os.path.exists(logname) == True:
        logname = os.path.join(cfg.data_dir, "srv", datetime.datetime.today().strftime("%Y.%m.%d_%H.%M.%f") + ".log")
    log.info("Writing logs to:\n\t%s" % (logname))
    # createDaemon
    # this was adopted with a minor changes from Chad J. Schroeder  daemonization script
    # http://code.activestate.com/recipes/278731-creating-a-daemon-the-python-way/
    # daemonization a double fork magic
    sys.stdout.flush()
    sys.stderr.flush()

    global redirected_filename, this_stdout, this_stderr
    if redirected_filename != None:
        this_stdout.close()
        this_stderr.close()
        sys.stdout, sys.stderr = sys.__stdout__, sys.__stderr__

    try:
        pid = os.fork()
    except OSError as e:
        raise Exception("%s [%d]" % (e.strerror, e.errno))

    if (pid == 0):  # i.e. first child

        # print "pid of 1 child",os.getpid()
        os.setsid()  # set to be session leader
        try:
            pid = os.fork()
        except OSError as e:
            raise Exception("%s [%d]" % (e.strerror, e.errno))
        if (pid == 0):  # i.e. grand child
            os.setsid()  # set to be session leader
            os.chdir(cfg.data_dir)
            # os.umask(755)
            # print "pid of 2 child",os.getpid()
            # print "AKRR Server PID is",os.getpid()
        else:
            # print "pid of 1 child",os.getpid()
            os._exit(0)  # i.e. first child is exiting here
    else:
        # print "pid of 0 child",os.getpid()
        # read the output from daemon till find that it is in the loop
        # wait till daemon start writing logs
        if redirected_filename != None:
            this_stdout = open(redirected_filename, 'a')
            this_stderr = open(redirected_filename, 'a')

            sys.stdout = this_stdout
            sys.stderr = this_stderr
        dt = 0.25
        t0 = time.time()
        while time.time() - t0 < 10.0 and not os.path.isfile(logname):
            time.sleep(dt)
        if not os.path.isfile(logname):
            log.error("AKRR Server have not start logging yet. Something is wrong! Exiting...")
            kill_child_processes(os.getpid())
            os._exit(1)  # i.e. parent of first child is exiting here

        log.info("following log: %s", logname)
        logfile = open(logname, "r")
        REST_API_up = False
        in_the_main_loop = False
        t0 = time.time()
        while time.time() - t0 < 20.0:
            line = logfile.readline()
            if len(line) != 0:
                print(line, end=' ')
                if line.count("Listening on ") > 0:
                    REST_API_up = True
                if line.count("Got into the running loop on ") > 0:
                    in_the_main_loop = True
                if REST_API_up and in_the_main_loop:
                    break
            else:
                time.sleep(dt)
        if not REST_API_up:
            log.error("AKRR REST API is not up.\n Something is wrong. Exiting...")
            kill_child_processes(os.getpid())
            os._exit(1)  # i.e. parent of first child is exiting here
        if not in_the_main_loop:
            log.error("AKRR Server have not reached the loop.\n Something is wrong. Exiting...")
            kill_child_processes(os.getpid())
            os._exit(1)  # i.e. parent of first child is exiting here

        # if here everything should be fine
        log.info("\nAKRR Server successfully reached the loop.")
        os._exit(0)  # i.e. parent of first child is exiting here

    # close all file descriptors
    import resource  # Resource usage information.
    maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    if (maxfd == resource.RLIM_INFINITY):
        maxfd = 1024

    print()
    # print "Redirect the standard I/O to\n\t%s"%(logname)
    # Iterate through and close all file descriptors.
    for fd in range(maxfd - 1, -1, -1):
        try:
            os.close(fd)
            pass
        except OSError:  # ERROR, fd wasn't open to begin with (ignored)
            # print fd
            pass
    # print "1Redirect the standard I/O to\n\t%s"%(logname)
    # Redirect the standard I/O
    # The standard I/O file descriptors are redirected to /dev/null by default.
    REDIRECT_TO = "/dev/null"
    if (hasattr(os, "devnull")):
        REDIRECT_TO = os.devnull
    f0 = os.open(REDIRECT_TO, os.O_RDONLY)  # standard input (0)
    f1 = os.open(logname, os.O_WRONLY | os.O_CREAT)  # standard output (1)
    # f2=os.open(logname, os.O_WRONLY | os.O_APPEND )    # standard output (1)
    # Duplicate standard input to standard output and standard error.
    # os.dup2(0, 1)            # standard output (1)
    os.dup2(1, 2)  # standard error (2)

    # finally
    log.info("Starting Application Remote Runner")
    # akrrcfg.PrintOutResourceAndAppSummary()
    global akrrscheduler
    akrrscheduler = akrrScheduler()
    akrrscheduler.run()

    # Iterate through and close all file descriptors.
    for fd in range(maxfd - 1, -1, -1):
        try:
            os.close(fd)
            pass
        except OSError:  # ERROR, fd wasn't open to begin with (ignored)
            # print fd
            pass
    return None


def akrrServerStop():
    """Stop AKRR server"""
    pid = akrrGetPIDofServer(bDeletePIDFileIfPIDdoesNotExist=True)
    if pid == None:
        log.warning("Can not stop AKRR server because none is running.")
        return

    # send a signal to terminate
    os.kill(pid, signal.SIGTERM)

    try:
        # wait till proccess will finished
        while True:
            os.kill(pid, 0)
            time.sleep(0.2)
    except Exception:
        pass

    log.info("Stoped AKRR server (PID: " + str(pid) + ")")
    return None


def akrrServerCheckNRestart():
    """Check AKRR server status if not running"""
    pid = akrrGetPIDofServer(bDeletePIDFileIfPIDdoesNotExist=True)
    t = str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"))

    if pid == None:
        print("%s: AKRR server is down will start it" % (t,))
        akrrServerStart()
    else:
        print("%s: AKRR Server is up and it's PID is %d" % (t, pid))
    return None


def akrrDeleteTaskWithExternalServerInterupt(task_id):
    """remove the task from AKRR server"""
    # @todo do we still use it?
    pid = akrrGetPIDofServer()

    if pid != None:
        # ask the server not to start new tasks and subtasks
        os.kill(pid, signal.SIGUSR1)

    # sleep a bit
    time.sleep(1)

    try:
        sch = akrrScheduler()

        # check if the task is in SCHEDULEDTASKS
        sch.ScheduledTasksCur.execute('''SELECT * FROM SCHEDULEDTASKS
            WHERE task_id=%s ;''', (task_id,))
        tasksToRemove = sch.ScheduledTasksCur.fetchone()
        if tasksToRemove != None:
            sch.ScheduledTasksCur.execute('''DELETE FROM SCHEDULEDTASKS
                WHERE task_id=%s;''', (task_id,))
            sch.ScheduledTasksCon.commit()
            sch.ScheduledTasksCur.execute('''SELECT * FROM SCHEDULEDTASKS
            WHERE task_id=%s ;''', (task_id,))
            tasksToRemove = sch.ScheduledTasksCur.fetchone()
            if tasksToRemove == None:
                print("Task %d was removed from SCHEDULEDTASKS." % (task_id))
        else:
            # check if the task is in ACTIVETASKS
            sch.ActiveTasksCur.execute('''SELECT task_lock,status FROM ACTIVETASKS
                WHERE task_id=%s ;''', (task_id,))
            tasksToRemove = sch.ActiveTasksCur.fetchone()
            if tasksToRemove != None:
                print("Trying to remove task from ACTIVETASKS")
                (task_lock, status) = tasksToRemove
                while task_lock != 0:
                    sch.ActiveTasksCur.execute('''SELECT task_lock,status FROM ACTIVETASKS
                       WHERE task_id=%s ;''', (task_id,))
                    (task_lock, status) = sch.ActiveTasksCur.fetchone()

                CanBeSafelyRemoved = False
                # get task handler
                sch.ActiveTasksCur.execute('''SELECT task_id,resource,app,datetimestamp FROM ACTIVETASKS
                        WHERE task_id=%s;''', (task_id,))
                (task_id, resourceName, appName, timeStamp) = sch.ActiveTasksCur.fetchone()
                # Redirect logging
                # taskDir=akrrtask.GetLocalTaskDir(resourceName,appName,timeStamp)
                # akrrtask.RedirectStdoutToLog(os.path.join(taskDir,'proc','log'))
                th = akrrtask.akrrGetTaskHandler(resourceName, appName, timeStamp)

                CanBeSafelyRemoved = th.Terminate()

                if CanBeSafelyRemoved:
                    print("The task can be safely removed")
                    # Redirect logging back
                    # akrrtask.RedirectStdoutBack()

                    # remove from DB
                    sch.ActiveTasksCur.execute('''DELETE FROM ACTIVETASKS
                        WHERE task_id=%s;''', (task_id,))
                    sch.ActiveTasksCon.commit()
                    # remove from local disk
                    th.DeleteRemoteFolder()
                    th.DeleteLocalFolder()


                else:
                    print("Task can NOT be remove safely. Unimplemented status:")
                    print("\t%s" % (status))

                # check again
                sch.ActiveTasksCur.execute('''SELECT task_lock,status FROM ACTIVETASKS
                    WHERE task_id=%s ;''', (task_id,))
                tasksToRemove = sch.ActiveTasksCur.fetchone()
                if tasksToRemove == None:
                    print("Task %d was removed from ACTIVETASKS." % (task_id))
                else:
                    print("Task %d was NOT removed from ACTIVETASKS." % (task_id))
            else:
                print("Task %d is NOT in SCHEDULEDTASKS or ACTIVETASKS." % (task_id))

        if pid != None:
            # restore schedule functionality
            os.kill(pid, signal.SIGUSR2)
    except Exception:
        log.exception("Exception occurred during akrrDeleteTaskWithExternalServerInterupt")
        if pid != None:
            # restore schedule functionality
            os.kill(pid, signal.SIGUSR2)
        raise


def akrrd_main2(action='', append=False, output_file=None):
    if action == 'startdeb':
        log.basicConfig(level=log.DEBUG)
        print("Starting Application Remote Runner")
        # check if AKRR already up
        pid = akrrGetPIDofServer(bDeletePIDFileIfPIDdoesNotExist=True)
        if pid != None:
            raise IOError("Can not start AKRR server because another instance is already running.")
        global akrrscheduler
        akrrscheduler = akrrScheduler()
        akrrscheduler.run()
        del akrrscheduler
    else:
        log_file1 = None
        log_file2 = None

        if output_file != None:
            global redirected_filename, this_stdout, this_stderr
            redirected_filename = output_file
            this_stdout = open(redirected_filename, 'w' if append == False else 'a')
            this_stderr = open(redirected_filename, 'a')
            sys.stdout = this_stdout
            sys.stderr = this_stderr

        if (action == 'start'):
            akrrServerStart()
        elif (action == 'stop'):
            akrrServerStop()
        elif (action == 'monitor'):
            sch = akrrScheduler()
            sch.monitor()
        elif (action == 'status'):
            sch = akrrScheduler()
            sch.status()
        elif (action == 'checknrestart'):
            akrrServerCheckNRestart()

        elif (action == 'restart'):
            log.info("Restarting AKRR")
            try:
                akrrServerStop()
            except Exception:
                log.exception("Exception was thrown during daemon stopping")
            akrrServerStart()

        if log_file1: log_file1.close()
        if log_file2: log_file2.close()


def akrrd_main():
    parser = argparse.ArgumentParser(description="""Application Kernel Remote Runner (AKRR) daemon launcher.
    Without arguments will launch AKRR in command line mode, i.e. stdout is to terminal
    """)
    parser.add_argument('-o', '--output-file', help="redirect stdout and stderr to file")
    parser.add_argument('-a', '--append', action='store_true',
                        help="append stdout and stderr to file rather then overwrite")

    subparsers = parser.add_subparsers(title='commands', dest='action');
    subparsers.add_parser('start', help='launch Application Remote Runner in daemon mode')
    subparsers.add_parser('stop', help='terminate Application Remote Runner')
    subparsers.add_parser('restart', help='restart AKRR daemon')
    subparsers.add_parser('checknrestart', help='check if AKRR daemon is up if not it will restart it')
    subparsers.add_parser('monitor', help='monitor the activity of Application Remote Runner')
    subparsers.add_parser('status', help='print current status of Application Remote Runner')
    subparsers.add_parser('startdeb', help='launch Application Remote Runner in foreground mode')

    args = parser.parse_args()

    akrrd_main2(args.action, args.append, args.output_file)


if __name__ == '__main__':
    akrrd_main()
