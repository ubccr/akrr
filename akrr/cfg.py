"""
AKRR configuration
"""

import os
import re

import MySQLdb
import MySQLdb.cursors

from akrr import get_akrr_dirs

from .util import log

from .akrrerror import *

# load default values
from .cfg_default import *

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

# load akrr parameters
with open(cfg_dir + "/akrr.conf", "r") as file_in:
    exec(file_in.read())

# set default values for unset variables
# make absolute paths from relative
if data_dir[0] != '/':
    data_dir = os.path.abspath(os.path.join(cfg_dir, data_dir))
if completed_tasks_dir[0] != '/':
    completed_tasks_dir = os.path.abspath(os.path.join(cfg_dir, completed_tasks_dir))

if restapi_certfile != '/':
    restapi_certfile = os.path.abspath(os.path.join(cfg_dir, restapi_certfile))

###################################################################################################
#
# Resources Config Routines
#
###################################################################################################
resources = {}


def verify_resource_params(resource: dict) -> dict:
    """
    Perform simplistic resource parameters validation
    raises TypeError or NameError on problems
    """

    import warnings
    # mapped renamed parameters
    renamed_parameters = [
        ('localScratch', 'local_scratch'),
        # ('batchJobTemplate', 'batch_job_template'),
        # ('remoteAccessNode', 'remote_access_node'),
        # ('akrrCommonCommandsTemplate', 'akrr_common_commands_template'),
        # ('networkScratch', 'network_scratch'),
        ('sshUserName', 'ssh_username'),
        ('sshPassword', 'ssh_password'),
        ('sshPrivateKeyFile', 'ssh_private_key_file'),
        ('sshPrivateKeyPassword', 'ssh_private_key_password'),
        ('remoteAccessMethod', 'remote_access_method'),
        # ('batchScheduler', 'batch_scheduler'),
        # ('appKerDir', 'appkernel_dir'),
        # ('akrrCommonCleanupTemplate', 'akrr_common_cleanup_tTemplate'),
        # ('akrrData', 'akrr_data')
    ]

    for old_key, new_key in renamed_parameters:
        if old_key in resource:
            resource[new_key] = resource.pop(old_key)
            warnings.warn("Resource parameter {} was renamed to {}".format(old_key, new_key), DeprecationWarning)
    
    # check that parameters for presents and type
    # format: key,type,can be None,must have parameter
    parameters_types = [
        ['info', str, False, False],
        ['local_scratch', str, False, True],
        ['batchJobTemplate', str, False, True],
        ['remoteAccessNode', str, False, True],
        ['name', str, False, False],
        ['akrrCommonCommandsTemplate', str, False, True],
        ['networkScratch', str, False, True],
        ['ppn', int, False, True],
        ['remote_copy_method', str, False, True],
        ['ssh_username', str, False, True],
        ['ssh_password', str, True, False],
        ['ssh_private_key_file', str, True, False],
        ['ssh_private_key_password', str, True, False],
        ['batchScheduler', str, False, True],
        ['remote_access_method', str, False, True],
        ['appKerDir', str, False, True],
        ['akrrCommonCleanupTemplate', str, False, True],
        ['akrr_data', str, False, True]
    ]

    for variable, m_type, nullable, must in parameters_types:
        if (must is True) and (variable not in resource):
            raise NameError("Syntax error in " + resource['name'] + "\nVariable %s is not set" % (variable,))
        if variable not in resource:
            continue
        if resource[variable] is None and not nullable:
            raise TypeError("Syntax error in " + resource['name'] + "\nVariable %s can not be None" % (variable,))
        if not isinstance(resource[variable], m_type) and not (resource[variable] is None and nullable):
            raise TypeError("Syntax error in " + resource['name'] +
                            "\nVariable %s should be %s" % (variable, str(m_type)) +
                            ". But it is " + str(type(resource[variable])))
    return resource


