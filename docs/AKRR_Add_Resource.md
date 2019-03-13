# AKRR: Adding a New HPC Resource

Addition of new HPC resource to AKRR consists of two steps: configuration of
new resource and deployment of AKRR's HPC resource-side scripts and application 
inputs. The last step also performs installation validation.

From the AKRR point of view, an HPC resource is a distinct and **homogeneous 
set** of computational nodes. The resource name should reflect such a set. For 
example,  if cluster "A" in addition to typical general purpose nodes has 
specialized nodes ( large memory, GPU or MIC accelerated nodes), it will be 
convenient to treat them as a separate resources and to name them as "A",  
"A_largemem", "A_GPU" and "A_MIC" for general purpose nodes, for large memory 
nodes, GPU or MIC accelerated nodes respectively. The name of the resource is 
separated from access node  (head node), the later is specified in configuration 
file.

AKRR uses the user-account under which its is running to access HPC resources. 
For the access, it will use ssh and scp commands.

# Required Information about Resource

*   Access credential to head node from machine where AKRR daemon is running 
(username and password or username, private key location on file system and 
pass-phrase)
*   Queuing system type (SLURM, PBS)
*   Batch job script header with resource request specifications
*   HPC resource specification
    *   processes per node count
*   HPC resource file-system layout
    *   local scratch location
    *   network scratch location
    *   future location for application kernel input and auxiliary files (should 
be in persistent location (i.e. not scratch))
    *   future location for application kernel run-time files (can be on 
scratch)

# Prerequerements

## Setting HPC Resource Default Shell to BASH

AKRR accesses and uses HPC resource as a regular user and as a regular user it 
has its' preference to shell flavor. It is intended to be used with bash. Consult your system 
user guide or consultants on how to do that, please note that in the majority of 
large HPC sites the UNIX _chsh_ command is not the preferred way.

# Adding New Resource

To add new resource run AKRR CLI with _resource add_ options:

```bash
akrr resource add
```

This script will:

*   ask to choose a resource from OpenXDMoD resources list
*   prompt for AKRR resource name
*   ask for a queuing system
*   ask for resource access credential
*   ask for locations of AKRR working directories on resource
*   finally it initiate resource configuration file and populate most of the 
parameters in it 

If the resource is not present in OpenXDMoD resources list enter 0 when prompt 
for resoure id. When prompt for resource name enter human friendly name as 
discussed earlier, for example _fatboy_gpu, the name can be different from 
XDMoD name._

> **Tips and Tricks**
>
> If resource headnode do not reply on pinging use __--no-ping__ do disable that check.
>
> If your system is fairly non-standard (for example non-default port for ssh, 
> usage of globus-ssh for access and similar) you can use __--minimalistic__ option.
> This option sets a minimalistic interactive session and the generated 
> configuration file must be manually edited.

Below is sample output:

