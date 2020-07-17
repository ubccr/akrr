# AKRR: Deployment of Enzo Application Kernel on a Resource

[Enzo](https://enzo-project.org/) is astrophysics simulation code, 
that uses an Adaptive Mesh Refinement (AMR) to solve some of its PDE

For further convenience of application kernel deployment lets define APPKER and RESOURCE environment 
variable which will contain the HPC resource name:

```bash
export RESOURCE=<resource_name>
export APPKER=enzo
```

# Install Application

Enzo is rarely installed system-wide. One of the purposes of application kernels is to monitor 
the performance of application which is used by regular users. 
In this case it was added to monitor the performance of AMR code. 
So if there is no Enzo users on your system you can skip this app kernel.

On HPC resource
```bash
# Get to executable directory
cd $AKRR_APPKER_DIR/execs

# see https://enzo-project.org/BootCamp.html for more details
git clone https://github.com/enzo-project/enzo-dev
cd enzo-dev
./configure
cd src/enzo
# choose something close to you machine from:
ls Make.mach.*
# edit it if needed and run
make machine-tacc-stampede-intel
# check config
make show-config
# update option for example set high optimization instead of debug 
make opt-high
# check config again
make show-config
make
cd ../ring/
make
cd ../inits/
make
``` 

# Generate Initiate Configuration File

Generate Initiate Configuration File:

**On AKRR server**
```bash
akrr app add -a $APPKER -r $RESOURCE
```
Sample output:
```text
[INFO] Generating application kernel configuration for gamess on ub-hpc
[INFO] Application kernel configuration for gamess on ub-hpc is in: 
        /home/akrruser/akrr/etc/resources/ub-hpc/gamess.app.conf
```

# Edit Configuration File

Below is listing of example configuration file located at ~/akrr/etc/resources/$RESOURCE/gamess.app.conf

**~/akrr/etc/resources/$RESOURCE/gamess.app.conf**
```python
appkernel_run_env_template = """
# Load application enviroment
module load gamess
module list

# set executable location
VERNO=01
EXE=$GAMESS_DIR/gamess.$VERNO.x

# set how to run app kernel
RUN_APPKERNEL="$AKRR_APPKER_DIR/execs/gamess/rungms $INPUT $VERNO $AKRR_CORES"
"""
```

It contain only one parameter _appkernel_run_env_template_ which need to be edited:

1) First part is "Load application environment", here you need to set proper enviroment. For example:

```bash
# Load application environment
module load gamess/11Nov2017R3
module list
```

2) Second part is "set executable location", it set the location of executables absolute path to 
gamess should be placed to EXE variable (application signature will be calculated for that 
executable) as well as version (VERNO). Use values which we find earlier. For example:

```bash
# set executable location
VERNO=01
EXE=/util/academic/gamess/11Nov2017R3/impi/gamess/gamess.$VERNO.x
```

3)Fourth part is "set how to run app kernel", it set RUN_APPKERNEL, which specify how to execute GAMESS:
```bash
#Set how to ran app kernel
RUN_APPKERNEL="$AKRR_APPKER_DIR/execs/gamess/rungms $INPUT $VERNO $AKRR_NODES $AKRR_CORES_PER_NODE"
```
Most likely you don't need to modify anything here, just ensure that `rungms` refer to your 
version which was modified earlied..


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
#SBATCH --time=00:20:00
#SBATCH --output=/projects/ccrstaff/general/nikolays/huey/akrr_data/gamess/2019.04.29.20.03.58.405597/stdout
#SBATCH --error=/projects/ccrstaff/general/nikolays/huey/akrr_data/gamess/2019.04.29.20.03.58.405597/stderr
#SBATCH --constraint="CPU-L5520"
#SBATCH --exclusive


#Common commands
export AKRR_NODES=2
export AKRR_CORES=16
export AKRR_CORES_PER_NODE=8
export AKRR_NETWORK_SCRATCH="/projects/ccrstaff/general/nikolays/huey/tmp"
export AKRR_LOCAL_SCRATCH="/tmp"
export AKRR_TASK_WORKDIR="/projects/ccrstaff/general/nikolays/huey/akrr_data/gamess/2019.04.29.20.03.58.405597"
export AKRR_APPKER_DIR="/projects/ccrstaff/general/nikolays/huey/appker"
export AKRR_AKRR_DIR="/projects/ccrstaff/general/nikolays/huey/akrr_data"

export AKRR_APPKER_NAME="gamess"
export AKRR_RESOURCE_NAME="ub-hpc"
export AKRR_TIMESTAMP="2019.04.29.20.03.58.405597"
export AKRR_APP_STDOUT_FILE="$AKRR_TASK_WORKDIR/appstdout"

export AKRR_APPKERNEL_INPUT="/projects/ccrstaff/general/nikolays/huey/appker/inputs/gamess/c8h10-cct-mp2.inp"
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
export AKRR_TMP_WORKDIR=`mktemp -d /projects/ccrstaff/general/nikolays/huey/tmp/gamess.XXXXXXXXX`
echo "Temporary working directory: $AKRR_TMP_WORKDIR"
cd $AKRR_TMP_WORKDIR

#Copy inputs
cp /projects/ccrstaff/general/nikolays/huey/appker/inputs/gamess/c8h10-cct-mp2.inp ./
INPUT=$(echo /projects/ccrstaff/general/nikolays/huey/appker/inputs/gamess/c8h10-cct-mp2.inp | xargs basename )



