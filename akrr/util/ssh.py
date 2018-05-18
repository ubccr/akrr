import copy
import re
import sys
import time

from akrr.util import log
from akrr.akrrerror import AkrrError

ssh_timeout = 60
shell_prompt = "PROMPTtTtT"
ssh_time_sleep = 0.25
ssh_command_start_echo = "StArTEd_ExeCUTEtIoM_SucCeSsFully"
ssh_command_end_echo = "ExeCUTEd_SucCeSsFully"


def ssh_access(remote_machine, ssh='ssh', username=None, password=None,
               private_key_file=None, private_key_password=None,
               logfile=None, command=None, pwd1=None, pwd2=None):
    """
    login to remote machine and return pexpect.spawn instance.
    if command!=None will execute commands and return the output
    """
    # pack command line and arguments
    cmd = ssh
    mode = 'ssh'
    if ssh.find('scp') >= 0:
        mode = 'scp'

    cmd_arg = []
    # Add identity file if needed
    if private_key_file is not None:
        cmd_arg.extend(["-i", private_key_file])
        cmd += " -i " + private_key_file
    # Add username@host
    if mode == 'ssh':
        if username is not None:
            cmd_arg.append("%s@%s" % (username, remote_machine))
            cmd += " %s@%s" % (username, remote_machine)
        else:
            cmd_arg.append("%s" % remote_machine)
            cmd += " %s" % remote_machine

        if command is not None and ssh != 'ssh-copy-id':
            cmd_arg.append("\" %s;echo %s\"" % (command, ssh_command_start_echo))
            cmd += " \"echo %s;%s;echo %s\"" % (ssh_command_start_echo, command, ssh_command_end_echo)
    else:
        command = pwd2
        cmd += " %s %s" % (pwd1, pwd2)
    log.debug(cmd)

    # find the prompt

    # Try to get access
    from akrr import pexpect

    rsh = None
    try:
        rsh = pexpect.spawn(cmd, encoding='utf-8')

        rsh.logfile_read = logfile

        expect = [
            "Are you sure you want to continue connecting (yes/no)?",
            '[Pp]assword:',
            "Enter passphrase for key"
        ]

        if mode == 'ssh' and command is None and password is None and private_key_password is None:
            # i.e. expecting passwordless access
            expect.append('[#\$>]\s*')

        on_headnode = False

        ssh_timeout_new = ssh_timeout
        if mode == 'ssh' and command is None:
            ssh_timeout_new = 2.0
        count_passes = 0
        password_count = 0
        private_key_password_count = 0

        while not on_headnode:
            try:
                i = rsh.expect(expect, timeout=ssh_timeout_new)
            except pexpect.TIMEOUT as e:
                if mode == 'ssh' and command is None:
                    # add prompts
                    if count_passes == 0:
                        if password is None and private_key_password is None:
                            expect.append('[#\$>]\s*')
                            ssh_timeout_new = ssh_timeout
                        i = 6
                    else:
                        # assuming it has unrecognized prompt
                        # lets try to sent it
                        rsh.sendline(" export PS1='%s '" % shell_prompt)
                        rsh.expect(shell_prompt, timeout=ssh_timeout)  # twice because one from echo
                        rsh.expect(shell_prompt, timeout=ssh_timeout)
                        i = 6
                else:
                    raise e
            count_passes += 1
            if i == 0:  # Are you sure you want to continue connecting (yes/no)?
                rsh.sendline('yes')
            if i == 1:  # [pP]assword
                if password is not None:
                    if password_count > 0:
                        rsh.sendcontrol('c')
                        rsh.close(force=True)
                        del rsh
                        raise AkrrError("Password for %s is incorrect." % remote_machine)
                    time.sleep(ssh_time_sleep)  # so that the remote host have some time to turn off echo
                    rsh.sendline(password)
                    # add prompt search since password already asked
                    expect.append('[#\$>]\s*')
                    password_count += 1
                else:
                    rsh.sendcontrol('c')
                    rsh.close(force=True)
                    del rsh
                    raise AkrrError("%s had requested a password and one was not provided." % remote_machine)
            if i == 2:
                if private_key_password is not None:
                    if private_key_password_count > 0:
                        # i.e. PrivateKeyPassword was entered several times incorrectly and
                        # now remote servise asking for password
                        rsh.sendcontrol('c')
                        rsh.close(force=True)
                        del rsh
                        raise AkrrError("Private key password for %s is incorrect." % remote_machine)
                    time.sleep(ssh_time_sleep)  # so that the remote host have some time to turn off echo
                    rsh.sendline(private_key_password)
                    # add prompt search since password already asked
                    expect.append('[#\$>]\s*')
                    private_key_password_count += 1
                else:
                    rsh.sendcontrol('c')
                    rsh.close(force=True)
                    del rsh
                    raise AkrrError("%s had requested a private key password and one was not provided." %
                                    remote_machine)
            if i >= 3:
                on_headnode = True
                # are we really there?

        if mode == 'ssh' and command is None:
            rsh.sendline(" echo %s;\\\nexport PS1='%s ';\\\necho %s" % (ssh_command_start_echo, shell_prompt,
                                                                        ssh_command_end_echo))
            rsh.sendline(" ")
            rsh.sendline(" ")

            # this pattern ensure proper handling when it thinks that in ssh hello message there is a prompt
            r = ssh_command_end_echo + r'.+' + shell_prompt + r'.+' + shell_prompt + r'.+' + shell_prompt
            rsh.expect(r, timeout=ssh_timeout)
            time.sleep(1)
            # test that we really in prompt
            msg = ssh_command(rsh, "echo TeStTeStTeStThEproMPT")
            if msg.strip() != "TeStTeStTeStThEproMPT":
                raise AkrrError("%s can not determine prompt." % remote_machine)
        rsh.remote_machine = remote_machine
        if logfile is not None:
            logfile.flush()
    except pexpect.TIMEOUT as e:
        msg = copy.deepcopy(rsh.before)
        rsh.close(force=True)
        del rsh
        raise AkrrError("Timeout period elapsed prior establishing the connection to %s.\n" % remote_machine + msg, e=e)
    except pexpect.EOF as e:
        executed_successfully = False
        if command is not None:
            ll = rsh.before.splitlines(False)
            if len(ll) > 1:
                if ll[-1].endswith(ssh_command_end_echo) or ll[-2].endswith(ssh_command_end_echo):
                    executed_successfully = True
            if len(ll) > 0:
                if ll[-1].endswith(ssh_command_end_echo):
                    executed_successfully = True
            if mode == 'scp':
                executed_successfully = True
            if ssh == 'ssh-copy-id':
                executed_successfully = True
        if command is None or (command is not None and executed_successfully is False):
            msg = copy.deepcopy(rsh.before)
            rsh.close(force=True)
            del rsh
            raise AkrrError("Probably %s refused the connection. " % remote_machine + msg, e=e)
        else:
            # user trying to execute command remotely
            msg = copy.deepcopy(rsh.before)
            rsh.close(force=True)
            del rsh
            return msg[(msg.find('\n', msg.find(ssh_command_start_echo) + 5) + len("\n") + 0):
                       msg.rfind(ssh_command_end_echo)]

    if mode == 'ssh' and command is not None:
        return copy.deepcopy(rsh.before)
    return rsh


