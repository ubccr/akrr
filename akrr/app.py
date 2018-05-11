import os
import shutil

from . import cfg
from .util import log
from .akrrerror import AkrrValueException


def app_add(resource, appkernel, dry_run=False):
    """add app configuration to resource"""
    log.info("Generating application kernel configuration for %s on %s", appkernel, resource)

    try:
        cfg.FindResourceByName(resource)
    except Exception:
        msg = "Can not find resource: %s" % resource
        log.error(msg)
        raise AkrrValueException(msg)
    try:
        cfg.FindAppByName(appkernel)
    except Exception:
        msg = "Can not find application kernel: %s" % appkernel
        log.error(msg)
        raise AkrrValueException(msg)

    cfg_filename = os.path.join(cfg.cfg_dir, 'resources', resource, appkernel + ".app.conf")
    cfg_template_filename = os.path.join(cfg.templates_dir, appkernel + ".app.conf")

    if os.path.isfile(cfg_filename):
        msg = "Configuration file for %s on %s already exist. For regeneration delete it, %s" % (appkernel, resource,cfg_filename)
        log.error(msg)
        log.info("Application kernel configuration for %s on %s is in: \n\t%s", appkernel, resource, cfg_filename)
        raise AkrrValueException(msg)

    if not os.path.isfile(cfg_template_filename):
        msg = "Can not find template file for application kernel: %s" % cfg_template_filename
        log.error(msg)
        raise AkrrValueException(msg)

    if dry_run:
        log.dry_run("Initial application kernel configuration for %s on %s, should be copied \n\tfrom %s to %s" %
                    (appkernel, resource, cfg_template_filename, cfg_filename))
    else:
        shutil.copyfile(cfg_template_filename, cfg_filename)
        if os.path.isfile(cfg_filename):
            log.info("Application kernel configuration for %s on %s is in: \n\t%s", appkernel, resource, cfg_filename)


def app_list():
    from .cfg import apps
    return list(apps.keys())