def load_resource(resource_name: str):
    """
    load resource configuration file, do minimalistic validation
    return dict with resource parameters
    
    raises error if can not load
    """
    import warnings
    from .util import exec_files_to_dict

    try:
        default_resource_cfg_filename = os.path.join(default_dir, "default.resource.conf")
        resource_cfg_filename = os.path.join(cfg_dir, 'resources', resource_name, "resource.conf")

        if not os.path.isfile(default_resource_cfg_filename):
            raise AkrrError(
                "Default resource configuration file do not exists (%s)!" % default_resource_cfg_filename)
        if not os.path.isfile(resource_cfg_filename):
            raise AkrrError(
                "Configuration file for resource %s does not exist (%s)!" % (resource_name, resource_cfg_filename))

        # execute conf file
        resource = exec_files_to_dict(default_resource_cfg_filename, resource_cfg_filename)

        # mapped options in resource input file to those used in AKRR
        if 'name' not in resource:
            resource['name'] = resource_name

        # here should be depreciated options and renames
        if 'akrrData' in resource:
            warnings.warn("Rename akrrData to akrr_data", DeprecationWarning)
            resource['akrr_data'] = resource['akrrData']
        if 'appKerDir' in resource:
            resource['AppKerDir'] = resource['appKerDir']

        # last modification time for future reloading
        resource['default_resource_cfg_filename'] = default_resource_cfg_filename
        resource['resource_cfg_filename'] = resource_cfg_filename
        resource['default_resource_cfg_file_last_mod_time'] = os.path.getmtime(default_resource_cfg_filename)
        resource['resource_cfg_file_last_mod_time'] = os.path.getmtime(resource_cfg_filename)

        # here should be validation
        resource = verify_resource_params(resource)

        return resource
    except Exception:
        log.exception("Exception occurred during resource configuration loading for %s." % resource_name)
        raise AkrrError("Can not load resource configuration for %s." % resource_name)


def load_all_resources():
    """
    load all resources from configuration directory
    """
    global resources
    for resource_name in os.listdir(cfg_dir + "/resources"):
        if resource_name not in ['notactive', 'templates']:
            log.debug2("loading "+resource_name)
            try:
                resource = load_resource(resource_name)
                resources[resource_name] = resource
            except Exception as e:
                log.exception("Exception occurred during resources loading:"+str(e))


def find_resource_by_name(resource_name):
    """
    return resource parameters
    if resource configuration file was modified will reload it
    
    raises error if can not find
    """
    global resources
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


###################################################################################################
# App Kernels Config Routines
apps = {}


def verify_app_params(app):
    """
    Perform simplistic app parameters validation
    
    raises error
    """
    # check that parameters for presents and type
    # format: key,type,can be None,must have parameter
    parameters_types = [
        ['parser', str, False, True],
        ['executable', str, True, True],
        ['input', str, True, True],
        ['walllimit', int, False, True],
        ['runScript', dict, False, False]
    ]

    for variable, m_type, nullable, must in parameters_types:
        if must and (variable not in app):
            raise NameError("Syntax error in " + app['name'] + "\nVariable %s is not set" % (variable,))
        if variable not in app:
            continue
        if app[variable] is None and not nullable:
            raise TypeError("Syntax error in " + app['name'] + "\nVariable %s can not be None" % (variable,))
        if not isinstance(app[variable], m_type) and not (app[variable] is None and nullable):
            raise TypeError("Syntax error in " + app['name'] +
                            "\nVariable %s should be %s" % (variable, str(m_type)) +
                            ". But it is " + str(type(app[variable])))


def load_app(app_name):
    """
    load app configuration file, do minimalistic validation
    return dict with app parameters
    
    raises error if can not load
    """
    from .util import exec_files_to_dict
    try:
        default_app_cfg_filename = os.path.join(default_dir, "default.app.conf")
        app_cfg_filename = os.path.join(default_dir, app_name + ".app.conf")

        if not os.path.isfile(default_app_cfg_filename):
            raise AkrrError(
                "Default application kernel configuration file do not exists (%s)!" % default_app_cfg_filename)
        if not os.path.isfile(app_cfg_filename):
            raise AkrrError("application kernel configuration file do not exists (%s)!" % app_cfg_filename)

        app = exec_files_to_dict(default_app_cfg_filename, app_cfg_filename)

        # load resource specific parameters
        for resource_name in os.listdir(os.path.join(cfg_dir, "resources")):
            if resource_name not in ['notactive', 'templates']:
                resource_specific_app_cfg_filename = os.path.join(cfg_dir, "resources", resource_name,
                                                                  app_name + ".app.conf")
                if os.path.isfile(resource_specific_app_cfg_filename):
                    app['appkernelOnResource'][resource_name] = exec_files_to_dict(
                        resource_specific_app_cfg_filename, var_in=app['appkernelOnResource']['default'])
                    app['appkernelOnResource'][resource_name][
                        'resource_specific_app_cfg_filename'] = resource_specific_app_cfg_filename
                    app['appkernelOnResource'][resource_name]['resource_specific_app_cfg_file_last_mod_time'] = \
                        os.path.getmtime(resource_specific_app_cfg_filename)

        # mapped options in app input file to those used in AKRR
        if 'name' not in app:
            app['name'] = app_name
        if 'nickname' not in app:
            app['nickname'] = app_name + ".@nnodes@"

        # last modification time for future reloading
        app['default_app_cfg_filename'] = default_app_cfg_filename
        app['app_cfg_filename'] = app_cfg_filename
        app['default_app_cfg_file_last_mod_time'] = os.path.getmtime(default_app_cfg_filename)
        app['app_cfg_file_last_mod_time'] = os.path.getmtime(app_cfg_filename)

        # here should be validation
        verify_app_params(app)

        return app
    except Exception:
        log.exception("Exception occurred during app kernel configuration loading for %s." % app_name)
        raise AkrrError("Can not load app configuration for %s." % app_name)


