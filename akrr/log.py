from logging import INFO,DEBUG
from logging import basicConfig,critical,error,warn,warning,info,debug,getLogger


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