def ssh_resource(resource, command=None):
    name = resource['name']
    headnode = resource.get('remoteAccessNode', name)
    remote_access_method = resource.get('remote_access_method', 'ssh')
    username = resource.get('ssh_username', None)
    ssh_password = resource.get('ssh_password', None)
    ssh_private_key_file = resource.get('ssh_private_key_file', None)
    ssh_private_key_password = resource.get('ssh_private_key_password', None)

    logfile = sys.stdout
    # logfile=None

    rsh = ssh_access(headnode, ssh=remote_access_method, username=username, password=ssh_password,
                     private_key_file=ssh_private_key_file, private_key_password=ssh_private_key_password,
                     logfile=logfile,
                     command=command)
    return rsh


def scp_from_resource(resource, pwd1, pwd2, opt=""):
    name = resource['name']
    remote_machine = resource.get('remoteAccessNode', name)
    remote_invocation_method = resource.get('remote_copy_method', 'scp') + " " + opt + " "
    username = resource.get('ssh_username', None)
    ssh_password = resource.get('ssh_password', None)
    ssh_private_key_file = resource.get('ssh_private_key_file', None)
    ssh_private_key_password = resource.get('ssh_private_key_password', None)

    logfile = sys.stdout
    # logfile=None
    pwd1fin = ""
    if username is not None:
        pwd1fin += " %s@%s:%s" % (username, remote_machine, pwd1)
    else:
        pwd1fin += " %s:%s" % (remote_machine, pwd1)

    rsh = ssh_access(remote_machine, ssh=remote_invocation_method, username=username, password=ssh_password,
                     private_key_file=ssh_private_key_file, private_key_password=ssh_private_key_password,
                     logfile=logfile,
                     pwd1=pwd1fin, pwd2=pwd2)
    return rsh


def scp_to_resource(resource, pwd1, pwd2, opt="", logfile=None):
    if logfile is None:
        logfile = sys.stdout
    name = resource['name']
    remote_machine = resource.get('remoteAccessNode', name)
    remote_invocation_method = resource.get('remote_copy_method', 'scp') + " " + opt + " "
    username = resource.get('ssh_username', None)
    ssh_password = resource.get('ssh_password', None)
    ssh_private_key_file = resource.get('ssh_private_key_file', None)
    ssh_private_key_password = resource.get('ssh_private_key_password', None)

    # logfile = sys.stdout
    # logfile=None
    pwd2fin = ""
    if username is not None:
        pwd2fin += " %s@%s:%s" % (username, remote_machine, pwd2)
    else:
        pwd2fin += " %s:%s" % (remote_machine, pwd2)

    rsh = ssh_access(remote_machine, ssh=remote_invocation_method, username=username, password=ssh_password,
                     private_key_file=ssh_private_key_file, private_key_password=ssh_private_key_password,
                     logfile=logfile,
                     pwd1=pwd1, pwd2=pwd2fin)
    return rsh


def ssh_command_no_return(sh, cmd):
    from akrr.pexpect.exceptions import ExceptionPexpect

    cmd_fin = " " + cmd
    try:
        # flush the buffer
        sh.read_nonblocking(1000000, 0)
    except (ValueError, ExceptionPexpect):
        pass

    sh.sendline(cmd_fin)
    sh.expect(shell_prompt, timeout=ssh_timeout)

    msg = sh.before
    return msg


def ssh_command(sh, cmd):
    from akrr.pexpect.exceptions import ExceptionPexpect

    cmd_fin = " echo %s;\\\n%s;\\\necho %s" % (ssh_command_start_echo, cmd, ssh_command_end_echo)
    try:
        # flush the buffer
        sh.read_nonblocking(1000000, 0)
    except (ValueError, ExceptionPexpect):
        pass

    sh.sendline(cmd_fin)
    sh.expect(shell_prompt, timeout=ssh_timeout)
    msg = sh.before
    msg = msg[(msg.find('\n', msg.rfind(ssh_command_start_echo) + 5) + len("\n") + 0):msg.rfind(ssh_command_end_echo)]
    regex = re.compile(r'\x1b[^m]*m')
    return regex.sub("", msg)
