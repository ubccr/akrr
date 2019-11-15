import os
import shutil

from . import cfg
from .util import log
from .akrrerror import AkrrValueException


def app_add(resource: str, appkernel: str, execution_method: str = "hpc", dry_run: bool =False):
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
    cfg_default_template_filename = os.path.join(cfg.templates_dir, appkernel + ".app.conf")
    cfg_template_filename = os.path.join(cfg.templates_dir, "%s.%s.app.conf" % (appkernel, execution_method))
    if (not os.path.isfile(cfg_template_filename)) and execution_method == "hpc":
        cfg_template_filename = cfg_default_template_filename

    if (not os.path.isfile(cfg_template_filename)) and os.path.isfile(cfg_default_template_filename):
        msg = ("Can not find template file for %s application kernel in %s execution mode.\n"
               "Try default execution mode (hpc) and customize it for your needs."
               ) % (appkernel, cfg_template_filename)
        log.error(msg)
        raise AkrrValueException(msg)

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
    from prettytable import PrettyTable
    from .cfg import apps, resources
    from akrr.db import get_akrr_db
    from collections import OrderedDict
    db, cur = get_akrr_db(dict_cursor=True)

    # appkernels
    cur.execute("select * from app_kernels")
    app_table = OrderedDict(((a["name"], a) for a in cur.fetchall()))
    pt = PrettyTable()
    pt.field_names = ["App", "Enabled"]
    pt.align["App"] = "l"
    # Apps in db
    for app_name, app_opt in app_table.items():
        pt.add_row([app_name, app_opt["enabled"] > 0])
    # Apps not in db
    for app_name in apps.keys():
        if app_name not in app_table:
            pt.add_row([app_name, "None"])

    log.info("All available appkernels:\n" + str(pt))

    # get enable table
    cur.execute("select * from resources")
    resource_app_enabled = OrderedDict(((r["name"], {"apps": OrderedDict(), **r}) for r in cur.fetchall()))

    cur.execute(
        "select ra.id as resource_app_kernels_id,\n"
        "       ra.resource_id,r.name as resource, xdmod_resource_id,\n"
        "                      r.name as resource,r.enabled as resource_enabled,\n"
        "       ra.app_kernel_id,a.name as app,a.enabled as app_enabled,\n"
        "       ra.enabled as resource_app_enabled, a.nodes_list\n"
        "from resource_app_kernels ra\n"
        "left join resources r on ra.resource_id=r.id\n"
        "left join app_kernels a on ra.app_kernel_id=a.id")
    for ra in cur.fetchall():
        resource_app_enabled[ra["resource"]]["apps"][ra["app"]] = ra

    pt = PrettyTable()
    pt.field_names = ["Resource", "App", "Enabled"]
    pt.align["Resource"] = "l"
    for resource_name, resource_opt in resources.items():
        for app_name, app_opt in apps.items():
            if resource_name in app_opt['appkernel_on_resource']:
                ra_enabled = None
                if resource_name in resource_app_enabled and app_name in resource_app_enabled[resource_name]["apps"]:
                    ra_enabled = resource_app_enabled[resource_name]["apps"][app_name]["resource_app_enabled"] != 0
                pt.add_row([resource_name, app_name, ra_enabled])

    log.info("Appkernels on resources\n" + str(pt))
    return


def app_enable(resource, appkernel, enable=True, dry_run=False):
    """enabling/disabline AK on resource"""
    import argparse
    log.info(("Enabling " if enable else "Disabling ") +
             ("%s" % resource if appkernel is None else"%s on %s" % (appkernel, resource) ))
    if enable:
        return on_parsed(argparse.Namespace(resource=resource, application=appkernel))
    else:
        return off_parsed(argparse.Namespace(resource=resource, application=appkernel))


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
