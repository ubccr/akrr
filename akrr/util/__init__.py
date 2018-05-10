import re
import datetime


def which(program):
    """
    return full path of executable.
    If program is full path return it
    otherwise look in PATH. If still executable is not found return None.
    """
    import os

    def is_exe(file_path):
        return os.path.isfile(file_path) and os.access(file_path, os.X_OK)

    file_dir, _ = os.path.split(program)
    if file_dir:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def get_formatted_repeat_in(repeat_in):
    """
    Return  formatted repeat_in with following formatting:
    "%01d-%02d-%03d %02d:%02d:%02d" % (years,months,days,hours,minutes,seconds)
    :param repeat_in:
    :return: formatted repeat_in
    """
    repeat_in_formatted = None
    if repeat_in is None:
        return None

    repeat_in = repeat_in.strip()
    if repeat_in_formatted is None or repeat_in_formatted == '':
        match = re.match(r'^(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)$', repeat_in, 0)
        if match is not None:
            g = match.group(1, 2, 3, 4, 5, 6)
            repeat_in_formatted = "%01d-%02d-%03d %02d:%02d:%02d" % (
                int(g[0]), int(g[1]), int(g[2]), int(g[3]), int(g[4]), int(g[5]))
    if repeat_in_formatted is None:
        match = re.match(r'^(\d+)-(\d+)-(\d+) (\d+):(\d+)$', repeat_in, 0)
        if match is not None:
            g = match.group(1, 2, 3, 4, 5)
            repeat_in_formatted = "%01d-%02d-%03d %02d:%02d:%02d" % \
                                  (int(g[0]), int(g[1]), int(g[2]), int(g[3]), int(g[4]), 0)
    if repeat_in_formatted is None:
        match = re.match(r'^(\d+) (\d+):(\d+):(\d+)$', repeat_in, 0)
        if match is not None:
            g = match.group(1, 2, 3, 4)
            repeat_in_formatted = "%01d-%02d-%03d %02d:%02d:%02d" % (0, 0, int(g[0]), int(g[1]), int(g[2]), int(g[3]))
    if repeat_in_formatted is None:
        match = re.match(r'^(\d+) (\d+):(\d+)$', repeat_in, 0)
        if match is not None:
            g = match.group(1, 2, 3)
            repeat_in_formatted = "%01d-%02d-%03d %02d:%02d:%02d" % (0, 0, int(g[0]), int(g[1]), int(g[2]), 0)
    if repeat_in_formatted is None:
        match = re.match(r'^(\d+):(\d+):(\d+)$', repeat_in, 0)
        if match is not None:
            g = match.group(1, 2, 3)
            repeat_in_formatted = "%01d-%02d-%03d %02d:%02d:%02d" % (0, 0, 0, int(g[0]), int(g[1]), int(g[2]))
    if repeat_in_formatted is None:
        match = re.match(r'^(\d+):(\d+)$', repeat_in, 0)
        if match is not None:
            g = match.group(1, 2)
            repeat_in_formatted = "%01d-%02d-%03d %02d:%02d:%02d" % (0, 0, 0, int(g[0]), int(g[1]), 0)
    if repeat_in_formatted is None:
        match = re.match(r'^(\d+)$', repeat_in, 0)
        if match is not None:
            g = match.group(1)
            repeat_in_formatted = "%01d-%02d-%03d %02d:%02d:%02d" % (0, 0, int(g[0]), 0, 0, 0)
    
    return repeat_in_formatted


def get_timedelta_repeat_in(repeat_in):
    if repeat_in is None:
        raise IOError("There is no repeating period")
    repeat_in_formatted = get_formatted_repeat_in(repeat_in)
    if repeat_in_formatted is None:
        raise IOError("Incorrect data-time format for repeating period")

    # check the repeat values
    match = re.match(r'^(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)$', repeat_in_formatted, 0)
    g = match.group(1, 2, 3, 4, 5, 6)
    tao = (int(g[0]), int(g[1]), int(g[2]), int(g[3]), int(g[4]), int(g[5]))
    td = datetime.timedelta(days=tao[2], hours=tao[3], minutes=tao[4], seconds=tao[5])
    if tao[0] != 0 or tao[1] != 0:
        if tao[2] != 0 or tao[3] != 0 or tao[4] != 0 or tao[5] != 0:
            raise IOError(
                "If repeating period is calendar months or years then increment in day/hours/mins/secs should be zero.")
        td = datetime.timedelta(days=365*tao[0]+30*tao[1])
    return td


def get_formatted_time_to_start(time_to_start):
    # determine start_datetime
    start_datetime = None
    if time_to_start is None or time_to_start == "":  # i.e. start now
        start_datetime = datetime.datetime.today()

    if start_datetime is None:
        for datetime_format in ["%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%y-%m-%d %H:%M:%S", "%y-%m-%d %H:%M"]:
            try:
                start_datetime = datetime.datetime.strptime(time_to_start, datetime_format)
                break
            except ValueError:
                continue
    if start_datetime is None:
        for datetime_format in ["%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"]:
            try:
                start_datetime = datetime.datetime.strptime(
                    datetime.datetime.today().strftime("%Y-%m-%d ") + time_to_start, datetime_format)
                break
            except ValueError:
                continue

    if start_datetime is None:
        return None

    return start_datetime.strftime("%Y-%m-%d %H:%M:%S")


def get_datetime_time_to_start(time_to_start):
    time_to_start = get_formatted_time_to_start(time_to_start)
    if time_to_start is None:
        raise ValueError("Incorrect data-time format for time_to_start")
    time_to_start = datetime.datetime.strptime(time_to_start, "%Y-%m-%d %H:%M:%S")
    return time_to_start