**'akrr resource add' Sample Output**
```text
[INFO] Beginning Initiation of New Resource...
[INFO] Retrieving Resources from XDMoD Database...
[INFO] Found following resources from XDMoD Database:
    resource_id  name
              1  ub-hpc                                  

[INPUT]: Enter resource_id for import (enter 0 for no match):
1

[INPUT]: Enter AKRR resource name, hit enter to use same name as in XDMoD Database [ub-hpc]:


[INPUT]: Enter queuing system on resource (slurm or pbs): 
slurm

[INPUT]: Enter Resource head node (access node) full name (e.g. headnode.somewhere.org):
[ub-hpc] huey
[INPUT]: Enter username for resource access:
[akrruser] nikolays
[INFO] Can not access resource without password

[INFO] Select authentication method:
  0  The private and public keys was generated manually, right now. Try again.
  1  Generate new private and public key.
  2  Use password directly.
[INPUT]: Select option from list above:
[1] 

[INPUT]: Enter password for nikolays@vortex (will be used only during this session):

[INPUT]: Enter private key name:
[id_rsa_ub-hpc]
[INPUT]: Enter passphrase for new key (leave empty for passwordless access):

Generating public/private rsa key pair.
Your identification has been saved in /root/.ssh/id_rsa_ub-hpc.
Your public key has been saved in /home/akrruser/.ssh/id_rsa_ub-hpc.pub.
The key fingerprint is:
SHA256:imFr7yAbg56+ebMHDKkfjSSSBzA4MasEGMV3H+DaTHQ nikolays@huey
The key's randomart image is:
+---[RSA 2048]----+
|o  o= o.E        |
|*  +-....        |
|+= o .o. .       |
|o.   =  .        |
|*o.   o S        |
|o+.+ + .         |
|.o+.= .          |
|oO.o.o           |
|Bo .+o+.         |
+----[SHA256]-----+
/usr/bin/ssh-copy-id: INFO: Source of key(s) to be installed: "/home/akrruser/.ssh/id_rsa_ub-hpc.pub"
/usr/bin/ssh-copy-id: INFO: attempting to log in with the new key(s), to filter out any that are already installed
/usr/bin/ssh-copy-id: INFO: 1 key(s) remain to be installed -- if you are prompted now it is to install the new keys
UPDATED: March 6, 2015

You are accessing a University at Buffalo (UB) - Center for Computational Research (CCR)
computer system that is provided for CCR-authorized users only.

Password: 

Number of key(s) added: 1

Now try logging into the machine, with:   "ssh 'nikolays@huey'"
and check to make sure that only the key(s) you wanted were added.

[INFO] Checking for password-less access
[INFO] Can access resource without password

[INFO] Connecting to ub-hpc
[INFO]               Done

[INPUT]: Enter processors (cores) per node count:
8 
[INPUT]: Enter location of local scratch (visible only to single node):
[/tmp]
[INFO] Directory exist and accessible for read/write

[INPUT]: Enter location of network scratch (visible only to all nodes),used for temporary storage of app kernel input/output:
/user/nikolays/tmp
[INFO] Directory exist and accessible for read/write

[INPUT]: Enter future location of app kernels input and executable files:
[/user/nikolays/appker/ub-hpc]
[INFO] Directory huey:/user/nikolays/appker/ub-hpc does not exists, will try to create it
[INFO] Directory exist and accessible for read/write

[INPUT]: Enter future locations for app kernels working directories (can or even should be on scratch space):
[/user/nikolays/tmp/akrr_data/ub-hpc]
[INFO] Directory huey:/user/nikolays/tmp/akrr_data/ub-hpc does not exists, will try to create it
[INFO] Directory exist and accessible for read/write

[INFO] Initiating ub-hpc at AKRR
[INFO] Resource configuration is in /home/akrruser/akrr/etc/resources/ub-hpc/resource.conf
[INFO] Initiation of new resource is completed.
    Edit batch_job_header_template variable in /home/akrruser/akrr/etc/resources/ub-hpc/resource.conf
    and move to resource validation and deployment step.
    i.e. execute:
        akrr resource deploy -r ub-hpc
        
```

> **Tips and Tricks**
>
> reducing number of ssh connection
> AKRR would generate a large number of ssh connections. If you don't want to 
> stress you headnode in this manner you can set ssh to reuse the connections. Add 
> following to ~/.ssh/config :
>
> ```
> Host <your heanode name>  
> <TAB>ControlMaster auto  
> <TAB>ControlPath ~/.ssh/sockets/%l-%r@%h-%p  
> <TAB>ControlPersist 3600
> ```
> 
> Replace \<TAB\> with tab symbol. See ssh documentation for more details
>

## Edit Resource Configuration File

Edit resource parameter file $HOME/akrr/etc/resources/\<RESOURCE\>/resource.conf 
. In most cases the only parameter which should be 
adjusted is _batch_job_header_template_ at the end of the file.

Below is example of the resource configuration file:

