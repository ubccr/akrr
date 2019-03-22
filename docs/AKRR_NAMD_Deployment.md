# Deployment of NAMD Applications Kernels on a Resource

Here the deployment of namd application kernel is described. This application kernel is 
based on NAMD application.

For simplicity lets define APPKER and RESOURCE enviroment varible which will contain the HPC 
resource name:

```bash
export RESOURCE=rush
export APPKER=xdmod.app.md.namd
```

## Install Application or Identify where it is Installed

NAMD is very often installed system-wide. One of the purposes of application kernels is to monitor 
the performance of application which is used by regular users. If NAMD is not installed then you 
need to install it or choose not to use it.

Majority of HPC resources utilize some kind of module system. Execute it and see is NAMD already 
installed

**On resource**
```text
> module avail namd

-------------------------------- /util/academic/modulefiles/Core --------------------------------
   namd/2.8-MPI-CUDA             namd/2.10-ibverbs          (D)    namd/2.12b1-multicore
   namd/2.9b2-IBVERBS            namd/2.10-multicore-CUDA          namd/2.12-ibverbs-smp-CUDA
   namd/2.9-IBVERBS-SRC          namd/2.10-multicore-MIC           namd/2.12-ibverbs-smp
   namd/2.9-IBVERBS              namd/2.10-multicore               namd/2.12-ibverbs
   namd/2.9-MPI-CUDA             namd/2.11-ibverbs-smp-CUDA        namd/2.12-multicore-CUDA
   namd/2.9-MPI                  namd/2.11-MPI                     namd/2.12-multicore
   namd/2.10-ibverbs-smp-CUDA    namd/2.11-multicore-CUDA
   namd/2.10-ibverbs-smp         namd/2.12b1-ibverbs
...
```

write down the name of module you want to use.

## Generate Initiate Configuration File

Generate Initiate Configuration File:

**On AKRR server**
```bash
akrr app add -a $APPKER -r $RESOURCE
```
Sample output:
```tetxt
[INFO] Generating application kernel configuration for namd on ub-hpc
[INFO] Application kernel configuration for namd on ub-hpc is in: 
        /home/akrruser/akrr/etc/resources/ub-hpc/namd.app.conf
```

## Edit Configuration File

Below is listing of generated configuration file located at ~/akrr/etc/resources/$RESOURCE/namd.app.conf


**~/akrr/etc/resources/$RESOURCE/namd.app.conf**
```python
appkernel_run_env_template = """
#Load application environment
module load namd
export CONV_RSH=ssh

#set executable location
EXE=`which namd2`
charmrun_bin=`which charmrun`

#prepare nodelist for charmmrun
for n in $AKRR_NODELIST; do echo host $n>>nodelist; done

#set how to run app kernel
RUN_APPKERNEL="$charmrun_bin  +p$AKRR_CORES ++nodelist nodelist $EXE ./input.namd"
"""
```

It contain only one parameter _appkernel_run_env_template_ which need to be edited:

1) First part is "Load application environment", here you need to set proper environment. For example:
```bash
#Load application environment
module load namd/2.12-ibverbs
export CONV_RSH=ssh
```

The last line above specify to use ssh for application launching.

2) Second part is "set executable location", it set the location of executables absolute path to 
namd2 should be placed to EXE variable (application signature will be calculated for that 
executable). For example:

```bash
#set executable location
EXE=`which namd2`
charmrun_bin=`which namd2`
```

3)Third part is "prepare nodelist for charmmrun", it setup nodelist file which later will be used by 
charmm run
```bash
#prepare nodelist for charmmrun 
for n in $AKRR_NODELIST; do echo host $n>>nodelist; done
```

4)Fourth part is "set how to run app kernel", it set RUN_APPKERNEL, which specify how to execute 
namd:
```bash
#set how to run app kernel
RUN_APPKERNEL="$charmrun_bin +p$AKRR_CORES ++nodelist nodelist $EXE ./input.namd"
```

If MPI version of namd is used the ~/akrr/etc/resources/$RESOURCE/namd.app.conf can look 
like:

**~/akrr/etc/resources/$RESOURCE/namd.app.conf**
```python
appkernel_run_env_template="""
#Load application environment
module load namd/2.11-MPI
module list

#set executable location
EXE=`which namd2`

#set how to run app kernel
RUN_APPKERNEL="mpirun -n $AKRR_CORES -hostfile $PBS_NODEFILE $EXE ./input.namd"
"""
```

