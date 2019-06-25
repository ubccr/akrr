## Deployment on vortex notes

So vortex now has singularity, so I'm gonna try and do everything there from now on.
So on vortex I'm making 2 resources, one that does singularity stuff, the other that does bare metal stuff (then maybe a 3rd with bare metal singularity?)

Setting up vortex_doc_sing (using singularity through my docker images)
```bash
[hoffmaps@dhcp-128-205-70-4 resources]$ akrr resource add --no-ping
[INFO] Beginning Initiation of New Resource...
[INFO] Retrieving Resources from XDMoD Database...
[INFO] Found following resources from XDMoD Database:
    resource_id  name


[INPUT]: Enter AKRR resource name:
vortex_dock_sing

[INPUT]: Enter queuing system on resource (slurm, pbs or openstack): 
slurm

[INPUT]: Enter Resource head node (access node) full name (e.g. headnode.somewhere.org):
[vortex_dock_sing] vortex.ccr.buffalo.edu
[WARNING] Can not ping vortex.ccr.buffalo.edu, but asked to ignore it.
[INPUT]: Enter username for resource access:
[hoffmaps] hoffmaps
[INFO] Checking for password-less access
[INFO] Can access resource without password

[INFO] Connecting to vortex_dock_sing
[INFO]               Done

[INPUT]: Enter processors (cores) per node count:
8
[INPUT]: Enter location of local scratch (visible only to single node):
[/tmp]
[INFO] Directory exist and accessible for read/write

[INPUT]: Enter location of network scratch (visible only to all nodes),used for temporary storage of app kernel input/output:
/gpfs/scratch/hoffmaps/network_scratch
[INFO] Directory exist and accessible for read/write

[INPUT]: Enter future location of app kernels input and executable files:
[/user/hoffmaps/appker/vortex_dock_sing]/gpfs/scratch/hoffmaps/akrr_project/appker/vortex_dock_sing
[INFO] Directory exist and accessible for read/write

[INPUT]: Enter future locations for app kernels working directories (can or even should be on scratch space):
[/gpfs/scratch/hoffmaps/network_scratch/akrr_data/vortex_dock_sing]
[INFO] Directory vortex.ccr.buffalo.edu:/gpfs/scratch/hoffmaps/network_scratch/akrr_data/vortex_dock_sing does not exists, will try to create it
[INFO] Directory exist and accessible for read/write

[INFO] Initiating vortex_dock_sing at AKRR
[INFO] Resource configuration is in /home/hoffmaps/projects/akrr/etc/resources/vortex_dock_sing/resource.conf
[INFO] Initiation of new resource is completed.
    Edit batch_job_header_template variable in /home/hoffmaps/projects/akrr/etc/resources/vortex_dock_sing/resource.conf
    and move to resource validation and deployment step.
    i.e. execute:
        akrr resource deploy -r vortex_dock_sing
```
So I started it up, then edited the resource config: updated below
```bash
# Resource parameters

# Processors (cores) per node
ppn = 8

# head node for remote access
remote_access_node = "vortex.ccr.buffalo.edu"
# Remote access method to the resource (default ssh)
remote_access_method = "ssh"
# Remote copy method to the resource (default scp)
remote_copy_method = "scp"

# Access authentication
ssh_username = "hoffmaps"
ssh_password = None
ssh_private_key_file = None
ssh_private_key_password = None

# Scratch visible across all nodes (absolute path or/and shell environment variable)
network_scratch = "/gpfs/scratch/hoffmaps/network_scratch"
# Local scratch only locally visible (absolute path or/and shell environment variable)
local_scratch = "/tmp"
# Locations for app. kernels working directories (can or even should be on scratch space)
akrr_data = "/gpfs/scratch/hoffmaps/network_scratch/akrr_data/vortex_dock_sing"
# Location of executables and input for app. kernels
appkernel_dir = "/gpfs/scratch/hoffmaps/akrr_project/appker/vortex_dock_sing"

# batch options
batch_scheduler = "slurm"

# job script header
batch_job_header_template = """#!/bin/bash
#SBATCH --partition=preprod
#SBATCH --qos=preprod
#SBATCH --nodes={akrr_num_of_nodes}
#SBATCH --ntasks-per-node={akrr_ppn}
#SBATCH --time={akrr_walltime_limit}
#SBATCH --output={akrr_task_work_dir}/stdout
#SBATCH --error={akrr_task_work_dir}/stderr
#SBATCH --exclusive
##SBATCH --constraint=CPU-L5520
"""
```
Things to note:
- I went with 8 ppn, as we've been doing
- set partition and qos to preprod (for testing, eventually want general-compute)
- set constraint to CPU-L5520, as we've sorta had (not yet active bc testing)
- note the scratch directories and such. /gpfs/scratch/hoffmaps/ is the main directory, not my home

Then I deployed
```bash
akrr resource deploy -r vortex_dock_sing
```
See the output file example for how deployment should look.

Next: look at deploying singularity images on vortex



