# AKRR: Deployment of IMB Applications Kernels on a Resource

Here the deployment of xdmod.benchmark.mpi.imb application kernel is described. This application 
kernel is based on Intel MPI Benchmark (IOR) which design to measure the network performance.

For further convenience of application kernel deployment lets define APPKER and RESOURCE environment 
variable which will contain the HPC resource name:

```bash
export RESOURCE=<resource_name>
export APPKER=imb
```

# Installing IMB

In this section the IMB installation process will be described, see also IMB documentation for 
installation details ( 
[https://software.intel.com/en-us/articles/intel-mpi-benchmarks](https://software.intel.com/en-us/
articles/intel-mpi-benchmarks) ).

## Installing with Spack

First install Spack and set it up to reuse system-wide packages, see [Spack Install and Setup](AKRR_Spack_Install_and_Setup.md).

```bash
# To install
$AKRR_APPKER_DIR/execs/spack/bin/spack -v install intel-mpi-benchmarks
```


## Building IMB Executables

First we need to install IMB. Below is a sample listing of commands for IMB installation:

```bash
#cd to application kernel executable directory
cd $AKRR_APPKER_DIR/execs

# obtain latest version of IMB
wget https://github.com/intel/mpi-benchmarks/archive/IMB-v2019.2.tar.gz
tar xvzf IMB-v2019.2.tar.gz
# create link 
ln -s mpi-benchmarks-IMB-v2019.2 imb

#load MPI compiler
module load intel-mpi/2018.3 intel/18.3

cd imb
export CC=mpiicc
make IMB-MPI1
make IMB-EXT
```

# Generate Initiate Configuration File

Generate Initiate Configuration File:

**On AKRR server**
```bash
akrr app add -a $APPKER -r $RESOURCE
```
Sample output:
```text
[INFO] Generating application kernel configuration for imb on ub-hpc
[INFO] Application kernel configuration for imb on ub-hpc is in: 
        /home/akrruser/akrr/etc/resources/ub-hpc/imb.app.conf
```

# Edit Configuration File

In contrast to others application kernels IMB uses only one process per node. Therefore during 
configuration of IMB it is importent to ensure that only one process is run per node. 

Below is a listing of configuration file located at 
~/akrr/etc/resources/$RESOURCE/imb.app.conf for SLURM:

**~/akrr/etc/resources/$RESOURCE/imb.app.conf**
```python
appkernel_run_env_template = """
#Load application enviroment
module load intel/13.0
module load intel-mpi/4.1.0
module list

export I_MPI_PMI_LIBRARY=/usr/lib64/libpmi.so

ulimit -s unlimited

#set how to run mpi applications, one process per node
RUNMPI="srun --ntasks-per-node=1 -n {akrr_num_of_nodes}"
"""
```

Here srun with --ntasks-per-node=1 is used to set one process per node execution.
Modify loading application enviroment to reflect mpi library with which imb was compile.

Below is an example for PBS:

**~/akrr/etc/resources/$RESOURCE/xdmod.benchmark.io.ior.inp.py**
```python
appKernelRunEnvironmentTemplate="""
#Load application enviroment
module swap mvapich2 impi/4.1.3.048/intel64
module list

ulimit -s unlimited
#set how to run mpi applications, one process per node
cat $PBS_NODEFILE|uniq >> all_nodes
cat all_nodes
RUNMPI="mpirun -n $AKRR_NODES -machinefile all_nodes"
"""
```

Here, we first generates machine file containing only one node per process and uses this file with 
mpirun.

# Generate Batch Job Script and Execute it Manually (Optional) 

The purpose of this step is to ensure that the configuration lead to correct workable batch job 
script. Here first batch job script is generated with 'akrr_ctl.sh batch_job'. Then this script is 
executed in interactive session (this improves the turn-around in case of errors). If script fails 
to execute, the issues can be fixed first in that script itself and then merged to configuration 
file.

This step is somewhat optional because it is very similar to next step. However the opportunity to 
work in interactive session improve turn-around time because there is no need to stay in queue for 
each iteration.

First generate the script to standard output and examine it:

```bash
akrr task new --dry-run --gen-batch-job-only -n 2 -r $RESOURCE -a $APPKER
```

