import time
import os

import sys
import datetime
import re
import multiprocessing
import signal
import copy
import subprocess
import socket

from typing import Union

from . import cfg
import akrr.db

import akrr.util.time
from akrr.util.time import time_stamp_to_datetime_str
from .util import log
from . import akrr_task

from .akrrerror import AkrrError

akrr_scheduler = None


class _FakeProcess:
    def __init__(self):
        self.exitcode = 0
        self.is_alive = True

    def join(self, _):
        self.is_alive = False
        return

    def is_alive(self):
        return self.is_alive


def _start_the_task_step(resource_name, app_name, time_stamp, results_queue,
                         fatal_errors_count=0, fails_to_submit_to_the_queue=0):
    try:
        # Redirect logging
        task_dir = akrr_task.get_local_task_dir(resource_name, app_name, time_stamp)
        if cfg.redirect_task_processing_to_log_file:
            akrr_task.redirect_stdout_to_log(os.path.join(task_dir, 'proc', 'log'))

        # Do the task
        th = akrr_task.get_task_handler(resource_name, app_name, time_stamp)

        th.fatal_errors_count = fatal_errors_count
        th.fails_to_submit_to_the_queue = fails_to_submit_to_the_queue

        repeat_in = th.to_do_next()

        if th.state_changed():
            akrr_task.dump_task_handler(th)

        m_pid = os.getpid()
        results_queue.put({
            'pid': m_pid,
            "status": th.status,
            "status_info": th.status_info,
            "repeat_in": repeat_in,
            "fatal_errors_count": th.fatal_errors_count,
            "fails_to_submit_to_the_queue": th.fails_to_submit_to_the_queue,
        })

        # Redirect logging back
        if cfg.redirect_task_processing_to_log_file:
            akrr_task.redirect_stdout_back()

        return 0
    except Exception as e:
        log.exception("Exception was thrown during StartTheStep")
        log.log_traceback(str(e))
        if akrr_task.log_file is not None:
            akrr_task.redirect_stdout_back()
        return 1


