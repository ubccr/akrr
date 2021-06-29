"""
OpenStack utilities
"""
import os
import json
import time
import random
from akrr.util import log
from akrr.util import ssh

from akrr.akrrerror import AkrrOpenStackException


class OpenStack:
    """
    Wrapper for OpenStack command line interface
    """
    def __init__(self, env_set_script="openstack_env_set.sh"):
        self._env_set_script = env_set_script
        self._which_env_set_script = None
        self._shell = None
        self._token = None

        print("Start Session")
        self._start_session()

    def __del__(self):
        """
        Do tocken revocation to solve problem with having too many tokens.
        """
        self.token_revoke()

    def _start_session(self):
        import akrr.pexpect.replwrap

        self._shell = akrr.pexpect.replwrap.bash()

        self._set_env()

    def _set_env(self):
        # get location of openstack_env_set_script
        if self._which_env_set_script is None:
            if os.path.isfile(self._env_set_script):
                self._which_env_set_script = self._env_set_script
            else:
                self._which_env_set_script = self._shell.run_command("which " + self._env_set_script)
                self._which_env_set_script = self._which_env_set_script.strip()

                if self._which_env_set_script.endswith(self._env_set_script):
                    self._which_env_set_script = os.path.expanduser(self._which_env_set_script)
            log.debug("which_openstack_env_set_script: " + self._which_env_set_script)

        # check presence of openstack_env_set_script
        if not os.path.isfile(self._which_env_set_script):
            msg = "Can not find openstack environment setup script: " + self._env_set_script
            msg += "\n" + self._which_env_set_script
            log.error(msg)
            raise FileNotFoundError(msg)

        # set environment
        self.run_cmd("source " + self._which_env_set_script)
        self._token = self.run_cmd("echo $OS_TOKEN").strip()

    def run_cmd(self, cmd):
        out = self._shell.run_command(cmd)
        log.debug(cmd+"\n"+out)
        return out

    def run_cloud_cmd(self, cmd):
        out = self._shell.run_command("openstack "+cmd)
        log.debug(cmd+"\n"+out)
        if out.count("Failed to validate token"):
            self._set_env()
            out = self._shell.run_command("openstack "+cmd)
            log.debug(cmd+"\n"+out)
            if out.count("Failed to validate token"):
                raise Exception("Can not execute openstack command!\n"+out)
        return out

    def token_revoke(self):
        if self._token is not None:
            self.run_cloud_cmd("token revoke " + self._token)