```python
# Resource parameters

# Processors (cores) per node
ppn = 8

# head node for remote access
remote_access_node = "huey"
# Remote access method to the resource (default ssh)
remote_access_method = "ssh"
# Remote copy method to the resource (default scp)
remote_copy_method = "scp"

# Access authentication
ssh_username = "nikolays"
ssh_password = None
ssh_private_key_file = None
ssh_private_key_password = None

# Scratch visible across all nodes (absolute path or/and shell environment variable)
network_scratch = "/user/nikolays/tmp"
# Local scratch only locally visible (absolute path or/and shell environment variable)
local_scratch = "/tmp"
# Locations for app. kernels working directories (can or even should be on scratch space)
akrr_data = "/user/nikolays/tmp/akrr_data/ub-hpc"
# Location of executables and input for app. kernels
appkernel_dir = "/user/nikolays/appker/ub-hpc"

# batch options
batch_scheduler = "slurm"

# job script header
batch_job_header_template = """#!/bin/bash
#SBATCH --partition=normal
#SBATCH --qos=normal
#SBATCH --nodes={akrr_num_of_nodes}
#SBATCH --ntasks-per-node={akrr_ppn}
#SBATCH --time={akrr_walltime_limit}
#SBATCH --output={akrr_task_work_dir}/stdout
#SBATCH --error={akrr_task_work_dir}/stderr
#SBATCH --exclusive
"""
```

> **Configuration File Format**
>
> All AKRR configuration files utilize python syntax. Below is a short example on the syntax:
> 
> ```python
> # pound sign for comments
> 
> # value assignment to variable
> db_host = "127.0.0.1"
> export_db_host = db_host
> 
> # triple quotes for long multi-line strings
> batch_job_header_template = """#!/bin/bash
> #SBATCH --partition=normal
> #SBATCH --nodes={akrr_num_of_nodes}
> #SBATCH --ntasks-per-node={akrr_ppn}
> #SBATCH --time={akrr_walltime_limit}
> #SBATCH --output={akrr_task_work_dir}/stdout
> #SBATCH --error={akrr_task_work_dir}/stderr
> #SBATCH --exclusive
> """
> ```

Batch job script files which is submited to HPC resource for execution is 
generated using the template. Variables 
in curly brackets are replaced by their values.

For example line "#SBATCH --nodes={akrrNNodes}" listed above in 
batchJobHeaderTemplate template variable

will become "#SBATCH --nodes=2" in batch job script if application kernel should 
run on two nodes.

In order to enter shell curly brackets they should be enter as double curly 
brackets. All double curly brackets will be replaced with single curly bracket 
during batch job script generation.

> Example:
>
> "awk "{{for (i=0;i<$_TASKS_PER_NODE;++i)print}}"
> 
> in  template variable will become:
>
> "awk "{for (i=0;i<$_TASKS_PER_NODE;++i)print}"
>
> in  batch job script.
>

The commented parameters will assume default values. Below is the description of 
the parameters and their default values:

| Parameter                             | Optional | Description                                                                                                                                                                                     | Default Value |
|---------------------------------------|----------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------|
| ppn                                   | N        | Processors (cores) per node                                                                                                                                                                     | Must be set   |
| remote_access_node                    | N        | head node name for remote access                                                                                                                                                                | Must be set   |
| remote_access_method                  | Y        | Remote access method to the resource. Default is ssh, gsissh can be used.Here command line options to ssh can be specified as well (e.g. "ssh -p 23")                                           | 'ssh'         |
| remote_copy_method                    | Y        | Remote copy method to the resource. Default is scp, gsiscp can be used.Here command line options to ssh can be specified as well.                                                               | 'scp'         |
| **Access authentication**                                                                                                                                                                                                                                          |
| ssh_username                          | N        | username for remote access                                                                                                                                                                      | Must be set   |
| ssh_password                          | Y        | password                                                                                                                                                                                        | None          |
| ssh_private_key_file                  | Y        | location of private key, full name must be used                                                                                                                                                 | None          |
| ssh_private_key_password              | Y        | private key pass-phrase                                                                                                                                                                         | None          |
| **File-system locations on HPC resource**                                                                                                                                                                                                                          |
| network_scratch                       | N        | Scratch visible across all computational nodes(absolute path or/and shell environment variable)                                                                                                 | '$SCRATCH'    |
| local_scratch                         | N        | Local scratch only visible locally to a computational node(absolute path or/and shell environment variable)                                                                                     | '/tmp'        |
| akrr_data                             | N        | Top directory for app. kernels working directories. The last has a lifespan of taskexecution and can or even should be on scratch space. This directory will beautomatically created if needed. | Must be set   |
| appkernel_dir                         | N        | Location of executables and input for app. kernels. The content of this directorywill be filled during next step (validation and deployment)                                                    | Must be set   |
| **Batch job script settings**                                                                                                                                                                                                                                      |
| batch_scheduler                       | N        | Scheduler type: slurm or pbs. sge might work as well but was not tested                                                                                                                         | Must be set   |
| batch_job_header_template             | N        | Header for batch job script. Describe the resources requests and set AKRR_NODELIST environment variable containing list of all nodes.See below for more detailed information.                   | Must be set   |