## Generate Batch Job Script and Execute it Manually (Optional) 

The purpose of this step is to ensure that the configuration lead to correct workable batch job 
script. Here first batch job script is generated with 'akrr task new --gen-batch-job-only'
command. This allows interactive execution to improve turn-around in case of errors. If script fails 
to execute, the issues can be fixed first in that script itself and then merged to configuration 
file.

This step is somewhat optional because it is very similar to next step. However the opportunity to 
work in interactive session improve turn-around time because there is no need to stay in queue for 
each iteration.

First generate the script to standard output and examine it:

```bash
akrr task new --dry-run --gen-batch-job-only -n 2 -r $RESOURCE -a $APPKER
```
```text
DryRun: Should submit following to REST API (POST to scheduled_tasks) {'resource_param': "{'nnodes':2}", 'time_to_start': None, 'repeat_in': None, 'app': 'namd', 'resource': 'ub-hpc'}
[INFO] Directory /home/akrruser/akrr/log/data/ub-hpc/namd does not exist, creating it.
[INFO] Directory /home/akrruser/akrr/log/comptasks/ub-hpc/namd does not exist, creating it.
[INFO] Creating task directory: /home/akrruser/akrr/log/data/ub-hpc/namd/2019.03.20.19.41.07.389241
[INFO] Creating task directories: 
        /home/akrruser/akrr/log/data/ub-hpc/namd/2019.03.20.19.41.07.389241/jobfiles
        /home/akrruser/akrr/log/data/ub-hpc/namd/2019.03.20.19.41.07.389241/proc
[INFO] auto_walltime_limit is on, trying to estimate walltime limit...
[WARNING] There are only %d previous run, need at least 5 for walltime limit autoset
[INFO] Below is content of generated batch job script:
#!/bin/bash
#SBATCH --partition=general-compute 
#SBATCH --qos=general-compute
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=8
#SBATCH --time=00:13:00
#SBATCH --output=/user/nikolays/tmp/akrr_data/ub-hpc/namd/2019.03.20.19.41.07.389241/stdout
#SBATCH --error=/user/nikolays/tmp/akrr_data/ub-hpc/namd/2019.03.20.19.41.07.389241/stderr
#SBATCH --constraint="CPU-L5520"
#SBATCH --exclusive


#Common commands
export AKRR_NODES=2
export AKRR_CORES=16
export AKRR_CORES_PER_NODE=8
export AKRR_NETWORK_SCRATCH="/user/nikolays/tmp"
export AKRR_LOCAL_SCRATCH="/tmp"
export AKRR_TASK_WORKDIR="/user/nikolays/tmp/akrr_data/ub-hpc/namd/2019.03.20.19.41.07.389241"
export AKRR_APPKER_DIR="/user/nikolays/appker/ub-hpc"
export AKRR_AKRR_DIR="/user/nikolays/tmp/akrr_data/ub-hpc"

export AKRR_APPKER_NAME="namd"
export AKRR_RESOURCE_NAME="ub-hpc"
export AKRR_TIMESTAMP="2019.03.20.19.41.07.389241"
export AKRR_APP_STDOUT_FILE="$AKRR_TASK_WORKDIR/appstdout"

export AKRR_APPKERNEL_INPUT="/user/nikolays/appker/ub-hpc/inputs/namd/apoa1_nve"
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


#create working dir
export AKRR_TMP_WORKDIR=`mktemp -d /user/nikolays/tmp/namd.XXXXXXXXX`
echo "Temporary working directory: $AKRR_TMP_WORKDIR"
cd $AKRR_TMP_WORKDIR

#Copy inputs
cp /user/nikolays/appker/ub-hpc/inputs/namd/apoa1_nve/* ./



#Load application environment
module load namd/2.12-ibverbs
export CONV_RSH=ssh

#set executable location
EXE=`which namd2`
charmrun_bin=`which charmrun`

#prepare nodelist for charmmrun
for n in $AKRR_NODELIST; do echo host $n>>nodelist; done

#set how to run app kernel
RUN_APPKERNEL="$charmrun_bin  +p$AKRR_CORES ++nodelist nodelist $EXE ./input.namd"


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

[INFO] Removing generated files from file-system as only batch job script printing was requested
```

