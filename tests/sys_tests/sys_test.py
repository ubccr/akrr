import pytest
import re
from akrr.cli import CLI
from akrr.akrrerror import AkrrValueException

@pytest.mark.dependency()
def test_akrr_daemon_status():
    CLI().run(["-v", "daemon", "status"])


@pytest.mark.dependency()
def test_add_gromacs_micro():
    # init config
    CLI().run(["-v", "app", "add","-r", "localhost", "-a", "xdmod.app.md.gromacs.micro", "--dry-run"])
    CLI().run(["-v", "app", "add","-r", "localhost", "-a", "xdmod.app.md.gromacs.micro"])

    # do not overwrite existing conf
    with pytest.raises(AkrrValueException):
        CLI().run(["-v", "app", "add","-r", "localhost", "-a", "xdmod.app.md.gromacs.micro"])

    # check that batch-job script can be generated
    CLI().run(["-v", "task", "new","-r", "localhost", "-a", "xdmod.app.md.gromacs.micro",
               "-n", "1", "--dry-run", "--show-batch-job"])

    # validate its run-ability
    CLI().run("app validate -r localhost -a xdmod.app.md.gromacs.micro -n 1".split())


@pytest.mark.dependency(depends=["test_add_gromacs_micro"])
def test_use_gromacs_micro(caplog):
    import logging
    caplog.set_level(logging.INFO)

    # add task to execute right now
    caplog.clear()
    CLI().run("task new -r localhost -a xdmod.app.md.gromacs.micro -n 1".split())
    for record in caplog.records:
        m = re.search(r'Successfully submitted new task. The task id is ([0-9]+)', record.msg)
        if m is not None:
            break
    assert m is not None
    task_id = m.group(1)

    # list tasks
    caplog.clear()
    CLI().run("task list".split())
    for record in caplog.records:
        print(record.msg)

    # remove it

    # add periodically executed task
    CLI().run("task new -r localhost -a xdmod.app.md.gromacs.micro -n 1".split())
    # list tasks
    CLI().run("task list".split())
    CLI().run("task list -r localhost -a xdmod.app.md.gromacs.micro".split())
    # CLI().run("task list".split())
    # remove it

    # add periodically executed task
    # remove it

