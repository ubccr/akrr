# AKRR: Deployment of Graph500 Applications Kernels on a Resource

Here the deployment of graph500 application kernel is described. This application 
kernel is based on Graph500 which design to measure the performance of graph operations.

For further convenience of application kernel deployment lets define APPKER and RESOURCE environment 
variable which will contain the HPC resource name:

```bash
export RESOURCE=<resource_name>
export APPKER=graph500
```

# Installing Graph500

In this section the Graph500 installation process will be described, see also Graph500 documentation for 
installation details ( 
[https://github.com/graph500/graph500](https://github.com/graph500/graph500) ).

## Building IMB Executables

First we need to install Graph500. Below is a sample listing of commands for Graph500 installation:

```bash
#cd to application kernel executable directory
cd $AKRR_APPKER_DIR/execs

# obtain latest version of IMB
wget https://github.com/graph500/graph500/archive/refs/tags/3.0.1.tar.gz
tar xvzf 3.0.1.tar.gz
# create link 
ln -s graph500-3.0.1 graph500

#load MPI compiler
module load intel-mpi intel

cd graph500/src
# edit Makefile in particular add -xMIC-AVX512 or -xCORE-AVX512 (for arch. opt.) and MPICC = mpiicc:
# CFLAGS = -xMIC-AVX512 -Drestrict=__restrict__ -O3 -DGRAPH_GENERATOR_MPI -DREUSE_CSR_FOR_VALIDATION -I../aml
# MPICC = mpiicc
make
```

The rest is similar to other ak.

Generate Initiate Configuration File:

**On AKRR server**
```bash
akrr app add -a $APPKER -r $RESOURCE
```

Edit Configuration File in particular *appkernel_run_env_template* to reflect system enviroment:

```python
ppn = 32

appkernel_run_env_template = """
#Load application environment
module list

#set how to run app kernel
RUN_APPKERNEL="ibrun $EXE"
"""
```

Another importent parameter is *ppn*, which is MPI processes per node. Current implementation of Graph500 works 
efficiently only on 2^N, where N is number of MPI processes so if you have non 2^something nodes for example 48 cores per node
lower it to nearest power of too, i.e. 32. Graph500 can work on non power of 2 but it is very inefficient for systems with 48 and 68 cores per node
we found that using 32 and 64 cores respectevly is faster.


First generate the script to standard output and examine it (Optional) :

```bash
akrr task new --dry-run --gen-batch-job-only -n 2 -r $RESOURCE -a $APPKER
```

Next generate the script on resource:

```bash
akrr task new --gen-batch-job-only -n 2 -r $RESOURCE -a $APPKER
```

The output contains the working directory for this task on remote resource. On remote resource get 
to that directory and submit batch script for execution.

**On remote resource**
```bash
#get to working directory
cd /projects/ccrstaff/general/nikolays/huey/akrr_data/graph500/2021.07.22.18.55.05.595133

#run ior application kernel
sbatch graph500.job
```

Examine appstdout file, which contains application kernel output.

If it looks ok you can move to the next step

Perform Validation Run:
```bash
akrr app validate -n 2 -r $RESOURCE -a $APPKER 
```
Schedule regular execution of application kernel.

Now this application kernel can be submitted for regular execution:

```bash
#Perform a test run on all nodes count
akrr task new -r $RESOURCE -a $APPKER -n 2,4,8

#Start daily execution from today on nodes 2,4,8 and distribute execution time between 1:00 and 5:00
akrr task new -r $RESOURCE -a $APPKER -n 2,4,8 -t0 "01:00" -t1 "05:00" -p 1

# Run on all nodes count 20 times (default number of runs to establish baseline)
akrr task new -r $RESOURCE -a $APPKER -n 2,4,8 --n-runs 20
```

Up: [Deployment of Application Kernels on Resource](AKRR_Deployment_of_Application_Kernel_on_Resource.md)