def load_all_app():
    """
    load all resources from configuration directory
    """
    global apps
    for fl in os.listdir(os.path.join(akrr_mod_dir, 'default_conf')):
        if fl == "default.app.conf":
            continue
        if fl.endswith(".app.conf"):
            app_name = re.sub('.app.conf$', '', fl)
            # log("loading "+app_name)
            try:
                app = load_app(app_name)
                apps[app_name] = app
            except Exception as e:
                log.exception("Exception occurred during app kernel configuration loading: " + str(e))


def find_app_by_name(app_name):
    """
    return apps parameters
    if resource configuration file was modified will reload it
    
    raises error if can not find
    """
    global apps
    if app_name not in apps:
        app = load_app(app_name)
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
            resource_specific_app_cfg_filename = os.path.join(cfg_dir, "resources", resource_name,
                                                              app_name + ".app.conf")
            if os.path.isfile(resource_specific_app_cfg_filename):
                if resource_name not in app['appkernelOnResource']:
                    reload_app_cfg = True
                else:
                    if app['appkernelOnResource'][resource_name]['resource_specific_app_cfg_file_last_mod_time'] != \
                            os.path.getmtime(resource_specific_app_cfg_filename):
                        reload_app_cfg = True
    # check if new resources were removed
    for resource_name in app['appkernelOnResource']:
        if resource_name not in ['default']:
            resource_specific_app_cfg_filename = os.path.join(cfg_dir, "resources", resource_name,
                                                              app_name + ".app.conf")
            if not os.path.isfile(resource_specific_app_cfg_filename):
                reload_app_cfg = True

    if reload_app_cfg:
        del apps[app_name]
        app = load_app(app_name)
        apps[app_name] = app
    return apps[app_name]


def print_out_resource_and_app_summary():
    msg = "Resources and app kernels configuration summary:\n"

    msg = msg + "Resources:\n"
    for _, r in resources.items():
        msg = msg + "    "+r['name']

    msg = msg + "Applications:"
    for _, a in apps.items():
        msg = msg + "    {} {}".format(a['name'], a['walllimit'])
    log.info(msg)


# check rest-api certificate
if not os.path.isfile(restapi_certfile):
    # assuming it is relative to akrr.conf file
    restapi_certfile = os.path.abspath(os.path.join(cfg_dir, restapi_certfile))
if not os.path.isfile(restapi_certfile):
    raise ValueError('Cannot locate SSL certificate for rest-api HTTPS server', restapi_certfile)


load_all_resources()

load_all_app()


def getDB(dictCursor=False):
    if dictCursor:
        db = MySQLdb.connect(host=akrr_db_host, port=akrr_db_port, user=akrr_db_user,
                             passwd=akrr_db_passwd, db=akrr_db_name, cursorclass=MySQLdb.cursors.DictCursor)
    else:
        db = MySQLdb.connect(host=akrr_db_host, port=akrr_db_port, user=akrr_db_user,
                             passwd=akrr_db_passwd, db=akrr_db_name)
    cur = db.cursor()
    return db, cur


def getAKDB(dictCursor=False):
    if dictCursor:
        db = MySQLdb.connect(host=ak_db_host, port=ak_db_port, user=ak_db_user,
                             passwd=ak_db_passwd, db=ak_db_name, cursorclass=MySQLdb.cursors.DictCursor)
    else:
        db = MySQLdb.connect(host=ak_db_host, port=ak_db_port, user=ak_db_user,
                             passwd=ak_db_passwd, db=ak_db_name)
    cur = db.cursor()
    return db, cur


def getXDDB(dictCursor=False):
    if dictCursor:
        db = MySQLdb.connect(host=xd_db_host, port=xd_db_port, user=xd_db_user,
                             passwd=xd_db_passwd, db=xd_db_name, cursorclass=MySQLdb.cursors.DictCursor)
    else:
        db = MySQLdb.connect(host=xd_db_host, port=xd_db_port, user=xd_db_user,
                             passwd=xd_db_passwd, db=xd_db_name)
    cur = db.cursor()
    return db, cur


def getExportDB(dictCursor=False):
    if dictCursor:
        db = MySQLdb.connect(host=export_db_host, port=export_db_port, user=export_db_user,
                             passwd=export_db_passwd, db=export_db_name, cursorclass=MySQLdb.cursors.DictCursor)
    else:
        db = MySQLdb.connect(host=export_db_host, port=export_db_port, user=export_db_user,
                             passwd=export_db_passwd, db=export_db_name)
    cur = db.cursor()
    return db, cur
