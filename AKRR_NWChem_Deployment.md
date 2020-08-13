# AKRR: Deployment of NWChem Application Kernel on a Resource

NWChem is computational chemistry software which includes large range of quantum chemistry methods. 
It was specidically designed with HPC systems in mind. NWChem applications kernel can be used to 
monitory the performance of system-wide NWChem installation. It also links against linear algebra 
library and can use file-system for cache storage. Thus it also can work as a probe to monitor 
performance of these items. If there is nobody uses NWChem on your site you can skip it. However, 
unlike benchmarks (HPCC, IOR, IMB) which stress a particular subsystem 
NWChem application kernel works more like an integrated test and the affects on it can be much milder
(for example like in case of Meltdown/Spectre remidies).
 

For further convenience of application kernel deployment lets define APPKER and RESOURCE environment 
variable which will contain the HPC resource name:

```bash
export RESOURCE=<resource_name>
export APPKER=nwchem
```

# Install Application or Identify where it is Installed

NWChem is very often installed system-wide. One of the purposes of application kernels is to monitor 
the performance of application which is used by regular users. If NWChem is not installed then you 
might need to install this application on your resource or opted not to use it.

Majority of HPC resources utilize some kind of module system. Execute it and see is NWChem already 
installed

**On resource**
```bash
module avail nwchem
```
```text
---------------- /util/academic/modulefiles/Core -----------------
   nwchem/6.0    nwchem/6.8 (D)
```

We'll use  nwchem/6.8.

# Generate Initiate Configuration File

Generate Initiate Configuration File:

**On AKRR server**
```bash
akrr app add -a $APPKER -r $RESOURCE
```
Sample output:
```text
[INFO] Generating application kernel configuration for nwchem on ub-hpc
[INFO] Application kernel configuration for nwchem on ub-hpc is in: 
        /home/akrruser/akrr/etc/resources/ub-hpc/nwchem.app.conf
```

# Edit Configuration File

Below is listing of example configuration file located at ~/akrr/etc/resources/$RESOURCE/nwchem.app.conf

**~/akrr/etc/resources/$RESOURCE/nwchem.app.conf**
```python
appkernel_run_env_template = """
# Load application environment
module load nwchem
module list

# make srun works with intel mpi
export I_MPI_PMI_LIBRARY=/usr/lib64/libpmi.so

# set executable location
EXE=`which nwchem`

#set how to run app kernel
RUN_APPKERNEL="srun $EXE $INPUT"
"""
```
It contain only one parameter _appkernel_run_env_template_ which need to be edited:

1) First part is "Load application environment", here you need to set proper enviroment. For example:

```bash
# Load application environment
module load nwchem
module list
```

2) Second part is "set executable location", it set the location of executables absolute path to 
nwchem should be placed to EXE variable (application signature will be calculated for that 
executable). For example:

```bash
#set executable location
EXE=`which nwchem`
```

3)Fourth part is "set how to run app kernel", it set RUN_APPKERNEL, which specify how to execute namd:
```bash
#Set how to ran app kernel
RUN_APPKERNEL="srun $EXE $INPUT"
```


# Generate Batch Job Script and Execute it Manually (Optional) 


The purpose of this step is to ensure that the configuration lead to correct workable batch job 
script. Here, at first batch job script is generated with 'akrr_ctl.sh batch_job'. Then this script 
is executed in interactive session (this improves the turn-around in case of errors). If script 
fails to execute, the issues can be fixed first in that script itself and then merged to 
configuration file.

This step is somewhat optional because it is very similar to next step. However the opportunity to 
work in interactive session improve turn-around time because there is no need to stay in queue for 
each iteration.

First generate the script to standard output and examine it:

```bash
akrr task new --dry-run --gen-batch-job-only -n 2 -r $RESOURCE -a $APPKER
```

**Portion of "_akrr task new --dry-run --gen-batch-job-only -n 2 -r $RESOURCE -a $APPKER_" output showing generated 
batch script**
```bash
#!/bin/bash
#SBATCH --partition=general-compute 
#SBATCH --qos=general-compute
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=8
#SBATCH --time=00:22:00
#SBATCH --output=/projects/ccrstaff/general/nikolays/huey/akrr_data/nwchem/2019.03.25.19.42.00.933217/stdout
#SBATCH --error=/projects/ccrstaff/general/nikolays/huey/akrr_data/nwchem/2019.03.25.19.42.00.933217/stderr
#SBATCH --constraint="CPU-L5520"
#SBATCH --exclusive


#Common commands
export AKRR_NODES=2
export AKRR_CORES=16
export AKRR_CORES_PER_NODE=8
export AKRR_NETWORK_SCRATCH="/projects/ccrstaff/general/nikolays/huey/tmp"
export AKRR_LOCAL_SCRATCH="/tmp"
export AKRR_TASK_WORKDIR="/projects/ccrstaff/general/nikolays/huey/akrr_data/nwchem/2019.03.25.19.42.00.933217"
export AKRR_APPKER_DIR="/projects/ccrstaff/general/nikolays/huey/appker"
export AKRR_AKRR_DIR="/projects/ccrstaff/general/nikolays/huey/akrr_data"

export AKRR_APPKER_NAME="nwchem"
export AKRR_RESOURCE_NAME="ub-hpc"
export AKRR_TIMESTAMP="2019.03.25.19.42.00.933217"
export AKRR_APP_STDOUT_FILE="$AKRR_TASK_WORKDIR/appstdout"

export AKRR_APPKERNEL_INPUT="/projects/ccrstaff/general/nikolays/huey/appker/inputs/nwchem/aump2.nw"
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
export AKRR_TMP_WORKDIR=`mktemp -d /projects/ccrstaff/general/nikolays/huey/tmp/nwchem.XXXXXXXXX`
echo "Temporary working directory: $AKRR_TMP_WORKDIR"
cd $AKRR_TMP_WORKDIR

#Copy inputs
cp /projects/ccrstaff/general/nikolays/huey/appker/inputs/nwchem/aump2.nw ./
INPUT=$(echo /projects/ccrstaff/general/nikolays/huey/appker/inputs/nwchem/aump2.nw | xargs basename )

ulimit -s unlimited

# set the NWCHEM_PERMANENT_DIR and NWCHEM_SCRATCH_DIR in the input file
# first, comment out any NWCHEM_PERMANENT_DIR and NWCHEM_SCRATCH_DIR in the input file
if [ -e $INPUT ]
then
    sed -i -e "s/scratch_dir/#/g" $INPUT
    sed -i -e "s/permanent_dir/#/g" $INPUT
    # then add our own
    echo "scratch_dir $AKRR_TMP_WORKDIR" >> $INPUT
    echo "permanent_dir $AKRR_TMP_WORKDIR" >> $INPUT
fi



# Load application environment
module load nwchem
module list

# make srun works with intel mpi
export I_MPI_PMI_LIBRARY=/usr/lib64/libpmi.so

# set executable location
EXE=`which nwchem`

#set how to run app kernel
RUN_APPKERNEL="srun $EXE $INPUT"


#Generate AppKer signature
appsigcheck.sh $EXE $AKRR_TASK_WORKDIR/.. > $AKRR_APP_STDOUT_FILE


#Execute AppKer
akrr_write_to_gen_info "appkernel_start_time" "`date`"
$RUN_APPKERNEL >> $AKRR_APP_STDOUT_FILE 2>&1
akrr_write_to_gen_info "appkernel_end_time" "`date`"




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

```

