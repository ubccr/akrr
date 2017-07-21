
def get_akrr_dirs():
    """return akrr directories"""
    import os
    import inspect
    from util import which
    
    #AKRR configuration can be in three places
    # 1) AKRR_CONF if AKRR_CONF enviroment variable is defined
    # 2) ~/akrr/etc/akrr.conf if initiated from RPM or global python install
    # 3) <path to AKRR sources>/etc/akrr.conf for in source installation
    
    in_src_install=False
    
    akrr_mod_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    akrr_bin_dir = None
    if os.path.isfile(os.path.join(os.path.dirname(akrr_mod_dir),'bin','akrr')):
        akrr_bin_dir=os.path.join(os.path.dirname(akrr_mod_dir),'bin')
        akrr_cli_fullpath=os.path.join(akrr_bin_dir,'akrr')
        in_src_install=True
    else:
        akrr_cli_fullpath=which('akrr')
        akrr_bin_dir=os.path.dirname(akrr_cli_fullpath)
    
    #determin akrr_home
    akrr_cfg=os.getenv("AKRR_CONF")
    if akrr_cfg==None:
        if in_src_install:
            akrr_home=os.path.dirname(akrr_mod_dir)
            akrr_cfg=os.path.join(akrr_home,'etc','akrr.conf')
            #log.info("In-source installation, AKRR configuration is in "+akrr_cfg)
        else:
            akrr_home=os.path.expanduser("~/akrr")
            akrr_cfg=os.path.expanduser("~/akrr/etc/akrr.conf")
            #log.info("AKRR configuration is in "+akrr_cfg)
        
    else:
        akrr_home=os.path.dirname(os.path.dirname(akrr_cfg))
        #log.info("AKRR_CONF is set. AKRR configuration is in "+akrr_cfg)
    
    
    
    #location of akrr cfg directory
    cfg_dir = os.path.dirname(akrr_cfg)
    
    #directory with templates
    templates_dir=os.path.join(akrr_mod_dir,'templates')
    default_dir=os.path.join(akrr_mod_dir,'default_conf')
    #directory with appkernels inputs and some script archives
    appker_repo_dir=os.path.join(akrr_mod_dir,'appker_repo')
    
    return {
        'in_src_install':in_src_install,
        'akrr_mod_dir':akrr_mod_dir,
        'akrr_bin_dir':akrr_bin_dir,
        'akrr_cli_fullpath':akrr_cli_fullpath,
        'akrr_cfg':akrr_cfg,
        'akrr_home':akrr_home,
        'cfg_dir':cfg_dir,
        'templates_dir':templates_dir,
        'default_dir':default_dir,
        'appker_repo_dir':appker_repo_dir,
    }
