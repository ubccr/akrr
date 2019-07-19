"""
AK runs output, logs, pickels and batch jobs script manipulation
"""
import os
import re
import datetime
import shutil

from akrr.util import log, get_list_from_comma_sep_values
from akrr.util.time import time_stamp_to_datetime

_digits_dots = re.compile('^[0-9.]+$')
_digits = re.compile('^[0-9]+$')
_state_dump = re.compile('^[0-9]+\.st$')

class Archive:
    """
    Class for manipulation with AK runs output, logs, pickels and batch jobs scripts
    """
    def __init__(self, dry_run=False, comp_task_dir=None):
        self.dry_run = dry_run
        self.comp_task_dir = os.path.abspath(comp_task_dir)
        if self.comp_task_dir is None:
            import akrr.cfg
            self.comp_task_dir = akrr.cfg.completed_tasks_dir

    @staticmethod
    def get_resources_dir_list(comp_task_dir, resources):
        """get list with full path to resources directory with complete tasks"""
        resources_dir_list = []

        for resource_dir in os.listdir(comp_task_dir):
            resource_dir_fullpath = os.path.join(comp_task_dir, resource_dir)
            if not os.path.isdir(resource_dir_fullpath):
                continue
            if resources is not None and resource_dir not in resources:
                continue
            resources_dir_list.append(resource_dir_fullpath)
        return resources_dir_list

    @staticmethod
    def get_appker_dir_list(resource_dir_fullpath, appkernels):
        """get list with full path to resource/appker directory with complete tasks"""
        appkers_dir_list = []

        for appker_dir in os.listdir(resource_dir_fullpath):
            appker_dir_fullpath = os.path.join(resource_dir_fullpath, appker_dir)
            if not os.path.isdir(appker_dir_fullpath):
                continue
            if appkernels is not None and appker_dir not in appkernels:
                continue
            appkers_dir_list.append(appker_dir_fullpath)
        return appkers_dir_list

    @staticmethod
    def get_tasks_in_resource_app_dir(resource_app_dir, old_layout_only=False):
        """
        Get list of task directories in resource/appkernel directory
        """
        tasks_dir_list = []

        for task_dir in os.listdir(resource_app_dir):
            task_dir_fullpath = os.path.join(resource_app_dir, task_dir)
            if not os.path.isdir(task_dir_fullpath):
                continue
            if _digits.match(task_dir):
                if old_layout_only is False:
                    # new layout
                    # task_dir is year_dir
                    # task_dir_fullpath is year_dir_fullpath
                    for month_dir in os.listdir(task_dir_fullpath):
                        if _digits.match(month_dir) is None:
                            continue
                        month_dir_fullpath = os.path.join(task_dir_fullpath, month_dir)
                        tasks_dir_list += Archive.get_tasks_in_resource_app_dir(month_dir_fullpath)
            elif _digits_dots.match(task_dir):
                # old layout
                tasks_dir_list.append(task_dir_fullpath)
        return tasks_dir_list

    def get_tasks_dir_list(self, resources=None, appkernels=None, old_layout_only=False):
        """
        Get list of task directories
        """
        tasks_dir_list = []

        for resouce_dir in Archive.get_resources_dir_list(self.comp_task_dir, resources):
            for resource_app_dir in Archive.get_appker_dir_list(resouce_dir, appkernels):
                tasks_dir_list += Archive.get_tasks_in_resource_app_dir(resource_app_dir, old_layout_only)

        return tasks_dir_list

    def remove_tasks_state_dumps(self, days_old: int, resources=None, appkernels=None) -> None:
        """
        remove tasks state dumps
        """

        resources = get_list_from_comma_sep_values(resources)
        appkernels = get_list_from_comma_sep_values(appkernels)

        log.info("Removing tasks state dumps")
        log.debug("resources filter: " + str(resources))
        log.debug("appkernels filter: " + str(appkernels))
        log.debug("days: " + str(days_old))
        log.debug("dry_run: " + str(self.dry_run))
        log.debug("comp_task_dir: "+str(self.comp_task_dir))

        timenow = datetime.datetime.now()
        seconds_in_day = 24*3600
        count = 0
        for task_dir in self.get_tasks_dir_list(resources, appkernels):
            try:
                time_stamp = os.path.basename(task_dir)
                activate_time = time_stamp_to_datetime(time_stamp)
                days_passed = (timenow-activate_time).total_seconds()/seconds_in_day
                if days_passed < days_old:
                    continue

                proc_dir = os.path.join(task_dir, "proc")
                if not os.path.isdir(proc_dir):
                    continue

                if log.verbose:
                    print("in:", task_dir)

                for state_file in os.listdir(proc_dir):
                    if _state_dump.match(state_file) is None:
                        continue
                    if log.verbose:
                        print("    delete:", state_file)
                    state_file_fullpath = os.path.join(proc_dir, state_file)
                    count += 1
                    if not self.dry_run:
                        os.remove(state_file_fullpath)
            except:
                log.error("Cannot process: "+task_dir)
        log.info("Removed %d task state dumps" % count)

    def remove_tasks_workdir(self, days_old: int, resources=None, appkernels=None) -> None:
        """
        remove tasks state dumps
        """

        resources = get_list_from_comma_sep_values(resources)
        appkernels = get_list_from_comma_sep_values(appkernels)

        log.info("Removing tasks workdir")
        log.debug("resources filter: " + str(resources))
        log.debug("appkernels filter: " + str(appkernels))
        log.debug("days: " + str(days_old))
        log.debug("dry_run: " + str(self.dry_run))
        log.debug("comp_task_dir: "+str(self.comp_task_dir))

        timenow = datetime.datetime.now()
        seconds_in_day = 24*3600
        count = 0
        for task_dir in self.get_tasks_dir_list(resources, appkernels):
            try:
                time_stamp = os.path.basename(task_dir)
                activate_time = time_stamp_to_datetime(time_stamp)
                days_passed = (timenow-activate_time).total_seconds()/seconds_in_day
                if days_passed < days_old:
                    continue

                workdir_dir = os.path.join(task_dir, "jobfiles", "workdir")
                if not os.path.isdir(workdir_dir):
                    continue

                if log.verbose:
                    print("Found workdir:", workdir_dir)

                count += 1
                if not self.dry_run:
                    shutil.rmtree(workdir_dir)
            except:
                log.error("Cannot process: "+task_dir)
        log.info("Removed %d task workdirs" % count)

    def update_layout(self, resources=None, appkernels=None) -> None:
        """
        update resource/appkernel/task to resource/appkernel/year/month/task layout
        """

        resources = get_list_from_comma_sep_values(resources)
        appkernels = get_list_from_comma_sep_values(appkernels)

        log.info("Updating layout")
        log.debug("resources filter: " + str(resources))
        log.debug("appkernels filter: " + str(appkernels))
        log.debug("dry_run: " + str(self.dry_run))
        log.debug("comp_task_dir: "+str(self.comp_task_dir))

        timenow = datetime.datetime.now()
        seconds_in_day = 24*3600
        count = 0
        for task_dir in self.get_tasks_dir_list(resources, appkernels, old_layout_only=True):
            try:
                time_stamp = os.path.basename(task_dir)
                activate_time = time_stamp_to_datetime(time_stamp)
                year = str(activate_time.year)
                month = "%02d" % activate_time.month

                year_month_dir = os.path.join(os.path.dirname(task_dir), year, month)

                if log.verbose:
                    print("Move:", task_dir)
                    print("  to:", year_month_dir)

                count += 1
                if not self.dry_run:
                    os.makedirs(year_month_dir, exist_ok=True)
                    shutil.move(task_dir, year_month_dir)
            except:
                log.error("Cannot process: "+task_dir)
                import traceback
                traceback.print_exc()
        log.info("Moved %d task dirs" % count)


    def run(self):
        log.info("Running archiving")
        log.debug("update_dir_layout: " + str(self.update_dir_layout))
        log.debug("remove_tasks_state_dumps: " + str(self.remove_tasks_state_dumps))
        log.debug("resources: " + str(self.resources))
        log.debug("appkernels: " + str(self.appkernels))
        log.debug("days: " + str(self.days))
        log.debug("dry_run: " + str(self.dry_run))
        log.debug("comp_task_dir: "+str(self.comp_task_dir))

        if self.remove_tasks_state_dumps:
            self.do_remove_tasks_state_dumps()