**Sample output**
```bash
DryRun: Should submit following to REST API (POST to scheduled_tasks) {'repeat_in': None, 'time_to_start': None, 'resource': 'ub-hpc', 'app': 'imb', 'resource_param': "{'nnodes':2}"}
[INFO] Directory /home/akrruser/akrr/log/data/ub-hpc/imb does not exist, creating it.
[INFO] Directory /home/akrruser/akrr/log/comptasks/ub-hpc/imb does not exist, creating it.
[INFO] Creating task directory: /home/akrruser/akrr/log/data/ub-hpc/imb/2019.03.22.18.54.01.638476
[INFO] Creating task directories: 
        /home/akrruser/akrr/log/data/ub-hpc/imb/2019.03.22.18.54.01.638476/jobfiles
        /home/akrruser/akrr/log/data/ub-hpc/imb/2019.03.22.18.54.01.638476/proc
[INFO] auto_walltime_limit is on, trying to estimate walltime limit...
[INFO] There are only 0 previous run, need at least 5 for walltime limit autoset
[INFO] Below is content of generated batch job script:
#!/bin/bash
#SBATCH --partition=general-compute 
#SBATCH --qos=general-compute
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=8
#SBATCH --time=00:30:00
#SBATCH --output=/projects/ccrstaff/general/nikolays/huey/akrr_data/imb/2019.03.22.18.54.01.638476/stdout
#SBATCH --error=/projects/ccrstaff/general/nikolays/huey/akrr_data/imb/2019.03.22.18.54.01.638476/stderr
#SBATCH --constraint="CPU-L5520"
#SBATCH --exclusive


#Common commands
export AKRR_NODES=2
export AKRR_CORES=16
export AKRR_CORES_PER_NODE=8
export AKRR_NETWORK_SCRATCH="/projects/ccrstaff/general/nikolays/huey/tmp"
export AKRR_LOCAL_SCRATCH="/tmp"
export AKRR_TASK_WORKDIR="/projects/ccrstaff/general/nikolays/huey/akrr_data/imb/2019.03.22.18.54.01.638476"
export AKRR_APPKER_DIR="/projects/ccrstaff/general/nikolays/huey/appker"
export AKRR_AKRR_DIR="/projects/ccrstaff/general/nikolays/huey/akrr_data"

export AKRR_APPKER_NAME="imb"
export AKRR_RESOURCE_NAME="ub-hpc"
export AKRR_TIMESTAMP="2019.03.22.18.54.01.638476"
export AKRR_APP_STDOUT_FILE="$AKRR_TASK_WORKDIR/appstdout"

export AKRR_APPKERNEL_INPUT="/projects/ccrstaff/general/nikolays/huey/appker/execs/imb/src/IMB-EXT"
export AKRR_APPKERNEL_EXECUTABLE="/projects/ccrstaff/general/nikolays/huey/appker/execs/imb/src/IMB-MPI1"

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


#create working dir
mkdir workdir
cd workdir

export AKRR_APPKER_EXEC_DIR=/projects/ccrstaff/general/nikolays/huey/appker/execs/imb/src



#Load application enviroment
module load module load intel-mpi/2018.3 intel/18.3
module list

export I_MPI_PMI_LIBRARY=/usr/lib64/libpmi.so

ulimit -s unlimited

#set how to run mpi applications, one process per node
RUNMPI="srun --ntasks-per-node=1 -n 2"


#Generate AppKer signature
appsigcheck.sh /projects/ccrstaff/general/nikolays/huey/appker/execs/imb/src/IMB-MPI1 $AKRR_TASK_WORKDIR/.. >> $AKRR_APP_STDOUT_FILE
appsigcheck.sh /projects/ccrstaff/general/nikolays/huey/appker/execs/imb/src/IMB-EXT  $AKRR_TASK_WORKDIR/.. >> $AKRR_APP_STDOUT_FILE


#Execute AppKer
echo "Checking that running one process per node (for debugging)"
${RUNMPI} hostname

akrr_write_to_gen_info "appkernel_start_time" "`date`"
${RUNMPI} ${AKRR_APPKER_EXEC_DIR}/IMB-MPI1 -multi 0 -npmin 2 -iter 1000 >> $AKRR_APP_STDOUT_FILE 2>&1
${RUNMPI} ${AKRR_APPKER_EXEC_DIR}/IMB-EXT  -multi 0 -npmin 2 -iter 1000 >> $AKRR_APP_STDOUT_FILE 2>&1
akrr_write_to_gen_info "appkernel_end_time" "`date`"




#clean-up
cd ..
if [ "${AKRR_DEBUG=no}" = "no" ]
then
        echo "Deleting input files"
        rm -rf workdir
fi



akrr_write_to_gen_info "end_time" "`date`"

[INFO] Removing generated files from file-system as only batch job script printing was requested
```

