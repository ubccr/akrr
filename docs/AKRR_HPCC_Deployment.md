# AKRR: Deployment of HPCC Applications Kernels on a Resource

HPCC benchmark have a number of tests including linear algebra and memory benchmark which are good to monitore 
the performance of CPU compute power and memory. Because HPCC is linked with liner algebra and fast Fourier 
transformations  library. HPCC application kernel also monitor performance of respective libraries.

For simplicity lets define APPKER and RESOURCE environment variables which will contain the HPC 
resource name:

```bash
export RESOURCE=rush
export APPKER=hpcc
```

# Installing HPCC

In this section example of HPCC installation on HPC resource will be described, see also HPCC benchmark 
documentation for more installation details 
([http://icl.cs.utk.edu/hpcc/](http://icl.cs.utk.edu/hpcc/)).

** on HPC resource**
```bash
# Go to Application Kernel executable directory
cd $AKRR_APPKER_DIR/execs
# Environment variable $AKRR_APPKER_DIR should be setup automatically during initial
# deployment to HPC resource

# Load modules
module load intel/18.3
module load intel-mpi/2018.3
module load mkl/2018.3
 
# We need to make bench of interfaces to mkl library, unfortunately they are not precompiled
# Lets compile them in $AKRR_APPKER_DIR/execs/libs/<interface_name>
# and install in $AKRR_APPKER_DIR/execs/libs/lib
mkdir -p $AKRR_APPKER_DIR/execs/libs
mkdir -p $AKRR_APPKER_DIR/execs/libs/lib

#make fftw2x_cdft interface to mkl
cd $AKRR_APPKER_DIR/execs/libs
cp -r $MKLROOT/interfaces/fftw2x_cdft ./
cd fftw2x_cdft
make libintel64 PRECISION=MKL_DOUBLE interface=ilp64 MKLROOT=$MKLROOT INSTALL_DIR=$AKRR_APPKER_DIR/execs/libs/lib


#make FFTW C wrapper library
cd $AKRR_APPKER_DIR/execs/libs
cp -r $MKLROOT/interfaces/fftw2xc ./
cd fftw2xc
make libintel64 PRECISION=MKL_DOUBLE MKLROOT=$MKLROOT INSTALL_DIR=$AKRR_APPKER_DIR/execs/libs/lib

 
#get the code
cd $AKRR_APPKER_DIR/execs
wget http://icl.cs.utk.edu/projectsfiles/hpcc/download/hpcc-1.5.0.tar.gz
tar xvzf hpcc-1.5.0.tar.gz
cd hpcc-1.5.0
# Prepare makefile
# HPCC reuses makefiles from High Performance Linpack (thus do not forget to get to hpc directory)
# you can start with something close from hpl/setup directory
# or start from one of our make file
# place Make.intel64_hpcresource file to hpcc-1.4.2/hpl
cd hpl

wget https://raw.githubusercontent.com/ubccr/akrr/master/akrr/appker_repo/execs/misc/hpcc/Make.intel64_hpcresource
# edit Make.intel64_hpcresource to fit your system 
# if you have intel based system with intel compilers and intel-mpi
# most likely you don't need to change it
 
#compile hpcc in hpcc-1.4.2 root directory
cd ..
make arch=intel64_hpcresource
#if it is compiled successfully hpcc binary should appear in hpcc-1.4.2 directory


#create a link to hpcc
cd ..
ln -s hpcc-1.5.0 hpcc
 

 
#now we can test it on headnode (optional)
cd hpcc
mv _hpccinf.txt hpccinf.txt

mpirun -np 4 ./hpcc
cat hpccoutf.txt
```


# Generate Initiate Configuration File

Generate Initiate Configuration File:

**On AKRR server**
```bash
akrr app add -a $APPKER -r $RESOURCE
```
Sample output:
```text
[INFO] Generating application kernel configuration for hpcc on ub-hpc
[INFO] Application kernel configuration for hpcc on ub-hpc is in: 
        /home/akrruser/akrr/etc/resources/ub-hpc/hpcc.app.conf
```

# Edit Configuration File

Below is a listing of configuration file located at 
~/akrr/etc/resources/$RESOURCE/hpcc.app.conf for SLURM:

**initial ~/akrr/etc/resources/$RESOURCE/hpcc.app.conf**
```python
appkernel_run_env_template = """
# Load application environment
module load intel
module load intel-mpi
module load mkl
module list

# make srun works with intel mpi
export I_MPI_PMI_LIBRARY=/usr/lib64/libpmi.so

# set how to run app kernel
RUN_APPKERNEL="srun {appkernel_dir}/{executable}"
"""
```

Update loading environment variables and the way how hpcc is executed:

**~/akrr/etc/resources/$RESOURCE/hpcc.app.conf**
```python
appkernel_run_env_template = """
# Load application environment
module load intel/18.3
module load intel-mpi/2018.3
module load mkl/2018.3
module list

# make srun works with intel mpi
export I_MPI_PMI_LIBRARY=/usr/lib64/libpmi.so

# set how to run app kernel
RUN_APPKERNEL="srun {appkernel_dir}/{executable}"
"""
```

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

**Portion of "_akrr task new --dry-run --gen-batch-job-only -n 2 -r $RESOURCE -a $APPKER_" output showing generated 
batch script**
```bash
#!/bin/bash
#SBATCH --partition=general-compute 
#SBATCH --qos=general-compute
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=8
#SBATCH --time=00:40:00
#SBATCH --output=/projects/ccrstaff/general/nikolays/huey/akrr_data/hpcc/2019.03.25.16.00.23.886859/stdout
#SBATCH --error=/projects/ccrstaff/general/nikolays/huey/akrr_data/hpcc/2019.03.25.16.00.23.886859/stderr
#SBATCH --constraint="CPU-L5520"
#SBATCH --exclusive


#Common commands
export AKRR_NODES=2
export AKRR_CORES=16
export AKRR_CORES_PER_NODE=8
export AKRR_NETWORK_SCRATCH="/projects/ccrstaff/general/nikolays/huey/tmp"
export AKRR_LOCAL_SCRATCH="/tmp"
export AKRR_TASK_WORKDIR="/projects/ccrstaff/general/nikolays/huey/akrr_data/hpcc/2019.03.25.16.00.23.886859"
export AKRR_APPKER_DIR="/projects/ccrstaff/general/nikolays/huey/appker"
export AKRR_AKRR_DIR="/projects/ccrstaff/general/nikolays/huey/akrr_data"

export AKRR_APPKER_NAME="hpcc"
export AKRR_RESOURCE_NAME="ub-hpc"
export AKRR_TIMESTAMP="2019.03.25.16.00.23.886859"
export AKRR_APP_STDOUT_FILE="$AKRR_TASK_WORKDIR/appstdout"

export AKRR_APPKERNEL_INPUT="/projects/ccrstaff/general/nikolays/huey/appker/inputs/hpcc/hpccinf.txt.8x2"
export AKRR_APPKERNEL_EXECUTABLE="/projects/ccrstaff/general/nikolays/huey/appker/execs/hpcc/hpcc"

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

#Copy inputs
cp /projects/ccrstaff/general/nikolays/huey/appker/inputs/hpcc/hpccinf.txt.8x2 ./hpccinf.txt

EXE=/projects/ccrstaff/general/nikolays/huey/appker/execs/hpcc/hpcc



# Load application environment
module load intel/18.3
module load intel-mpi/2018.3
module load mkl/2018.3
module list

# make srun works with intel mpi
export I_MPI_PMI_LIBRARY=/usr/lib64/libpmi.so

# set how to run app kernel
RUN_APPKERNEL="srun /projects/ccrstaff/general/nikolays/huey/appker/execs/hpcc/hpcc"


#Generate AppKer signature
appsigcheck.sh $EXE $AKRR_TASK_WORKDIR/.. > $AKRR_APP_STDOUT_FILE


#Execute AppKer
akrr_write_to_gen_info "appkernel_start_time" "`date`"
$RUN_APPKERNEL >> $AKRR_APP_STDOUT_FILE 2>&1
akrr_write_to_gen_info "appkernel_end_time" "`date`"




cat hpccoutf.txt  >> $AKRR_APP_STDOUT_FILE 2>&1

cd ..

akrr_write_to_gen_info "cpu_speed" "`grep 'cpu MHz' /proc/cpuinfo`"

#clean-up
if [ "${AKRR_DEBUG=no}" = "no" ]
then
        echo "Deleting input files"
        rm -rf workdir
fi



akrr_write_to_gen_info "end_time" "`date`"
```

Next generate the script on resource:

```bash
akrr task new --dry-run --gen-batch-job-only -n 2 -r $RESOURCE -a $APPKER
```

**Output of "_akrr task new --gen-batch-job-only -n 2 -r $RESOURCE -a $APPKER_"**
```text
[INFO] Creating task directory: /home/akrruser/akrr/log/data/ub-hpc/hpcc/2019.03.25.16.01.28.633071
[INFO] Creating task directories: 
        /home/akrruser/akrr/log/data/ub-hpc/hpcc/2019.03.25.16.01.28.633071/jobfiles
        /home/akrruser/akrr/log/data/ub-hpc/hpcc/2019.03.25.16.01.28.633071/proc
[INFO] Creating batch job script and submitting it to remote machine
[INFO] Directory huey:/projects/ccrstaff/general/nikolays/huey/akrr_data/hpcc/2019.03.25.16.01.28.633071 does not exists, will try to create it
[INFO] auto_walltime_limit is on, trying to estimate walltime limit...
[INFO] There are only 0 previous run, need at least 5 for walltime limit autoset
[INFO] Local copy of batch job script is /home/akrruser/akrr/log/data/ub-hpc/hpcc/2019.03.25.16.01.28.633071/jobfiles/hpcc.job

[INFO] Application kernel working directory on ub-hpc is /projects/ccrstaff/general/nikolays/huey/akrr_data/hpcc/2019.03.25.16.01.28.633071
[INFO] Batch job script location on ub-hpc is /projects/ccrstaff/general/nikolays/huey/akrr_data/hpcc/2019.03.25.16.01.28.633071/hpcc.job
```

The output contains the working directory for this task on remote resource. On remote resource get 
to that directory and start interactive session (request same number of nodes, in example above the 
script was generated for 2 nodes).

**On remote resource**
```bash
#get to working directory
cd /projects/ccrstaff/general/nikolays/huey/akrr_data/hpcc/2019.03.25.16.01.28.633071
#check hpcc.job is there
ls
#start interactive session
salloc --nodes=2 --ntasks-per-node=8 --time=01:00:00 --exclusive --constraint="CPU-L5520"
#wait till you get access to interactive session
#run ior application kernel
bash hpcc.job

# or submit as normal batch script
sbatch hpcc.job

```

Examine appstdout file, which contains application kernel output ([appstdout sample](AKRR_HPCC_appsout_sample.md)). 
If it looks ok you can move to the next step


# Perform Validation Run

On this step application kernel installation on 
the resource is validated. It executes the application kernel and analyses its results. If it fails the problems 
need to be fixed and another round of validation (as detailed above) should be performed.

```bash
akrr app validate -n 2 -r $RESOURCE -a $APPKER 
```

See [HPCC validation output sample](AKRR_HPCC_appkernel_validation_sample.md)

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