Next generate the script on resource:
```bash
akrr task new --gen-batch-job-only -n 2 -r $RESOURCE -a $APPKER 
```
```text
[INFO] Creating task directory: /home/akrruser/akrr/log/data/ub-hpc/namd/2019.03.20.19.42.33.945872
[INFO] Creating task directories: 
        /home/akrruser/akrr/log/data/ub-hpc/namd/2019.03.20.19.42.33.945872/jobfiles
        /home/akrruser/akrr/log/data/ub-hpc/namd/2019.03.20.19.42.33.945872/proc
[INFO] Creating batch job script and submitting it to remote machine
[INFO] Directory huey:/user/nikolays/tmp/akrr_data/ub-hpc/namd does not exists, will try to create it
[INFO] Directory huey:/user/nikolays/tmp/akrr_data/ub-hpc/namd/2019.03.20.19.42.33.945872 does not exists, will try to create it
[INFO] auto_walltime_limit is on, trying to estimate walltime limit...
[WARNING] There are only 0 previous run, need at least 5 for walltime limit autoset
[INFO] Local copy of batch job script is /home/akrruser/akrr/log/data/ub-hpc/namd/2019.03.20.19.42.33.945872/jobfiles/namd.job

[INFO] Application kernel working directory on ub-hpc is /user/nikolays/tmp/akrr_data/ub-hpc/namd/2019.03.20.19.42.33.945872
[INFO] Batch job script location on ub-hpc is /user/nikolays/tmp/akrr_data/ub-hpc/namd/2019.03.20.19.42.33.945872/namd.job
```

The output contains the working directory for this task on remote resource. On remote resource get 
to that directory and start interactive session (request same number of nodes, in example above the 
script was generated for 2 nodes).

**On remote resource**
```text
> cd /user/nikolays/tmp/akrr_data/ub-hpc/namd/2019.03.20.19.42.33.945872
> ls
namd.job
> salloc --partition=debug --nodes=2 --ntasks-per-node=8 --time=01:00:00 --exclusive --constraint="CPU-L5520"
salloc: Granted job allocation 10835
> bash namd.job 
Temporary working directory: /user/nikolays/tmp/namd.3EaG6beEQ
Deleting temporary files
```

Examine appstdout file, which contains application kernel output:

