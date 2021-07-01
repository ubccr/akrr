"""
GoogleCloud utilities
"""
import os
import json
import time
import random
from akrr.util import log
from akrr.util import ssh

from akrr.akrrerror import AkrrOpenStackException

from pprint import pprint
class GoogleCloudCLI:
    """
    Wrapper for GoogleCloud command line interface
    """
    def __init__(self, env_set_script=None):
        self._env_set_script = env_set_script
        self._which_env_set_script = None
        self._shell = None
        self._token = None

        print("Start Session")
        self._start_session()

    def __del__(self):
        """
        Do token revocation to solve problem with having too many tokens.
        """
        self.token_revoke()

    def _start_session(self):
        import akrr.pexpect.replwrap

        self._shell = akrr.pexpect.replwrap.bash()

        self._set_env()

    def _set_env(self):
        # get location of _env_set_script
        if self._which_env_set_script is None and self._env_set_script is not None:
            if os.path.isfile(self._env_set_script):
                self._which_env_set_script = self._env_set_script
            else:
                self._which_env_set_script = self._shell.run_command("which " + self._env_set_script)
                self._which_env_set_script = self._which_env_set_script.strip()

                if self._which_env_set_script.endswith(self._env_set_script):
                    self._which_env_set_script = os.path.expanduser(self._which_env_set_script)
            log.debug("_which_env_set_script: " + self._which_env_set_script)

        # check presence of _which_env_set_script
        if self._which_env_set_script is not None and not os.path.isfile(self._which_env_set_script):
            msg = "Can not find google cloud environment setup script: " + self._env_set_script
            msg += "\n" + self._which_env_set_script
            log.error(msg)
            raise FileNotFoundError(msg)

        # set environment
        if self._which_env_set_script is not None:
            self.run_cmd("source " + self._which_env_set_script)
            # self._token = self.run_cmd("echo $OS_TOKEN").strip()

    def run_cmd(self, cmd):
        out = self._shell.run_command(cmd)
        log.debug(cmd+"\n"+out)
        return out

    def run_cloud_cmd(self, cmd):
        out = self._shell.run_command("gcloud "+cmd)
        return out

    def token_revoke(self):
        if self._token is not None:
            # self.run_open_stack_cmd("token revoke "+self._token)
            pass

