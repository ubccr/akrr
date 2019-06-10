## Notes on trying to get akrr to run on openstack and run the various docker images..?

NOTE: with the resource config, it makes a new instance on openstack, so the attached volume should have the docker already installed on it
- Gonna start by trying that

```bash
# making volume with docker on it
openstack volume create --image centos7-ccr-20181127-1 --size 20 --description "volume to put docker on" dockervolume

# spinning off instance
openstack server create --flavor c8.m16 --volume dockervolume --network lakeeffect-199.109.195 --security-group default --security-group SSH --key-name openstack-testing akrrtemp

# ssh into the volume
ssh -i openstack-testing.key centos@199.109.192.15

```
Then I needed to install docker on the volume.
Followed instructions here: https://docs.docker.com/install/linux/docker-ce/centos/

```bash
sudo yum install -y yum-utils \
  device-mapper-persistent-data \
  lvm2

sudo yum-config-manager \
    --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo

sudo yum install docker-ce docker-ce-cli containerd.io

sudo systemctl start docker
# now we want to make it so that any user can use docker, not just super users

# stop docker daemon
sudo systemctl stop docker

sudo groupadd docker
sudo usermod -aG docker $USER
# so the centos user should be fine now to use docker normally
```
So now, in theory, docker is installed on the volume.
I'll try stopping the instance and starting up another with the same volume and we'll see if it works
- Stopped instance and deleted it
- Now will try to start a new instance and run docker commands on it

```bash
openstack server create --flavor c8.m16 --volume dockervolume --network lakeeffect-199.109.195 --security-group default --security-group SSH --key-name openstack-testing akrrtemp

ssh -i openstack-testing.key centos@199.109.192.13

# success! but we do need to start the docker daemon first
sudo systemctl start docker
docker run hello-world

# so the volume with docker on it is: dockervolume

```
so now we want to deploy the resource.
First make the resource and such (this now from OpenStackNotes.md)

```bash
akrr resource add --minimalistic
```

```text
[INFO] Beginning Initiation of New Resource...
[INFO] Retrieving Resources from XDMoD Database...
[INFO] Found following resources from XDMoD Database:
    resource_id  name
              1  UBHPC                                   
              2  ub-hpc                                  
[INPUT]: Enter resource_id for import (enter 0 for no match):
2
[INPUT]: Enter AKRR resource name, hit enter to use same name as in XDMoD Database [ub-hpc]:
lakeeffect
[INPUT]: Enter queuing system on resource (slurm, pbs or openstack): 
openstack
[INFO] Initiating lakeeffect at AKRR
[INFO] Resource configuration is in /home/akrruser/akrr_src2/etc/resources/lakeeffect/resource.conf
[INFO] Initiation of new resource is completed.
    Edit batch_job_header_template variable in /home/akrruser/akrr_src2/etc/resources/lakeeffect/resource.conf
    and move to resource validation and deployment step.
    i.e. execute:
        akrr resource deploy -r lakeeffect
```

Copy enviroment setter to akrr resource config directory:

```bash eval=F
cp <somewhere>/lakeeffect-xdmod-openrc.sh /home/akrruser/akrr/etc/resources/lakefffect
```

```bash
# I edited the default config for lakeeffect
# this is my ~/akrr/etc/resources/lakeeffect/resource.conf
# Resource parameters

# Processors (cores) per node
ppn = 8

# head node for remote access
remote_access_node = None
# Remote access method to the resource (default ssh)
remote_access_method = "ssh"
# Remote copy method to the resource (default scp)
remote_copy_method = "scp"

# Access authentication
ssh_username = "centos"
ssh_password = None
ssh_private_key_file = "/home/hoffmaps/projects/openstack/keypairs/openstack-testing.key"
ssh_private_key_password = None

# Scratch visible across all nodes (absolute path or/and shell environment variable)
network_scratch = "/home/centos/appker/network_scratch"
# Local scratch only locally visible (absolute path or/and shell environment variable)
local_scratch = "/home/centos/appker/network_scratch"
# Locations for app. kernels working directories (can or even should be on scratch space)
akrr_data = "/home/centos/appker/akrr_data"
# Location of executables and input for app. kernels
appkernel_dir = "/home/centos/appker/resource"

# batch options
batch_scheduler = "openstack"

# job script header
batch_job_header_template = """#!/bin/bash
"""

openstack_env_set_script = "lakeeffect-benchmarks-openrc.sh"
openstack_flavor = "c8.m16"
openstack_volume = "dockervolume"
openstack_network = "lakeeffect-199.109.195"
openstack_security_group = ["default", "SSH"]
openstack_key_name = "openstack-testing"
openstack_server_name = "akrrtemp"
openstack_floating_ip_attach = None

# due to current implementation (only one volume)
# the limit is 1 active task
max_number_of_active_tasks = 1

```