#Load application enviroment
module load gamess/11Nov2017R3
module list

#set executable location
VERNO=01
EXE=/util/academic/gamess/11Nov2017R3/impi/gamess/gamess.$VERNO.x

#set how to run app kernel
RUN_APPKERNEL="$AKRR_APPKER_DIR/execs/gamess/rungms $INPUT $VERNO $AKRR_NODES $AKRR_CORES_PER_NODE"


#Generate AppKer signature
appsigcheck.sh $EXE $AKRR_TASK_WORKDIR/.. > $AKRR_APP_STDOUT_FILE


ATTEMPTS_TO_LAUNCH=0
while ! grep -q "EXECUTION OF GAMESS TERMINATED NORMALLY" $AKRR_APP_STDOUT_FILE
do
    echo "Attempt to launch GAMESS: $ATTEMPTS_TO_LAUNCH" >> $AKRR_APP_STDOUT_FILE 2>&1
    echo "Attempt to launch GAMESS: $ATTEMPTS_TO_LAUNCH"
    rm -rf *
    mkdir scr
    mkdir supout
    cp /projects/ccrstaff/general/nikolays/huey/appker/inputs/gamess/c8h10-cct-mp2.inp ./
    $RUN_APPKERNEL >> $AKRR_APP_STDOUT_FILE 2>&1
    
    if [ "$ATTEMPTS_TO_LAUNCH" -ge 6 ]; then
        break
    fi
    
    ((ATTEMPTS_TO_LAUNCH++))
done
akrr_write_to_gen_info "attemptsToLaunch" "$ATTEMPTS_TO_LAUNCH"
echo "Total attempt to launch GAMESS is $ATTEMPTS_TO_LAUNCH"




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
[INFO] Creating task directory: /home/akrruser/akrr/log/data/ub-hpc/gamess/2019.04.29.20.04.39.697226
[INFO] Creating task directories: 
        /home/akrruser/akrr/log/data/ub-hpc/gamess/2019.04.29.20.04.39.697226/jobfiles
        /home/akrruser/akrr/log/data/ub-hpc/gamess/2019.04.29.20.04.39.697226/proc
[INFO] Creating batch job script and submitting it to remote machine
[INFO] Directory huey:/projects/ccrstaff/general/nikolays/huey/akrr_data/gamess does not exists, will try to create it
[INFO] Directory huey:/projects/ccrstaff/general/nikolays/huey/akrr_data/gamess/2019.04.29.20.04.39.697226 does not exists, will try to create it
[INFO] auto_walltime_limit is on, trying to estimate walltime limit...
[INFO] There are only 0 previous run, need at least 5 for walltime limit autoset
[INFO] Local copy of batch job script is /home/akrruser/akrr/log/data/ub-hpc/gamess/2019.04.29.20.04.39.697226/jobfiles/gamess.job

[INFO] Application kernel working directory on ub-hpc is /projects/ccrstaff/general/nikolays/huey/akrr_data/gamess/2019.04.29.20.04.39.697226
[INFO] Batch job script location on ub-hpc is /projects/ccrstaff/general/nikolays/huey/akrr_data/gamess/2019.04.29.20.04.39.697226/gamess.job
```

The output contains the working directory for this task on remote resource. On remote resource get 
to that directory and start interactive session (request same number of nodes, in example above the 
script was generated for 2 nodes).

**On remote resource**
```bash
#get to working directory
cd /projects/ccrstaff/general/nikolays/huey/akrr_data/gamess/2019.04.29.20.04.39.697226
#check hpcc.job is there
ls
#start interactive session
salloc --nodes=2 --ntasks-per-node=8 --time=01:00:00 --exclusive --constraint="CPU-L5520"
#wait till you get access to interactive session
#run ior application kernel
bash gamess.job

# or submit as normal batch script
sbatch gamess.job

#examine output
cat appstdout
```

Examine appstdout file, which contains application kernel output ([appstdout sample](AKRR_GAMESS_appsout_sample.md)). 
If it looks ok you can move to the next step

# Perform Validation Run

On this step appkernel_validation.py utility is used to validate application kernel installation on 
particular resource. It execute application kernel and analyses its' results. If it fails the 
problems need to be fixed and another round of validation should be performed.

```bash
akrr app validate -n 2 -r $RESOURCE -a $APPKER 
```

See [validation output sample](AKRR_GAMESS_appkernel_validation_sample.md)

# Schedule regular execution of application kernel.

Now this application kernel can be submitted for regular execution:

# Perform a test run on all nodes count
```bash
#Perform a test run on all nodes count
akrr task new -r $RESOURCE -a $APPKER -n 1,2,4,8

#Start daily execution from today on nodes 1,2,4,8 and distribute execution time between 1:00 and 5:00
akrr task new -r $RESOURCE -a $APPKER -n 1,2,4,8 -t0 "01:00" -t1 "05:00" -p 1
```

see [Scheduling and Rescheduling Application Kernels](AKRR_Tasks_Scheduling.md) and 
[Setup Walltime Limit](AKRR_Walltimelimit_Setting.md) for more details.


Up: [Deployment of Application Kernels on Resource](AKRR_Deployment_of_Application_Kernel_on_Resource.md)