**On remote resource**
```text
> cat appstdout
 ===ExeBinSignature=== MD5: 45f97315d9290c3c631d78e3defad52f /util/academic/namd/NAMD_2.12_Linux-x86_64-ibverbs/namd2
===ExeBinSignature=== MD5: a67349ee487ece290224fbca93b5811b /lib64/libibverbs.so.1
===ExeBinSignature=== MD5: bbb4814755042554781fce1b1da6fdb1 /lib64/libdl.so.2
===ExeBinSignature=== MD5: 23902bbccc0e350c1fdf09d070f3cd48 /lib64/libpthread.so.0
===ExeBinSignature=== MD5: 2705d15430ebce01274ef94967122bcb /lib64/libm.so.6
===ExeBinSignature=== MD5: b06038960f153e36545ed9ea947f80f6 /lib64/libstdc++.so.6
===ExeBinSignature=== MD5: c8f2c137eee1a4581bc0be7b63d2c603 /lib64/libgcc_s.so.1
===ExeBinSignature=== MD5: a2737e5fc2c2059bd357ef6015c99262 /lib64/libc.so.6
===ExeBinSignature=== MD5: 07711242213230dc1139fc71f31754cf /lib64/libnl-route-3.so.200
===ExeBinSignature=== MD5: 43d5e221199ce5536fa5f86b12c40a58 /lib64/libnl-3.so.200
Charmrun> scalable start enabled. 
Charmrun> IBVERBS version of charmrun
Charmrun> started all node programs in 2.783 seconds.
Converse/Charm++ Commit ID: v6.7.1-0-gbdf6a1b-namd-charm-6.7.1-build-2016-Nov-07-136676
Warning> Randomization of stack pointer is turned on in kernel, thread migration may not work! Run 'echo 0 > /proc/sys/kernel/randomize_va_space' as root to disable it, or try run with '+isomalloc_sync'.  
Charm++> scheduler running in netpoll mode.
CharmLB> Load balancer assumes all CPUs are same.
Charm++> Running on 2 unique compute nodes (8-way SMP).
Charm++> cpu topology info is gathered in 0.012 seconds.
Info: NAMD 2.12 for Linux-x86_64-ibverbs
Info: 
Info: Please visit http://www.ks.uiuc.edu/Research/namd/
Info: for updates, documentation, and support information.
Info: 
Info: Please cite Phillips et al., J. Comp. Chem. 26:1781-1802 (2005)
Info: in all publications reporting results obtained with NAMD.
Info: 
Info: Based on Charm++/Converse 60701 for net-linux-x86_64-ibverbs-iccstatic
Info: Built Wed Dec 21 11:35:18 CST 2016 by jim on harare.ks.uiuc.edu
Info: 1 NAMD  2.12  Linux-x86_64-ibverbs  16    cpn-d13-16.int.ccr.buffalo.edu  nikolays
Info: Running on 16 processors, 16 nodes, 2 physical nodes.
Info: CPU topology information available.
Info: Charm++/Converse parallel runtime startup completed at 0.025507 s
Info: 131.637 MB of memory in use based on /proc/self/stat
Info: Configuration file is ./input.namd
Info: Changed directory to .
TCL: Suspending until startup complete.
Info: SIMULATION PARAMETERS:
Info: TIMESTEP               2
Info: NUMBER OF STEPS        1200
Info: STEPS PER CYCLE        20

...
<more NAMD output>
...

Info: useSync: 0 useProxySync: 0
LDB: =============== DONE WITH MIGRATION ================ 72.7068
Info: Benchmark time: 16 CPUs 0.0951892 s/step 0.550864 days/ns 308.785 MB memory
Info: Benchmark time: 16 CPUs 0.0955705 s/step 0.55307 days/ns 308.785 MB memory
TIMING: 500  CPU: 48.7655, 0.0967451/step  Wall: 48.8295, 0.0968651/step, 0.0188349 hours remaining, 308.785156 MB of memory in use.
ENERGY:     500      2119.3682     10836.2433      5712.6289       177.9260        -300554.0570     16944.7914         0.0000         0.0000     33421.0085        -231342.0906       171.6328   -264763.0991   -231171.7215       168.3237          -1980.8393     -1951.1466    921491.4634     -1734.6994     -1734.6442

Info: Benchmark time: 16 CPUs 0.0948333 s/step 0.548804 days/ns 308.785 MB memory
Info: Benchmark time: 16 CPUs 0.0960609 s/step 0.555908 days/ns 308.785 MB memory
Info: Benchmark time: 16 CPUs 0.0942993 s/step 0.545713 days/ns 308.785 MB memory
Info: Benchmark time: 16 CPUs 0.095285 s/step 0.551418 days/ns 308.785 MB memory
TIMING: 1000  CPU: 96.0494, 0.0945676/step  Wall: 96.4553, 0.0952516/step, 0.00529176 hours remaining, 308.785156 MB of memory in use.
ENERGY:    1000      2029.9736     10858.2028      5703.0889       180.3306        -302100.8892     17982.1676         0.0000         0.0000     33997.1245        -231350.0014       174.5915   -265347.1258   -231170.4272       173.3323          -1695.3973     -1666.3302    921491.4634     -1819.9177     -1819.8952

WRITING EXTENDED SYSTEM TO OUTPUT FILE AT STEP 1200
WRITING COORDINATES TO OUTPUT FILE AT STEP 1200
The last position output (seq=-2) takes 0.025 seconds, 320.508 MB of memory in use
WRITING VELOCITIES TO OUTPUT FILE AT STEP 1200
The last velocity output (seq=-2) takes 0.025 seconds, 320.508 MB of memory in use
====================================================

WallClock: 149.040894  CPUTime: 148.148071  Memory: 320.507812 MB
```

If it looks ok you can move to the next step

## Perform Validation Run

On this step _akrr app validate_ command is used to validate application kernel installation on 
particular resource. It execute application kernel and analyses its' results. If it fails the 
problems need to be fixed and another round of validation should be performed.

```bash
akrr app validate -n 2 -r $RESOURCE -a $APPKER 
```

