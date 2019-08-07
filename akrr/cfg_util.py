"""
Configuration utilities for AKRR, resources and app
"""


# pylint: disable=too-many-branches
import os

from akrr.akrrerror import AkrrError
from akrr.cfg import default_dir, cfg_dir
from akrr.util import log


def verify_resource_params(resource: dict, warnings_as_exceptions: bool = False) -> dict:
    """
    Perform simplistic resource.py parameters validation
    raises TypeError or NameError on problems
    """

    import warnings
    # mapped renamed parameters
    renamed_parameters = [
        ('localScratch', 'local_scratch'),
        ('batchJobTemplate', 'batch_job_template'),
        ('remoteAccessNode', 'remote_access_node'),
        ('akrrCommonCommandsTemplate', 'akrr_common_commands_template'),
        ('sshUserName', 'ssh_username'),
        ('sshPassword', 'ssh_password'),
        ('sshPrivateKeyFile', 'ssh_private_key_file'),
        ('sshPrivateKeyPassword', 'ssh_private_key_password'),
        ('remoteAccessMethod', 'remote_access_method'),
        ('batchScheduler', 'batch_scheduler'),
        ('batchJobHeaderTemplate', 'batch_job_header_template'),
        ('appKerDir', 'appkernel_dir'),
        ('AppKerDir', 'appkernel_dir'),
        ('akrrCommonCleanupTemplate', 'akrr_common_cleanup_template'),
        ('akrrData', 'akrr_data'),
        ('autoWalltimeLimit', 'auto_walltime_limit'),
        ('autoWalltimeLimitOverhead', 'auto_walltime_limit_overhead'),
        ('appkernelOnResource', 'appkernel_on_resource'),
        ('networkScratch', 'network_scratch'),
        ('nodeListSetterTemplate', 'node_list_setter_template'),
        ('nodeListSetter', 'node_list_setter'),
        ('runScriptPreRun', 'run_script_pre_run'),
        ('runScriptPostRun', 'run_script_post_run'),
        ('akrrRunAppKer', 'akrr_run_appkernel'),
        ('requestTwoNodesForOneNodeAppKer', 'appkernel_requests_two_nodes_for_one'),
        ('runScript', 'run_script'),
    ]

    for old_key, new_key in renamed_parameters:
        if old_key in resource:
            resource[new_key] = resource[old_key]

            if not warnings_as_exceptions:
                warnings.warn("Resource parameter {} was renamed to {}".format(old_key, new_key), DeprecationWarning)
            else:
                raise DeprecationWarning("Resource parameter {} was renamed to {}".format(old_key, new_key))

    # @todo check string templates for deprecated variables

    # check that parameters for presents and type
    # format: key,type,can be None,must have parameter
    parameters_types = {
        'info': [str, False, False],
        'local_scratch': [str, False, True],
        'batch_job_template': [str, False, True],
        'name': [str, False, False],
        'akrr_common_commands_template': [str, False, True],
        'network_scratch': [str, False, True],
        'ppn': [int, False, True],
        'remote_copy_method': [str, False, True],
        'ssh_username': [str, False, True],
        'ssh_password': [str, True, False],
        'ssh_private_key_file': [str, True, False],
        'ssh_private_key_password': [str, True, False],
        'batch_scheduler': [str, False, True],
        'remote_access_method': [str, False, True],
        'appkernel_dir': [str, False, True],
        'akrr_common_cleanup_template': [str, False, True],
        'akrr_data': [str, False, True],
        'max_number_of_active_tasks': [int, True, True],
    }

    for variable, (m_type, nullable, must) in parameters_types.items():
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
    # level 2 parameters
    # check that parameters for presents and type
    # format: key,type,can be None,must have parameter
    parameters_types_2 = {
        'remote_access_node': [str, True if resource['batch_scheduler'].lower() == "openstack" else False, True]
    }

    for variable, (m_type, nullable, must) in parameters_types_2.items():
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

    # mapped parameters which still uses internally different name
    # these eventually should be renamed
    renamed_parameters = [
    ]

    for old_key, new_key in renamed_parameters:
        if old_key in resource:
            resource[new_key] = resource[old_key]

    return resource


