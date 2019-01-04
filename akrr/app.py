import os
import shutil

from . import cfg
from .util import log
from .akrrerror import AkrrValueException


def app_add(resource, appkernel, dry_run=False):
    """add app configuration to resource"""
    log.info("Generating application kernel configuration for %s on %s", appkernel, resource)

    try:
        cfg.find_resource_by_name(resource)
    except Exception:
        msg = "Can not find resource: %s" % resource
        log.error(msg)
        raise AkrrValueException(msg)
    try:
        cfg.find_app_by_name(appkernel)
    except Exception:
        msg = "Can not find application kernel: %s" % appkernel
        log.error(msg)
        raise AkrrValueException(msg)

    cfg_filename = os.path.join(cfg.cfg_dir, 'resources', resource, appkernel + ".app.conf")
    cfg_template_filename = os.path.join(cfg.templates_dir, appkernel + ".app.conf")

    if os.path.isfile(cfg_filename):
        msg = "Configuration file for %s on %s already exist. For regeneration delete it, %s" % (appkernel, resource,
                                                                                                 cfg_filename)
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


def on_parsed(args):
    """
    Handles the appropriate execution of an 'On' mode request given
    the provided command line arguments.
    """
    data = {
        'application': args.application if args.application else ''
    }

    try:
        from akrr import akrrrestclient

        result = akrrrestclient.put(
            '/resources/{0}/on'.format(args.resource),
            data=data)
        if result.status_code == 200:
            message = 'Successfully enabled {0} -> {1}.\n{2}' if args.application and args.resource \
                else 'Successfully enabled all applications on {0}.\n{1}'
            parameters = (args.application, args.resource, result.text) if args.application and args.resource \
                else (args.resource, result.text)
            log.info(message.format(*parameters))
        else:
            log.error(
                'something went wrong.%s:%s',
                result.status_code,
                result.text)
    except Exception as e:
        log.error('''
            An error occured while communicating
            with the REST API.
            %s: %s
            ''',
                  e.args[0] if len(e.args) > 0 else '',
                  e.args[1] if len(e.args) > 1 else '')


def off_parsed(args):
    """
    Handles the appropriate execution of an 'Off' mode request given
    the provided command line arguments.
    """
    data = {
        'application': args.application if args.application else ''
    }

    try:
        from akrr import akrrrestclient

        result = akrrrestclient.put(
            '/resources/{0}/off'.format(args.resource),
            data=data)

        if result.status_code == 200:
            message = 'Successfully disabled {0} -> {1}.\n{2}' if args.application and args.resource \
                else 'Successfully disabled all applications on {0}.\n{1}'
            parameters = (args.application, args.resource, result.text) if args.application and args.resource \
                else (args.resource, result.text)
            log.info(message.format(*parameters))
        else:
            log.error(
                'something went wrong. %s:%s',
                result.status_code,
                result.text)
    except Exception as e:
        log.error('''
            An error occured while communicating
            with the REST API.
            %s: %s
            ''',
                  e.args[0] if len(e.args) > 0 else '',
                  e.args[1] if len(e.args) > 1 else '')


def resource_app_enable(resource=None, appkernel=None, dry_run=False):
    print(resource, appkernel, dry_run)
    raise NotImplemented("resource_app_enable is not implemented yet!")