Next generate the script on resource:

```bash
akrr task new --gen-batch-job-only -n 2 -r $RESOURCE -a $APPKER
```
```text
[INFO] Creating task directory: /home/akrruser/akrr/log/data/ub-hpc/nwchem/2019.03.25.19.42.42.584465
[INFO] Creating task directories: 
        /home/akrruser/akrr/log/data/ub-hpc/nwchem/2019.03.25.19.42.42.584465/jobfiles
        /home/akrruser/akrr/log/data/ub-hpc/nwchem/2019.03.25.19.42.42.584465/proc
[INFO] Creating batch job script and submitting it to remote machine
[INFO] Directory huey:/projects/ccrstaff/general/nikolays/huey/akrr_data/nwchem does not exists, will try to create it
[INFO] Directory huey:/projects/ccrstaff/general/nikolays/huey/akrr_data/nwchem/2019.03.25.19.42.42.584465 does not exists, will try to create it
[INFO] auto_walltime_limit is on, trying to estimate walltime limit...
[INFO] There are only 0 previous run, need at least 5 for walltime limit autoset
[INFO] Local copy of batch job script is /home/akrruser/akrr/log/data/ub-hpc/nwchem/2019.03.25.19.42.42.584465/jobfiles/nwchem.job

[INFO] Application kernel working directory on ub-hpc is /projects/ccrstaff/general/nikolays/huey/akrr_data/nwchem/2019.03.25.19.42.42.584465
[INFO] Batch job script location on ub-hpc is /projects/ccrstaff/general/nikolays/huey/akrr_data/nwchem/2019.03.25.19.42.42.584465/nwchem.job
```

The output contains the working directory for this task on remote resource. On remote resource get 
to that directory and start interactive session (request same number of nodes, in example above the 
script was generated for 2 nodes).

**On remote resource**
```bash
#get to working directory
cd /projects/ccrstaff/general/nikolays/huey/akrr_data/nwchem/2019.03.25.19.42.42.584465
#check hpcc.job is there
ls
#start interactive session
salloc --nodes=2 --ntasks-per-node=8 --time=01:00:00 --exclusive --constraint="CPU-L5520"
#wait till you get access to interactive session
#run ior application kernel
bash nwchem.job

# or submit as normal batch script
sbatch nwchem.job

#examine output
cat appstdout
```

Examine appstdout file, which contains application kernel output ([appstdout sample](AKRR_NWChem_appsout_sample.md)). 
If it looks ok you can move to the next step

# Perform Validation Run

On this step appkernel_validation.py utility is used to validate application kernel installation on 
particular resource. It execute application kernel and analyses its' results. If it fails the 
problems need to be fixed and another round of validation should be performed.

```bash
akrr app validate -n 2 -r $RESOURCE -a $APPKER 
```

See [NWChem validation output sample](AKRR_NWChem_appkernel_validation_sample.md)

# Schedule regular execution of application kernel.

Now this application kernel can be submitted for regular execution:

# Perform a test run on all nodes count
```bash
#Perform a test run on all nodes count
akrr task new -r $RESOURCE -a $APPKER -n 1,2,4,8

#Start daily execution from today on nodes 1,2,4,8 and distribute execution time between 1:00 and 5:00
akrr task new -r $RESOURCE -a $APPKER -n 1,2,4,8 -t0 "01:00" -t1 "05:00" -p 1

# Run on all nodes count 20 times (default number of runs to establish baseline)
akrr task new -r $RESOURCE -a $APPKER -n 1,2,4,8 --n-runs 20
```

see [Scheduling and Rescheduling Application Kernels](AKRR_Tasks_Scheduling.md) and 
[Setup Walltime Limit](AKRR_Walltimelimit_Setting.md) for more details.


Up: [Deployment of Application Kernels on Resource](AKRR_Deployment_of_Application_Kernel_on_Resource.md)
