"""
AKRR configuration
"""

import os
import re

from akrr import get_akrr_dirs
from akrr.util import log, clear_from_build_in_var

# load default values
from .cfg_default import *  # pylint: disable=wildcard-import,unused-wildcard-import

# get directories locations for this installation
akrr_dirs = get_akrr_dirs()

in_src_install = akrr_dirs['in_src_install']
akrr_mod_dir = akrr_dirs['akrr_mod_dir']
akrr_bin_dir = akrr_dirs['akrr_bin_dir']
akrr_cli_fullpath = akrr_dirs['akrr_cli_fullpath']
akrr_cfg = akrr_dirs['akrr_cfg']
akrr_home = akrr_dirs['akrr_home']
cfg_dir = akrr_dirs['cfg_dir']
templates_dir = akrr_dirs['templates_dir']
default_dir = akrr_dirs['default_dir']
appker_repo_dir = akrr_dirs['appker_repo_dir']

from akrr.cfg_util import load_resource, load_app

# Resource configurations are stored here
resources = {}

# Application configurations are stored here
apps = {}


def load_all_resources():
    """
    load all resources from configuration directory
    """
    global resources  # pylint: disable=global-statement
    for resource_name in os.listdir(os.path.join(cfg_dir, "resources")):
        if resource_name not in ['notactive', 'templates']:
            log.debug2("loading "+resource_name)
            try:
                resource = load_resource(resource_name)
                resources[resource_name] = resource
            except Exception as e:  # pylint: disable=broad-except
                log.exception("Exception occurred during resources loading:"+str(e))


def find_resource_by_name(resource_name):
    """
    return resource parameters
    if resource configuration file was modified will reload it

    raises error if can not find
    """
    global resources  # pylint: disable=global-statement
    if resource_name not in resources:
        resource = load_resource(resource_name)
        resources[resource_name] = resource

    resource = resources[resource_name]
    if os.path.getmtime(resource['default_resource_cfg_filename']) != \
            resource['default_resource_cfg_file_last_mod_time'] or \
            os.path.getmtime(resource['resource_cfg_filename']) != resource['resource_cfg_file_last_mod_time']:
        del resources[resource_name]
        resource = load_resource(resource_name)
        resources[resource_name] = resource
    return resources[resource_name]


def load_all_app():
    """
    load all resources from configuration directory
    """
    global apps
    global resources  # pylint: disable=global-statement
    for filename in os.listdir(os.path.join(akrr_mod_dir, 'default_conf')):
        if filename == "default.app.conf":
            continue
        if not filename.endswith(".app.conf"):
            continue
        if filename.count(".") != 2:
            continue

        app_name = re.sub(r'\.app\.conf$', '', filename)
        try:
            app = load_app(app_name, resources)
            apps[app_name] = app
        except Exception as e:  # pylint: disable=broad-except
            log.exception("Exception occurred during app kernel configuration loading: " + str(e))


def find_app_by_name(app_name):
    """
    return apps parameters
    if resource configuration file was modified will reload it

    raises error if can not find
    """
    global apps  # pylint: disable=global-statement
    global resources  # pylint: disable=global-statement
    if app_name not in apps:
        app = load_app(app_name, resources)
        apps[app_name] = app
        return apps[app_name]

    reload_app_cfg = False
    app = apps[app_name]
    #
    if (os.path.getmtime(app['default_app_cfg_filename']) != app['default_app_cfg_file_last_mod_time'] or
            os.path.getmtime(app['app_cfg_filename']) != app['app_cfg_file_last_mod_time']):
        reload_app_cfg = True

    # check if new resources was added
    for resource_name in os.listdir(os.path.join(cfg_dir, "resources")):
        if resource_name not in ['notactive', 'templates']:
            app_on_resource_cfg_filename = os.path.join(cfg_dir, "resources", resource_name,
                                                        app_name + ".app.conf")
            if os.path.isfile(app_on_resource_cfg_filename):
                if resource_name not in app['appkernel_on_resource']:
                    reload_app_cfg = True
                else:
                    if app['appkernel_on_resource'][resource_name]['resource_specific_app_cfg_file_last_mod_time'] != \
                            os.path.getmtime(app_on_resource_cfg_filename):
                        reload_app_cfg = True
    # check if new resources were removed
    for resource_name in app['appkernel_on_resource']:
        if resource_name not in ['default']:
            app_on_resource_cfg_filename = os.path.join(cfg_dir, "resources", resource_name,
                                                        app_name + ".app.conf")
            if not os.path.isfile(app_on_resource_cfg_filename):
                reload_app_cfg = True

    if reload_app_cfg:
        del apps[app_name]
        app = load_app(app_name, resources)
        apps[app_name] = app
    return apps[app_name]


def verify_akrr_conf(warnings_as_exceptions: bool = False):
    """
    Verify akrr.conf parameters,
    return values to update
    """
    import warnings

    # set default values for unset variables
    # make absolute paths from relative
    global data_dir
    if data_dir[0] != '/':
        data_dir = os.path.abspath(os.path.join(cfg_dir, data_dir))
    global completed_tasks_dir
    if completed_tasks_dir[0] != '/':
        completed_tasks_dir = os.path.abspath(os.path.join(cfg_dir, completed_tasks_dir))

    global restapi_certfile
    if restapi_certfile != '/':
        restapi_certfile = os.path.abspath(os.path.join(cfg_dir, restapi_certfile))

    # check rest-api certificate
    if not os.path.isfile(restapi_certfile):
        # assuming it is relative to akrr.conf file
        restapi_certfile = os.path.abspath(os.path.join(cfg_dir, restapi_certfile))
    if not os.path.isfile(restapi_certfile):
        raise ValueError('Cannot locate SSL certificate for rest-api HTTPS server', restapi_certfile)

    # Check for removed parameters:
    removed_parameters = [
        "export_db_host",
        "export_db_port",
        "export_db_user",
        "export_db_passwd",
        "export_db_name"
    ]
    for param in removed_parameters:
        if param in globals():
            msg = "Parameter {} was removed from akrr.conf".format(param)
            if not warnings_as_exceptions:
                warnings.warn(msg, DeprecationWarning)
            else:
                raise DeprecationWarning(msg)


# load akrr parameters
with open(cfg_dir + "/akrr.conf", "r") as file_in:
    exec(file_in.read())  # pylint: disable=exec-used


verify_akrr_conf()


load_all_resources()
load_all_app()