We'll see how this works

```bash
akrr resource deploy -r lakeeffect
```
On first doing this, I got a Timeout error.
The fix:
in the openstack environment script, instead of asking for input, I just put

```bash
export OS_API_KEY_INPUT=[API_KEY]
```
So then it ran fine, up until the test job. It submitted the test job but got an error back, so I'm checking that out now
- Analyzing the stderr, it looks like it couldn't find akrr_util.bash as well as the other scripts/commands, so somehow maybe we have to add those in?
- I'll try it again - yeah same problem duh
- NOTE: It's possible you could have to delete some entries into the ~/.ssh/known_hosts file, bc otherwise there could be a connection refused error
- NOTE: the connection error might only happen a few times, don't immediately cancel out the program

Okay so I'm finding a few problems I think
- Looking at stderr, says it can't find all the akrr functions (they're in akrr_util.bash)
- Analyzing the volume: the execs tar was not unpacked for some reason, but unpacking it did give a seemingly proper akrr_util.bash
- I looked at a different run, and it was unpacked but akrr_util.bash was literally just empty. not sure what that's about

So I left it unpacked, so maybe it won't have to do the unpacking and whatnot
- Leaving it unpacked did indeed allow the test job to run to completion, but another erro happened immediately after:
```bash
Traceback (most recent call last):
  File "/home/hoffmaps/projects/akrr/bin/akrr", line 65, in <module>
    akrr.cli.CLI().run()
  File "/home/hoffmaps/projects/akrr/akrr/cli/__init__.py", line 154, in run
    return cli_args.func(cli_args)
  File "/home/hoffmaps/projects/akrr/akrr/cli/commands.py", line 293, in resource_deploy_handler
    return resource_deploy(args)
  File "/home/hoffmaps/projects/akrr/akrr/cli/resource_deploy.py", line 779, in resource_deploy
    openstack_server.create()
  File "/home/hoffmaps/projects/akrr/akrr/util/openstack.py", line 137, in create
    if self.is_server_running():
  File "/home/hoffmaps/projects/akrr/akrr/util/openstack.py", line 114, in is_server_running
    out = json.loads(out.strip())
  File "/usr/lib64/python3.6/json/__init__.py", line 354, in loads
    return _default_decoder.decode(s)
  File "/usr/lib64/python3.6/json/decoder.py", line 339, in decode
    obj, end = self.raw_decode(s, idx=_w(s, 0).end())
  File "/usr/lib64/python3.6/json/decoder.py", line 357, in raw_decode
    raise JSONDecodeError("Expecting value", s, err.value) from None
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)

```
So there's some error with the json thing, in the code the command seems valid
Looked into code a bit more, something weird:
Running the 
out = self.openstack.run_open_stack_cmd("server list -f json --name "+self.name)
leads to out being this:
	out:  __init__() missing 1 required positional argument: 'token'
No clue what __init__ or 'token' it is, so I'm looking for that now.
Also weird is that running the deploy again, its getting to that point a lot faster...and I'm not sure why. Usually it wouldn't be until after the test that the error gets printed

- Just ran it again, with no changes, and it ran to completion fine without any errors. Is it possible that somehow I ran them too close together or something? 
- I did add some print statements in openstack.py, but deleted them after it worked fine.
- So it appears that the resource is all set to start working, I got the okay from the code, since the only warnings were about the execs and inputs already being there, which had sense