class AkrrDaemon:
    """
    AkrrDaemon - start task execution
    """
    def __init__(self, adding_new_tasks=False):
        # rest api process
        self.restapi_proc = None
        # load Scheduled Tasks DB
        self.dbCon, self.dbCur = akrr.db.get_akrr_db()

        # Sanitizing, set task_lock to 0 in case if previous instance didn't exit properly
        if not adding_new_tasks:
            self.dbCur.execute("UPDATE active_tasks SET task_lock=0 WHERE task_lock>0 ;")
            self.dbCon.commit()
        #
        self.maxTaskHandlers = cfg.max_task_handlers
        self.max_wall_time_for_task_handlers = cfg.max_wall_time_for_task_handlers

        self.workers = []
        self.Results = {}
        self.ResultsQueue = multiprocessing.Queue()

        self.repeat_after_forcible_termination = cfg.repeat_after_forcible_termination
        self.max_fatal_errors_for_task = cfg.max_fatal_errors_for_task

        self.bRunScheduledTasks = True
        self.bRunActiveTasks_StartTheStep = True
        self.bRunActiveTasks_CheckTheStep = True
        self.LastOpSignal = None

        self.proc_queue_to_master = None
        self.proc_queue_from_master = None

    def __del__(self):
        if self.dbCon is not None:
            self.dbCon.commit()
            if self.dbCur is not None:
                self.dbCur.close()
            self.dbCon.close()
        if self.restapi_proc is not None:
            self.restapi_proc.terminate()

    def add_fatal_errors_for_task_count(self, task_id: Union[str, int], count: int=1):
        """
        Increment fatal error count of task with id `task_id` by `count`
        """
        self.dbCur.execute('''SELECT fatal_errors_count FROM active_tasks WHERE task_id=%s ;''', (task_id,))
        fatal_errors_count = self.dbCur.fetchall()[0][0]
        fatal_errors_count += count
        self.dbCur.execute('''UPDATE active_tasks SET fatal_errors_count=%s WHERE task_id=%s ;''',
                           (fatal_errors_count, task_id))
        self.dbCon.commit()

    def run_scheduled_tasks(self):
        """
        Start task which are due for execution
        """
        time_now_str = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
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

        self.dbCur.execute(
            '''SELECT task_id, time_to_start, repeat_in, resource, app, resource_param, 
                      app_param, task_param, group_id, parent_task_id
               FROM mod_akrr.scheduled_tasks AS s
               WHERE s.time_to_start<=%s
               ORDER BY s.time_to_start ASC''', (time_now_str,))

        tasks_to_activate = self.dbCur.fetchall()

        for task_to_activate in tasks_to_activate:
            (task_id, time_to_start, repeat_in, resource, app, resource_param, app_param, task_param_str, group_id,
             parent_task_id) = task_to_activate

            task_param = eval(task_param_str)
            if task_param.get('test_run', False) is False:
                if resource_enabled.get(resource, 0) == 0 or appkernel_enabled.get(app, 0) == 0:
                    continue


            task_activated = False
            task_handler = None
            start_task_execution = True
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
                    "Task parameters: %s\n\t" % task_param_str +
                    "Parent task id: %s" % parent_task_id)

                # check limit for resource on max number of active tasks
                if cfg.find_resource_by_name(resource).get('max_number_of_active_tasks', -1) >= 0:
                    # get number of active tasks
                    self.dbCur.execute(
                        '''SELECT task_id, resource, app
                           FROM mod_akrr.active_tasks
                           WHERE resource like %s''', (resource,))
                    activate_task = self.dbCur.fetchall()
                    if len(activate_task) >= cfg.find_resource_by_name(resource).get('max_number_of_active_tasks', -1):
                        continue
                
                # checks if there is a limit to the number of active tasks akrr can have
                if cfg.max_number_of_active_tasks_total >= 0:
                    # checks list of all active tasks
                    self.dbCur.execute(
                        '''SELECT task_id, resource, app
                           FROM mod_akrr.active_tasks''')
                    active_tasks_total = self.dbCur.fetchall()
                    # if there's too many active tasks, break out of the loop
                    if len(active_tasks_total) >= cfg.max_number_of_active_tasks_total:
                        return

                if cfg.find_resource_by_name(resource).get('active', True) is False:
                    raise AkrrError("%s is marked as inactive in AKRR" % resource)

                # Commit all what was pushed before but not committed
                # so we can rollback if something will go wrong
                self.dbCon.commit()
                self.dbCon.commit()

                # Check If resource is on maintenance
                self.dbCur.execute(
                    '''SELECT * FROM akrr_resource_maintenance
                       WHERE (resource="*" OR resource=%s OR resource LIKE %s OR resource LIKE %s OR resource LIKE %s)
                       AND start<=%s AND %s<=end;''',
                    (resource, resource, resource, resource, time_now_str, time_now_str))

                resources_on_maintenance = self.dbCur.fetchall()
                if len(resources_on_maintenance) > 0:
                    start_task_execution = False
                    log.warning("Resource (%s) is under maintenance:" % resource)
                    for resource_on_maintenance in resources_on_maintenance:
                        log.warning(resource_on_maintenance)
                    if repeat_in is not None:
                        log.warning("This app. kernel is scheduled for repeat run, thus will skip this run")
                    else:
                        log.warning("Will postpone the execution by one day")
                        self.dbCur.execute('''UPDATE scheduled_tasks
                            SET time_to_start=%s
                            WHERE task_id=%s ;''', (time_to_start + datetime.timedelta(days=1), task_id))
                        self.dbCon.commit()

                # if a bundle task send subtask to  scheduled_tasks
                if app.count("bundle") > 0:
                    task_param = eval(task_param_str)
                    if 'AppKers' in task_param:
                        for subtask_app in task_param['AppKers']:
                            subtask_task_param = "{'masterTaskID':%d}" % (task_id,)
                            self.add_task(time_to_start, None, resource, subtask_app, resource_param, app_param,
                                          subtask_task_param, group_id, parent_task_id)

                if start_task_execution:
                    task_handler = akrr_task.get_new_task_handler(
                        task_id, resource, app, resource_param, app_param, task_param_str)
                    akrr_task.dump_task_handler(task_handler)
                    next_check_time = (datetime.datetime.today() + datetime.timedelta(minutes=1)).strftime(
                        "%Y-%m-%d %H:%M:%S")
                    # First we'll copy it to ActiveTasks
                    self.dbCur.execute(
                        '''INSERT INTO active_tasks 
                           (task_id,next_check_time,datetime_stamp,time_activated,time_to_start,repeat_in,
                            resource,app,resource_param,app_param,task_lock,task_param,group_id,parent_task_id)
                           VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,0,%s,%s,%s);''',
                        (task_id, next_check_time, task_handler.timeStamp,
                         time_stamp_to_datetime_str(task_handler.timeStamp),
                         time_to_start, repeat_in, resource, app, resource_param, app_param, task_param_str,
                         group_id, parent_task_id))
                    # Sanity check on repeat
                    repeat_in = akrr.util.time.verify_repeat_in(repeat_in)

                    # Schedule next
                    if repeat_in is not None:
                        next_time = akrr.util.time.get_next_time(time_to_start.strftime("%Y-%m-%d %H:%M:%S"), repeat_in)
                        log.info("Schedule another task for %s" % next_time)
                        self.add_task(next_time, repeat_in, resource, app, resource_param, app_param, task_param_str,
                                      group_id, parent_task_id)
                        # self.dbCon.commit()
                if self.bRunScheduledTasks is False:
                    # means that the termination signal was send while this function is already running
                    raise IOError("Can not activate task because got a massage to postpone activation")
                task_activated = True
            except Exception as e:
                log.exception("Can not submit job to active tasks")
                log.log_traceback(str(e))
                self.dbCon.rollback()
                self.dbCon.rollback()
                if task_handler is not None:
                    task_handler.DeleteLocalFolder()
            del task_handler
            if task_activated is True:
                # Now commit the changes
                self.dbCon.commit()
                if repeat_in is not None:
                    self.dbCon.commit()
                # Now we need to delete it from ScheduledTasks
                self.dbCur.execute('''DELETE FROM scheduled_tasks
                    WHERE task_id=%s;''', (task_id,))
                self.dbCon.commit()

            print("<" * 120)

    def run_active_tasks__start_the_step(self):
        """
        For task with expired next_check_time and currently not handled
        start a proccess to handle it
        """
        time_now = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        # Get all tasks which should be started
        self.dbCur.execute('''SELECT task_id,resource,app,datetime_stamp,fatal_errors_count,fails_to_submit_to_the_queue FROM active_tasks
            WHERE next_check_time<=%s AND task_lock=0
            ORDER BY next_check_time ASC ;''', (time_now,))
        tasks_to_check = self.dbCur.fetchall()

        i_tasks_send = 0
        for row in tasks_to_check:
            if self.maxTaskHandlers == 0:
                # Executing task by main thread
                (task_id, resource_name, app_name, time_stamp, fatal_errors_count, fails_to_submit_to_the_queue) = row
                log.info("Working on:\n\t%s" % (akrr_task.get_local_task_dir(resource_name, app_name, time_stamp)))

                self.workers.append({
                    "task_id": task_id,
                    "pid": os.getpid(),
                    "start_time": datetime.datetime.today(),
                    "process": _FakeProcess(),
                })

                _start_the_task_step(
                    resource_name, app_name, time_stamp, self.ResultsQueue, 0, fails_to_submit_to_the_queue)
                self.dbCon.commit()
                continue

            if len(self.workers) >= self.maxTaskHandlers:
                # all workers are busy skipping the
                return

            (task_id, resource_name, app_name, time_stamp, fatal_errors_count, fails_to_submit_to_the_queue) = row
            log.info("Working on:\n\t%s" % (akrr_task.get_local_task_dir(resource_name, app_name, time_stamp)))
            try:
                p = multiprocessing.Process(
                    target=_start_the_task_step,
                    args=(resource_name, app_name, time_stamp, self.ResultsQueue, 0, fails_to_submit_to_the_queue))
                p.start()
                pid = p.pid
                self.dbCur.execute('''UPDATE active_tasks SET task_lock=%s WHERE task_id=%s ;''', (pid, task_id))

                self.workers.append({
                    "task_id": task_id,
                    "pid": pid,
                    "start_time": datetime.datetime.today(),
                    "process": p,
                })

                i_tasks_send += 1
            except Exception as e:
                log.exception("Exception occurred during process start for next step execution")
                log.log_traceback(str(e))
                self.add_fatal_errors_for_task_count(task_id)

        if i_tasks_send > 0:
            self.dbCon.commit()

    def run_active_tasks__check_the_step(self):
        """
        check the task's step state
        """
        # Get all tasks which should be started

        i_worker = 0
        init_workers_num = len(self.workers)
        workers_num = len(self.workers)
        if workers_num == 0:
            return

        while i_worker < workers_num:
            p = self.workers[i_worker]['process']
            task_id = self.workers[i_worker]['task_id']
            pid = self.workers[i_worker]['pid']

            self.dbCur.execute('''SELECT fatal_errors_count,fails_to_submit_to_the_queue FROM active_tasks
                WHERE task_id=%s;''', (task_id,))
            (fatal_errors_count, fails_to_submit_to_the_queue) = self.dbCur.fetchall()[0]

            while not self.ResultsQueue.empty():
                r = self.ResultsQueue.get()
                self.Results[r['pid']] = r

            p.join(0.5)

            if p.is_alive():
                dt = datetime.datetime.today() - self.workers[i_worker]['start_time']
                if dt > self.max_wall_time_for_task_handlers:
                    p.terminate()  # will handle it next round
                i_worker += 1
                continue

            if p.exitcode == -signal.SIGTERM:
                # process the case when process was terminated
                dt = datetime.datetime.today() - self.workers[i_worker]['start_time']
                if dt > self.max_wall_time_for_task_handlers:
                    # 1) exceed the max time (the process, not the real task on remote machine)
                    status = "Task handler process was terminated."
                    status_info = "The task handler process was terminated probably due to overtime."
                    repeat_in = self.repeat_after_forcible_termination
                    fatal_errors_count += 1
                else:
                    # 2) the process was killed by system or by user
                    status = "Task handler process was terminated."
                    status_info = "The task handler process was terminated externally."
                    repeat_in = self.repeat_after_forcible_termination
                    fatal_errors_count += 1
            else:
                # process normal exit of process
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
                    status_info = "the process was finished but results was not sent. " \
                                  "At this point treat it as forcibly terminated"
                    repeat_in = self.repeat_after_forcible_termination
                    fatal_errors_count += 1
                else:
                    r = self.Results[pid]
                    status = copy.deepcopy(r['status'])
                    status_info = copy.deepcopy(r['status_info'])
                    repeat_in = copy.deepcopy(r['repeat_in'])
                    fatal_errors_count += r['fatal_errors_count']
                    fails_to_submit_to_the_queue = r['fails_to_submit_to_the_queue']
                    del self.Results[pid]

            time_now = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
            if fatal_errors_count > self.max_fatal_errors_for_task:
                # if too much errors terminate the execution
                repeat_in = None
                log.error("Number of errors exceeded allowed maximum and task was terminated.")
                self.dbCon.commit()
                self.dbCon.commit()
                self.dbCur.execute(
                    '''SELECT resource,app,datetime_stamp FROM active_tasks WHERE task_id=%s;''', (task_id,))
                (resource, app, datetime_stamp) = self.dbCur.fetchone()
                th = akrr_task.get_task_handler(resource, app, datetime_stamp)
                th.status = "Error: Number of errors exceeded allowed maximum and task was terminated." + th.status
                th.ReportFormat = "Error"
                th.process_results()
                if th.push_to_db is not None:
                    log.error("Can not push to DB")
                akrr_task.dump_task_handler(th)
                status = copy.deepcopy(th.status)
                status_info = copy.deepcopy(th.status_info)
                del th

            # Read log

            # Update error counters on DB
            self.dbCur.execute('''UPDATE active_tasks
                SET fatal_errors_count=%s,fails_to_submit_to_the_queue=%s
                WHERE task_id=%s ;''', (fatal_errors_count, fails_to_submit_to_the_queue, task_id))
            self.dbCon.commit()
            # update DB
            if status == "Done" or repeat_in is None:
                # we need to remove it from active_tasks and add to completed_tasks
                resource = None
                app = None
                datetime_stamp = None
                try:
                    self.dbCon.commit()
                    self.dbCon.commit()
                    self.dbCur.execute(
                        '''SELECT status_update_time,status,status_info,time_to_start,repeat_in,resource,app,
                            datetime_stamp,time_activated,
                            time_submitted_to_queue,resource_param,app_param,task_param,group_id,
                            fatal_errors_count,fails_to_submit_to_the_queue,
                            parent_task_id 
                        FROM active_tasks
                        WHERE task_id=%s;''', (task_id,))
                    (status_update_time, status_prev, status_info_prev, time_to_start, repeat_in, resource, app,
                     datetime_stamp, time_activated, time_submitted_to_queue, resource_param, app_param, task_param,
                     group_id, fatal_errors_count, fails_to_submit_to_the_queue, parent_task_id) = self.dbCur.fetchone()

                    self.dbCur.execute(
                        '''INSERT INTO completed_tasks
                           (task_id,time_finished,status,status_info,time_to_start,repeat_in,
                           resource,app,datetime_stamp,
                           time_activated,time_submitted_to_queue,resource_param,app_param,task_param,
                           group_id,fatal_errors_count,fails_to_submit_to_the_queue,parent_task_id)
                           VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);''',
                        (task_id, status_update_time, status, status_info, time_to_start, repeat_in,
                         resource, app, datetime_stamp, time_activated, time_submitted_to_queue,
                         resource_param, app_param, task_param, group_id, fatal_errors_count,
                         fails_to_submit_to_the_queue, parent_task_id))
                    self.dbCur.execute('''DELETE FROM active_tasks WHERE task_id=%s;''', (task_id,))
                except Exception as e:
                    log.exception(
                        "Exception occurred during moving task record from active_tasks to completed_tasks table")
                    log.log_traceback(str(e))
                    self.dbCon.rollback()
                    self.dbCon.rollback()

                    fatal_errors_count += 1
                    self.dbCur.execute('''UPDATE active_tasks
                        SET task_lock=0,fatal_errors_count=%s
                        WHERE task_id=%s ;''', (fatal_errors_count, task_id))

                self.dbCon.commit()
                self.dbCon.commit()

                # now the last thing moving the directory
                task_dir = os.path.join(cfg.data_dir, resource, app, datetime_stamp)
                comp_tasks_dir = os.path.join(cfg.completed_tasks_dir, resource, app)
                log.info(
                    "Task is completed. Moving its' working directory\n" +
                    "\tfrom %s" % task_dir + "\n" +
                    "\tto %s" % (os.path.join(comp_tasks_dir, datetime_stamp))
                )
                import shutil
                shutil.move(task_dir, comp_tasks_dir)

            else:
                # we need to resubmit and update
                next_round = datetime.datetime.today() + repeat_in
                next_round = next_round.strftime("%Y-%m-%d %H:%M:%S")
                self.dbCur.execute('''UPDATE active_tasks
                    SET task_lock=0, status=%s,status_info=%s,next_check_time=%s,status_update_time=%s
                    WHERE task_id=%s ;''', (status, status_info, next_round, time_now, task_id))
                self.dbCon.commit()
            # remove worker from list

            self.workers.pop(i_worker)
            workers_num = len(self.workers)
        if init_workers_num != len(self.workers):
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
        def sigterm_handler(signum, _):
            log.info("Received termination signal. Actual signal is %s." % signum)
            log.info("Going to clean up ...")
            self.bRunScheduledTasks = False
            self.bRunActiveTasks_StartTheStep = False
            self.bRunActiveTasks_CheckTheStep = True
            self.LastOpSignal = "SEGTERM"

        def no_new_tasks(_signum, _):
            log.info("Activation of new tasks is postponed.")
            self.bRunScheduledTasks = False
            self.bRunActiveTasks_StartTheStep = False
            self.bRunActiveTasks_CheckTheStep = True
            self.LastOpSignal = "Run"

        def new_tasks_on(_signum, _):
            log.info("Activation of new tasks is allowed.")
            self.bRunScheduledTasks = True
            self.bRunActiveTasks_StartTheStep = True
            self.bRunActiveTasks_CheckTheStep = True
            self.LastOpSignal = "Run"

        signal.signal(signal.SIGTERM, sigterm_handler)
        signal.signal(signal.SIGINT, sigterm_handler)
        signal.signal(signal.SIGUSR1, no_new_tasks)
        signal.signal(signal.SIGUSR2, new_tasks_on)

        # start rest api
        from . import akrrrestapi
        log.info("Starting REST-API Service")
        self.proc_queue_to_master = multiprocessing.Queue(1)
        self.proc_queue_from_master = multiprocessing.Queue(1)
        self.restapi_proc = multiprocessing.Process(target=akrrrestapi.start_rest_api,
                                                    args=(self.proc_queue_to_master, self.proc_queue_from_master))
        self.restapi_proc.start()

        # go to the loop
        self.run_loop()

        # reset signal
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        if os.path.isfile(os.path.join(cfg.data_dir, "akrr.pid")):
            os.remove(os.path.join(cfg.data_dir, "akrr.pid"))

    def check_db_and_reconnect(self):
        """check the db connection and reconnect"""
        attempts_to_reconnect = 0
        while True:
            db_connected = False
            try:
                self.dbCur.execute('''SELECT * FROM  `resources`  ''')
                self.dbCur.fetchall()
                db_connected = True
            except Exception as e:
                log.exception("Exception occurred during DB connection checking.")
                log.log_traceback(str(e))

            if db_connected:
                return True

            if attempts_to_reconnect > 3 * 360:
                log.error("Have tried %d to reconnect to DB and failed" % attempts_to_reconnect)
                import MySQLdb
                raise MySQLdb.MySQLError("Have tried %d to reconnect to DB and failed" % attempts_to_reconnect)

            if attempts_to_reconnect > 0:
                log.warning(
                    "Have tried %d to reconnect to DB and failed. Will wait for 10 sec and tried again\n" %
                    attempts_to_reconnect)
                time.sleep(10)

            log.info("Trying to reconnect to DB.")
            self.dbCon, self.dbCur = akrr.db.get_akrr_db()
            attempts_to_reconnect += 1

    def run_loop(self):
        log.info("#" * 100)
        log.info("Got into the running loop on " + datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"))
        log.info("#" * 100 + "\n")
        num_of_critical_fails = 0
        while True:
            try:
                self.check_db_and_reconnect()

                if self.bRunScheduledTasks:
                    self.run_scheduled_tasks()
                if self.bRunActiveTasks_StartTheStep:
                    self.run_active_tasks__start_the_step()
                if self.bRunActiveTasks_CheckTheStep:
                    self.run_active_tasks__check_the_step()

                self.run_rest_api_requests()

                if self.LastOpSignal == "SEGTERM":
                    log.info("Trying to shut down REST API...")
                    if self.restapi_proc.is_alive():
                        self.restapi_proc.terminate()
                    if self.restapi_proc.is_alive():
                        log.info("REST API PID %s", self.restapi_proc.pid)
                        os.kill(self.restapi_proc.pid, signal.SIGKILL)
                    if len(self.workers) == 0 and not self.restapi_proc.is_alive():
                        log.info(
                            "There is no active processes handling the task"
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
            except Exception as e:
                log.exception("Exception occurred in main loop!")
                log.log_traceback(str(e))
                num_of_critical_fails += 1
                time.sleep(10)
                if num_of_critical_fails > 360:
                    log.error("Too many errors! Shutting down the daemon!")
                    if self.restapi_proc.is_alive():
                        self.restapi_proc.terminate()
                    if self.restapi_proc.is_alive():
                        log.debug("REST API PID", self.restapi_proc.pid)
                        os.kill(self.restapi_proc.pid, signal.SIGKILL)
                    for w in self.workers:
                        if w['p'].is_alive():
                            w['p'].terminate()
                        if w['p'].is_alive():
                            os.kill(w['p'].pid, signal.SIGKILL)
                    exit(1)

    def run_rest_api_requests(self):
        """Execute REST API requests which can not be handled without interruptions"""
        if self.restapi_proc is None:
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
            log.exception(str(e))
        self.proc_queue_from_master.put(response)

    def monitor(self):
        while True:
            sys.stdout.write("\x1b[J\x1b[2J\x1b[H")
            sys.stdout.flush()

            pid = get_daemon_pid()
            if pid is None:
                log.info("AKRR Server is down")
            else:
                log.info("AKRR Server is up and it's PID is %d" % pid)

            log.info("Scheduled Tasks (%s) :" % (str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"))))
            self.dbCur.execute('''SELECT * FROM scheduled_tasks ORDER BY time_to_start ASC;''')
            tasks = self.dbCur.fetchall()
            for row in tasks:
                log.info(row)
                log.info("Active Tasks (%s) :" % (str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"))))

            self.dbCur.execute('''SELECT task_id,resource,app,datetime_stamp,next_check_time,task_lock,status,
            status_info,status_update_time
                FROM active_tasks
                ORDER BY next_check_time,time_to_start ASC;''')

            tasks = self.dbCur.fetchall()
            for row in tasks:
                log.info(row)

            log.info("Completed Tasks (%s) :" % (str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"))))

            self.dbCur.execute('''SELECT task_id,resource,app,datetime_stamp,resource_param,app_param,status,
                status_info,time_finished
                FROM completed_tasks
                ORDER BY time_finished DESC;''')

            tasks = self.dbCur.fetchall()
            for row in tasks[:3]:
                log.info(row)
            time.sleep(1)

    def check_status(self):
        """like monitor only print once"""
        pid = get_daemon_pid()
        if pid is None:
            log.info("AKRR Server is down")
            return
        else:
            log.info("AKRR Server is up and it's PID is %d" % pid)

        from .task_api import task_list

        task_list()

        msg = "Completed Tasks (%s) :\n" % (str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")))

        self.dbCur.execute(
            '''SELECT task_id,resource,app,datetime_stamp,resource_param,app_param,status,status_info,time_finished
            FROM completed_tasks
            ORDER BY time_finished DESC LIMIT 5;''')

        tasks = self.dbCur.fetchall()
        msg = msg + "\n".join([str(row) for row in tasks])
        log.info(msg)

        # Tasks completed with errors
        self.dbCur.execute(
            '''SELECT task_id,time_finished,status, status_info,time_to_start,datetime_stamp,repeat_in,resource,app,
            resource_param,app_param,task_param,group_id
            FROM completed_tasks
            ORDER BY time_finished  DESC LIMIT 5;''')
        tasks = self.dbCur.fetchall()

        if len(tasks) == 0:
            log.info("\nThere were no tasks completed with errors.")
        else:
            log.info("\nTasks completed with errors (last %d):" % (len(tasks)))
            for row in tasks:
                (task_id, time_finished, status, status_info, time_to_start, datetime_stamp, repeat_in, resource, app,
                 resource_param, app_param, task_param, group_id) = row
                if re.match("ERROR:", status, re.M):
                    task_dir = akrr_task.get_local_task_dir(resource, app, datetime_stamp, False)
                    log.info("Done with errors: %s %5d %s\n" % (time_finished, task_id, task_dir), resource_param,
                             app_param, task_param, group_id, "\n", status, "\n", status_info)

    def reprocess_completed_tasks(self, resource, appkernel, time_start, time_end, verbose=False):
        """
        reprocess the output from Completed task one more time with hope that new task handlers have a
        better implementation of error handling
        """

        log.info("""Reprocess the output from Completed task one more time with hope that new task handlers 
        have a better implementation of error handling""")
        log.info("Current time: %s" % (str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"))))
        log.info("Resource:", resource)
        log.info("Application kernel:", appkernel)
        if time_start is not None and time_end is not None:
            log.info("Time frame: from ", time_start, "till", time_end)
        if time_start is None and time_end is not None:
            log.info("Time frame: till", time_end)
        if time_start is not None and time_end is None:
            log.info("Time frame: from ", time_start)

        sql_quote = "SELECT task_id,time_finished,status, status_info,time_to_start,datetime_stamp,repeat_in," \
                    "resource,app,resource_param,app_param,task_param,group_id" \
                    "FROM completed_tasks\n"
        cond = []
        if resource is not None:
            cond.append("resource LIKE \"" + resource + "\"\n")
        if appkernel is not None:
            cond.append("app LIKE \"" + appkernel + "\"\n")
        if time_start is not None:
            cond.append("time_finished >= \"" + time_start + "\"\n")
        if time_end is not None:
            cond.append("time_finished <= \"" + time_end + "\"\n")
        if len(cond) > 0:
            sql_quote += "WHERE\n" + " AND ".join(cond)
        sql_quote += "ORDER BY task_id ASC;"

        self.dbCur.execute(sql_quote)

        tasks = self.dbCur.fetchall()

        db, cur = akrr.db.get_akrr_db()
        for row in tasks:
            (task_id, time_finished, status, status_info, time_to_start, datetime_stamp, repeat_in, resource, app,
             resource_param, app_param, task_param, group_id) = row
            task_dir = akrr_task.get_local_task_dir(resource, app, datetime_stamp, False)
            if verbose:
                log.info("task_id:  %-10d     started:      %s    finished: %s    group_id: %s" % (
                         task_id, time_to_start, time_finished, group_id))
                log.info("resource: %-14s application: %-40s timestamp: %s" % (resource, app, datetime_stamp))
                log.info("resource_param: %s    app_param: %s    task_param: %s    " % (
                         resource_param, app_param, task_param))
                log.info("TaskDir:", task_dir)
                log.info("-" * 120)
                log.info("status: %s" % status)

            # Get All States
            ths = []

            proc_task_dir = os.path.join(task_dir, 'proc')
            task_states = []
            for f in os.listdir(proc_task_dir):
                if re.match("(\d+).st", f, 0) is not None:
                    task_states.append(f)
            task_states = sorted(task_states)
            for task_state in task_states:
                pickle_filename = os.path.join(proc_task_dir, task_state)
                th = akrr_task.get_task_handler_from_pkl(pickle_filename)
                th.statefilename = task_state
                th.set_dir_names(cfg.completed_tasks_dir)

                ths.append(th)

            ths[-1].process_results()
            ths[-1].push_to_db_raw(cur, task_id, time_finished)

            if re.match("ERROR:", ths[-1].status, re.M):
                log.info("Done with errors:", task_dir, ths[-1].status)
            if ths[-1].status != status or ths[-1].status_info != status_info:
                log.info("status changed")
                log.info(status)
                log.info(ths[-1].status)
                self.dbCur.execute('''UPDATE completed_tasks
                    SET status=%s,status_info=%s
                    WHERE task_id=%s ;''', (ths[-1].status, ths[-1].status_info, task_id))
                self.dbCon.commit()
        db.commit()
        cur.close()
        log.info("Reprocessing complete")

    def error_analysis__task(self, task_id, resource, app):
        # Get applicable reg_exp
        print(task_id, resource, app)

        # Get appstdout,stderr,stdout
        self.dbCur.execute('''SELECT appstdout,stderr,stdout
            FROM akrr_errmsg
            WHERE task_id=%s;''', (task_id,))

        rows = self.dbCur.fetchall()

        appstdout, stderr, stdout = (None, None, None)
        if len(rows) > 0:
            appstdout, stderr, stdout = rows[0]

        # Get akrr_status_info and  akrr_status
        self.dbCur.execute('''SELECT status,status_info
            FROM completed_tasks
            WHERE task_id=%s;''', (task_id,))
        rows = self.dbCur.fetchall()
        akrr_status, akrr_status_info = (None, None)
        if len(rows) > 0:
            akrr_status, akrr_status_info = rows[0]

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
            ['akrr_status_info', akrr_status_info],
            ['akrr_status', akrr_status],
        ]
        # apply reg. exp.
        rslt = None
        for reg_exp_id, reg_exp, reg_exp_opt, source in raw:
            source = source.split(',')
            for stc_name, stc in strings_to_comp:
                if (source == "*" or source.count(stc_name) > 0) and stc is not None:
                    rslt = re.search(reg_exp, stc, eval(reg_exp_opt))
                    if rslt is not None:
                        rslt = [rslt, stc_name, reg_exp_id, reg_exp, reg_exp_opt]
                        break
            if rslt is not None:
                break
        # push results to db
        if rslt is not None:
            regres, stc_name, reg_exp_id, reg_exp, reg_exp_opt = rslt
            log.info("\treg_exp_id=", reg_exp_id)
            log.info("\treg_exp=", reg_exp)
            log.info("\tfound_in=", stc_name)
            self.dbCur.execute('''UPDATE  akrr_errmsg
            SET err_regexp_id=%s
            WHERE task_id=%s;''', (reg_exp_id, task_id))
        else:
            log.error("\tUnknown Error")
            self.dbCur.execute('''UPDATE  akrr_errmsg
            SET err_regexp_id=%s
            WHERE task_id=%s;''', (1000, task_id))
        self.dbCon.commit()

    def error_analysis(self, date_from, date_to):
        """
        reprocess the output from Completed task one more time with hope that new task handlers have a better
        implementation of error handling
        """

        log.info("""Reprocess the output from Completed task""")
        log.info("Time: %s" % (str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"))))

        log.info("Analysing period:", date_from, date_to)
        self.dbCur.execute('''SELECT instance_id,resource,reporter
            FROM akrr_xdmod_instanceinfo
            WHERE status=0 AND collected >= %s AND collected < %s
            ORDER BY collected ASC;''', (date_from, date_to))

        tasks = self.dbCur.fetchall()
        log.info("Total number of task to process:", len(tasks))
        for raw in tasks:
            task_id, resource, app = raw
            self.error_analysis__task(task_id, resource, app)
            log.info("Done")

    def add_task_noraise(self, time_to_start, repeat_in, resource, app,
                         resource_param="{}", app_param="{}", task_param="{}",
                         group_id="None", parent_task_id=None):
        """
        Add task to schedule, do not raise exception
        """
        try:
            return self.add_task(time_to_start, repeat_in, resource, app, resource_param, app_param, task_param,
                                 group_id, parent_task_id)
        except Exception as e:
            log.exception("Exception occurred during add_task_noraise")
            log.log_traceback(str(e))
            return None

    def add_task(self,
                 time_to_start: Union[None, str, datetime.datetime], repeat_in: Union[None, str],
                 resource, app, resource_param,
                 app_param, task_param,
                 group_id, parent_task_id, dry_run=False):
        """Check the format and add task to schedule"""
        log.info(">" * 100)
        log.info("Adding new task")

        # determine timeToStart
        if time_to_start is None or time_to_start == "":
            # i.e. start now
            time_to_start = datetime.datetime.today()
        elif isinstance(time_to_start, datetime.datetime):
            # if got datetime
            time_to_start = copy.deepcopy(time_to_start)
        else:
            # if got string
            time_to_start = akrr.util.time.get_datetime_time_to_start(time_to_start)

        # determine repeat_in
        repeat_in = akrr.util.time.get_formatted_repeat_in(repeat_in)

        # check if resource exists
        cfg.find_resource_by_name(resource)
        # check if app exists
        cfg.find_app_by_name(app)
        # determine repeatIn
        log.info(
            "New task:\n\t" +
            "Starting time: %s\n\t" % time_to_start.strftime("%Y-%m-%d %H:%M:%S") +
            "Repeating period: %s\n\t" % repeat_in +
            "Resource: %s\n\t" % resource +
            "Resource parameters: %s\n\t" % resource_param +
            "Application kernel: %s\n\t" % app +
            "Application kernel parameters: %s\n\t" % app_param +
            "Task parameters: %s\n" % task_param
        )
        task_id = None
        if not dry_run:
            self.dbCur.execute(
                '''INSERT INTO scheduled_tasks (time_to_start,repeat_in,resource,app,
                resource_param,app_param,task_param,group_id,parent_task_id)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)''', (
                 time_to_start.strftime("%Y-%m-%d %H:%M:%S"), repeat_in, resource, app, resource_param, app_param,
                 task_param, group_id, parent_task_id))
            task_id = self.dbCur.lastrowid

            self.dbCon.commit()
            if parent_task_id is None:
                self.dbCur.execute("""UPDATE scheduled_tasks
                        SET parent_task_id=%s
                        WHERE task_id=%s""",
                                   (task_id, task_id))
                self.dbCon.commit()

        log.info("task id: %s", task_id)
        log.info("<" * 120)
        return task_id


def validate_task_parameters(k, v):
    """
    validate value of task variable, reformat if needed/possible
    raise error if value is incorrect. Return value or reformatted value
    """
    if k == "repeat_in":
        v = akrr.util.time.get_formatted_repeat_in(v, raise_on_fail=True)

    if k == "time_to_start":
        v = v.strip().strip('"').strip("'")
        v = akrr.util.time.get_formatted_time_to_start(v)
        if v is None:
            raise ValueError('Unknown format for time_to_start')

    if k == 'task_param' or k == 'resource_param' or k == 'app_param':
        try:
            v2 = eval(v)
        except Exception:
            raise ValueError('Unknown format for ' + k)
        if not isinstance(v2, dict):
            raise ValueError('Unknown format for ' + k + '. Must be dict.')

    if k == 'resource_param':
        v2 = eval(v)
        if 'nnodes' not in v2:
            raise ValueError('nnodes must be present in ' + k)
        if not isinstance(v2['nnodes'], int):
            raise ValueError("incorrect format for resource_param['nnodes'] must be integer")
    if k == "resource":
        try:
            cfg.find_resource_by_name(v)
        except Exception:
            log.exception("Exception occurred during resource record searching.")
            raise ValueError('Unknown resource: ' + v)
    if k == "app":
        try:
            cfg.find_app_by_name(v)
        except Exception:
            log.exception("Exception occurred during app kernel; record searching.")
            raise ValueError('Unknown application kernel: ' + v)
    if k == "next_check_time":
        v = v.strip().strip('"').strip("'")
        v = akrr.util.time.get_formatted_time_to_start(v)
        if v is None:
            raise ValueError('Unknown format for next_check_time')
    return v


def delete_task(task_id, remove_from_scheduled_queue=True, remove_from_active_queue=True, remove_derived_task=True):
    """
    remove the task from AKRR server
    
    remove_from_scheduled_queue=True and remove_from_active_queue=False and remove_derived_task=False
    remove only from scheduled queue
    
    remove_from_scheduled_queue=False and remove_from_active_queue=True and remove_derived_task=False
    remove only from active queue
    
    remove_from_scheduled_queue=True and remove_from_active_queue=True and remove_derived_task=False
    remove from scheduled or active queue
    
    remove_from_scheduled_queue=True and remove_from_active_queue=True and remove_derived_task=True
    remove this and all derivative tasks from scheduled or active queue
    """
    db, cur = akrr.db.get_akrr_db(True)
    cur.execute('''SELECT * FROM scheduled_tasks WHERE task_id=%s''', (task_id,))
    possible_task = cur.fetchall()

    scheduled_task = None
    active_task = None
    complete_task = None

    if len(possible_task) == 1:
        # task still in scheduled_tasks queue
        scheduled_task = possible_task[0]
    else:
        # task might be in active_tasks queue
        cur.execute('''SELECT * FROM active_tasks
            WHERE task_id=%s''', (task_id,))
        possible_task = cur.fetchall()

        if len(possible_task) == 1:
            active_task = possible_task[0]
        else:
            # task might be complete_tasks
            cur.execute('''SELECT * FROM completed_tasks
                WHERE task_id=%s''', (task_id,))
            possible_task = cur.fetchall()
            if len(possible_task) == 1:
                complete_task = possible_task[0]
            else:
                raise ValueError("""Task %d is not in queue""" % task_id)

    if remove_from_scheduled_queue and scheduled_task is not None:
        cur.execute('''DELETE FROM scheduled_tasks
                WHERE task_id=%s;''', (task_id,))
        db.commit()

    if remove_from_active_queue and active_task is not None:
        log.info("Trying to remove task from active_tasks")
        t0 = datetime.datetime.now()
        while active_task['task_lock'] != 0:
            # i.e. one of child process is working on this task, will wait till it finished
            if akrr_scheduler is not None:
                # i.e. it is master
                akrr_scheduler.runActiveTasks_CheckTheStep()

            cur.execute('''SELECT * FROM active_tasks
                WHERE task_id=%s''', (task_id,))
            active_task = cur.fetchone()
            if t0 - datetime.datetime.now() > datetime.timedelta(seconds=120):
                raise Exception("child process handling subtask for too long")

        # get task handler
        th = akrr_task.get_task_handler(active_task['resource'], active_task['app'], active_task['datetime_stamp'])

        can_be_safely_removed = th.terminate()

        if can_be_safely_removed:
            log.info("The task can be safely removed")
            # remove from DB
            cur.execute('''DELETE FROM active_tasks WHERE task_id=%s;''', (task_id,))
            db.commit()
            # remove from local disk
            th.delete_remote_folder()
            th.delete_local_folder()
        else:
            raise Exception("Task can NOT be remove safely. Unimplemented status:" + active_task['status'])

    if remove_derived_task:
        # find derived tasks
        task = scheduled_task
        if task is None:
            task = active_task
        if task is None:
            task = complete_task
        if task['parent_task_id'] is not None:
            task_id = task['task_id']
            tasks_to_delete = []

            if remove_from_scheduled_queue:
                cur.execute('''SELECT * FROM scheduled_tasks WHERE parent_task_id=%s''', (task_id,))
                possible_tasks = cur.fetchall()

                for possible_task in possible_tasks:
                    if possible_task['task_id'] > task_id:
                        tasks_to_delete.append(possible_task['task_id'])

            if remove_from_active_queue:
                cur.execute('''SELECT * FROM active_tasks WHERE parent_task_id=%s''', (task_id,))
                possible_tasks = cur.fetchall()

                for possible_task in possible_tasks:
                    if possible_task['task_id'] > task_id:
                        tasks_to_delete.append(possible_task['task_id'])

            for task_to_delete in tasks_to_delete:
                delete_task(task_to_delete, remove_from_scheduled_queue=remove_from_scheduled_queue,
                            remove_from_active_queue=remove_from_active_queue, remove_derived_task=False)

    cur.close()
    db.close()
    return


def update_task_parameters(task_id, new_param, update_derived_task=True):
    """
    update task parameters
    """
    log.info("Akrr Update Task Parameters: %r" % task_id)

    db, cur = akrr.db.get_akrr_db(True)
    cur.execute('''SELECT * FROM scheduled_tasks
            WHERE task_id=%s''', (task_id,))
    possible_task = cur.fetchall()

    scheduled_task = None
    active_task = None
    complete_task = None

    log.info("Length of Possible Tasks: %r" % len(possible_task))
    if len(possible_task) == 1:
        # task still in scheduled_tasks queue
        scheduled_task = possible_task[0]
    else:
        # task might be in active_tasks queue
        cur.execute('''SELECT * FROM active_tasks
            WHERE task_id=%s''', (task_id,))
        possible_task = cur.fetchall()

        if len(possible_task) == 1:
            active_task = possible_task[0]
        else:
            # task might be complete_tasks
            cur.execute('''SELECT * FROM completed_tasks
                WHERE task_id=%s''', (task_id,))
            possible_task = cur.fetchall()
            if len(possible_task) == 1:
                complete_task = possible_task[0]
            else:
                raise IOError("""Task %d is not in queue""" % task_id)

    if scheduled_task is not None:
        possible_keys_to_change = list(scheduled_task.keys())
        possible_keys_to_change.remove('task_id')
        possible_keys_to_change.remove('parent_task_id')
        possible_keys_to_change.remove('app')
        possible_keys_to_change.remove('resource')

        log.info("Scheduled Task Keys: %r" % (list(scheduled_task.keys()),))
        log.info("Possible Keys: %r" % (possible_keys_to_change,))
        log.info("New Params: %r " % (new_param,))
        # pack mysql update
        update_set_var = []
        update_set_value = []
        for k in new_param:
            if k in possible_keys_to_change:
                update_set_var.append(k + "=%s")
                update_set_value.append(validate_task_parameters(k, new_param[k]))
            else:
                raise IOError('Can not update %s' % k)

        update_set_value.append(scheduled_task['task_id'])

        if len(update_set_var) > 0:
            # update the db
            cur.execute('UPDATE scheduled_tasks SET ' + ", ".join(update_set_var) + " WHERE task_id=%s",
                        tuple(update_set_value))
            db.commit()
    else:
        if not update_derived_task:
            raise IOError('Can not update task because it left scheduled_task queue')

    if update_derived_task and scheduled_task is None:
        # find derived tasks
        task = scheduled_task
        if task is None:
            task = active_task
        if task is None:
            task = complete_task

        if task['parent_task_id'] is not None:
            task_id = task['task_id']
            tasks_to_update = []

            cur.execute('''SELECT * FROM scheduled_tasks
                WHERE parent_task_id=%s''', (task_id,))
            possible_tasks = cur.fetchall()

            for possible_task in possible_tasks:
                if possible_task['task_id'] > task_id:
                    tasks_to_update.append(possible_task)

            for task_to_update in tasks_to_update:
                update_task_parameters(task_to_update['task_id'], new_param, update_derived_task=False)
        else:
            raise IOError('Can not update task because it left scheduled_task queue')

    cur.close()
    db.close()
    return


def get_daemon_pid(delete_pid_file_if_daemon_down=False):
    """Return the PID of AKRR server"""
    from akrr.util import pid_alive
    pid = None
    if os.path.isfile(os.path.join(cfg.data_dir, "akrr.pid")):
        # print "Read process pid from",os.path.join(akrr.data_dir,"akrr.pid")

        fin = open(os.path.join(cfg.data_dir, "akrr.pid"), "r")
        lines = fin.readlines()
        pid = int(lines[0])
        fin.close()

        # Check For the existence of a unix pid
        if pid_alive(pid):
            try:
                fin = open("/proc/%d/cmdline" % pid, 'r')
                cmd = fin.read()
                fin.close()

                if cmd.count('akrr') and cmd.count('daemon') and cmd.count('start'):
                    return pid
            except Exception as e:
                log.log_traceback(str(e))
        else:
            # if here means that previous session was crushed
            if delete_pid_file_if_daemon_down:
                log.warning("WARNING:File %s exists meaning that the previous execution was finished incorrectly."
                            "Removing pid file." %
                            (os.path.join(cfg.data_dir, "akrr.pid")))
                os.remove(os.path.join(cfg.data_dir, "akrr.pid"))
                return None
            else:
                raise IOError("File %s exists meaning that the previous execution was finished incorrectly." %
                              (os.path.join(cfg.data_dir, "akrr.pid")))

    return pid


redirected_filename = None
this_stdout = None
this_stderr = None


def daemon_start():
    """Start AKRR server"""
    # check if AKRR already up
    pid = get_daemon_pid(delete_pid_file_if_daemon_down=True)
    if pid is not None:
        raise AkrrError("Can not start AKRR server because another instance is already running.")

    # check if something already listening on REST API port
    restapi_host = 'localhost'
    if cfg.restapi_host != "":
        restapi_host = cfg.restapi_host
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((restapi_host, cfg.restapi_port))
    if result == 0:
        raise AkrrError(
            "Can not start AKRR server because another service listening on %s:%d!" % (restapi_host, cfg.restapi_port))

    def kill_child_processes(parent_pid, sig=signal.SIGTERM):
        ps_command = subprocess.Popen("ps -o pid --ppid %d --noheaders" % parent_pid, shell=True,
                                      stdout=subprocess.PIPE)
        ps_output = ps_command.stdout.read()
        return_code = ps_command.wait()
        assert return_code == 0, "ps command returned %d" % return_code
        for pid_str in ps_output.decode(encoding=cfg.encoding).split("\n")[:-1]:
            os.kill(int(pid_str), sig)

    # make dir for logs and check the biggest number
    if not os.path.isdir(cfg.data_dir):
        raise IOError("Directory %s does not exist or is not directory." % cfg.data_dir)
    if not os.path.isdir(os.path.join(cfg.data_dir, "srv")):
        log.info("Directory %s does not exist, creating it." % (os.path.join(cfg.data_dir, "srv")))
        os.mkdir(os.path.join(cfg.data_dir, "srv"))
    log_name = os.path.join(cfg.data_dir, "srv", datetime.datetime.today().strftime("%Y.%m.%d_%H.%M.%f") + ".log")
    while os.path.exists(log_name):
        log_name = os.path.join(cfg.data_dir, "srv", datetime.datetime.today().strftime("%Y.%m.%d_%H.%M.%f") + ".log")
    log.info("Writing logs to:\n\t%s" % log_name)
    # createDaemon
    # this was adopted with a minor changes from Chad J. Schroeder  daemonization script
    # http://code.activestate.com/recipes/278731-creating-a-daemon-the-python-way/
    # daemonization a double fork magic
    sys.stdout.flush()
    sys.stderr.flush()

    global redirected_filename, this_stdout, this_stderr
    if redirected_filename is not None:
        this_stdout.close()
        this_stderr.close()
        sys.stdout, sys.stderr = sys.__stdout__, sys.__stderr__

    try:
        pid = os.fork()
    except OSError as e:
        raise Exception("%s [%d]" % (e.strerror, e.errno))

    if pid == 0:
        # i.e. first child
        os.setsid()  # set to be session leader
        try:
            pid = os.fork()
        except OSError as e:
            raise Exception("%s [%d]" % (e.strerror, e.errno))
        if pid == 0:  # i.e. grand child
            os.setsid()  # set to be session leader
            os.chdir(cfg.data_dir)
        else:
            exit(0)  # i.e. first child is exiting here
    else:
        # read the output from daemon till find that it is in the loop
        # wait till daemon start writing logs
        if redirected_filename is not None:
            this_stdout = open(redirected_filename, 'a')
            this_stderr = open(redirected_filename, 'a')

            sys.stdout = this_stdout
            sys.stderr = this_stderr
        dt = 0.25
        t0 = time.time()
        while time.time() - t0 < 10.0 and not os.path.isfile(log_name):
            time.sleep(dt)
        if not os.path.isfile(log_name):
            log.error("AKRR Server have not start logging yet. Something is wrong! Exiting...")
            kill_child_processes(os.getpid())
            exit(1)  # i.e. parent of first child is exiting here

        log.info("following log: %s", log_name)
        logfile = open(log_name, "r")
        rest_api_up = False
        in_the_main_loop = False
        t0 = time.time()
        while time.time() - t0 < 20.0:
            line = logfile.readline()
            if len(line) != 0:
                print(line, end=' ')
                if line.count("Listening on ") > 0:
                    rest_api_up = True
                if line.count("Got into the running loop on ") > 0:
                    in_the_main_loop = True
                if rest_api_up and in_the_main_loop:
                    break
            else:
                time.sleep(dt)
        if not rest_api_up:
            log.error("AKRR REST API is not up.\n Something is wrong. Exiting...")
            kill_child_processes(os.getpid())
            exit(1)  # i.e. parent of first child is exiting here
        if not in_the_main_loop:
            log.error("AKRR Server have not reached the loop.\n Something is wrong. Exiting...")
            kill_child_processes(os.getpid())
            exit(1)  # i.e. parent of first child is exiting here

        # if here everything should be fine
        log.info("\nAKRR Server successfully reached the loop.")
        exit(0)  # i.e. parent of first child is exiting here

    # close all file descriptors
    import resource  # Resource usage information.
    maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    if maxfd == resource.RLIM_INFINITY:
        maxfd = 1024

    # Iterate through and close all file descriptors.
    for fd in range(maxfd - 1, -1, -1):
        try:
            os.close(fd)
            pass
        except OSError:  # ERROR, fd wasn't open to begin with (ignored)
            # print fd
            pass

    # Redirect the standard I/O
    # The standard I/O file descriptors are redirected to /dev/null by default.
    redirect_to = "/dev/null"
    if hasattr(os, "devnull"):
        redirect_to = os.devnull
    os.open(redirect_to, os.O_RDONLY)  # standard input (0)
    os.open(log_name, os.O_WRONLY | os.O_CREAT)  # standard output (1)
    # f2=os.open(logname, os.O_WRONLY | os.O_APPEND )    # standard output (1)
    # Duplicate standard input to standard output and standard error.
    # os.dup2(0, 1)            # standard output (1)
    os.dup2(1, 2)  # standard error (2)

    # finally
    log.info("Starting Application Remote Runner")

    global akrr_scheduler
    akrr_scheduler = AkrrDaemon()
    akrr_scheduler.run()

    # Iterate through and close all file descriptors.
    for fd in range(maxfd - 1, -1, -1):
        try:
            os.close(fd)
            pass
        except OSError:  # ERROR, fd wasn't open to begin with (ignored)
            pass
    return None


def daemon_stop():
    """Stop AKRR server"""
    from akrr.util import pid_alive
    pid = get_daemon_pid(delete_pid_file_if_daemon_down=True)
    if pid is None:
        log.warning("Can not stop AKRR server because none is running.")
        return
    log.info("Sending termination signal to AKRR server (PID: " + str(pid) + ")")
    # send a signal to terminate
    os.kill(pid, signal.SIGTERM)

    # wait till process will finished
    while pid_alive(pid):
        time.sleep(0.2)

    log.info("Stopped AKRR server (PID: " + str(pid) + ")")
    return None


def daemon_check_and_start_if_needed():
    """Check AKRR daemon, start it if needed"""
    pid = get_daemon_pid(delete_pid_file_if_daemon_down=True)
    t = str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"))

    if pid is None:
        log.info("%s: AKRR server is down will start it" % (t,))
        daemon_start()
    else:
        log.info("%s: AKRR Server is up and it's PID is %d" % (t, pid))
    return None


def daemon_start_in_debug_mode(max_task_handlers=None, redirect_task_processing_to_log_file=None):
    """
    Start daemon in debug mode, that is in foreground, debug printing, logs printed to stdout
    and with `max_task_handlers` processes for task handling (0 means main process will do the job) and
    if `redirect_task_processing_to_log_file` is set to False, task processing logs will be printed
    to stdout.
    """
    log.basicConfig(level=log.DEBUG)
    log.info("Starting Application Remote Runner")

    # check if AKRR already up
    pid = get_daemon_pid(delete_pid_file_if_daemon_down=True)
    if pid is not None:
        raise AkrrError("Can not start AKRR server because another instance is already running.")

    if max_task_handlers is not None:
        cfg.max_task_handlers = max_task_handlers

    if redirect_task_processing_to_log_file is not None:
        cfg.redirect_task_processing_to_log_file = bool(redirect_task_processing_to_log_file)

    global akrr_scheduler
    akrr_scheduler = AkrrDaemon()
    akrr_scheduler.run()
    del akrr_scheduler
