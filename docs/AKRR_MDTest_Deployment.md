# AKRR: Deployment of MDTest Applications Kernels on a Resource

MDTest benchmark measures the performance of parallel file-systems on meta data operations.

For simplicity lets define APPKER and RESOURCE environment variable which will contain the HPC 
resource name and application kernel name:

```bash
export RESOURCE=<resource_name>
export APPKER=mdtest
```

## Installing MDTest

MDTest is now part of IOR benchmark, so If you already install IOR it should be there already. 
Otherwise see [IOR Deployment](AKRR_IOR_Deployment.md).

# Generate Initiate Configuration File

Generate Initiate Configuration File:

**On AKRR server**
```bash
akrr app add -a $APPKER -r $RESOURCE
```
Sample output:
```text
[INFO] Generating application kernel configuration for mdtest on ub-hpc
[INFO] Application kernel configuration for mdtest on ub-hpc is in: 
        /home/akrruser/akrr/etc/resources/ub-hpc/mdtest.app.conf
```


# Edit Configuration File

Below is a listing of configuration file located at 
~/akrr/etc/resources/$RESOURCE/mdtest.app.conf for SLURM:

**initial ~/akrr/etc/resources/$RESOURCE/mdtest.app.conf**
```python
appKernelRunEnvironmentTemplate = """
# Load application enviroment
module load intel intel-mpi
module list

export I_MPI_PMI_LIBRARY=/usr/lib64/libpmi.so

# set executable location
EXE=$AKRR_APPKER_DIR/execs/ior/src/mdtest

# set how to run app kernel
RUNMPI="srun"
"""
```

In first section we set proper environment mdtest to work, we also place mdtest executable location to EXE 
variable (binary in $EXE will be used to generate application signature).

I_MPI_PMI_LIBRARY variable allows srun to function properly.

RUNMPI specify which command to use to start MPI processes.


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

**Sample output of akrr task new --dry-run --gen-batch-job-only -n 2 -r $RESOURCE -a $APPKER**
```bash
[INFO] Generating application kernel configuration for mdtest on ub-hpc
[INFO] Application kernel configuration for mdtest on ub-hpc is in: 
        /home/akrruser/akrr/etc/resources/ub-hpc/mdtest.app.conf
[akrruser@xdmod ~]$ vi /home/akrruser/akrr/etc/resources/ub-hpc/mdtest.app.conf
[akrruser@xdmod ~]$ akrr task new --dry-run --gen-batch-job-only -n 2 -r $RESOURCE -a $APPKER 
DryRun: Should submit following to REST API (POST to scheduled_tasks) {'time_to_start': None, 'resource_param': "{'nnodes':2}", 'resource': 'ub-hpc', 'app': 'mdtest', 'repeat_in': None}
[INFO] Directory /home/akrruser/akrr/log/data/ub-hpc/mdtest does not exist, creating it.
[INFO] Directory /home/akrruser/akrr/log/comptasks/ub-hpc/mdtest does not exist, creating it.
[INFO] Creating task directory: /home/akrruser/akrr/log/data/ub-hpc/mdtest/2019.05.01.19.23.08.369371
[INFO] Creating task directories: 
        /home/akrruser/akrr/log/data/ub-hpc/mdtest/2019.05.01.19.23.08.369371/jobfiles
        /home/akrruser/akrr/log/data/ub-hpc/mdtest/2019.05.01.19.23.08.369371/proc
[INFO] auto_walltime_limit is on, trying to estimate walltime limit...
[INFO] There are only 0 previous run, need at least 5 for walltime limit autoset
[INFO] Below is content of generated batch job script:
#!/bin/bash
#SBATCH --partition=general-compute 
#SBATCH --qos=general-compute
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=8
#SBATCH --time=00:30:00
#SBATCH --output=/projects/ccrstaff/general/nikolays/huey/akrr_data/mdtest/2019.05.01.19.23.08.369371/stdout
#SBATCH --error=/projects/ccrstaff/general/nikolays/huey/akrr_data/mdtest/2019.05.01.19.23.08.369371/stderr
#SBATCH --constraint="CPU-L5520"
#SBATCH --exclusive


#Common commands
export AKRR_NODES=2
export AKRR_CORES=16
export AKRR_CORES_PER_NODE=8
export AKRR_NETWORK_SCRATCH="/projects/ccrstaff/general/nikolays/huey/tmp"
export AKRR_LOCAL_SCRATCH="/tmp"
export AKRR_TASK_WORKDIR="/projects/ccrstaff/general/nikolays/huey/akrr_data/mdtest/2019.05.01.19.23.08.369371"
export AKRR_APPKER_DIR="/projects/ccrstaff/general/nikolays/huey/appker"
export AKRR_AKRR_DIR="/projects/ccrstaff/general/nikolays/huey/akrr_data"

export AKRR_APPKER_NAME="mdtest"
export AKRR_RESOURCE_NAME="ub-hpc"
export AKRR_TIMESTAMP="2019.05.01.19.23.08.369371"
export AKRR_APP_STDOUT_FILE="$AKRR_TASK_WORKDIR/appstdout"

export AKRR_APPKERNEL_INPUT="/projects/ccrstaff/general/nikolays/huey/appker/inputs"
export AKRR_APPKERNEL_EXECUTABLE="/projects/ccrstaff/general/nikolays/huey/appker/execs"

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
export AKRR_TMP_WORKDIR=`mktemp -d /projects/ccrstaff/general/nikolays/huey/tmp/namd.XXXXXXXXX`
echo "Temporary working directory: $AKRR_TMP_WORKDIR"
cd $AKRR_TMP_WORKDIR

case $AKRR_NODES in
1)
    ITER=20
    ;;
2)
    ITER=10
    ;;
4)
    ITER=5
    ;;
8)
    ITER=2
    ;;
*)
    ITER=1
    ;;
esac




# Load application enviroment
module load intel/18.3 intel-mpi/18.3
module list

export I_MPI_PMI_LIBRARY=/usr/lib64/libpmi.so
export I_MPI_FABRICS_LIST="tcp"

# set executable location
EXE=$AKRR_APPKER_DIR/execs/ior/src/mdtest

# set how to run app kernel
RUNMPI="srun"


#Generate AppKer signature
appsigcheck.sh $EXE $AKRR_TASK_WORKDIR/.. > $AKRR_APP_STDOUT_FILE


# Execute AppKer
akrr_write_to_gen_info "appkernel_start_time" "`date`"

echo "#Testing single directory" >> $AKRR_APP_STDOUT_FILE 2>&1
$RUNMPI $EXE -v -I 32 -z 0 -b 0 -i $ITER >> $AKRR_APP_STDOUT_FILE 2>&1

echo "#Testing single directory per process" >> $AKRR_APP_STDOUT_FILE 2>&1
$RUNMPI $EXE -v -I 32 -z 0 -b 0 -i $ITER -u >> $AKRR_APP_STDOUT_FILE 2>&1

echo "#Testing single tree directory" >> $AKRR_APP_STDOUT_FILE 2>&1
$RUNMPI $EXE -v -I 4 -z 4 -b 2 -i $ITER >> $AKRR_APP_STDOUT_FILE 2>&1
 
echo "#Testing single tree directory per process" >> $AKRR_APP_STDOUT_FILE 2>&1
$RUNMPI $EXE -v -I 4 -z 4 -b 2 -i $ITER -u >> $AKRR_APP_STDOUT_FILE 2>&1

akrr_write_to_gen_info "appkernel_end_time" "`date`"





# clean-up
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

Next generate the script on resource:
```bash
akrr task new --gen-batch-job-only -n 2 -r $RESOURCE -a $APPKER
```
```text
[INFO] Creating task directory: /home/akrruser/akrr/log/data/ub-hpc/mdtest/2019.05.01.19.24.29.308629
[INFO] Creating task directories: 
        /home/akrruser/akrr/log/data/ub-hpc/mdtest/2019.05.01.19.24.29.308629/jobfiles
        /home/akrruser/akrr/log/data/ub-hpc/mdtest/2019.05.01.19.24.29.308629/proc
