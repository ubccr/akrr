import os

import akrr.util
from akrr.cli.resource_deploy import dry_run
from akrr.util import log as log


def check_dir_simple(sh, d):
    """
    check that directory exists and verify its accessibility
    return None,message if does not exists
    return True,message if can write there
    return False,message if can not write there
    """
    dir(sh)
    cmd = "if [ -d \"%s\" ]\n then \n echo EXIST\n else echo DOES_NOT_EXIST\n fi" % (d,)
    msg = akrr.util.ssh.ssh_command(sh, cmd)
    if msg.find("DOES_NOT_EXIST") >= 0:
        return None, "Directory %s:%s does not exists!" % (sh.remote_machine, d)

    cmd = "echo test > " + os.path.join(d, 'akrr_test_write')
    # print cmd
    akrr.util.ssh.ssh_command(sh, cmd)
    # print msg
    cmd = "cat " + os.path.join(d, 'akrr_test_write')
    # print cmd
    msg = akrr.util.ssh.ssh_command(sh, cmd)
    # print msg
    if msg.strip() == "test":
        cmd = "rm " + os.path.join(d, 'akrr_test_write')
        akrr.util.ssh.ssh_command(sh, cmd)
        return True, "Directory exist and accessible for read/write"
    else:
        return False, "Directory %s:%s is NOT accessible for read/write!" % (sh.remote_machine, d)


def check_dir(sh, d, exit_on_fail=True, try_to_create=True):
    status, msg = check_dir_simple(sh, d)
    if try_to_create is True and status is None:
        log.info("Directory %s:%s does not exists, will try to create it", sh.remote_machine, d)
        if not dry_run:
            cmd = "mkdir -p \"%s\"" % (d,)
            akrr.util.ssh.ssh_command(sh, cmd)
            status, msg = check_dir_simple(sh, d)
        else:
            status, msg = (True, "Directory exist and accessible for read/write")
    if exit_on_fail is False:
        return status, msg

    if status is None:
        log.error("Directory %s:%s does not exists!", sh.remote_machine, d)
        exit()
    elif status is True:
        return True, msg
    else:
        log.error("Directory %s:%s is NOT accessible for read/write!", sh.remote_machine, d)
        exit()