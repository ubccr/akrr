import copy
import re
import sys
import time

from akrr.akrrerror import AkrrError

sshTimeout = 60
shellPrompt = "PROMPTtTtT"
sshTimeSleep = 0.25
sshCommandStartEcho = "StArTEd_ExeCUTEtIoM_SucCeSsFully"
sshCommandEndEcho = "ExeCUTEd_SucCeSsFully"


def sshAccess(remotemachine, ssh='ssh', username=None, password=None, PrivateKeyFile=None, PrivateKeyPassword=None,
              logfile=None, command=None, pwd1=None, pwd2=None):
    """login to remote machine and return pexpect.spawn instance.
    if command!=None will execute commands and return the output"""
    # pack command line and arguments
    cmd = ssh
    mode = 'ssh'
    if ssh.find('scp') >= 0:
        mode = 'scp'

    cmdarg = []
    # Add identity file if needed
    if PrivateKeyFile != None:
        cmdarg.extend(["-i", PrivateKeyFile])
        cmd += " -i " + PrivateKeyFile
    # Add username@host
    if mode == 'ssh':
        if username != None:
            cmdarg.append("%s@%s" % (username, remotemachine))
            cmd += " %s@%s" % (username, remotemachine)
        else:
            cmdarg.append("%s" % (remotemachine))
            cmd += " %s" % (remotemachine)

        if command != None and ssh != 'ssh-copy-id':
            cmdarg.append("\" %s;echo %s\"" % (command, sshCommandStartEcho))
            cmd += " \"echo %s;%s;echo %s\"" % (sshCommandStartEcho, command, sshCommandEndEcho)
    else:
        command = pwd2
        cmd += " %s %s" % (pwd1, pwd2)
    print(cmd)

    # find the prompt
    # if
    # tmp=$(set +x; (PS4=$PS1; set -x; :) 2>&1); tmp=${tmp#*.}; echo ${tmp%:}

    # Try to get access
    from akrr import pexpect

    rsh = None
    try:
        rsh = pexpect.spawn(cmd, encoding='utf-8')  # , logfile=logfile)
        # rsh.setwinsize(256,512)

        rsh.logfile_read = logfile

        expect = [
            "Are you sure you want to continue connecting (yes/no)?",
            '[Pp]assword:',
            "Enter passphrase for key",

            # username+'.*[\$>]\s*$',
            # '[#\$>]\s*',
            # '[^#]*[#\$]\s*',
            # ':~>\s*$'#,
            # shellPrompt
        ]
        addedPromptSearch = False
        if mode == 'ssh' and command == None and password == None and PrivateKeyPassword == None:
            # i.e. expecting passwordless access
            expect.append('[#\$>]\s*')
            addedPromptSearch = True
        bOnHeadnode = False

        sshTimeoutNew = sshTimeout
        if mode == 'ssh' and command == None:
            sshTimeoutNew = 2.0
        countPasses = 0
        PasswordCount = 0
        PrivateKeyPasswordCount = 0

        while not bOnHeadnode:
            i = -1
            try:
                i = rsh.expect(expect, timeout=sshTimeoutNew)
            except pexpect.TIMEOUT as e:
                if mode == 'ssh' and command == None:
                    # add prompts
                    if countPasses == 0:
                        if password == None and PrivateKeyPassword == None:
                            expect.append('[#\$>]\s*')
                            addedPromptSearch = True
                            sshTimeoutNew = sshTimeout
                        i = 6
                    else:
                        # assuming it has unrecognized prompt
                        # lets try to sent it
                        rsh.sendline(" export PS1='%s '" % (shellPrompt))
                        rsh.expect(shellPrompt, timeout=sshTimeout)  # twice because one from echo
                        rsh.expect(shellPrompt, timeout=sshTimeout)
                        i = 6
                else:
                    raise e
            countPasses += 1
            if i == 0:  # Are you sure you want to continue connecting (yes/no)?
                rsh.sendline('yes')
            if i == 1:  # [pP]assword
                if password != None:
                    if PasswordCount > 0:
                        rsh.sendcontrol('c')
                        rsh.close(force=True)
                        del rsh
                        raise AkrrError("Password for %s is incorrect." % remotemachine)
                    time.sleep(sshTimeSleep)  # so that the remote host have some time to turn off echo
                    rsh.sendline(password)
                    # add prompt search since password already asked
                    expect.append('[#\$>]\s*')
                    addedPromptSearch = True
                    PasswordCount += 1
                else:
                    rsh.sendcontrol('c')
                    rsh.close(force=True)
                    del rsh
                    raise AkrrError("%s had requested a password and one was not provided." % remotemachine)
            if i == 2:
                if PrivateKeyPassword != None:
                    if PrivateKeyPasswordCount > 0:
                        # i.e. PrivateKeyPassword was entered several times incorrectly and now remote servise asking for password
                        rsh.sendcontrol('c')
                        rsh.close(force=True)
                        del rsh
                        raise AkrrError("Private key password for %s is incorrect." % remotemachine)
                    time.sleep(sshTimeSleep)  # so that the remote host have some time to turn off echo
                    rsh.sendline(PrivateKeyPassword)
                    # add prompt search since password already asked
                    expect.append('[#\$>]\s*')
                    addedPromptSearch = True
                    PrivateKeyPasswordCount += 1
                else:
                    rsh.sendcontrol('c')
                    rsh.close(force=True)
                    del rsh
                    raise AkrrError("%s had requested a private key password and one was not provided." % remotemachine)
            if i >= 3:
                bOnHeadnode = True
                # are we really there?

        if mode == 'ssh' and command == None:
            rsh.sendline(
                " echo %s;\\\nexport PS1='%s ';\\\necho %s" % (sshCommandStartEcho, shellPrompt, sshCommandEndEcho))
            rsh.sendline(" ")
            rsh.sendline(" ")
            r = sshCommandEndEcho + r'.+' + shellPrompt + r'.+' + shellPrompt + r'.+' + shellPrompt
            rsh.expect(r,
                       timeout=sshTimeout)  # this pattern ensure proper handling when it thinks that in ssh hello message there is a prompt

            time.sleep(1)
            # test that we really in prompt
            msg = sshCommand(rsh, "echo TeStTeStTeStThEproMPT")
            if msg.strip() != "TeStTeStTeStThEproMPT":
                raise AkrrError("%s can not determine prompt." % remotemachine)
        rsh.remotemachine = remotemachine
        if logfile != None: logfile.flush()
        # print expect[i]
    except pexpect.TIMEOUT as e:
        # print "pexpect.TIMEOUT"
        msg = copy.deepcopy(rsh.before)
        rsh.close(force=True)
        del rsh
        raise AkrrError("Timeout period elapsed prior establishing the connection to %s.\n" % remotemachine + msg, e=e)
    except pexpect.EOF as e:
        ExeCUTEd_SucCeSsFully = False
        if command != None:
            ll = rsh.before.splitlines(False)
            if len(ll) > 1:
                if ll[-1].endswith(sshCommandEndEcho) or ll[-2].endswith(sshCommandEndEcho):
                    ExeCUTEd_SucCeSsFully = True
            if len(ll) > 0:
                if ll[-1].endswith(sshCommandEndEcho):
                    ExeCUTEd_SucCeSsFully = True
            if mode == 'scp':
                ExeCUTEd_SucCeSsFully = True
            if ssh == 'ssh-copy-id':
                ExeCUTEd_SucCeSsFully = True
        if command == None or (command != None and ExeCUTEd_SucCeSsFully == False):
            msg = copy.deepcopy(rsh.before)
            rsh.close(force=True)
            del rsh
            raise AkrrError("Probably %s refused the connection. " % remotemachine + msg, e=e)
        else:
            # user trying to execute command remotely
            msg = copy.deepcopy(rsh.before)
            rsh.close(force=True)
            del rsh
            return msg[(msg.find('\n', msg.find(sshCommandStartEcho) + 5) + len("\n") + 0):msg.rfind(sshCommandEndEcho)]
    # print "}"*100
    if mode == 'ssh' and command != None:
        # print "!"*100
        # print rsh.before
        # print "!"*100
        return copy.deepcopy(rsh.before)
    return rsh


