"""
Tests for akrr.util.ssh
"""


def get_ssh(testconfig):
    import akrr.util.ssh as ssh

    sshcfg = testconfig['ssh']

    sh = ssh.ssh_access(
        sshcfg['host'], ssh='ssh',
        username=sshcfg['user'], password=sshcfg['password'],
        private_key_file=sshcfg['private_key_name'], private_key_password=sshcfg['private_key_passphrase'],
        logfile=None, command=None, pwd1=None, pwd2=None)

    return sh


def prep_resource_dict(testconfig):
    """
    Prepare resource dict for sss_resource tests
    """
    sshcfg = testconfig['ssh']

    resource = {
        'name': sshcfg['host'],
        'remote_access_node': sshcfg['host'],
        'remote_access_method': 'ssh',
        'ssh_username': sshcfg['user'],
        'ssh_password': sshcfg['password'],
        'ssh_private_key_file': sshcfg['private_key_name'],
        'ssh_private_key_password': sshcfg['private_key_passphrase']
    }

    return resource


def test_ssh_access(testconfig):
    """
    tests ssh.ssh_access and ssh_access_multytry
    """
    import akrr.util.ssh as ssh
    sshcfg = testconfig['ssh']

    # run single command
    assert ssh.ssh_access(
        sshcfg['host'], ssh='ssh',
        username=sshcfg['user'], password=sshcfg['password'],
        private_key_file=sshcfg['private_key_name'], private_key_password=sshcfg['private_key_passphrase'],
        command='whoami').strip() == sshcfg['user']

    # run shell session
    sh = ssh.ssh_access_multytry(
        sshcfg['host'], ssh='ssh',
        username=sshcfg['user'], password=sshcfg['password'],
        private_key_file=sshcfg['private_key_name'], private_key_password=sshcfg['private_key_passphrase'])

    assert ssh.ssh_command(sh, 'whoami').strip() == sshcfg['user']

    del sh


def test_ssh_resource(testconfig):
    """
    tests ssh.ssh_access and ssh_access_multytry
    """
    import akrr.util.ssh as ssh
    sshcfg = testconfig['ssh']
    resource = prep_resource_dict(testconfig)

    # run single command
    assert ssh.ssh_resource(resource, 'whoami').strip() == sshcfg['user']

    # run shell session
    sh = ssh.ssh_resource(resource)
    assert ssh.ssh_command(sh, 'whoami').strip() == sshcfg['user']
    del sh


def test_check_dir(testconfig):
    import os
    import akrr.util.ssh as ssh
    sshcfg = testconfig['ssh']
    resource = prep_resource_dict(testconfig)

    sh = ssh.ssh_resource(resource)
    assert ssh.ssh_command(sh, 'whoami').strip() == sshcfg['user']
    pwd = ssh.ssh_command(sh, 'pwd').strip()
    dirname = os.path.join(pwd, "testdir1")
    ssh.ssh_command(sh, 'rm -rf '+dirname)

    # this dir is not exists should get None
    assert ssh.check_dir(sh, dirname, exit_on_fail=False, try_to_create=False)[0] is None
    # this dir is not exists should create it and return True
    assert ssh.check_dir(sh, dirname, exit_on_fail=False, try_to_create=True)[0] is True
    # this dir exists should return True
    assert ssh.check_dir(sh, dirname, exit_on_fail=False, try_to_create=False)[0] is True

    del sh


def test_scp(testconfig, tmpdir):
    """
    Copy file to and from resource
    """
    import os
    import akrr.util.ssh as ssh
    sshcfg = testconfig['ssh']
    resource = prep_resource_dict(testconfig)
    content = u"this is test.\ntest is this!\n"

    sh = ssh.ssh_resource(resource)
    pwd = ssh.ssh_command(sh, 'pwd').strip()
    # file_name1 = os.path.join(pwd, "testfile1")
    # ssh.ssh_command(sh, 'rm -rf '+file_name)

    p = tmpdir / "testfile1.txt"
    p.write_text(content, encoding='utf8')
    ssh.scp_to_resource(resource, str(p), pwd)

    ssh.ssh_command(sh, "cp testfile1.txt testfile2.txt")

    p = tmpdir / "testfile2.txt"
    ssh.scp_from_resource(resource, os.path.join(pwd, "testfile2.txt"), str(p))

    assert p.read_text(encoding='utf8').strip() == content.strip()
