# Debug flag, if True then akrr executed in debug mode, launched as akrr daemon startdeb
# it also imply daemon is executed in foreground
debug = False
# If not None overwrite max_task_handlers, 0 means executed by main thread
debug_max_task_handlers = None
# If not None overwrite redirect_task_processing_to_log_file
debug_redirect_task_processing_to_log_file = None
# Dry run option for certain operations
dry_run = False


def get_akrr_dirs(akrr_home: str = None):
    """
    return akrr directories

    AKRR home is determine in following order
    1) If akrr_home is set it will use it.
       This is mostly used during setup.
    2) AKRR_HOME if AKRR_HOME environment variable is defined.
       This is the case if akrr configs and appkernels running results
       are stored not in standard place.
    3) ~/akrr if initiated from RPM, that is akrr is in /usr/bin.
    4) <path to AKRR sources> for in source installation
    """
    import os
    import inspect
    from .util import which
    from akrr.util import log

    in_src_install: bool = False

    akrr_mod_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    if os.path.isfile(os.path.join(os.path.dirname(akrr_mod_dir), 'bin', 'akrr')):
        akrr_bin_dir = os.path.join(os.path.dirname(akrr_mod_dir), 'bin')
        akrr_cli_fullpath = os.path.join(akrr_bin_dir, 'akrr')
        in_src_install = True
    else:
        akrr_cli_fullpath = which('akrr')
        akrr_bin_dir = os.path.dirname(akrr_cli_fullpath)

    # determine akrr_home
    if akrr_home is None:
        akrr_home = os.getenv("AKRR_HOME")

    if akrr_home is None:
        if in_src_install:
            akrr_home = os.path.dirname(akrr_mod_dir)
            akrr_cfg = os.path.join(akrr_home, 'etc', 'akrr.conf')
            log.debug("In-source installation, AKRR configuration is in " + akrr_cfg)
        else:
            akrr_home = os.path.expanduser("~/akrr")
            akrr_cfg = os.path.expanduser("~/akrr/etc/akrr.conf")
            log.debug("AKRR configuration is in " + akrr_cfg)

    else:
        akrr_home = os.path.expanduser(akrr_home)
        akrr_cfg = os.path.join(akrr_home, 'etc', 'akrr.conf')
        log.debug("AKRR_HOME is set. AKRR configuration is in " + akrr_cfg)

    # location of akrr cfg directory
    cfg_dir = os.path.dirname(akrr_cfg)

    # directory with templates
    templates_dir = os.path.join(akrr_mod_dir, 'templates')
    default_dir = os.path.join(akrr_mod_dir, 'default_conf')
    # directory with appkernels inputs and some script archives
    appker_repo_dir = os.path.join(akrr_mod_dir, 'appker_repo')

    return {
        'in_src_install': in_src_install,
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
