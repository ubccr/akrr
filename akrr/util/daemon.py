from akrr.util import log


def get_daemon_pid(akrr_pid_file, delete_pid_file_if_daemon_down=False):
    """
    Return the PID of AKRR server
    """
    import os
    import psutil
    pid = None
    if os.path.isfile(akrr_pid_file):
        fin = open(akrr_pid_file, "r")
        lines = fin.readlines()
        pid = int(lines[0])
        fin.close()

        # Check For the existence of a unix pid
        if psutil.pid_exists(pid):
            try:
                cmd = " ".join(psutil.Process(pid=pid).cmdline())

                if cmd.count('akrr') and cmd.count('daemon') and cmd.count('start'):
                    return pid
            except Exception as e:
                log.log_traceback(str(e))
        else:
            # if here means that previous session was crushed
            if delete_pid_file_if_daemon_down:
                log.warning("WARNING:File %s exists meaning that the previous execution was finished incorrectly."
                            "Removing pid file." % akrr_pid_file)
                os.remove(akrr_pid_file)
                return None
            else:
                raise IOError("File %s exists meaning that the previous execution was finished incorrectly." %
                              akrr_pid_file)

    return pid


def daemon_stop(pid: int = None, timeout: float = 120.0):
    """
    Stop AKRR server. Return True on success or False on timeout
    """
    import os
    import time
    import psutil
    import signal

    if pid is None:
        log.info("AKRR is already not running.")
        return True
    log.info("Sending termination signal to AKRR server (PID: " + str(pid) + ")")
    # send a signal to terminate
    os.kill(pid, signal.SIGTERM)

    # wait till process will finished
    start = time.time()
    while psutil.pid_exists(pid):
        time.sleep(0.5)
        if time.time() - start > timeout:
            log.error("Can not stopped daemon!")
            return False

    log.info("Stopped AKRR server (PID: " + str(pid) + ")")
    return True