Next generate the script on resource:

```bash
akrr task new --gen-batch-job-only -n 2 -r $RESOURCE -a $APPKER
```

```text
[INFO] Creating task directory: /home/akrruser/akrr/log/data/ub-hpc/imb/2019.03.22.18.55.05.595133
[INFO] Creating task directories: 
        /home/akrruser/akrr/log/data/ub-hpc/imb/2019.03.22.18.55.05.595133/jobfiles
        /home/akrruser/akrr/log/data/ub-hpc/imb/2019.03.22.18.55.05.595133/proc
[INFO] Creating batch job script and submitting it to remote machine
[INFO] Directory huey:/projects/ccrstaff/general/nikolays/huey/akrr_data/imb does not exists, will try to create it
[INFO] Directory huey:/projects/ccrstaff/general/nikolays/huey/akrr_data/imb/2019.03.22.18.55.05.595133 does not exists, will try to create it
[INFO] auto_walltime_limit is on, trying to estimate walltime limit...
[INFO] There are only 0 previous run, need at least 5 for walltime limit autoset
[INFO] Local copy of batch job script is /home/akrruser/akrr/log/data/ub-hpc/imb/2019.03.22.18.55.05.595133/jobfiles/imb.job

[INFO] Application kernel working directory on ub-hpc is /projects/ccrstaff/general/nikolays/huey/akrr_data/imb/2019.03.22.18.55.05.595133
[INFO] Batch job script location on ub-hpc is /projects/ccrstaff/general/nikolays/huey/akrr_data/imb/2019.03.22.18.55.05.595133/imb.job
```

The output contains the working directory for this task on remote resource. On remote resource get 
to that directory and submit batch script for execution.

**On remote resource**
```bash
#get to working directory
cd /projects/ccrstaff/general/nikolays/huey/akrr_data/imb/2019.03.22.18.55.05.595133

#run ior application kernel
bash imb.job
```

Examine appstdout file, which contains application kernel output ([appstdout sample](AKRR_IMB_appsout_sample.md)).

If it looks ok you can move to the next step

# Perform Validation Run

On this step appkernel_validation.py utility is used to validate application kernel installation on 
the resource. It executes the application kernel and analyses its results. If it fails the problems 
need to be fixed and another round of validation (as detailed above) should be performed.

```bash
akrr app validate -n 2 -r $RESOURCE -a $APPKER 
```

See [validation output sample](AKRR_IMB_appkernel_validation_sample.md)

If validation was executed successfully IMB is installed and can be schedule for regular execution.

# Schedule regular execution of application kernel.

Now this application kernel can be submitted for regular execution:

```bash
#Perform a test run on all nodes count
akrr task new -r $RESOURCE -a $APPKER -n 2,4,8

#Start daily execution from today on nodes 2,4,8 and distribute execution time between 1:00 and 5:00
akrr task new -r $RESOURCE -a $APPKER -n 2,4,8 -t0 "01:00" -t1 "05:00" -p 1

# Run on all nodes count 20 times (default number of runs to establish baseline)
akrr task new -r $RESOURCE -a $APPKER -n 2,4,8 --n-runs 20
```

see [Scheduling and Rescheduling Application Kernels](AKRR_Tasks_Scheduling.md) and 
[Setup Walltime Limit](AKRR_Walltimelimit_Setting.md) for more details.

Up: [Deployment of Application Kernels on Resource](AKRR_Deployment_of_Application_Kernel_on_Resource.md)
