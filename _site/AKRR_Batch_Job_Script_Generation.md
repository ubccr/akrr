# Batch Job Script Generation from Nested Templates

AKRR is designed with a need to execute multiple application kernels on multiple HPC resources. 
The complexity of this task in part comes from
the fact that various HPC resources can be severely different in hardware and software. 
For example, HPC resources can use different queueing
systems, different vendors and versions of MPI, BLAS and others libraries. 
Furthermore, some applications can be compiled in number of way
which will affect how they should be executed (e.g. TCP/IP vs MPI). 
This makes impossible to create a single job script which will work on all
platforms. 
A large set of separate job scripts for every application kernel on every HPC resource would be unbearable to maintain. 
AKRR
addresses variability of batch job scripts by the use of templates. 

Job script is created from template for every new task.
The root template (variable ```batch_job_template```) for batch job script is located at 
```$AKRR_SRC/akrr/default_conf/default.resource.conf``` and listed bellow:

```python
...
# master batch job script template
batch_job_template = """{batch_job_header_template}

{akrr_common_commands_template}

{akrr_run_appkernel}

{akrr_common_cleanup_template}
"""

...

akrr_run_appkernel = """{run_script_pre_run}

{appkernel_run_env_template}

{akrr_gen_appker_sign}

{akrr_run_appkernel_template}

{run_script_post_runCustom}

{run_script_post_run}
"""
...
```

The variables in figure brackets will be replaced by their values during the batch job script creation.
For example content of variable ```akrr_run_appkernel``` will replace ```{akrr_run_appkernel}``` in ```batch_job_template```.
The replacement is performed recursively until all template variables replaced, 
that is template variable can contain other template variables. 
Double figure brackets will be eventually substituted with a single figure bracket.

During the batch job script creation the variables are read from following configurations and in shown order
(new records replaced old one, allowing to overwrite default values):

* Resource configuration (read from file-system):
    * ```$AKRR_SRC/akrr/default_conf/default.resource.conf``` *(should not be modified)*
    * ```$AKRR_HOME/etc/resources/<resource_name>/resource.conf``` *(resource specific config)*
* Application kernel configuration (read from file-system):
    * ```$AKRR_SRC/akrr/default_conf/default.app.conf``` *(should not be modified)*
    * ```$AKRR_SRC/akrr/default_conf/<appkernel_name>.app.conf``` *(should not be modified)*
    * ```$AKRR_HOME/etc/resources/<resource_name>/<appkernel_name>.conf``` *(appkernel on the resource specific config)*
* Task parameters (read from database for each task):
    * That is there number of nodes to use is specified.
    
The first variable in ```batch_job_template``` is ```{batch_job_header_template}```, 
which describes the resources request and other stuff which usually present in the
beginning of all job scripts for a given HPC resource. 
```batch_job_template``` should be defined in resource configuration file for each resource, for example:

```python
# Fragment of $AKRR_HOME/etc/resources/<resource_name>/resource.conf`
...

batch_job_header_template="""#!/bin/bash
#SBATCH --partition=general-compute
#SBATCH --qos=general-compute
#SBATCH --nodes={akrr_num_of_nodes}
#SBATCH --ntasks-per-node={akrr_ppn}
#SBATCH --time={akrr_walltime_limit}
#SBATCH --output={akrr_task_work_dir}/stdout
#SBATCH --error={akrr_task_work_dir}/stderr
#SBATCH --constraint=OPA,CPU-Gold-6130
#SBATCH --exclusive
"""

...
```

This header template will be used for generation of all batch job scripts on that resource.
This way if there is a need to update the header (for example set a new charging account) this can be done in one place.

The template variable ``{akrr_run_appkernel}`` build from multiple templates which is modified either in 
global default app configuration, particular app default configuration or/and resource specific app configuration depanding 
on particular application kernels execution pattern. Most often only ```{appkernel_run_env_template}``` need to be
modified for an appkernel config for specific resource.

See [Adding HPC Resource](AKRR_Add_Resource.md) for details on resource configuration and 
[Deployment of Application Kernels on Resource](AKRR_Deployment_of_Application_Kernel_on_Resource.md) 
as starting point for individual appkernels configurations.

