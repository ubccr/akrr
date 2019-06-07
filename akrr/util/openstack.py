"""
OpenStack utilities
"""
import os
import json
import time
import random
from akrr.util import log
from akrr.util import ssh


class OpenStack:
    """
    Wrapper for OpenStack command line interface
    """
    def __init__(self, openstack_env_set_script="openstack_env_set.sh"):
        self._openstack_env_set_script = openstack_env_set_script
        self._which_openstack_env_set_script = None
        self._shell = None
        self._token = None

        print("Start Session")
        self._start_session()

    def _start_session(self):
        import akrr.pexpect.replwrap

        self._shell = akrr.pexpect.replwrap.bash()

        self._set_openstack_env()

    def _set_openstack_env(self):
        # get location of openstack_env_set_script
        if self._which_openstack_env_set_script is None:
            if os.path.isfile(self._openstack_env_set_script):
                self._which_openstack_env_set_script = self._openstack_env_set_script
            else:
                self._which_openstack_env_set_script = self._shell.run_command("which "+self._openstack_env_set_script)
                self._which_openstack_env_set_script = self._which_openstack_env_set_script.strip()

                if self._which_openstack_env_set_script.endswith(self._openstack_env_set_script):
                    self._which_openstack_env_set_script = os.path.expanduser(self._which_openstack_env_set_script)
            log.debug("which_openstack_env_set_script: " + self._which_openstack_env_set_script)

        # check presence of openstack_env_set_script
        if not os.path.isfile(self._which_openstack_env_set_script):
            msg = "Can not find openstack environment setup script: " + self._openstack_env_set_script
            msg += "\n" + self._which_openstack_env_set_script
            log.error(msg)
            raise FileNotFoundError(msg)

        # set environment
        self.run_cmd("source " + self._which_openstack_env_set_script)
        self._token = self.run_cmd("echo $OS_TOKEN").strip()

    def run_cmd(self, cmd):
        out = self._shell.run_command(cmd)
        log.debug(cmd+"\n"+out)
        return out

    def run_open_stack_cmd(self, cmd):
        out = self._shell.run_command("openstack "+cmd)
        log.debug(cmd+"\n"+out)
        if out.count("Failed to validate token"):
            self._set_openstack_env()
            out = self._shell.run_command("openstack "+cmd)
            log.debug(cmd+"\n"+out)
            if out.count("Failed to validate token"):
                raise Exception("Can not execute openstack command!\n"+out)
        return out

    def token_revoke(self):
        if self._token is not None:
            self.run_open_stack_cmd("token revoke "+self._token)


class OpenStackServer:
    def __init__(self, resource=None, openstack=None, name=None,
                 flavor=None, volume=None, network=None, security_group=None, key_name=None,
                 ssh_username=None, ssh_private_key_file=None,
                 floating_ip_attach=False):
        from akrr.util import get_full_path
        if resource is not None:
            # @todo check that it is not spinning already
            self.openstack = OpenStack(get_full_path(
                resource["resource_cfg_directory"], resource["openstack_env_set_script"]))
            self.flavor = resource["openstack_flavor"]
            self.volume = resource["openstack_volume"]
            self.network = resource["openstack_network"]
            self.security_group = resource["openstack_security_group"]
            self.key_name = resource["openstack_key_name"]
            self.name = resource["openstack_server_name"]
            self.ssh_username = resource["ssh_username"]
            self.ssh_private_key_file = resource["ssh_private_key_file"]
            self.floating_ip_attach = resource["openstack_floating_ip_attach"]
        else:
            self.openstack = openstack
            self.flavor = flavor
            self.volume = volume
            self.network = network
            self.security_group = security_group
            self.key_name = key_name
            self.ssh_username = ssh_username
            self.ssh_private_key_file = ssh_private_key_file
            self.name = name
            self.floating_ip_attach = floating_ip_attach
        self.internal_network_ip = None
        self.flexible_ip = None
        self.ip = None

    def is_server_running(self):
        """check if server with same name already up"""
        out = self.openstack.run_open_stack_cmd("server list -f json --name "+self.name)
        out = json.loads(out.strip())
        if len(out) == 0:
            return False
        else:
            return True

    def _detect_network(self):
        out = self.openstack.run_open_stack_cmd("server list -f json --name " + self.name)
        out = json.loads(out.strip())
        if len(out) == 0:
            raise Exception("Openstack server didn't start!")
        out = out[0]

        s = out["Networks"]
        all_ips = s[s.find('=') + 1:].replace(',', ' ').split()
        self.internal_network_ip = all_ips[0]
        log.debug("internal_network_ip: "+self.internal_network_ip)
        if len(all_ips) > 1:
            self.flexible_ip = all_ips[-1]
            log.debug("flexible_ip: "+self.flexible_ip)
        self.ip = all_ips[-1]

    def create(self, delete_if_exists=False):
        if self.is_server_running():
            if delete_if_exists:
                self.delete()
            else:
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

        self.openstack.run_open_stack_cmd(" ".join(args))

        out = self.openstack.run_open_stack_cmd("server list -f json --name " + self.name)
        out = json.loads(out.strip())
        if len(out) == 0:
            raise Exception("Openstack server didn't start!")
        out = out[0]
        print(out)

        # wait for network
        if self.network is not None:
            while True:
                out = self.openstack.run_open_stack_cmd("server list -f json --name " + self.name)
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

            self.openstack.run_cmd("ssh-keygen -R %s" % self.internal_network_ip)

        # attach floating ip
        if self.floating_ip_attach:
            # get unused ip
            out = self.openstack.run_open_stack_cmd("floating ip list --long --status DOWN -f json")
            out = json.loads(out.strip())
            if len(out) == 0:
                raise Exception("Can not attach floating ip, there is no one available.!")
            # attach ip
            ip = out[random.randrange(len(out))]["Floating IP Address"]
            self.openstack.run_open_stack_cmd("server add floating ip %s %s" % (self.name, ip))

            # check
            out = self.openstack.run_open_stack_cmd("server list -f json --name " + self.name)
            out = json.loads(out.strip())
            s = out[0]["Networks"]
            all_ips = s[s.find('=') + 1:].replace(',', ' ').split()
            if ip not in all_ips:
                raise Exception("Can not attach floating ip!")

            self.flexible_ip = ip
            self.ip = ip

            self.openstack.run_cmd("ssh-keygen -R %s" % self.flexible_ip)

        # wait for ssh to get up
        if self.ssh_private_key_file is not None:
            ssh.ssh_access_multytry(self.ip, username=self.ssh_username, private_key_file=self.ssh_private_key_file,
                                    number_of_attempts=12, sleep_time=5, command="uname -a")
        else:
            time.sleep(5)

    def delete(self):
        count = 0
        while self.is_server_running():
            self.openstack.run_open_stack_cmd("server delete " + self.name)
            if count > 0:
                time.sleep(1)
            count += 1
            if count > 60:
                raise Exception("Can not delete server!")


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
        "floating_ip_attach": True
    }
    server = OpenStackServer(**server_param)
    server.create(delete_if_exists=True)
