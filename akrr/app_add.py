import os
import shutil

from . import cfg
import logging as log

verbose = False


def app_add(resource, appkernel, verbose=False):
    globals()['verbose'] = verbose

    log.info("Generating application kernel configuration for %s on %s", appkernel, resource)

    try:
        cfg.FindResourceByName(resource)
    except Exception:
        log.error("Can not find resource: %s", resource)
        exit(1)
    try:
        cfg.FindAppByName(appkernel)
    except Exception:
        log.error("Can not find application kernel: %s", appkernel)
        exit(1)

    cfgFilename = os.path.join(cfg.cfg_dir, 'resources', resource, appkernel + ".app.conf")
    cfgTemplateFilename = os.path.join(cfg.templates_dir, appkernel + ".app.conf")

    if os.path.isfile(cfgFilename):
        log.error("Configuration file for %s on %s already exist. For regeneration delete it", appkernel, resource)
        log.info("Application kernel configuration for %s on %s is in: \n\t%s", appkernel, resource, cfgFilename)
        exit(1)

    if not os.path.isfile(cfgTemplateFilename):
        log.error("Can not find template file for application kernel: %s", cfgTemplateFilename)
        exit(1)

    shutil.copyfile(cfgTemplateFilename, cfgFilename)
    if os.path.isfile(cfgFilename):
        log.info("Application kernel configuration for %s on %s is in: \n\t%s", appkernel, resource, cfgFilename)


if __name__ == '__main__':
    import argparse

    # TIME: to get to parsing
    parser = argparse.ArgumentParser('Initial configuration generation for application kernel on resource')
    # SETUP: the arguments that we're going to support
    parser.add_argument('-v', '--verbose', action='store_true', help="turn on verbose logging")
    parser.add_argument('resource', help="name of resource")
    parser.add_argument('appkernel', help="name of application kernel")
    # PARSE: them arguments
    args = parser.parse_args()

    app_add(args.resource, args.appkernel, verbose=args.verbose)
