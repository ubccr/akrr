import pytest
import re
from akrr.cli import CLI
from akrr.akrrerror import AkrrValueException

import warnings
warnings.filterwarnings("ignore", message=r'.*Certificate for .* has no .*subjectAltName.*')


def run_akrr(args, pattern=None, caplog=None, clear_log_before=True, clear_log_after=True):
    if caplog is not None and clear_log_before:
        caplog.clear()

    if isinstance(args,str):
        args = args.split()
    CLI().run(args)

    if pattern is not None:
        m = search_in_caplog(pattern, caplog)
    else:
        m = None

    if caplog is not None and clear_log_after:
        caplog.clear()

    return m


def search_in_caplog(pattern, caplog, clear_log=False):
    for record in caplog.records:
        m = re.search(pattern, str(record.msg))
        if m is not None:
            if clear_log:
                caplog.clear()
            return m
    if clear_log:
                caplog.clear()
    return None


@pytest.mark.dependency()
def test_akrr_daemon_status(caplog):
    assert run_akrr(
        "-v daemon status",
        r"AKRR Server is up and it", caplog) is not None


@pytest.mark.dependency()
def test_deploy_localhost2(caplog):
    CLI().run("resource deploy -r localhost2 -n 1".split())
    assert search_in_caplog(r'Successfully enabled localhost2', caplog) is not None
    assert search_in_caplog(r'DONE, you can move to next step', caplog) is not None
    caplog.clear()


def add_app_to_resource(resource, app, caplog):
    caplog.clear()
    # init config
    assert run_akrr(
        "-v app add -r {} -a {} --dry-run".format(resource, app),
        "Generating application kernel configuration for", caplog) is not None

    assert run_akrr(
        "-v app add -r {} -a {}".format(resource, app),
        "Application kernel configuration for .* is in", caplog) is not None

    # do not overwrite existing conf
    with pytest.raises(AkrrValueException):
        CLI().run("-v app add -r {} -a {}".format(resource, app).split())

    # check that batch-job script can be generated, mimicing checking script by user
    assert run_akrr(
        "-v task new -r {} -a {} -n 1 --dry-run --show-batch-job".format(resource, app),
        "Below is content of generated batch job script", caplog) is not None
    # validate its run-ability
    CLI().run("app validate -r {} -a {} -n 1".format(resource, app).split())
    assert search_in_caplog(r'Successfully enabled .* on', caplog) is not None
    assert search_in_caplog(r'DONE, you can move to next step!', caplog) is not None
    caplog.clear()


@pytest.mark.dependency()
def test_add_gromacs_micro(caplog):
    add_app_to_resource("localhost", "xdmod.app.md.gromacs.micro ", caplog)


@pytest.mark.dependency(depends=["test_deploy_localhost2"])
def test_add_gromacs_micro_on_localhost2(caplog):
    add_app_to_resource("localhost2", "xdmod.app.md.gromacs.micro ", caplog)


@pytest.mark.dependency(depends=["test_add_gromacs_micro", "test_add_gromacs_micro_on_localhost2"])
def test_use_gromacs_micro(caplog):
    import logging
    caplog.set_level(logging.INFO)

    # add task to execute right now
    m = run_akrr(
        "task new -r localhost -a xdmod.app.md.gromacs.micro -n 1",
        r'Successfully submitted new task. The task id is ([0-9]+)', caplog)
    assert m is not None
    task_id = m.group(1)

    # list tasks
    CLI().run("task list".split())
    assert search_in_caplog(r'[sS]cheduled tasks', caplog) is not None
    assert search_in_caplog(r'[aA]ctive tasks', caplog) is not None
    assert search_in_caplog(str(task_id), caplog) is not None
    caplog.clear()

    # add tasks for future execution
    m = run_akrr(
        "task new -r localhost -a xdmod.app.md.gromacs.micro -n 1 -s tomorrow",
        r'Successfully submitted new task. The task id is ([0-9]+)', caplog)
    assert m is not None
    task_id_1 = m.group(1)

    m = run_akrr(
        "task new -r localhost2 -a xdmod.app.md.gromacs.micro -n 1 -s tomorrow",
        r'Successfully submitted new task. The task id is ([0-9]+)', caplog)
    assert m is not None
    task_id_2 = m.group(1)

    m = run_akrr(
        "task new -r localhost -a test -n 1 -s tomorrow",
        r'Successfully submitted new task. The task id is ([0-9]+)', caplog)
    assert m is not None
    task_id_3 = m.group(1)

    # check task listing
    caplog.clear()

    CLI().run("task list".split())
    assert search_in_caplog(str(task_id_1), caplog) is not None
    assert search_in_caplog(str(task_id_2), caplog) is not None
    assert search_in_caplog(str(task_id_3), caplog) is not None
    caplog.clear()

    CLI().run("task list -r localhost".split())
    assert search_in_caplog(str(task_id_1), caplog) is not None
    assert search_in_caplog(str(task_id_2), caplog) is None
    assert search_in_caplog(str(task_id_3), caplog) is not None
    caplog.clear()

    CLI().run("task list -r localhost -a test".split())
    assert search_in_caplog(str(task_id_1), caplog) is None
    assert search_in_caplog(str(task_id_2), caplog) is None
    assert search_in_caplog(str(task_id_3), caplog) is not None
    caplog.clear()

    CLI().run("task list -scheduled".split())
    assert search_in_caplog(str(task_id_1), caplog) is not None
    assert search_in_caplog(str(task_id_2), caplog) is not None
    assert search_in_caplog(str(task_id_3), caplog) is not None
    caplog.clear()

    CLI().run("task list -r localhost -scheduled".split())
    assert search_in_caplog(str(task_id_1), caplog) is not None
    assert search_in_caplog(str(task_id_2), caplog) is None
    assert search_in_caplog(str(task_id_3), caplog) is not None
    caplog.clear()

    CLI().run("task list -r localhost -a test -scheduled".split())
    assert search_in_caplog(str(task_id_1), caplog) is None
    assert search_in_caplog(str(task_id_2), caplog) is None
    assert search_in_caplog(str(task_id_3), caplog) is not None
    caplog.clear()

    CLI().run("task list -active".split())
    assert search_in_caplog(str(task_id_1), caplog) is None
    assert search_in_caplog(str(task_id_2), caplog) is None
    assert search_in_caplog(str(task_id_3), caplog) is None
    caplog.clear()

    CLI().run("task list -r localhost -active".split())
    assert search_in_caplog(str(task_id_1), caplog) is None
    assert search_in_caplog(str(task_id_2), caplog) is None
    assert search_in_caplog(str(task_id_3), caplog) is None
    caplog.clear()

    CLI().run("task list -r localhost -a test -active".split())
    assert search_in_caplog(str(task_id_1), caplog) is None
    assert search_in_caplog(str(task_id_2), caplog) is None
    assert search_in_caplog(str(task_id_3), caplog) is None
    caplog.clear()

    # remove it
    #CLI().run("task delete -t {}".format(task_id_3).split())

    # add periodically executed task
    #CLI().run("task new -r localhost -a xdmod.app.md.gromacs.micro -n 1".split())
    # list tasks
    #CLI().run("task list".split())
    #CLI().run("task list -r localhost -a xdmod.app.md.gromacs.micro".split())



    # CLI().run("task list".split())


    # add periodically executed task
    # remove it