def sshResource(resource, command=None):
    name = resource['name']
    headnode = resource.get('remoteAccessNode', name)
    remoteAccessMethod = resource.get('remoteAccessMethod', 'ssh')
    username = resource.get('sshUserName', None)
    sshPassword = resource.get('sshPassword', None)
    sshPrivateKeyFile = resource.get('sshPrivateKeyFile', None)
    sshPrivateKeyPassword = resource.get('sshPrivateKeyPassword', None)

    logfile = sys.stdout
    # logfile=None

    rsh = sshAccess(headnode, ssh=remoteAccessMethod, username=username, password=sshPassword,
                    PrivateKeyFile=sshPrivateKeyFile, PrivateKeyPassword=sshPrivateKeyPassword, logfile=logfile,
                    command=command)
    return rsh


def scpFromResource(resource, pwd1, pwd2, opt=""):
    name = resource['name']
    remotemachine = resource.get('remoteAccessNode', name)
    remoteInvocationMethod = resource.get('remoteCopyMethod', 'scp') + " " + opt + " "
    username = resource.get('sshUserName', None)
    sshPassword = resource.get('sshPassword', None)
    sshPrivateKeyFile = resource.get('sshPrivateKeyFile', None)
    sshPrivateKeyPassword = resource.get('sshPrivateKeyPassword', None)

    logfile = sys.stdout
    # logfile=None
    pwd1fin = ""
    if username != None:
        pwd1fin += " %s@%s:%s" % (username, remotemachine, pwd1)
    else:
        pwd1fin += " %s:%s" % (remotemachine, pwd1)

    rsh = sshAccess(remotemachine, ssh=remoteInvocationMethod, username=username, password=sshPassword,
                    PrivateKeyFile=sshPrivateKeyFile, PrivateKeyPassword=sshPrivateKeyPassword, logfile=logfile,
                    pwd1=pwd1fin, pwd2=pwd2)
    return rsh


