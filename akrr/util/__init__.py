def which(program):
    """
    return full path of executable.
    If program is full path return it
    otherwise look in PATH. If still executable is not found return None.
    """
    import os

    def is_exe(file_path):
        return os.path.isfile(file_path) and os.access(file_path, os.X_OK)

    file_dir, _ = os.path.split(program)
    if file_dir:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None
