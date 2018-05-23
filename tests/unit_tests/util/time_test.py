import pytest
from datetime import datetime, timedelta, date


@pytest.mark.parametrize("program, expected", [
    ('ls', ['/usr/bin/ls', '/bin/ls']),
    ('un_existent_program', [None]),
])
def test_which(program, expected):
    from akrr.util import which
    assert which(program) in expected


@pytest.mark.parametrize("repeat_in, expected", [
    ("1-12-123 13:12:14", "1-12-123 13:12:14"),
    ("1-12-123 13:12", "1-12-123 13:12:00"),
    ("123 13:12:14", "0-00-123 13:12:14"),
    ("123 13:12", "0-00-123 13:12:00"),
    ("13:12:14", "0-00-000 13:12:14"),
    ("13:12", "0-00-000 13:12:00"),
    ("3", "0-00-003 00:00:00"),
    ("d1", None),
    ("1m", None),
    (None, None)
])
def test_get_formatted_repeat_in(repeat_in, expected):
    from akrr.util.time import get_formatted_repeat_in
    assert get_formatted_repeat_in(repeat_in) == expected


@pytest.mark.parametrize("repeat_in, expected", [
    ("1-12-123 13:12:14", None),
    ("1-12-123 13:12", None),
    ("123 13:56:14", timedelta(days=123, hours=13, minutes=56, seconds=14)),
    ("123 13:56", timedelta(days=123, hours=13, minutes=56, seconds=0)),
    ("13:56:14", timedelta(hours=13, minutes=56, seconds=14)),
    ("13:56", timedelta(hours=13, minutes=56)),
    ("3", timedelta(days=3)),
    ("d1", None),
    ("1m", None),
    (None, None)
])
def test_get_timedelta_repeat_in(repeat_in, expected):
    from akrr.util.time import get_timedelta_repeat_in
    if expected is None:
        with pytest.raises(IOError):
            get_timedelta_repeat_in(repeat_in)
    else:
        dt = get_timedelta_repeat_in(repeat_in)
        assert (dt.days, dt.seconds) == (expected.days, expected.seconds)


@pytest.mark.parametrize("time_to_start, expected", [
    ("2018-05-09 17:22:14", "2018-05-09 17:22:14"),
    ("2018-05-09 17:22", "2018-05-09 17:22:00"),
    ("18-05-09 17:22:14", "2018-05-09 17:22:14"),
    ("18-05-09 17:22", "2018-05-09 17:22:00"),
    ("2018-05-09T17:22:14", "2018-05-09 17:22:14"),
    ("2018-05-09T17:22", "2018-05-09 17:22:00"),
    ("18-05-09T17:22:14", "2018-05-09 17:22:14"),
    ("18-05-09T17:22", "2018-05-09 17:22:00"),
    ("17:22:14", date.today().strftime("%Y-%m-%d") + " 17:22:14"),
    ("17:22", date.today().strftime("%Y-%m-%d") + " 17:22:00"),
    ("1b", None),
    (None, "start_now"),
    ("", "start_now"),
    ("today", "start_now"),
    ("now", "start_now")
])
def test_get_formatted_time_to_start(time_to_start, expected):
    from akrr.util.time import get_formatted_time_to_start

    if expected == "start_now":
        dt = datetime.strptime(get_formatted_time_to_start(time_to_start), "%Y-%m-%d %H:%M:%S") - \
             datetime.today()
        assert abs(dt.total_seconds()) < 10
    else:
        assert get_formatted_time_to_start(time_to_start) == expected


date_today = date.today()


@pytest.mark.parametrize("time_to_start, expected", [
    ("2018-05-09 17:22:14", datetime(year=2018, month=5, day=9, hour=17, minute=22, second=14)),
    ("2018-05-09 17:22", datetime(year=2018, month=5, day=9, hour=17, minute=22)),
    ("18-05-09 17:22:14", datetime(year=2018, month=5, day=9, hour=17, minute=22, second=14)),
    ("18-05-09 17:22", datetime(year=2018, month=5, day=9, hour=17, minute=22)),
    ("2018-05-09", datetime(year=2018, month=5, day=9, hour=0, minute=0)),
    ("18-05-09", datetime(year=2018, month=5, day=9, hour=0, minute=0)),
    ("17:22:14", datetime(year=date_today.year, month=date_today.month, day=date_today.day,
                          hour=17, minute=22, second=14)),
    ("17:22", datetime(year=date_today.year, month=date_today.month, day=date_today.day, hour=17, minute=22)),
    ("1b", None),
    (None, "start_now"),
    ("", "start_now")
])
def test_get_datetime_time_to_start(time_to_start, expected):
    from akrr.util.time import get_datetime_time_to_start

    if expected is None:
        with pytest.raises(ValueError):
            get_datetime_time_to_start(time_to_start)
    elif expected == "start_now":
        dt = get_datetime_time_to_start(time_to_start) - datetime.today()
        assert abs(dt.total_seconds()) < 10
    else:
        assert get_datetime_time_to_start(time_to_start) == expected


@pytest.mark.parametrize("repeat_in, expect_exception, expected", [
    ("0-0-0 0:0:0", False, (0, 0, 0, 0, 0, 0)),
    ("10-12-1 99:164:23", False, (10, 12, 1, 99, 164, 23)),
    ("1012-1 99:164:23", True, None),
    (None, True, None),
])
def test_repeat_in_to_tuple(repeat_in, expect_exception, expected):
    from akrr.util.time import repeat_in_to_tuple
    if expect_exception:
        with pytest.raises(ValueError):
            repeat_in_to_tuple("1 day")
    else:
        assert repeat_in_to_tuple(repeat_in) == expected


def test_get_next_time():
    from akrr.util.time import get_next_time

    def s(t):
        return t.strftime("%Y-%m-%d %H:%M:%S")

    t0 = datetime.now() - timedelta(hours=1, minutes=5)

    assert get_next_time(s(t0), "0-0-1 0:0:0") == s(t0+timedelta(days=1))
    assert get_next_time(s(t0-timedelta(days=5)), "0-0-1 0:0:0") == s(t0+timedelta(days=1))

    assert get_next_time(s(t0), "0-0-7 0:0:0") == s(t0+timedelta(days=7))
    assert get_next_time(s(t0-timedelta(days=14)), "0-0-7 0:0:0") == s(t0+timedelta(days=7))

    assert get_next_time(s(t0), "0-0-0 6:0:0") == s(t0 + timedelta(hours=6))
    assert get_next_time(s(t0 - timedelta(hours=12)), "0-0-0 6:0:0") == s(t0 + timedelta(hours=6))