class OpenStackServer:
    def __init__(self, resource=None, cloud_cli=None, name=None,
                 flavor=None, volume=None, network=None, security_group=None, key_name=None,
                 ssh_username=None, ssh_private_key_file=None,
                 floating_ip_attach=False, floating_ip_network=None,
                 floating_ip_delete_after_use=False):
        from akrr.util import get_full_path
        if resource is not None:
            # @todo check that it is not spinning already
            self.cloud_cli = OpenStack(get_full_path(
                resource["resource_cfg_directory"], resource["openstack_env_set_script"]))
            self.flavor = resource["openstack_flavor"]
            self.volume = resource["openstack_volume"]
            self.network = resource["openstack_network"]
            self.security_group = resource["openstack_security_group"]
            self.key_name = resource["openstack_key_name"]
            self.name = resource["openstack_server_name"]
            self.ssh_username = resource["ssh_username"]
            self.ssh_private_key_file = resource["ssh_private_key_file"]
            self.floating_ip_attach = resource.get("openstack_floating_ip_attach", False)
            self.floating_ip_network = resource.get("openstack_floating_ip_network", None)
            self.floating_ip_delete_after_use = resource.get("openstack_floating_ip_delete_after_use", False)
        else:
            self.cloud_cli = cloud_cli
            self.flavor = flavor
            self.volume = volume
            self.network = network
            self.security_group = security_group
            self.key_name = key_name
            self.ssh_username = ssh_username
            self.ssh_private_key_file = ssh_private_key_file
            self.name = name
            self.floating_ip_attach = floating_ip_attach
            self.floating_ip_network = floating_ip_network
            self.floating_ip_delete_after_use = floating_ip_delete_after_use
        self.internal_network_ip = None
        self.flexible_ip = None
        self.ip = None

    def is_server_running(self, shut_off_is_down: bool = False) -> bool:
        """check if server with same name already up"""
        cmd = "server list -f json --name "+self.name
        out = self.cloud_cli.run_cloud_cmd(cmd)
        try:
            out = json.loads(out.strip())
        except json.JSONDecodeError as e:  # added to hopefully track error better
            log.error("Can get status of OpenStack instance:")
            log.error("Command: " + cmd)
            log.error("Output: " + out)
            raise e
        if len(out) == 0:
            return False
        else:
            if shut_off_is_down:
                if "Status" in out[0]:
                    if out[0]["Status"] == "SHUTOFF":
                        return False
                    else:
                        return True
                else:
                    raise AkrrOpenStackException("No status record for instance:%s" % str(out[0]))

            else:
                return True

    def _detect_network(self):
        out = self.cloud_cli.run_cloud_cmd("server list -f json --name " + self.name)
        out = json.loads(out.strip())
        if len(out) == 0:
            raise Exception("Openstack server didn't start!")
        out = out[0]

        s = out["Networks"]
        all_ips = s[s.find('=') + 1:].replace(',', ' ').split()
        # Get only ip4
        all_ips = [ip for ip in all_ips if ip.count(".") > 0]
        self.internal_network_ip = all_ips[0]
        log.debug("internal_network_ip: "+self.internal_network_ip)
        if len(all_ips) > 1:
            self.flexible_ip = all_ips[-1]
            log.debug("flexible_ip: "+self.flexible_ip)
        self.ip = all_ips[-1]

    def create(self, delete_if_exists=False):
        if self.is_server_running(shut_off_is_down=True):
            if delete_if_exists:
                log.debug("Container with same name is already running. Will delete it and create it again.")
                self.delete()
            else:
                log.debug("Container with same name is already running, will reuse it.")
                self._detect_network()
                return

        args = [
            "server create",
            "--flavor " + self.flavor,
            "--volume " + self.volume,
            "--network " + self.network,
            "--key-name " + self.key_name
        ]

        if self.security_group is not None and isinstance(self.security_group, (list, tuple)):
            args.append(" ".join(["--security-group " + v for v in self.security_group]))
        args.append(self.name)

        self.cloud_cli.run_cloud_cmd(" ".join(args))

        out = self.cloud_cli.run_cloud_cmd("server list -f json --name " + self.name)
        out = json.loads(out.strip())
        if len(out) == 0:
            raise Exception("Openstack server didn't start!")
        out = out[0]
        print(out)

        # wait for network
        if self.network is not None:
            while True:
                out = self.cloud_cli.run_cloud_cmd("server list -f json --name " + self.name)
                out = json.loads(out.strip())
                if len(out) == 0:
                    raise Exception("Openstack server didn't start!")
                out = out[0]
                if out["Networks"] == "":
                    time.sleep(1)
                else:
                    break

            s = out["Networks"]
            self.internal_network_ip = s[s.find('=')+1:].replace(',', ' ').split()[0]
            log.debug("internal_network_ip:" + self.internal_network_ip)
            self.ip = self.internal_network_ip

            self.cloud_cli.run_cmd("ssh-keygen -R %s" % self.internal_network_ip)

        # attach floating ip
        if self.floating_ip_attach:
            # get unused ip
            floating_ip_creating_count = 0
            while True:
                out = self.cloud_cli.run_cloud_cmd("floating ip list --long --status DOWN -f json")
                out = json.loads(out.strip())
                if len(out) == 0 and (self.floating_ip_network is None or floating_ip_creating_count > 0):
                    raise Exception("Can not attach floating ip, there is no one available.!")
                if len(out) == 0 and self.floating_ip_network is not None:
                    # create floating ip, if floating_ip_network provided
                    self.cloud_cli.run_cloud_cmd("floating ip create " + self.floating_ip_network)
                    floating_ip_creating_count += 1
                if len(out) > 0:
                    break

            # attach ip
            ip = out[random.randrange(len(out))]["Floating IP Address"]
            self.cloud_cli.run_cloud_cmd("server add floating ip %s %s" % (self.name, ip))

            # check
            out = self.cloud_cli.run_cloud_cmd("server list -f json --name " + self.name)
            out = json.loads(out.strip())
            s = out[0]["Networks"]
            all_ips = s[s.find('=') + 1:].replace(',', ' ').split()
            if ip not in all_ips:
                raise Exception("Can not attach floating ip!")

            self.flexible_ip = ip
            self.ip = ip

            self.cloud_cli.run_cmd("ssh-keygen -R %s" % self.flexible_ip)

        # wait for ssh to get up
        if self.ssh_private_key_file is not None:
            ssh.ssh_access_multytry(self.ip, username=self.ssh_username, private_key_file=self.ssh_private_key_file,
                                    number_of_attempts=20, sleep_time=5, command="uname -a")
        else:
            time.sleep(5)

    def delete(self):
        # release floating ip
        if self.floating_ip_attach and self.flexible_ip:
            self.cloud_cli.run_cmd("server remove floating %s %s" % (self.name, self.flexible_ip))
        # stop
        count = 0
        while self.is_server_running(shut_off_is_down=True):
            if count % 30 == 0:
                self.cloud_cli.run_cloud_cmd("server stop " + self.name)
            if count > 0:
                time.sleep(1)
            count += 1
            if count > 60:
                raise Exception("Can not stop server!")
        # delete
        count = 0
        while self.is_server_running():
            if count % 30 == 0:
                self.cloud_cli.run_cloud_cmd("server delete " + self.name)
            if count > 0:
                time.sleep(1)
            count += 1
            if count > 60:
                raise Exception("Can not delete server!")
        # delete floating ip
        if self.floating_ip_delete_after_use and self.flexible_ip:
            self.cloud_cli.run_cmd("floating ip delete %s" % self.flexible_ip)


if __name__ == "__main__":
    log.set_verbose()
    server_param = {
        "openstack": OpenStack(),
        "flavor": "c1.m4",
        "volume": "aktestvolume",
        "network": "XDMoD",
        "security_group": ("default", "allow-from-ub"),
        "key_name": "nikolays",
        "name": "aktest",
        "floating_ip_attach": True,
        "floating_ip_network": True,
        "floating_ip_delete_after_use": False
    }
    server = OpenStackServer(**server_param)
    server.create(delete_if_exists=True)