[INFO] Creating batch job script and submitting it to remote machine
[INFO] Directory huey:/projects/ccrstaff/general/nikolays/huey/akrr_data/mdtest does not exists, will try to create it
[INFO] Directory huey:/projects/ccrstaff/general/nikolays/huey/akrr_data/mdtest/2019.05.01.19.24.29.308629 does not exists, will try to create it
[INFO] auto_walltime_limit is on, trying to estimate walltime limit...
[INFO] There are only 0 previous run, need at least 5 for walltime limit autoset
[INFO] Local copy of batch job script is /home/akrruser/akrr/log/data/ub-hpc/mdtest/2019.05.01.19.24.29.308629/jobfiles/mdtest.job

[INFO] Application kernel working directory on ub-hpc is /projects/ccrstaff/general/nikolays/huey/akrr_data/mdtest/2019.05.01.19.24.29.308629
[INFO] Batch job script location on ub-hpc is /projects/ccrstaff/general/nikolays/huey/akrr_data/mdtest/2019.05.01.19.24.29.308629/mdtest.job
```

**On remote resource**
```bash
#get to working directory
cd /projects/ccrstaff/general/nikolays/huey/akrr_data/mdtest/2019.05.01.19.24.29.308629
#manually start batch job script
sbatch mdtest.job
```

Examine appstdout file, which contains application kernel output ([appstdout sample](AKRR_MDTest_appsout_sample.md)).

If it looks ok you can move to the next step

# Perform Validation Run

On this step appkernel_validation.py utility is used to validate application kernel installation on 
the resource. It executes the application kernel and analyses its results. If it fails the problems 
need to be fixed and another round of validation (as detailed above) should be performed.

```bash
akrr app validate -n 2 -r $RESOURCE -a $APPKER 
```

See [IOR validation output sample](AKRR_MDTest_appkernel_validation_sample.md)

DONE, you can move to next step!

# Schedule regular execution of application kernel.

Now this application kernel can be submitted for regular execution:

```bash
#Perform a test run on all nodes count
akrr task new -r $RESOURCE -a $APPKER -n 1,2,4,8

#Start daily execution from today on nodes 1,2,4,8 and distribute execution time between 1:00 and 5:00
akrr task new -r $RESOURCE -a $APPKER -n 1,2,4,8 -t0 "01:00" -t1 "05:00" -p 1
```

see [Scheduling and Rescheduling Application Kernels](AKRR_Tasks_Scheduling.md) and 
[Setup Walltime Limit](AKRR_Walltimelimit_Setting.md) for more details.

# Troubleshooting


## During linking stage of compilation got: "undefined reference to \`gpfs_fcntl'"

The linker does not by default link the necessary GPFS library, you can instead do this step manually, for example:

```bash
cd src
mpiicc  -g -O2   -o ior -lgpfs ior.o utilities.o parse_options.o aiori-POSIX.o aiori-MPIIO.o
```

Or rerun configuration with corrected LIBS (correct configure option for your needs), for example:

```bash
./configure --with-hdf5=no --with-ncmpi=no  LIBS="-lgpsf"
```

Up: [Deployment of Application Kernels on Resource](AKRR_Deployment_of_Application_Kernel_on_Resource.md)