def verify_app_params(app: dict, warnings_as_exceptions: bool = False) -> dict:
    """
    Perform simplistic app.py parameters validation

    raises error
    """

    import warnings
    # mapped renamed parameters
    renamed_parameters = [
        ('input', 'input_param'),
        ('akrrNNodes', 'akrr_num_of_nodes'),
        ('akrrNCores', 'akrr_num_of_cores'),
        ('akrrPPN', 'akrr_ppn'),
        ('akrrTaskWorkingDir', 'akrr_task_work_dir'),
        ('akrrAppKerName', 'akrr_appkernel_name'),
        ('akrrResourceName', 'akrr_resource_name'),
        ('akrrTimeStamp', 'akrr_time_stamp'),
        ('akrrWallTimeLimit', 'akrr_walltime_limit'),
        ('appKernelRunEnvironmentTemplate', 'appkernel_run_env_template'),
        ('akrr_run_appkernelnelTemplate', 'akrr_run_appkernel_template')
    ]

    for old_key, new_key in renamed_parameters:
        if old_key in app:
            app[new_key] = app[old_key]
            if not warnings_as_exceptions:
                warnings.warn("Resource parameter {} was renamed to {}".format(old_key, new_key), DeprecationWarning)
            else:
                raise DeprecationWarning("Resource parameter {} was renamed to {}".format(old_key, new_key))

    # check that parameters for presents and type
    # format: key,type,can be None,must have parameter
    parameters_types = [
        ['parser', str, False, True],
        ['executable', str, True, True],
        ['input_param', str, True, True],
        ['walltime_limit', int, False, True],
        ['run_script', dict, False, False]
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

    # mapped parameters which still uses internally different name
    # these eventually should be renamed
    renamed_parameters = [
    ]

    for old_key, new_key in renamed_parameters:
        if old_key in app:
            app[old_key] = app[new_key]
    return app


def print_resource_and_app_summary(resources=None, apps=None) -> None:
    """
    Print summary on configured resources and apps
    """
    msg = "Resources and app kernels configuration summary:\n"

    if resources is None:
        from akrr.cfg import resources
    if apps is None:
        from akrr.cfg import apps

    msg = msg + "Resources:\n"
    for _, r in resources.items():
        msg = msg + "    " + r['name']

    msg = msg + "Applications:"
    for _, a in apps.items():
        msg = msg + "    {} {}".format(a['name'], a['walltime_limit'])
    log.info(msg)


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

        # last modification time for future reloading
        resource['default_resource_cfg_filename'] = default_resource_cfg_filename
        resource['resource_cfg_filename'] = resource_cfg_filename
        resource['resource_cfg_directory'] = os.path.dirname(resource_cfg_filename)
        resource['default_resource_cfg_file_last_mod_time'] = os.path.getmtime(default_resource_cfg_filename)
        resource['resource_cfg_file_last_mod_time'] = os.path.getmtime(resource_cfg_filename)

        # here should be validation
        resource = verify_resource_params(resource)

        return resource
    except Exception:
        log.exception("Exception occurred during resource configuration loading for %s." % resource_name)
        raise AkrrError("Can not load resource configuration for %s." % resource_name)


def load_app(app_name):
    """
    load app configuration file, do minimalistic validation
    return dict with app parameters

    raises error if can not load
    """
    from akrr.util import exec_files_to_dict
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
                app_on_resource_cfg_filename = os.path.join(cfg_dir, "resources", resource_name,
                                                            app_name + ".app.conf")
                if os.path.isfile(app_on_resource_cfg_filename):
                    app['appkernel_on_resource'][resource_name] = exec_files_to_dict(
                        app_on_resource_cfg_filename, var_in=app['appkernel_on_resource']['default'])
                    app['appkernel_on_resource'][resource_name][
                        'resource_specific_app_cfg_filename'] = app_on_resource_cfg_filename
                    app['appkernel_on_resource'][resource_name]['resource_specific_app_cfg_file_last_mod_time'] = \
                        os.path.getmtime(app_on_resource_cfg_filename)

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
        app = verify_app_params(app)

        return app
    except Exception:
        log.exception("Exception occurred during app kernel configuration loading for %s." % app_name)
        raise AkrrError("Can not load app configuration for %s." % app_name)

