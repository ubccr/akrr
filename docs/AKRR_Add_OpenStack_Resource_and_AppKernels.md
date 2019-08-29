# Adding OpenStack Resource

Unlike with tradition HPC resource OpenStack provides only basic operation system and for running
appkernels we need to make volume for instances with required software.

For cloud instances we chose to use Docker to run appkernels and limit parallel execution by one instance, 
thus where gonna be no extra steps for installing each particular application.

In order to add OpenStack to AKRR we need:

* On AKRR host install OpenStack client and authentication script.
* Create OpenStack Volume for appkernel execution and installing necessary software on it.
* Add OpenStack to AKRR as new resource.
* Validate appkernels execution.


## Installing OpenStack Client and Authentication Script

Install OpenStack command line client and authorization

```bash
# Get pip if it is not yet installed
sudo yum install python36-pip

# Install OpenStack command line client
sudo pip3.6 install python-cinderclient==3.6.1
sudo pip3.6 install python-openstackclient

# Install OpenStack authorization, consult you OpenStack provider 
# for that, in CCR UB it is:
sudo pip3.6 install git+https://github.com/ubccr/v3oidcmokeyapikey.git

# Prior installation
# you might need to remove distribution provided pyYaml (pip want to install different version):
# sudo yum remove python36-PyYAML
```

