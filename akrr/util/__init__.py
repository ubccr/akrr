from typing import Union, List


def which(program: str) -> Union[str, None]:
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


def clear_from_build_in_var(dict_in: dict) -> dict:
    """
    Return dict without  build-in variable and modules emerged in dict_in from exec function call
    """
    import inspect

    tmp = {}
    exec('wrong_fields_dict="wrong_fields_dict"', tmp)
    tmp.pop('wrong_fields_dict')
    wrong_fields = list(tmp.keys())

    dict_out = {}
    for key, val in dict_in.items():
        if inspect.ismodule(val):
            continue
        if wrong_fields.count(key) > 0:
            continue
        dict_out[key] = val

    return dict_out


def exec_files_to_dict(*files: str, var_in: dict=None) -> dict:
    """
    execute python from files and return dict with variables from that files.
    If var_in is specified initiate variables dictionary with it.
    """
    if var_in is None:
        tmp = {}
    else:
        import copy
        tmp = copy.deepcopy(var_in)

    for f in files:
        with open(f, "r") as file_in:
            exec(file_in.read(), tmp)
    return clear_from_build_in_var(tmp)
