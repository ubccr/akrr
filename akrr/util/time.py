import datetime
import re

from typing import Optional, Tuple, Union


def to_time(time):
    """
    Converts a string of the format: HH:MI to a datetime.time object. Returns None if the string
    fails validation.

    :type time str

    :param time:
    :return: a datetime.time representation of the provided time string. None if it fails validation.
    """
    if time and isinstance(time, str) and len(time) > 0:
        parts = time.split(':')
        if len(parts) >= 2:
            hours = int(parts[0].strip())
            minutes = int(parts[1].strip())
            return datetime.time(hours, minutes)


def to_datetime(time):
    """
    converts the provided datetime.time into a datetime.datetime object.

    :type time datetime.time

    :param time: that is to be converted into datetime.time object.
    :return: datetime.datetime object representation of the provided 'time' parameter
    """
    if time and isinstance(time, datetime.time):
        return datetime.datetime.now().replace(hour=time.hour, minute=time.minute, second=0, microsecond=0)


def time_stamp_to_datetime(time_stamp: str) -> datetime.datetime:
    """
    Convert time_stamp string (%Y.%m.%d.%H.%M.%S.%f) to datatime
    """
    return datetime.datetime.strptime(time_stamp, "%Y.%m.%d.%H.%M.%S.%f")


def time_stamp_to_datetime_str(time_stamp: str) -> str:
    """
    Reformat time_stamp (%Y.%m.%d.%H.%M.%S.%f) to %Y-%m-%d %H:%M:%S
    """
    return datetime.datetime.strptime(time_stamp, "%Y.%m.%d.%H.%M.%S.%f").strftime("%Y-%m-%d %H:%M:%S")


def get_formatted_repeat_in(repeat_in: Union[None, str], raise_on_fail: bool=False):
    """
    Return  formatted repeat_in with following formatting:
    "%01d-%02d-%03d %02d:%02d:%02d" % (years,months,days,hours,minutes,seconds)
    :param repeat_in:
    :param raise_on_fail:
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

    if raise_on_fail and repeat_in_formatted is None:
        raise ValueError("Unknown repeat_in format")

    return repeat_in_formatted


def repeat_in_to_tuple(repeat_in: Optional[str]) -> Optional[Tuple[int, int, int, int, int, int]]:
    """
    return tuple with repeat_in values in following format
    (years,months,days,hours,minutes,seconds) or None
    Raises ValueError on incorrect format
    """
    if repeat_in is None:
        return None
    match = re.match(r'(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)', repeat_in, 0)
    if not match:
        raise ValueError("Unknown repeat_in format")
    else:
        g = match.group(1, 2, 3, 4, 5, 6)
        return int(g[0]), int(g[1]), int(g[2]), int(g[3]), int(g[4]), int(g[5])


def verify_repeat_in(repeat_in: Optional[str]):
    """
    Verify `repeat_in` return standardized format, if format is unknown return None
    return None if all values are zero
    """
    if repeat_in is None:
        return None

    from . import log

    try:
        tao = repeat_in_to_tuple(repeat_in)
    except ValueError:
        log.error("Unknown repeat_in format, will set it to None")
        return None

    if tao[0] == 0 and tao[1] == 0 and tao[2] == 0 and tao[3] == 0 and tao[4] == 0 and tao[5] == 0:
        log.warning("repeat_in is zero will set it to None")
        return None

    return repeat_in


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
    if time_to_start is None or time_to_start in ["", "today", "now"]:
        start_datetime = datetime.datetime.today()

    if time_to_start in ["tomorrow"]:
        start_datetime = datetime.datetime.today()+datetime.timedelta(days=1)

    if start_datetime is None:
        for datetime_format in ["%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%y-%m-%d %H:%M:%S", "%y-%m-%d %H:%M",
                                "%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S", "%y-%m-%dT%H:%M:%S", "%y-%m-%dT%H:%M",
                                "%Y-%m-%d", "%y-%m-%d"]:
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


def calculate_random_start_time(start_time, periodicity, time_start, time_end):
    """
    Calculate a new, random start time based on the provided parameters.

    :type start_time str
    :type periodicity str
    :type time_start str
    :type time_end str

    :param start_time: - a string in the format 'YYYY-MM-DD HH24:MI:SS'
    :param periodicity: a string in the format ''
    :param time_start: a string in the format 'HH24:MI'
    :param time_end: a string in the format 'HH24:MI'

    :return: a new datetime.datetime with a randomized day / time constrained by
            the provided periodicity and time_start / time_end
    """
    import random

    time_to_start = get_datetime_time_to_start(start_time).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0)
    repeat_in = get_timedelta_repeat_in(periodicity)

    if time_to_start and repeat_in:
        spans_multiple_days = repeat_in.days > 1
        if spans_multiple_days:
            chosen_day = random.randint(0, repeat_in.days)

            chosen_start_time = to_time(time_start)
            chosen_end_time = to_time(time_end)
            chosen_start_datetime = to_datetime(chosen_start_time)
            chosen_end_datetime = to_datetime(chosen_end_time)

            difference = chosen_end_datetime - chosen_start_datetime
            lower_bound = chosen_start_datetime - datetime.datetime.now().replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0)

            chosen_time = random.randint(
                lower_bound.seconds,
                difference.seconds + repeat_in.seconds)
            chosen_datetime = time_to_start + datetime.timedelta(
                days=chosen_day,
                seconds=chosen_time)
            return chosen_datetime.strftime('%Y-%m-%d %H:%M:%S')
        else:
            chosen_start_time = to_time(time_start)
            chosen_end_time = to_time(time_end)
            chosen_start_datetime = to_datetime(chosen_start_time)
            chosen_end_datetime = to_datetime(chosen_end_time)

            difference = chosen_end_datetime - chosen_start_datetime

            chosen_time = random.randint(
                chosen_start_time.second,
                difference.seconds)
            chosen_datetime = time_to_start + datetime.timedelta(
                seconds=chosen_time)
            return chosen_datetime.strftime('%Y-%m-%d %H:%M:%S')

    return start_time


def get_next_time(previous_time_to_start: str, repeat_in: str) -> str:
    """
    Calculate next time for scheduling, the return time is `previous_time_to_start`
    incremented by `repeat_in` possibly several times until it is in the future
    """
    at0 = get_datetime_time_to_start(previous_time_to_start)
    adt = get_timedelta_repeat_in(repeat_in)
    tao = repeat_in_to_tuple(repeat_in)
    current_time = datetime.datetime.now()

    if tao[0] != 0 or tao[1] != 0:
        # i.e. monthly or annually
        at1 = at0
        # schedule task only for the future
        while at1 < current_time:
            y = at1.year + tao[0]
            m = at1.month + tao[1]
            if m > 12:
                y += 1
                m -= 12
            at1 = at1.replace(year=y, month=m)
    else:
        at1 = at0 + adt
        # schedule task only for the future
        while at1 < current_time:
            at1 += adt

    return at1.strftime("%Y-%m-%d %H:%M:%S")