**Sample output**
```text
[INFO] Validating namd application kernel installation on ub-hpc
[INFO] ################################################################################
[INFO] Validating ub-hpc parameters from /home/akrruser/akrr/etc/resources/ub-hpc/resource.conf
[INFO] Syntax of /home/akrruser/akrr/etc/resources/ub-hpc/resource.conf is correct and all necessary parameters are present.
[INFO] Syntax of /usr/lib/python3.4/site-packages/akrr/default_conf/namd.app.conf is correct and all necessary parameters are present.
[INFO] ################################################################################
[INFO] Validating resource accessibility. Connecting to ub-hpc.
================================================================================
[INFO] Successfully connected to ub-hpc


[INFO] Checking directory locations

[INFO] Checking: huey:/user/nikolays/tmp/akrr_data/ub-hpc
[INFO] Directory exist and accessible for read/write

[INFO] Checking: huey:/user/nikolays/appker/ub-hpc
[INFO] Directory exist and accessible for read/write

[INFO] Checking: huey:/user/nikolays/tmp
[INFO] Directory exist and accessible for read/write
[INFO] 
[INFO] Checking: huey:/tmp
[INFO] Directory exist and accessible for read/write
[INFO] 
[INFO] ################################################################################
[INFO] Will send test job to queue, wait till it executed and will analyze the output
Will use AKRR REST API at https://localhost:8091/api/v1
[INFO] 
Submitted test job to AKRR, task_id is 3144531



================================================================================
Tast status:
Task is in scheduled_tasks queue.
It schedule to be started on2019-03-20T19:56:26

time: 2019-03-20 19:56:26 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: None
Status info:
None

time: 2019-03-20 19:56:36 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
             10836 general-c namd.job nikolays  R       0:05      2 cpn-d13-[18-19]


time: 2019-03-20 19:56:43 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
             10836 general-c namd.job nikolays  R       2:30      2 cpn-d13-[18-19]


time: 2019-03-20 19:59:14 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Task was completed successfully.
Status info:
Done

time: 2019-03-20 19:59:21 

================================================================================
Tast status:
Task is completed!
        status: 1
        status_info: Done

time: 2019-03-20 19:59:26 [INFO] Test job is completed analyzing output

[INFO] 
Test kernel execution summary:
status: 1
status_info: Done
processing message:
None
Local working directory for this task: /home/akrruser/akrr/log/comptasks/ub-hpc/namd/2019.03.20.19.56.26.518355
Location of some important generated files:
        Batch job script: /home/akrruser/akrr/log/comptasks/ub-hpc/namd/2019.03.20.19.56.26.518355/jobfiles/namd.job
        Application kernel output: /home/akrruser/akrr/log/comptasks/ub-hpc/namd/2019.03.20.19.56.26.518355/jobfiles/appstdout
        Batch job standard output: /home/akrruser/akrr/log/comptasks/ub-hpc/namd/2019.03.20.19.56.26.518355/jobfiles/stdout
        Batch job standard error output: /home/akrruser/akrr/log/comptasks/ub-hpc/namd/2019.03.20.19.56.26.518355/jobfiles/stderr
        XML processing results: /home/akrruser/akrr/log/comptasks/ub-hpc/namd/2019.03.20.19.56.26.518355/result.xml
        Task execution logs: /home/akrruser/akrr/log/comptasks/ub-hpc/namd/2019.03.20.19.56.26.518355/proc/log


[INFO] 
Enabling namd on ub-hpc for execution

[INFO] Successfully enabled namd on ub-hpc
[INFO] 
DONE, you can move to next step!
```

# Schedule regular execution of application kernel.

Now this application kernel can be submitted for regular execution:

```bash
#Perform a test run on all nodes count
python $AKRR_HOME/src/akrrctl.py new_task -r $RESOURCE -a $APPKER -n 1,2,4,8

#Start daily execution from today on nodes 1,2,4,8 and distribute execution time between 1:00 and 5:00
akrr task new -r $RESOURCE -a $APPKER -n 1,2,4,8 -t0 "01:00" -t1 "05:00" -p 1
```

see [Scheduling and Rescheduling Application Kernels](AKRR_Tasks_Scheduling.md) and 
[Setup Walltime Limit](AKRR_Walltimelimit_Setting.md) for more details.

Next [IOR Deployment](AKRR_IOR_Deployment.md)
