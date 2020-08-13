## Notes on setting up Akrr to work with OpenStack

(This assumes you've already set up the OpenStack CLI and set up Docker on OpenStack, as well as get AKRR working normally of course)

You want to add the resource in a minimalistic fasion (so you can make sure the config variables are correct)

```bash
akrr resource add --minimalistic
```
Once you do that, go to the directory where it made the resource config and take a look at it.
It should look something like this (I added notes about what each thing should be)

```bash
# This was my config when I (Phillip Hoffmann, CCR 2019 Intern) was working with OpenStack)
# Resource parameters

# Processors (cores) per node
ppn = 8
# Dependent on the flavor you're using for your instance


# head node for remote access
remote_access_node = "headnode.somewhere.org" # was None earlier, I believe it didn't work
# Don't worry too much about this, Akrr figures out how to connect 

# Remote access method to the resource (default ssh)
remote_access_method = "ssh"
# Remote copy method to the resource (default scp)
remote_copy_method = "scp"

# Access authentication
# username on the instance (often its just the os you're using)
ssh_username = "centos"

# assuming you're using ssh key to get into the instance, bc that's how the cli works
ssh_password = None

# path to the private key that corresponds with the openstack_key_name specified below
ssh_private_key_file = "/home/hoffmaps/projects/openstack/keypairs/openstack-testing.key"
ssh_private_key_password = None

# these are all dependent on the volume and how you want the volume to be set up
# these will be used during the deploy step
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

# path to the openstack rc file you got with api access (check out setting_up_openstack_cli.md)
openstack_env_set_script = "lakeeffect-benchmarks-openrc.sh"

openstack_flavor = "c8.m16"

# volume that has docker installed on it
openstack_volume = "dockervolume"

# check out the Network tab in web interface for options with this potentially
openstack_network = "lakeeffect-199.109.195"
openstack_security_group = ["default", "SSH"]

# name of the key-pair that should already exist in openstack setup (you should have private key above)
openstack_key_name = "openstack-testing"

# just the name for the instance when it spins up
openstack_server_name = "akrrtemp"
openstack_floating_ip_attach = None

# due to current implementation (only one volume)
# the limit is 1 active task
max_number_of_active_tasks = 1
# if you have more than 1 you risk akrr trying to use the same volume twice which doesn't work
```
After you change your configuration to suit your setup, try deploying it.

```bash
akrr resource deploy -r <openstack resource>

```
If you get a timeout error, it probably means you still have the rc script asking for input. You need to put in your API Key and have it not ask for your input. Check out setting_up_openstack_cli.md

You may get another connection refused error, in which case you might have to delete some entries in your ~/.ssh/known_hosts file, since it could be that the host generated has the same address as something in there, so it needs to recognize that it's a new one. So you should delete the hosts that have the same first 3 parts of the ip address (at least from my experience).

You may get an error that the test job didn't run correctly. It's possible that when unpacking the execs and inputs tars from github, something went wrong. I noticed that there were a couple times where akrr unpacked the tars and the files were all there, but they were all blank for some reason. Going into the volume and manually unpacking the tars seems to have fixed the issue. If you find something went wrong with the test job, especially that a function wasn't being found, it's likely because the files from the tar are blank. Creating a new instance with the volume and unpacking it manually allows you to make sure the files aren't blank.


If you are trying to deploy or run akrr on openstack too often, you may get an error like the following:
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
What this usually means is that you're sending too many requests (HTTP 429 error). The way it works is by requesting access with a token, and if you ask for too many tokens in a short period of time, it denies you access. Akrr doesn't realize this until it tries to get something from the server, which it can't access since it doesn't have the token, and so there is no value where it expects it.

The easiest fix to this is just to wait a bit and try again. A potential solution is somehow saving the token somewhere and then re-using it for future runs, but when I was the intern, it didn't have that capability (at least as far as I was aware).

Note that the above error could occur when trying to validate or run appkernels too, its not just with resource deployment.

After akrr is all set up and the test job runs successfully, you can move on to deploying various appkernels on openstack.
 







