# AKRR: Deployment of HPCG Applications Kernels on a Resource

The High Performance Conjugate Gradients (HPCG) benchmark solves 3D elliptic partial differential equation (PDE) using a preconditioned conjugate gradient 
algorithm with Gauss-Seidel preconditioner to measure the resource performance. Thus the measured performance
is more relative, in general, to performance of over PDE solvers and methods with sparse matrices than High Performance 
LINPACK (HPL) benchmark (part of HPCC). This way monitoring performance of HPCG would help to identify the performance
degradation events affecting PDE solvers.

For simplicity lets define APPKER and RESOURCE environment variables which will contain the HPC 
resource name:

```bash
export RESOURCE=<resource_name>
export APPKER=hpcg
```

# Installing HPCG

Currently, there are two versions of HPCG: 
the [original](https://www.hpcg-benchmark.org) from Sandia National Laboratories
and [Intel Optimized HPCG Benchmark](https://software.intel.com/en-us/mkl-linux-developer-guide-intel-optimized-high-performance-conjugate-gradient-benchmark).

There are some differences between original and Intel version. 

The original version need to be compiled from source code.
 
The Intel version comes precompiled with MKL library.

## Locating Intel HPCG Binary in Intel MKL Library

```bash
# load mkl enviroment
module load intel/18.3
module load intel-mpi/2018.3
module load mkl/2018.3

# the binaries should be in
ls $MKLROOT/benchmarks/hpcg/bin
# hpcg.dat  xhpcg_avx  xhpcg_avx2  xhpcg_knl  xhpcg_skx
# 


```

choose one which match architecture of your HPC resource
for example $MKLROOT/benchmarks/hpcg/bin/xhpcg_skx

## (Alternatively) Compiling Original Version of HPCG from Source Code


Here is notes on HPCG compilation on HPC resource, see also HPCG benchmark 
documentation for more details .

** on HPC resource**
```bash
# Go to Application Kernel executable directory
cd $AKRR_APPKER_DIR/execs
# Environment variable $AKRR_APPKER_DIR should be setup automatically during initial
# deployment to HPC resource

# Load modules
module load intel/18.3
module load intel-mpi/2018.3
 
#get the code
wget https://github.com/hpcg-benchmark/hpcg/archive/HPCG-release-3-0-0.tar.gz
tar xvzf HPCG-release-3-0-0.tar.gz
cd hpcg-HPCG-release-3-0-0

# in setup directory there are number of Make.<arch> which setup parameters for make
# chose one which fit your need the best, edit it (note that in CXXFLAGS vector instruction set
# is specified, ensure that it is correct for you system)

# make building directory (note that in-source compiling have some problem)
mkdir build
cd build/
# Run configure script like  ../configure <arch>
# where <arch> is suffix of Make.<arch> edited earlier 
../configure MPI_ICPC
make
# xhpcg binary should be in bin directory
# it path is $AKRR_APPKER_DIR/execs/hpcg-HPCG-release-3-0-0/build/bin/xhpcg
```




# Generate Initiate Configuration File

Generate Initiate Configuration File:

**On AKRR server**
```bash
akrr app add -a $APPKER -r $RESOURCE
```
Sample output:
```text
[INFO] Generating application kernel configuration for hpcg on ub-hpc-skx
[INFO] Application kernel configuration for hpcg on ub-hpc-skx is in: 
        /home/akrruser/akrr/etc/resources/ub-hpc-skx/hpcg.app.conf
```

# Edit Configuration File

Below is a listing of configuration file located at 
~/akrr/etc/resources/$RESOURCE/hpcg.app.conf for SLURM:

**initial ~/akrr/etc/resources/$RESOURCE/hpcg.app.conf**
```python
"""
Resource specific HPCG configuration
"""

appkernel_run_env_template = """
# Load application environment
module load intel
module load intel-mpi
module load mkl
module list

# set executable location
EXE=$MKLROOT/benchmarks/hpcg/bin/xhpcg_avx

# Set how to run app kernel
export OMP_NUM_THREADS=1
RUN_APPKERNEL="mpirun $EXE"
"""
```

Update loading environment variables and the way how hpcg is executed. In case of **Intel HPCG** 
final configuration might look like:

**~/akrr/etc/resources/$RESOURCE/hpcg.app.conf**
```python
"""
Resource specific HPCG configuration
"""

appkernel_run_env_template = """
# Load application environment
module load intel/18.3
module load intel-mpi/2018.3
module load mkl/2018.3
module list

# set executable location
EXE=$MKLROOT/benchmarks/hpcg/bin/xhpcg_skx

# Set how to run app kernel
export OMP_NUM_THREADS=1
RUN_APPKERNEL="mpirun $EXE"
"""
```

In case of **original HPCG** final configuration might look like:
**~/akrr/etc/resources/$RESOURCE/hpcg.app.conf**
```python
"""
Resource specific HPCG configuration
"""

appkernel_run_env_template = """
# Load application environment
module load intel/18.3
module load intel-mpi/2018.3
module list

# set executable location
EXE=$AKRR_APPKER_DIR/execs/hpcg-HPCG-release-3-0-0/build/bin/xhpcg

# Set how to run app kernel
export OMP_NUM_THREADS=1
RUN_APPKERNEL="mpirun $EXE"
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
[output example](AKRR_HPCG_generated_batch_script_sample.md)

Next generate the script on resource:

```bash
akrr task new --gen-batch-job-only -n 2 -r $RESOURCE -a $APPKER
```

**Output of "_akrr task new --gen-batch-job-only -n 2 -r $RESOURCE -a $APPKER_"**
```text
[INFO] Creating task directory: /home/akrruser/akrr/log/data/ub-hpc-skx/hpcg/2019.03.29.13.35.43.449206
[INFO] Creating task directories: 
        /home/akrruser/akrr/log/data/ub-hpc-skx/hpcg/2019.03.29.13.35.43.449206/jobfiles
        /home/akrruser/akrr/log/data/ub-hpc-skx/hpcg/2019.03.29.13.35.43.449206/proc
[INFO] Creating batch job script and submitting it to remote machine
[INFO] Directory vortex:/projects/ccrstaff/general/nikolays/huey_slx/tmp/akrr_data/ub-hpc-skx/hpcg/2019.03.29.13.35.43.449206 does not exists, will try to create it
[INFO] auto_walltime_limit is on, trying to estimate walltime limit...
[INFO] There are only 0 previous run, need at least 5 for walltime limit autoset
[INFO] Local copy of batch job script is /home/akrruser/akrr/log/data/ub-hpc-skx/hpcg/2019.03.29.13.35.43.449206/jobfiles/hpcg.job

[INFO] Application kernel working directory on ub-hpc-skx is /projects/ccrstaff/general/nikolays/huey_slx/tmp/akrr_data/ub-hpc-skx/hpcg/2019.03.29.13.35.43.449206
[INFO] Batch job script location on ub-hpc-skx is /projects/ccrstaff/general/nikolays/huey_slx/tmp/akrr_data/ub-hpc-skx/hpcg/2019.03.29.13.35.43.449206/hpcg.job
```

The output contains the working directory for this task on remote resource. On remote resource get 
to that directory and start interactive session (request same number of nodes, in example above the 
script was generated for 2 nodes).

**On remote resource**
```bash
# get to working directory 
# (See output from running "akrr task new --gen-batch-job-only -n 2 -r $RESOURCE -a $APPKER")
cd /projects/ccrstaff/general/nikolays/huey_slx/tmp/akrr_data/ub-hpc-skx/hpcg/2019.03.29.13.35.43.449206
# check hpcg.job is there
ls
# start interactive session
salloc --nodes=2 --ntasks-per-node=32 --time=01:00:00
# wait till you get access to interactive session
# run ior application kernel
bash hpcg.job

# or submit as normal batch script
sbatch hpcg.job

```

Examine appstdout file, which contains application kernel output ([appstdout sample](AKRR_HPCG_appsout_sample.md)). 
If it looks ok you can move to the next step


# Perform Validation Run

On this step application kernel installation on 
the resource is validated. It executes the application kernel and analyses its results. If it fails the problems 
need to be fixed and another round of validation (as detailed above) should be performed.

```bash
akrr app validate -n 2 -r $RESOURCE -a $APPKER 
```

See [HPCG validation output sample](AKRR_HPCG_appkernel_validation_sample.md)

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
