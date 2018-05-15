import pytest
import datetime


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
    ("123 13:56:14", datetime.timedelta(days=123, hours=13, minutes=56, seconds=14)),
    ("123 13:56", datetime.timedelta(days=123, hours=13, minutes=56, seconds=0)),
    ("13:56:14", datetime.timedelta(hours=13, minutes=56, seconds=14)),
    ("13:56", datetime.timedelta(hours=13, minutes=56)),
    ("3", datetime.timedelta(days=3)),
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
    ("17:22:14", datetime.date.today().strftime("%Y-%m-%d") + " 17:22:14"),
    ("17:22", datetime.date.today().strftime("%Y-%m-%d") + " 17:22:00"),
    ("1b", None),
    (None, "start_now"),
    ("", "start_now")
])
def test_get_formatted_time_to_start(time_to_start, expected):
    from akrr.util.time import get_formatted_time_to_start

    if expected == "start_now":
        dt = datetime.datetime.strptime(get_formatted_time_to_start(time_to_start), "%Y-%m-%d %H:%M:%S") - \
             datetime.datetime.today()
        assert abs(dt.total_seconds()) < 10
    else:
        assert get_formatted_time_to_start(time_to_start) == expected


date_today = datetime.date.today()


@pytest.mark.parametrize("time_to_start, expected", [
    ("2018-05-09 17:22:14", datetime.datetime(year=2018, month=5, day=9, hour=17, minute=22, second=14)),
    ("2018-05-09 17:22", datetime.datetime(year=2018, month=5, day=9, hour=17, minute=22)),
    ("18-05-09 17:22:14", datetime.datetime(year=2018, month=5, day=9, hour=17, minute=22, second=14)),
    ("18-05-09 17:22", datetime.datetime(year=2018, month=5, day=9, hour=17, minute=22)),
    ("2018-05-09", datetime.datetime(year=2018, month=5, day=9, hour=0, minute=0)),
    ("18-05-09", datetime.datetime(year=2018, month=5, day=9, hour=0, minute=0)),
    ("17:22:14", datetime.datetime(year=date_today.year, month=date_today.month, day=date_today.day,
                                   hour=17, minute=22, second=14)),
    ("17:22", datetime.datetime(year=date_today.year, month=date_today.month, day=date_today.day,
                                hour=17, minute=22)),
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
        dt = get_datetime_time_to_start(time_to_start) - datetime.datetime.today()
        assert abs(dt.total_seconds()) < 10
    else:
        assert get_datetime_time_to_start(time_to_start) == expected