## How to set _batch_job_header_template_

_batch_job_header_template _is a template used in the generation of batch job 
scripts. It specifies the resources (e.g. number of nodes) and other parameters 
used by scheduler.

The following are instructions on how to convert batch job script header to _batch_job_header_template_. 
For more details see [Batch Job Script Generation](AKRR_Batch_Job_Script_Generation.md). 

Below is a batch script which execute NAMD application on resorch which use Slurm:

```bash
#!/bin/bash
#SBATCH --partition=general-compute 
#SBATCH --qos=general-compute
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=8
#SBATCH --time=01:00:00
#SBATCH --output=output.stdout
#SBATCH --error=output.stderr
#SBATCH --constraint="CPU-L5520"
#SBATCH --exclusive

module load namd

srun $NAMDHOME/namd2 ./input.namd >& output.log 
```

We need to cut the top part of it, use it to replace the top section in the 
_batch_job_header_template _variable, and replace the requested resources with 
suitable template variables:

```python
batch_job_header_template = """#!/bin/bash
#SBATCH --partition=general-compute 
#SBATCH --qos=general-compute
#SBATCH --nodes={akrr_num_of_nodes}
#SBATCH --ntasks-per-node={akrr_ppn}
#SBATCH --time={akrr_walltime_limit}
#SBATCH --output={akrr_task_work_dir}/stdout
#SBATCH --error={akrr_task_work_dir}/stderr
#SBATCH --constraint="CPU-L5520"
#SBATCH --exclusive
"""
```

Number of nodes became _{akrr_num_of_nodes}_, processors per node became 
_{akrr_ppn}_, walltime becomes _{akrr_walltime_limit} and standard output and error 
became _{akrr_task_work_dir}/stdout_ and _{akrr_task_work_dir}/stderr_ respectively. 
These template variables 
will be substituted by the desired values during generation of batch job script 
for a particular task. The name of the files to where the standard output and 
error are redirected **always** should be stdout and stderr respectively.

Some template variable often used in batchJobHeaderTemplate is shown in table 
below:

| Variable Name         | Description                                                                      |
|-----------------------|----------------------------------------------------------------------------------|
| {akrr_num_of_nodes}   | Number of requested nodes                                                        |
| {akrr_ppn}            | Processors per node count, that means a total count of cores on a single node    |
| {akrr_num_of_cores}   | Number of requested cores                                                        |
| {akrr_walltime_limit} | Requested walltime, this field will be properly formatted                        |
| {akrr_task_work_dir}  | Location of working directory where the application kernel will be executed.     |
|                       | It is often used to redirect standard error and output to proper location, e.g.: |
|                       |     #SBATCH --output={akrr_task_work_dir}/stdout                                 |
|                       |     #SBATCH --error={akrr_task_work_dir}/stderr                                  |
|                       | Although such explicit definition of standard error and output redirected files are rarely used. | 
|                       | Some batch systems have been known to default to placing such output files in the user $HOME directory rather than the job submission directory. |
|                       | So use full name to be on a safe side |

## Visual Inspection of Generated Batch Job Script

Now, we can generate test application kernel batch job script and visually 
inspect it for mistake presence. Run:
```bash
akrr task new --dry-run --gen-batch-job-only -r <resource_name> -a test -n 2
```
This command will generate batch job script and output it to standard output. 
Below is example of the output

