from logging import INFO, DEBUG
from logging import basicConfig, critical, error, warning, info, debug, getLogger, exception

from . import colorize

verbose = False
error_count = 0
warning_count = 0


def debug2(msg, *args, **kwargs):
    """
    more verbose logging
    """
    if getLogger().level < 10:
        debug(msg, *args, **kwargs)


def dry_run(msg, *_, **__):
    print("DryRun: "+msg)


def empty_line():
    print()


def log_input(message, *args):
    if message:
        if len(args) > 0:
            formatted_message = message.format(*args)
        else:
            formatted_message = message
    else:
        formatted_message = ''

    print('[' + colorize.purple('INPUT') + ']: ' + formatted_message)


def log_traceback(m_str=None):
    import traceback
    msg = "###### Exception ######\n"
    if m_str is not None:
        msg = msg + m_str+"\n"

    msg = msg + traceback.format_exc()
    exception(msg)


def test_log():
    basicConfig(
        level=INFO,
        format="[%(asctime)s - %(levelname)s] %(message)s"
    )
    getLogger().setLevel(DEBUG)
    critical("test critical")
    error("test error")
    exception("test exception")
    warning("test warning")
    info("test info")