Get environment setup script from OpenStack portal (https://lakeeffect.ccr.buffalo.edu in case of CCR UB):

In the web portal, on top left Project->API Access, then download OpenStack RC File (Identity API v3), it is
available in "Download OpenStack RC File" dropdown botton on right. Save it somewhere.

Update the OpenStack RC script so that it didn't ask API key as user input but place it right in the script,
similar to following:

```bash eval=F
#!/usr/bin/env bash
unset OS_TOKEN
unset OS_AUTH_TYPE
#echo "Please enter your CCR API Key: "
#read -sr OS_API_KEY_INPUT
export OS_API_KEY="<here should be the key>"
export OS_AUTH_URL=https://lakeeffect.ccr.buffalo.edu:8770/v3
export OS_IDENTITY_API_VERSION=3
export OS_PROJECT_NAME="lakeeffect-benchmarks"
export OS_USERNAME="nikolays"
export OS_PROJECT_DOMAIN_NAME="lakeeffect"
export OS_INTERFACE=public
export OS_REGION_NAME="buffalo"
export OS_TOKEN=`openstack --os-auth-type v3oidcmokeyapikey --os-identity-provider ccr --os-protocol openid --os-discovery-endpoint https://sso.ccr.buffalo.edu/.well-known/openid-configuration --os-client-id ccr-os-api --os-redirect-uri https://localhost/ccrauth token issue -f value -c id`
export OS_AUTH_TYPE=v3token
```

Check your provide on how to get the API key. AKRR will use OpenStack command line tools to access cloud like 
a regular user. It will source this RC script prior the operation.

Source it and check available resources
```bash eval=F
source lakeeffect-xdmod-openrc.sh
openstack flavor list
openstack image list
```

Output example:
```
+--------+------------------+-------+------+-----------+-------+-----------+
| ID     | Name             |   RAM | Disk | Ephemeral | VCPUs | Is Public |
+--------+------------------+-------+------+-----------+-------+-----------+
| 101001 | c1.m1            |  1024 |   20 |         0 |     1 | True      |
| 101004 | c1.m4            |  4096 |   20 |         0 |     1 | True      |
| 102004 | c2.m4            |  4096 |   20 |         0 |     2 | True      |
| 102008 | c2.m8            |  8192 |   20 |         0 |     2 | True      |
| 104008 | c4.m8            |  8192 |   20 |         0 |     4 | True      |
| 104016 | c4.m16           | 16384 |   20 |         0 |     4 | True      |
| 108016 | c8.m16           | 16384 |   20 |         0 |     8 | True      |
| 108032 | c8.m32           | 32768 |   20 |         0 |     8 | True      |
| 116032 | c16.m32          | 32768 |   20 |         0 |    16 | True      |
| 116064 | c16.m64          | 65536 |   20 |         0 |    16 | True      |
+--------+------------------+-------+------+-----------+-------+-----------+
+--------------------------------------+----------------------------------+--------+
| ID                                   | Name                             | Status |
+--------------------------------------+----------------------------------+--------+
| eb259c93-82f1-4d9e-8318-b3546e5d02e6 | centos-7.6.1810-20190604         | active |
| 0847e343-cf30-4c24-a5c7-a01fb76735ee | ubuntu1604-ccr-20181127-1        | active |
| 0232b73a-1c16-4c33-96d9-3295b898ca4f | ubuntu1804-ccr-20181127-1        | active |
+--------------------------------------+----------------------------------+--------+
```
## Creating Volume for Application Kernels Execution

Create a volume which will be used to run application kernels:
```bash
openstack volume create --description "volume for appkernels execution" \
    --image centos-7.6.1810-20190604 --size=100 appkernels_volume
```

Output example:
```
+---------------------+--------------------------------------+
| Field               | Value                                |
+---------------------+--------------------------------------+
| attachments         | []                                   |
| availability_zone   | cbls                                 |
| bootable            | false                                |
| consistencygroup_id | None                                 |
| created_at          | 2019-08-28T14:34:31.000000           |
| description         | volume for appkernels execution      |
| encrypted           | False                                |
| id                  | SomeFancyHash123                     |
| multiattach         | False                                |
| name                | appkernels_volume                    |
| properties          |                                      |
| replication_status  | None                                 |
| size                | 100                                  |
| snapshot_id         | None                                 |
| source_volid        | None                                 |
| status              | creating                             |
| type                | rbd                                  |
| updated_at          | None                                 |
| user_id             | SomeFancyHash123                     |
+---------------------+--------------------------------------+
```

Spin-off instance (check that ssh key is both in OpenStack and in local ~/.ssh)
```bash
openstack server create --flavor c8.m16 \
  --volume appkernels_volume \
  --network lakeeffect-199.109.112 \
  --security-group default --security-group SSH \
  --key-name nikolays aktest
```

Output example:
```text
+-----------------------------+---------------------------------------------+
| Field                       | Value                                       |
+-----------------------------+---------------------------------------------+
| OS-DCF:diskConfig           | MANUAL                                      |
| OS-EXT-AZ:availability_zone | cbls                                        |
| OS-EXT-STS:power_state      | NOSTATE                                     |
| OS-EXT-STS:task_state       | scheduling                                  |
| OS-EXT-STS:vm_state         | building                                    |
| OS-SRV-USG:launched_at      | None                                        |
| OS-SRV-USG:terminated_at    | None                                        |
| accessIPv4                  |                                             |
| accessIPv6                  |                                             |
| addresses                   |                                             |
| adminPass                   | RandomPassword                              |
| config_drive                |                                             |
| created                     | 2019-08-28T14:54:28Z                        |
| flavor                      | c8.m16 (216122)                             |
| hostId                      |                                             |
| id                          | SomeFancyHash123                            |
| image                       |                                             |
| key_name                    | nikolays                                    |
| name                        | aktest                                      |
| progress                    | 0                                           |
| project_id                  | SomeFancyHash123                            |
| properties                  |                                             |
| security_groups             | name='SomeFancyHash123'                     |
|                             | name='SomeFancyHash123'                     |
| status                      | BUILD                                       |
| updated                     | 2019-08-28T14:54:28Z                        |
| user_id                     | SomeFancyHash123                            |
| volumes_attached            |                                             |
+-----------------------------+---------------------------------------------+
```

Check its ip and try to ssh
```bash
openstack server list --name aktest
```

Output example:
```
+--------------------------------------+--------+--------+--------------------------------------+-------+--------+
| ID                                   | Name   | Status | Networks                             | Image | Flavor |
+--------------------------------------+--------+--------+--------------------------------------+-------+--------+
| SomeFancyHash123                     | aktest | ACTIVE | lakeeffect-199.109.112=199.109.112.7 |       | c8.m16 |
+--------------------------------------+--------+--------+--------------------------------------+-------+--------+
```

Log in to instance
```bash
ssh -i <ssh identiry for cloud> centos@199.109.112.7
```

Now on instance install docker (see https://docs.docker.com/install/linux/docker-ce/centos/ for more details):
```bash
# Install dependencies
sudo yum install -y yum-utils \
  device-mapper-persistent-data \
  lvm2

# Add Docker Repo
sudo yum-config-manager \
    --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# Install Docker
sudo yum install docker-ce docker-ce-cli containerd.io

# Start Docker
sudo systemctl start docker

# Set it to start on boot
sudo systemctl enable docker

# Verify that docker is working
sudo docker run hello-world

# add centos user to docker group
sudo usermod -aG docker centos

# exit and re-loging for new group to work
exit
```
```bash
ssh -i <ssh identiry for cloud> centos@199.109.112.7

# test that docker can be executed as centos user
docker run hello-world
```

If everything fine now we can terminate instance
```bash
openstack server delete aktest
```

You can start an instance again to ensure that docker start up on boot


## OpenStack Resource Setup in AKRR

```bash eval=F
akrr resource add
```
```text
[INFO] Beginning Initiation of New Resource...
[INFO] Retrieving Resources from XDMoD Database...
[INFO] Found following resources from XDMoD Database:
    resource_id  name
              1  UBHPC                                   
              2  lakeeffect                                 

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

Copy environment setter to akrr resource config directory:

```bash
cp <somewhere>/lakeeffect-xdmod-openrc.sh $(AKRR_HOME:-~/akrr)/etc/resources/lakefffect
```

Edit resource config
```python
# Resource parameters

# Processors (cores) per node
ppn = 8

# head node for remote access
remote_access_node = "headnode.somewhere.org"
# Remote access method to the resource (default ssh)
remote_access_method = "ssh"
# Remote copy method to the resource (default scp)
remote_copy_method = "scp"

# Access authentication
ssh_username = "centos"
ssh_password = None
ssh_private_key_file = "/home/xdtas/.ssh/keyname"
ssh_private_key_password = None

# Scratch visible across all nodes (absolute path or/and shell environment variable)
network_scratch = "/home/centos/appkernel/network_scratch"
# Local scratch only locally visible (absolute path or/and shell environment variable)
local_scratch = "/home/centos/appkernel/network_scratch"
# Locations for app. kernels working directories (can or even should be on scratch space)
akrr_data = "/home/centos/appkernel/akrr_data"
# Location of executables and input for app. kernels
appkernel_dir = "/home/centos/appkernel/resource"

# batch options
batch_scheduler = "openstack"

# job script header
batch_job_header_template = """#!/bin/bash
"""

openstack_env_set_script = "lakeeffect-xdmod-openrc.sh"
openstack_flavor = "c8.m16"
openstack_volume = "aktestvolume"
openstack_network = "lakeeffect-149.102.15"
openstack_security_group = ["default", "SSH"]
openstack_key_name = "keyname"
openstack_server_name = "aktest"
openstack_floating_ip_attach = None
# due to current implementation (only one volume)
# the limit is 1 active task
max_number_of_active_tasks = 1
```

Deploy
```bash eval=F
akrr resource deploy -r lakeeffect
```


Next: [AKRR: Deployment of Application Kernel on Resource](AKRR_Deployment_of_Application_Kernel_on_Resource.md)