```text
DryRun: Should submit following to REST API (POST to scheduled_tasks) {'repeat_in': None, 'resource_param': "{'nnodes':2}", 'time_to_start': None, 'app': 'test', 'resource': 'ub-hpc'}
[INFO] Directory /home/akrruser/akrr/log/data/ub-hpc does not exist, creating it.
[INFO] Directory /home/akrruser/akrr/log/data/ub-hpc/test does not exist, creating it.
[INFO] Directory /home/akrruser/akrr/log/comptasks/ub-hpc does not exist, creating it.
[INFO] Directory /home/akrruser/akrr/log/comptasks/ub-hpc/test does not exist, creating it.
[INFO] Creating task directory: /home/akrruser/akrr/log/data/ub-hpc/test/2019.03.13.17.28.28.816451
[INFO] Creating task directories: 
        /home/akrruser/akrr/log/data/ub-hpc/test/2019.03.13.17.28.28.816451/jobfiles
        /home/akrruser/akrr/log/data/ub-hpc/test/2019.03.13.17.28.28.816451/proc
[INFO] auto_walltime_limit is on, trying to estimate walltime limit...
[WARNING] There are only %d previous run, need at least 5 for walltime limit autoset
[INFO] Below is content of generated batch job script:
#!/bin/bash
#SBATCH --partition=general-compute 
#SBATCH --qos=general-compute
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=8
#SBATCH --time=00:02:00
#SBATCH --output=/user/nikolays/tmp/akrr_data/ub-hpc/test/2019.03.13.17.28.28.816451/stdout
#SBATCH --error=/user/nikolays/tmp/akrr_data/ub-hpc/test/2019.03.13.17.28.28.816451/stderr
#SBATCH --constraint="CPU-L5520"
#SBATCH --exclusive


#Common commands
export AKRR_NODES=2
export AKRR_CORES=16
export AKRR_CORES_PER_NODE=8
export AKRR_NETWORK_SCRATCH="/user/nikolays/tmp"
export AKRR_LOCAL_SCRATCH="/tmp"
export AKRR_TASK_WORKDIR="/user/nikolays/tmp/akrr_data/ub-hpc/test/2019.03.13.17.28.28.816451"
export AKRR_APPKER_DIR="/user/nikolays/appker/ub-hpc"
export AKRR_AKRR_DIR="/user/nikolays/tmp/akrr_data/ub-hpc"

export AKRR_APPKER_NAME="test"
export AKRR_RESOURCE_NAME="ub-hpc"
export AKRR_TIMESTAMP="2019.03.13.17.28.28.816451"
export AKRR_APP_STDOUT_FILE="$AKRR_TASK_WORKDIR/appstdout"

export AKRR_APPKERNEL_INPUT="/user/nikolays/appker/ub-hpc/inputs"
export AKRR_APPKERNEL_EXECUTABLE="/user/nikolays/appker/ub-hpc/execs"

source "$AKRR_APPKER_DIR/execs/bin/akrr_util.bash"

#Populate list of nodes per MPI process
export AKRR_NODELIST=`srun -l --ntasks-per-node=$AKRR_CORES_PER_NODE -n $AKRR_CORES hostname -s|sort -n| awk '{printf "%s ",$2}' `

export PATH="$AKRR_APPKER_DIR/execs/bin:$PATH"

cd "$AKRR_TASK_WORKDIR"

#run common tests
akrr_perform_common_tests

#Write some info to gen.info, JSON-Like file
akrr_write_to_gen_info "start_time" "`date`"
akrr_write_to_gen_info "node_list" "$AKRR_NODELIST"



#normally in run_script_pre_run
#create working dir
export AKRR_TMP_WORKDIR=`mktemp -d /user/nikolays/tmp/test.XXXXXXXXX`
echo "Temporary working directory: $AKRR_TMP_WORKDIR"
cd $AKRR_TMP_WORKDIR

#Generate AppKer signature
appsigcheck.sh `which md5sum` > $AKRR_APP_STDOUT_FILE

echo "Checking that the shell is BASH"
echo $BASH 


#normally in run_script_post_run
#clean-up
cd $AKRR_TASK_WORKDIR
if [ "${AKRR_DEBUG=no}" = "no" ]
then
        echo "Deleting temporary files"
        rm -rf $AKRR_TMP_WORKDIR
else
        echo "Copying temporary files"
        cp -r $AKRR_TMP_WORKDIR workdir
        rm -rf $AKRR_TMP_WORKDIR
fi


akrr_write_to_gen_info "end_time" "`date`"

[INFO] Removing generated files from file-system as only batch job script printing was requested
```

_Test_ application kernel is specialized application kernel which inspects the 
resource deployment. Here mainly inspect the very top of the generated script 
and check is the resources request is generated properly. Modify 
_batch_job_header_template_ in configuration file if needed.

