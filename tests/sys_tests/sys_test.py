import pytest

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

    # validate its runability
    CLI().run("app validate -r localhost -a xdmod.app.md.gromacs.micro -n 1".split())
