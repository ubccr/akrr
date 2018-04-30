"""Execution of akrr resource config"""
from pprint import pprint

from akrr import log

from .util import get_bash

from . import cfg

super_fast_timeout = 1


def resource_add(
        resource_id=0,
        resource_name='localhost',
        queuing_system='slurm',
        headnode='localhost',
        user='user',
        ppn=4,
        local_scratch="",
        network_scratch="/scratch",
        appker_dir="",
        akrr_wd_dir="",
        ping_resource=True):
    # start bash shell

    bash = get_bash()
    bash.output = ""
    bash.timeoutMessage = 'Unexpected behavior of prep.sh (premature EOF or TIMEOUT)'

    bash.runcmd('which python3', printOutput=True)
    bash.runcmd('which ' + cfg.which_akrr, printOutput=True)

    cmd = "{}{} resource add{}{}".format(
        cfg.which_akrr,
        " -v" if cfg.verbose else "",
        " --dry-run" if cfg.dry_run else "",
        " --no-ping" if not ping_resource else "")

    bash.startcmd(cmd)

    # system access
    bash.expectSendline(
        r'.*INPUT.* Enter resource_id for import.*\n',
        str(resource_id), timeout=super_fast_timeout)

    bash.expectSendline(
        r'.*INPUT.* Enter AKRR resource name.*\n',
        resource_name, timeout=super_fast_timeout)

    bash.expectSendline(
        r'.*INPUT.* Enter queuing system on resource.*\n',
        queuing_system, timeout=super_fast_timeout)

    bash.expectSendline(
        r'.*INPUT.* Enter Resource head node.*\n\[\S+\] ',
        headnode, timeout=super_fast_timeout)

    bash.expectSendline(
        r'.*INPUT.* Enter username for resource access.*\n\[\S+\] ',
        user, timeout=super_fast_timeout)

    # @todo here should be options for password and public key

    # now system tries to access remote node
    bash.justExpect("Connecting to", timeout=30)
    bash.justExpect("Done", timeout=30)
    # system characteristics
    bash.expectSendline(
        r'.*INPUT.* Enter processors \(cores\) per node count.*\n',
        str(ppn), timeout=super_fast_timeout)

    bash.expectSendline(
        r'.*INPUT.* Enter location of local scratch.*\n.*\[\S+\]',
        local_scratch, timeout=super_fast_timeout)

    bash.expectSendline(
        r'.*INPUT.* Enter location of network scratch.*\n',
        network_scratch, timeout=super_fast_timeout)

    bash.expectSendline(
        r'.*INPUT.* Enter future location of app kernels input and executable files.*\n.*\[\S+\]',
        appker_dir, timeout=super_fast_timeout)

    bash.expectSendline(
        r'.*INPUT.* Enter future locations for app kernels working directories.*\n.*\[\S+\]',
        akrr_wd_dir, timeout=super_fast_timeout)

    bash.justExpect("Initiation of new resource is completed", timeout=30)
    bash.justExpect(bash.prompt)
    # @todo check presence of dirs in remote resource

    # here should be post editing


def add_all_resources(resource=None, **_):
    log.info("resource config: Initial resource configuration")
    if resource is not None or resource == "":
        resources_to_include = [r.stip() for r in resource.split(",")]
    else:
        resources_to_include = None

    resources_to_add = []

    if 'resource' not in cfg.yml:
        return

    for resource_rec in cfg.yml['resource']:
        if resources_to_include is None:
            resources_to_add.append(resource_rec)
        elif 'resource_name' is resource_rec and resource_rec['resource_name'] in resources_to_include:
            resources_to_add.append(resource_rec)

    for resource_rec in resources_to_add:
        resource_add(**resource_rec)


def resource_deploy(resource_name, test_appkernel=None, test_nodes=None, deploy_timeout=600, **_):
    bash = get_bash()
    bash.output = ""
    bash.timeoutMessage = 'Unexpected behavior of prep.sh (premature EOF or TIMEOUT)'

    bash.runcmd('which python3', printOutput=True)
    bash.runcmd('which ' + cfg.which_akrr, printOutput=True)

    # now deploy
    cmd = "{}{} resource deploy{}{}{}{}".format(
        cfg.which_akrr,
        " -v" if cfg.verbose else "",
        " -r " + resource_name,
        " -a {}".format(test_appkernel) if test_appkernel is not None else "",
        " --dry-run" if cfg.dry_run else "",
        " -n" if test_nodes is not None else "")
    bash.startcmd(cmd+" > out")

    bash.justExpect(bash.prompt, timeout=deploy_timeout)

    out=open("out", "rt").read()
    if out.count("you can move to next step")==0:
        log.error("Unsuccessful deployment\n"+out)
        exit(1)


def deploy_all_resources(resource=None, **_):
    log.info("Deploying AK to resources")
    if resource is not None or resource == "":
        resources_to_include = [r.stip() for r in resource.split(",")]
    else:
        resources_to_include = None

    resources_to_add = []

    if 'resource' not in cfg.yml:
        return

    for resource_rec in cfg.yml['resource']:
        if resources_to_include is None:
            resources_to_add.append(resource_rec)
        elif 'resource_name' is resource_rec and resource_rec['resource_name'] in resources_to_include:
            resources_to_add.append(resource_rec)

    for resource_rec in resources_to_add:
        resource_deploy(**resource_rec)


def cli_resource_add(parent_parser):
    """Configure new resource to AKRR"""
    parser = parent_parser.add_parser('add',
                                      description=cli_resource_add.__doc__)
    parser.add_argument(
        '-r', '--resource', help="name of resource for validation and deployment'")

    def handler(args):
        return add_all_resources(**vars(args))

    parser.set_defaults(func=handler)


def cli_resource_deploy(parent_parser):
    """deploy new resource to AKRR"""
    parser = parent_parser.add_parser('deploy',
                                      description=cli_resource_deploy.__doc__)
    parser.add_argument(
        '-r', '--resource', help="name of resource for validation and deployment'")

    def handler(args):
        return deploy_all_resources(**vars(args))

    parser.set_defaults(func=handler)


def cli_resource(parent_parser):
    """Resource manipulation"""
    parser = parent_parser.add_parser('resource', description=cli_resource.__doc__)
    subparsers = parser.add_subparsers(title="commands for resource")

    cli_resource_add(subparsers)
    cli_resource_deploy(subparsers)
