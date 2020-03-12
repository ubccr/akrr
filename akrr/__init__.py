from enum import Enum

# Debug flag, if True then akrr executed in debug mode, launched as akrr daemon startdeb
# it also imply daemon is executed in foreground
debug = False
# If not None overwrite max_task_handlers, 0 means executed by main thread
debug_max_task_handlers = None
# If not None overwrite redirect_task_processing_to_log_file
debug_redirect_task_processing_to_log_file = None
# Dry run option for certain operations
dry_run = False


class AKRRHomeType(Enum):
    unknown = 0
    in_default_path = 2
    in_env_path = 3


def get_akrr_dirs(akrr_home: str = None):
    """
    return akrr directories

    AKRR home is determine in following order
    1) If akrr_home is set it will use it. And set environment variable
       This is mostly used during setup.
    2) AKRR_HOME if AKRR_HOME environment variable is defined.
       This is the case if akrr configs and appkernels running results
       are stored not in standard place.
    3) ~/akrr if initiated from RPM, that is akrr is in /usr/bin.
    """
    import os
    import inspect
    from .util import which
    from akrr.util import log

    akrr_mod_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

    akrr_home_type = AKRRHomeType.unknown

    # default location
    akrr_home_default = os.path.expanduser("~/akrr")
    akrr_cfg_default = os.path.expanduser("~/akrr/etc/akrr.conf")

    if akrr_home:
        os.environ["AKRR_HOME"] = akrr_home

    # location from env
    if "AKRR_HOME" in os.environ:
        akrr_home_env = os.path.abspath(os.path.expanduser(os.environ["AKRR_HOME"]))
        akrr_cfg_env = os.path.join(akrr_home_env, 'etc', 'akrr.conf')
    else:
        akrr_home_env = None
        akrr_cfg_env = None

    # in source location
    if os.path.isfile(os.path.join(os.path.dirname(akrr_mod_dir), 'bin', 'akrr')):
        # i.e. akrr running from source code or non-standard location
        akrr_bin_dir = os.path.abspath(os.path.expanduser(os.path.join(os.path.dirname(akrr_mod_dir), 'bin')))
        akrr_cli_fullpath = os.path.join(akrr_bin_dir, 'akrr')
        in_src_run = True
    else:
        akrr_cli_fullpath = which('akrr')
        akrr_bin_dir = os.path.abspath(os.path.expanduser(os.path.dirname(akrr_cli_fullpath)))
        in_src_run = False

    if akrr_home_env and akrr_home_default and akrr_home_env != akrr_home_default:
        akrr_home = akrr_home_env
        akrr_cfg = akrr_cfg_env
        akrr_home_type = AKRRHomeType.in_env_path
        log.debug("AKRR_HOME is set. AKRR configuration is in " + akrr_cfg)
    else:
        akrr_home = akrr_home_default
        akrr_cfg = akrr_cfg_default
        akrr_home_type = AKRRHomeType.in_default_path
        log.debug("AKRR_HOME is in default location. AKRR configuration is in " + akrr_cfg)

    # location of akrr cfg directory
    cfg_dir = os.path.dirname(akrr_cfg)

    # directory with templates
    templates_dir = os.path.join(akrr_mod_dir, 'templates')
    default_dir = os.path.join(akrr_mod_dir, 'default_conf')
    # directory with appkernels inputs and some script archives
    appker_repo_dir = os.path.join(akrr_mod_dir, 'appker_repo')

    return {
        'in_src_install': in_src_run,
        'akrr_home_type': akrr_home_type,
        'akrr_mod_dir': akrr_mod_dir,
        'akrr_bin_dir': akrr_bin_dir,
        'akrr_cli_fullpath': akrr_cli_fullpath,
        'akrr_cfg': akrr_cfg,
        'akrr_home': akrr_home,
        'cfg_dir': cfg_dir,
        'templates_dir': templates_dir,
        'default_dir': default_dir,
        'appker_repo_dir': appker_repo_dir,
    }