# Resource Parameters Validation and Application Kernel Input Parameters Deployment

The following command will validate resource parameters and deploy application 
kernel input parameters

```bash
akrr resource deploy -r <resource_name>
```

This script will perform following operations:

*   Check configuration file syntax, parameters type and presence of non 
optional parameters
*   Test the connectivity to the head-node
*   Deploy application kernel input parameters and application signature 
calculator
*   Run a test job on the resource

The script will exit in case of failure. The error must be addressed and script 
must be rerun until successful execution. Below is example of successful 
execution:

```text

```

# Troubleshooting

## Incorrect $AKRR_NODELIST Environment variable

If you got following error messages:

* "Nodes are not detected, check batch_job_header_template and setup of AKRR_NODELIST 
  variable"
* "Can not ping compute nodes from head node"
* "Number of requested processes (processes per node \* nodes) do not match actual 
  processes executed"

Then there is a high chances that AKRR_NODELIST was not set properly from 
default templates.

AKRR_NODELIST is a list of nodes per each MPI process, i.e. same node name is 
repeated multiple times. For example for 2 node run on 4 cores per node machine 
it looks like "node3 node3 node3 node3 node7node7node7node7".

  

By default AKRR uses templates specific to queuing system (defined in 
$AKRR_HOME/src/default.resource.inp.py):

```python
#Node list setter
node_list_setter={
    'pbs':"""export AKRR_NODELIST=\`cat $PBS_NODEFILE\`""",
    'slurm':"""export AKRR_NODELIST=\`srun -l --ntasks-per-node=$AKRR_CORES_PER_NODE -n $AKRR_CORES hostname -s|sort -n| awk '{{printf "%s ",$2}}' \`"""
}
```

To modify the behavior node_list_setter_template can be define in specific resource 
configuration file ($AKRR_HOME/cfg/resources/$RESOURCE/resource.inp.py):

**portion of $AKRR_HOME/cfg/resources/$RESOURCE/resource.inp.py**

```python
#Node list setter
node_list_setter_template="""export AKRR_NODELIST=`srun -l --ntasks-per-node=$AKRR_CORES_PER_NODE -n $AKRR_CORES hostname -s|sort -n| awk '{{printf "%s ",$2}}' `"""
```

For SLURM alternative to srun can be:

**portion of $AKRR_HOME/cfg/resources/$RESOURCE/resource.inp.py**

```python
#Node list setter
node_list_setter_template="""_TASKS_PER_NODE=`echo $SLURM_TASKS_PER_NODE|sed "s/(x[0-9]*)//g"`
export AKRR_NODELIST=`scontrol show hostname $SLURM_NODELIST| awk "{{for (i=0;i<$_TASKS_PER_NODE;++i)print}}"
"""
```

# Advanced Debugging

Although resource_validation_and_deployment.py detects many problems with 
resource deployments, sometimes its output can be cryptic. The following 
strategy can be employed to find the problem.

1.  Generate batch job script
2.  Run it on resource
3.  Analyze output
4.  Fix the issues in batch job script
5.  Go to 2 until executed successfully
6.  merge changes in batch job script to respective template in configuration 
file

Batch job script can be generated by running following command:

```bash
akrr task new --gen-batch-job-only -r <resource_name> -a test -n 2
```

This command generate batch job script and copy it to proper location on remote 
resource. This location will be showed in output:

```text
[INFO]: Local copy of batch job script is 
/home/mikola/wsp/test/akrr/data/rush/test/2014.12.11.08.58.57.412410/jobfiles/
test.job

[INFO]: Application kernel working directory on rush is 
/panasas/scratch/nikolays/akrrdata/rush/test/2014.12.11.08.58.57.412410
[INFO]: Batch job script location on rush is 
/panasas/scratch/nikolays/akrrdata/rush/test/2014.12.11.08.58.57.412410/test.job
```

Now log into resource, go to the task working directory and manually submit to 
queue, check the output and determine the problem.  
  

Now AKRR can submit jobs to that resource

Next: [AKRR: Deployment of Application Kernel on Resource](AKRR_Deployment_of_Application_Kernel_on_Resource.md)