class GoogleCloudServer:
    def __init__(self, resource=None, cloud_cli=None,
                 project=None, name=None,
                 zone=None, machine_type=None, network_tier=None,
                 image=None, image_project=None,
                 boot_disk_size=None, boot_disk_type=None, boot_disk_device_name=None,
                 ssh_username=None, ssh_private_key_file=None,
                 docker_username=None, docker_password=None, task_id=None):
        if resource is not None:
            self.cloud_cli = GoogleCloudCLI()
            self.project = resource["googlecloud_project"]
            self.name = resource["googlecloud_name"]
            self.zone = resource["googlecloud_zone"]
            self.machine_type = resource["googlecloud_machine_type"]
            self.network_tier = resource["googlecloud_network_tier"]
            self.image = resource["googlecloud_image"]
            self.image_project = resource["googlecloud_image_project"]
            self.boot_disk_size = resource["googlecloud_boot_disk_size"]
            self.boot_disk_type = resource["googlecloud_boot_disk_type"]
            self.boot_disk_device_name = resource["googlecloud_boot_disk_device_name"]
            self.ssh_username = resource["ssh_username"]
            self.ssh_private_key_file = resource["ssh_private_key_file"]
            self.docker_username = resource["docker_username"]
            self.docker_password = resource["docker_password"]
        else:
            self.cloud_cli = cloud_cli
            self.project = project
            self.name = name
            self.zone = zone
            self.machine_type = machine_type
            self.network_tier = network_tier
            self.image = image
            self.image_project = image_project
            self.boot_disk_size = boot_disk_size
            self.boot_disk_type = boot_disk_type
            self.boot_disk_device_name = boot_disk_device_name
            self.ssh_username = ssh_username
            self.ssh_private_key_file = ssh_private_key_file
            self.docker_username = docker_username
            self.docker_password = docker_password

        if task_id is not None:
            self.name += "-" + str(task_id)
            self.boot_disk_device_name += "-" + str(task_id)
        self.internal_network_ip = None
        self.flexible_ip = None
        self.ip = None

    def is_server_running(self, shut_off_is_down: bool = False) -> bool:
        """check if server with same name already up"""
        out = self.cloud_cli.run_cloud_cmd(
            f"compute --project={self.project}  instances describe --zone={self.zone} {self.name} --format=json")
        try:
            out = json.loads(out.strip())
        except json.JSONDecodeError:
            return False
        return True

    def _detect_network(self):
        if self.network_tier is not None:
            while True:
                out = self.cloud_cli.run_cloud_cmd(
                    f"compute --project={self.project}  instances describe --zone={self.zone} {self.name} --format=json")
                try:
                    out = json.loads(out.strip())
                except json.JSONDecodeError:
                    raise Exception("server didn't start!")

                if "networkInterfaces" in out and len(out["networkInterfaces"]) > 0 and \
                        "accessConfigs" in out["networkInterfaces"][0] and \
                        len(out["networkInterfaces"][0]["accessConfigs"])>0 and \
                        "natIP" in out["networkInterfaces"][0]["accessConfigs"][0] and \
                        out["networkInterfaces"][0]["accessConfigs"][0]["natIP"] != "":
                    break
                else:
                    time.sleep(1)
            self.internal_network_ip = out["networkInterfaces"][0]["networkIP"]
            self.ip = out["networkInterfaces"][0]["accessConfigs"][0]["natIP"]
            self.flexible_ip = self.ip
            log.debug("flexible_ip: "+self.flexible_ip)

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
            "beta", "compute",
            "--project=" + self.project,
            "instances", "create", self.name,
            "--zone=" + self.zone,
            "--machine-type=" + self.machine_type,
            "--subnet=default",
            "--network-tier=" + self.network_tier,
            "--maintenance-policy=MIGRATE",
            "--no-service-account",
            "--no-scopes",
            "--image=" + self.image,
            "--image-project=" + self.image_project,
            "--boot-disk-size=" + self.boot_disk_size,
            "--boot-disk-type=" + self.boot_disk_type,
            "--boot-disk-device-name=" + self.boot_disk_device_name,
            "--no-shielded-secure-boot",
            "--shielded-vtpm",
            "--shielded-integrity-monitoring",
            "--reservation-affinity=any",
            "--format=json"
        ]

        out = self.cloud_cli.run_cloud_cmd(" ".join(args))
        pprint(out)

        out = self.cloud_cli.run_cloud_cmd(
            f"compute --project={self.project}  instances describe --zone={self.zone} {self.name} --format=json")
        try:
            out = json.loads(out.strip())
        except json.JSONDecodeError:
            print(out)
            raise Exception("server didn't start!")
        pprint(out)

        # wait for network
        if self.network_tier is not None:
            self._detect_network()
            self.cloud_cli.run_cmd("ssh-keygen -R %s" % self.ip)
        # add key
        out = self.cloud_cli.run_cloud_cmd(
            f"compute --project={self.project}  instances add-metadata {self.name} --zone={self.zone} --metadata-from-file ssh-keys={self.ssh_private_key_file}.pub --format=json")

        # wait for ssh to get up
        if self.ssh_private_key_file is not None:
            ssh.ssh_access_multytry(self.ip, username=self.ssh_username, private_key_file=self.ssh_private_key_file,
                                    number_of_attempts=20, sleep_time=5, command="uname -a")
        else:
            time.sleep(5)

        # login to docker
        if self.docker_username is not None and self.docker_password is not None:
            rsh = ssh.ssh_access_multytry(self.ip, username=self.ssh_username,
                                          private_key_file=self.ssh_private_key_file,
                                          number_of_attempts=20, sleep_time=5)
            rsh.sendline(f"docker login -u {self.docker_username}")
            rsh.expect("Password:", timeout=ssh.ssh_timeout)
            rsh.sendline(self.docker_password)
            rsh.expect(ssh.shell_prompt, timeout=ssh.ssh_timeout)

    def delete(self):
        # stop
        count = 0
        while self.is_server_running():
            if count % 30 == 0:
                self.cloud_cli.run_cloud_cmd(f"compute --project={self.project}  instances delete {self.name} --zone={self.zone} --format=json --quiet")
            if count > 0:
                time.sleep(1)
            count += 1
            if count > 60:
                raise Exception("Can not delete server!")


if __name__ == "__main__":
    log.set_verbose()
    server_param = {
        "cloud_cli": GoogleCloudCLI(),
        "project": "buffalo-openxdmod",
        "name": "akrr-test",
        "zone": "us-central1-a",
        "machine_type": "e2-highcpu-32",
        "network_tier": "PREMIUM",
        "image": "cos-89-16108-470-1",
        "image_project": "cos-cloud",
        "boot_disk_size": "30GB",
        "boot_disk_type": "pd-balanced",
        "boot_disk_device_name": "akrr_test",
        "ssh_username": "nsimakov_cm",
        "ssh_private_key_file": os.path.expanduser("~/.ssh/id_rsa_googlcloud"),
        "docker_username": "nsimakov",
        "docker_password": ""
    }
    server = GoogleCloudServer(**server_param)
    server.create(delete_if_exists=True)

    rsh = ssh.ssh_access_multytry(server.ip, username=server.ssh_username,
                                          private_key_file=server.ssh_private_key_file,
                                          number_of_attempts=20, sleep_time=5)

    ssh.ssh_command(rsh, "docker run -it --rm  --shm-size=4g nsimakov/appker:hpcc", 1200)
    ssh.ssh_command(rsh, "docker run -it --rm  --shm-size=4g nsimakov/containers:namd", 1200)
    #print(out)

    server.delete()