def scpToResource(resource, pwd1, pwd2, opt="", logfile=None):
    if logfile == None:
        logfile = sys.stdout
    name = resource['name']
    remotemachine = resource.get('remoteAccessNode', name)
    remoteInvocationMethod = resource.get('remoteCopyMethod', 'scp') + " " + opt + " "
    username = resource.get('sshUserName', None)
    sshPassword = resource.get('sshPassword', None)
    sshPrivateKeyFile = resource.get('sshPrivateKeyFile', None)
    sshPrivateKeyPassword = resource.get('sshPrivateKeyPassword', None)

    # logfile = sys.stdout
    # logfile=None
    pwd2fin = ""
    if username != None:
        pwd2fin += " %s@%s:%s" % (username, remotemachine, pwd2)
    else:
        pwd2fin += " %s:%s" % (remotemachine, pwd2)

    rsh = sshAccess(remotemachine, ssh=remoteInvocationMethod, username=username, password=sshPassword,
                    PrivateKeyFile=sshPrivateKeyFile, PrivateKeyPassword=sshPrivateKeyPassword, logfile=logfile,
                    pwd1=pwd1, pwd2=pwd2fin)
    return rsh


def sshCommandNoReturn(sh, cmd):
    cmdfin = " " + cmd
    try:
        # flush the buffer
        sh.read_nonblocking(1000000, 0)
    except:
        pass

    sh.sendline(cmdfin)
    sh.expect(shellPrompt, timeout=sshTimeout)

    msg = sh.before
    return msg


def sshCommand(sh, cmd):
    cmdfin = " echo %s;\\\n%s;\\\necho %s" % (sshCommandStartEcho, cmd, sshCommandEndEcho)
    try:
        # flush the buffer
        sh.read_nonblocking(1000000, 0)
    except:
        pass

    sh.sendline(cmdfin)
    sh.expect(shellPrompt, timeout=sshTimeout)
    msg = sh.before
    msg = msg[(msg.find('\n', msg.rfind(sshCommandStartEcho) + 5) + len("\n") + 0):msg.rfind(sshCommandEndEcho)]
    regex = re.compile(r'\x1b[^m]*m')
    return regex.sub("", msg)