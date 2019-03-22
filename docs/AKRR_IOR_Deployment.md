# AKRR: Deployment of IOR Applications Kernels on a Resource

IOR benchmark measures the performance of parallel file-systems. It can use differen IO APIs and 
can perform write and read in different modes like all processes writes to single 
file (N to 1 mode) or all processes writes to their own file (N to N mode).

Besides POSIX and MPIIO APIs for file system input-output, IOR can also test parallel HDF5 and NetCDF
libraries. You can choose which APIs to use, based on the API utilization in your center. HDF5 is a 
popular format and many scientific HPC application use it. NetCDF is arguably a bit 
less popular and the take longer time. So if you know (or strongly suspect) that nobody 
uses NetCDF on your system you might want to skip it.

If only the performance of parallel file-systems is of interest one can limit benchmarking to only POSIX 
and possible MPIIO API. This would save substantial amount of cycles.

For simplicity lets define APPKER and RESOURCE environment variable which will contain the HPC 
resource name and application kernel name:

```bash
export RESOURCE=<resource_name>
export APPKER=ior
```

## Installing IOR


In this section the IOR installation process will be described, see also IOR benchmark documentation 
for installation details ( 
[http://sourceforge.net/projects/ior-sio/](http://sourceforge.net/projects/ior-sio/) ).



### Installing HDF5 (optional)

It is preferred to use a system-wide installed parallel HDF5 library. This way 
_IOR_ will also test the workability and performance of this particular library installation. 
HDF5 is a popular format and are often deployed system-wide. Ensure that it was compiled with parallel 
support (for example by checking presence of h5pcc in $HDF5_HOME/bin). If there is no system-wide 
installed parallel HDF5 library than you might want to skip it.

Bellow are brief notes on parallel hdf5 installation,  
[http://www.hdfgroup.org/HDF5/](http://www.hdfgroup.org/HDF5/) for HDF5 installation details.

**On target resource:**
```bash
#get to application kernel executable directory
cd $AKRR_APPKER_DIR/execs

#create lib directory if needed and temporary directory for compilation
mkdir -p lib
mkdir -p lib\tmp
cd lib\tmp

#obtain parallel-netcdf source code
wget http://www.hdfgroup.org/ftp/HDF5/current/src/hdf5-1.8.14.tar.gz
tar xvzf hdf5-1.8.14.tar.gz
cd hdf5-1.8.14

#configure hdf5
./configure --prefix=$AKRR_APPKER_DIR/execs/lib/hdf5-1.8.14 --enable-parallel CC=`which mpiicc` CXX=`which mpiicpc`
make

#install
make install
cd $AKRR_APPKER_DIR/execs

#optionally clean-up
rm -rf $AKRR_APPKER_DIR/execs/lib/tmp/hdf5-1.8.14
```

### Installing Parallel NetCDF (optional)

IOR can also use parallel NetCDF format to test file system IO. Parallel NetCDF tends to be slower 
than other APIs and therefore significantly increases the application kernel execution time. 
Therefore, if you know that parallel NetCDF is used on your system and you want to monitor its 
performance then go ahead and add it. If you use system-wide installed library, check that it is 
parallel. Regular  serial NetCDF will not work (IOR needs the parallel version). Bellow is brief 
note on parallel-netcdf installation, refer to 
[http://trac.mcs.anl.gov/projects/parallel-netcdf](http://trac.mcs.anl.gov/projects/parallel-netcdf) 
for more details - note that currently IOR needs the linked version of parallel NetCDF, not the 
(unfortunately incompatible) NetCDF-4 parallel API.

Similar to HDF5, if there is no system-wide installation and no use on the system than skip it as it
would be not that much useful.

Bellow are brief notes on parallel NetCDF installation,  
```bash
#get to application kernel executable directory
cd $AKRR_APPKER_DIR/execs

#create lib directory if needed and temporary directory for compilation
mkdir -p lib
mkdir -p lib/tmp
cd lib/tmp

#obtain parallel-netcdf source code
wget http://ftp.mcs.anl.gov/pub/parallel-netcdf/parallel-netcdf-1.3.1.tar.gz
tar xvzf parallel-netcdf-1.3.1.tar.gz
cd parallel-netcdf-1.3.1


#check the location of mpi compilers
which mpicc
MPI_TOP_DIR=$(dirname $(dirname \`which mpicc\`))
#sample output:
#/usr/local/packages/mvapich2/2.0/INTEL-14.0.2/bin/mpicc


#configure parallel-netcdf, specify installation location and which mpi compiler to use
./configure --prefix=$AKRR_APPKER_DIR/execs/lib/pnetcdf-1.3.1 --with-mpi=$MPI_TOP_DIR

#compile (do not use parallel compilation i.e. -j option)
make

#install
make install
cd $AKRR_APPKER_DIR/execs

#optionally clean-up
rm -rf $AKRR_APPKER_DIR/execs/lib/tmp/parallel-netcdf-1.3.1\*
```

## Installing IOR

Now we need to install IOR. Below is a sample listing of commands for IOR installation, note that we 
download a version of the IOR code from our github repository (we made some minor modification to 
the IOR mainly stdout flushes to prevent race for output from multiple parallel processes). Refer to 
IOR benchmark documentation for more installation details ( 
[http://sourceforge.net/projects/ior-sio/](http://sourceforge.net/projects/ior-sio/) ).

Following is done on HPC resource.

```bash
#cd to application kernel executable directory
cd $AKRR_APPKER_DIR/execs
#remove older version of ior
rm -rf ior


#obtain latest version of IOR from our repository
git clone https://github.com/nsimakov/ior.git
#make configuration scripts
cd ior
./bootstrap

#load proper compilers and libs 
module intel intel-mpi
```

Configuration run for POSIX and MPIIO (i.e. without HDF5 and NetCDF):
```bash
./configure
```
> Optionally, IOR configuration with POSIX, MPIIO HDF5 and NetCDF:
> ```bash
> #set netcdf and hdf5 enviroment
> module load hdf5
> #configure IOR, note the specification of netcdf and hdf include and lib directories
> ./configure --with-hdf5=yes --with-ncmpi=yes \
>     CPPFLAGS="-I$AKRR_APPKER_DIR/execs/lib/pnetcdf-1.3.1/include -I/usr/local/packages/netcdf/4.2.1.1/INTEL-140-MVAPICH2-2.0/include" LDFLAGS="-L/usr/local/packages/hdf5/1.8.12/INTEL-140-MVAPICH2-2.0/lib -L$AKRR_APPKER_DIR/execs/lib/pnetcdf-1.3.1/lib"
> ```

Compilation:
```bash
#compile
make
 
#the binary should be src/ior
ls $AKRR_APPKER_DIR/execs/ior/src/ior
```

# Generate Initiate Configuration File

Generate Initiate Configuration File:

**On AKRR server**
```bash
akrr app add -a $APPKER -r $RESOURCE
```
Sample output:
```text
[INFO] Generating application kernel configuration for ior on ub-hpc
[INFO] Application kernel configuration for ior on ub-hpc is in: 
        /home/akrruser/akrr/etc/resources/ub-hpc/ior.app.conf
```
# Edit Configuration File

Configuring IOR is more complex than the NAMD based application kernel. The main issue with IOR is 
to try and bypass memory caching on compute and storage nodes (which will inflate the performance 
numbers, as it is doing i/o to memory rather than the actual storage system).

To avoid caching on multi-node tests (two nodes and larger) we use MPI processes reordering, for 
example if the file was written from node A and node B, after that node A will read what node B 
wrote and node B will read what node A wrote.

For singe node runs, the test is actually performed on 2 nodes where one node writes and another 
node reads. This way we (hopefully) obtain single node performance metrics without hitting local 
caches.

We have little influence on the storage node configuration/caches so the strategy here is to do all 
writes first (for all tests) and then do reads, the hope is that writing large files will overwrite 
the cache on storage node and the following reads will be done with minimal influence from storage 
nodes cache.

Configuring the IOR application kernel is essentially setting up the IOR execution in a way 
reflecting the above strategy for bypassing cache.

The most effective strategy to properly setup `ior` is to use an interactive 
session to test and define configurable parameters.

## Configuring parameters which defines how IOR will be executed

First, lets configure parameters which generally do not require an interactive debug session.

Below is a listing of the generated default configuration file located at 
~/akrr/etc/resources/$RESOURCE/ior.app.conf

**~/akrr/etc/resources/$RESOURCE/ior.app.conf**
```python
# which IO API/formats to check
testPOSIX = True
testMPIIO = False
testHDF5 = False
testNetCDF = False

# will do write test first and after that read, that minimize the caching impact from storage nodes
# require large temporary storage easily 100s GiB
doAllWritesFirst = True

appkernel_run_env_template = """
# load application environment
# module load hdf5
module list

# set executable location
EXE=$AKRR_APPKER_DIR/execs/ior/src/ior

# set how to run mpirun on all nodes
for node in $AKRR_NODELIST; do echo $node>>all_nodes; done
RUNMPI="mpiexec -n $AKRR_CORES -f all_nodes"

# set how to run mpirun on all nodes with offset, first print all nodes after node 1 and then node 1
sed -n "$(($AKRR_CORES_PER_NODE+1)),$(($AKRR_CORES))p" all_nodes > all_nodes_offset
sed -n "1,$(($AKRR_CORES_PER_NODE))p" all_nodes >> all_nodes_offset
RUNMPI_OFFSET="mpiexec -n $AKRR_CORES -f all_nodes_offset"
"""
```

`The first several lines specify which IO APIs to test:`

**Fragment of ~/akrr/etc/resources/$RESOURCE/ior.app.conf**
```python
#which IO API/formats to check
testPOSIX = True
testMPIIO = False
testHDF5 = False
testNetCDF = False
```

Set to True API you want to test, for HDF5 and NetCDF IOR should be compiled with its support. 

Next several lines instruct IOR application kernel to do all writes first and then do all reads:

**Fragment of ~/akrr/etc/resources/$RESOURCE/ior.app.conf**
```python
#will do write test first and after that read, that minimize the caching impact from storage nodes
#require large temporary storage easily 100s GiB 
doAllWritesFirst=True
```

The only reason not to do writes first is if you have limited storage size, as the size of all 
generated output files are quite substantial (after testing is done all generated files are removed, 
but you mush have sufficient space to hold the interim results). For example on 8 nodes of machine 
with 12 cores per node and all tests done the total size of writes will be 10 tests \* 200 MB per 
core  \* 12 cores per node \* 8 node =192 GB.

## Setting up _appkernel_run_env_template_

Now we need to set _appkernel_run_env_template_ template variable.

We will do it section by section and will use interactive session on resource to test the entries.

First lets generate _test_ application kernel batch job script (**not IOR script**, we will use 
this test job script to set AKRR predifined environment variable to use during entries validation):

**On AKRR Server**
```bash
akrr task new --gen-batch-job-only -n 2 -r $RESOURCE -a test
```

```test
[INFO] Creating task directory: /home/akrruser/akrr/log/data/ub-hpc/test/2019.03.22.15.36.10.391495
[INFO] Creating task directories: 
        /home/akrruser/akrr/log/data/ub-hpc/test/2019.03.22.15.36.10.391495/jobfiles
        /home/akrruser/akrr/log/data/ub-hpc/test/2019.03.22.15.36.10.391495/proc
[INFO] Creating batch job script and submitting it to remote machine
[INFO] Directory huey:/projects/ccrstaff/general/nikolays/huey/akrr_data/test/2019.03.22.15.36.10.391495 does not exists, will try to create it
[INFO] auto_walltime_limit is on, trying to estimate walltime limit...
[WARNING] One of last 5 runs have failed. Would not use autoset.
[INFO] Local copy of batch job script is /home/akrruser/akrr/log/data/ub-hpc/test/2019.03.22.15.36.10.391495/jobfiles/test.job

[INFO] Application kernel working directory on ub-hpc is /projects/ccrstaff/general/nikolays/huey/akrr_data/test/2019.03.22.15.36.10.391495
[INFO] Batch job script location on ub-hpc is /projects/ccrstaff/general/nikolays/huey/akrr_data/test/2019.03.22.15.36.10.391495/test.job
```

The output contains the working directory for this task on remote resource. On remote resource get 
to that directory and start interactive session (request same number of nodes, in example above the 
script was generated for 2 nodes).

**On remote resource**
```bash
#get to working directory
cd /projects/ccrstaff/general/nikolays/huey/akrr_data/test/2019.03.22.15.36.10.391495
#check that test.job is there
ls
#start interactive session
salloc --partition=general-compute --nodes=2 --ntasks-per-node=8 --time=01:00:00 --exclusive --constraint="CPU-L5520"
#wait till you get access to interactive session

#get to working directory again if not already there
cd /projects/ccrstaff/general/nikolays/huey/akrr_data/test/2019.03.22.15.36.10.391495
#load everything from test.job
source test.job 
#check AKRR predifined environment variable are loaded
echo $AKRR_NODES
#output should be 2

echo $AKRR_NODELIST
#output should be space separated list of hosts 
```

Now we ready to configure _appkernel_run_env_template (in ~/akrr/etc/resources/$RESOURCE/ior.app.conf).

### Setting up environment

In first section we set proper environment for IOR to work, we also place IOR executable location to EXE variable 
(binary in $EXE will be used to generate application signature):

**appkernel_run_env_template fragment of ior.app.conf**
```bash
# load application environment
# module load hdf5
module load intel-mpi intel
module list

#set executable location
EXE=$AKRR_APPKER_DIR/execs/ior/src/ior
```

Make the appropriate changes for your system in 
~/akrr/etc/resources/$RESOURCE/ior.app.conf and execute in interactive session, 
note addition of 'module load intel-mpi intel'.

check that IOR is working:

**On remote resource**
```bash
# load application environment
# module load hdf5
module load intel-mpi intel
module list

#set executable location
EXE=$AKRR_APPKER_DIR/execs/ior/src/ior


#let check is it working:
mpirun $EXE
```

The default file sizes for ior are quite small, so running ior with no arguments as above should 
return very quickly - unless something is wrong.

If it is not working modify the environment appropriately in 
~/akrr/etc/resources/$RESOURCE/ior.app.conf.

### Setting up How to run MPI application on All Nodes

Next, we setup how to run mpirun/mpiexec on all nodes:

**appkernel_run_env_template fragment of ior.app.conf**
```bash
#set how to run mpirun on all nodes
for node in $AKRR_NODELIST; do echo $node>>all_nodes; done
RUNMPI="mpiexec -n $AKRR_CORES -f all_nodes"
```

Nearly all mpi implementations accept a plain list of hosts(nodes) as a machines file on which to 
run the MPI tasks, although the options to use that list may vary. In this script we generate a list 
of all nodes (one per MPI process) and place in the $RUNMPI environment variable how to execute 
mpirun (or whatever MPI task launcher is preferred on your platform).

Adjust this section in ~/akrr/etc/resources/$RESOURCE/ior.app.conf and again 
execute in an interactive session, to check that IOR is working:

**On remote resource**
```bash
#set how to run mpirun on all nodes
for node in $AKRR_NODELIST; do echo $node>>all_nodes; done
RUNMPI="mpiexec -n $AKRR_CORES -f all_nodes"
```

Note that you **must** supply number of processes to your mpi launcher, some test do not use all 
processes. Therefore, without explicit specification of processes numbers the tests will be 
incorrect (for single node metrics).

Single-node performance is obtain from two node run where one will do writes and another reads.

Check that IOR is working:

**On remote resource**
```bash
#let check is it working:
$RUNMPI $EXE -vv
```

"-vv" option will make IOR more verbose and shows the processes assignment to nodes:

**Sample of $RUNMPI $EXE -vv output**
```text
Machine: Linux cpn-d13-16.int.ccr.buffalo.edu 3.10.0-957.1.3.el7.x86_64 #1 SMP Thu Nov 29 14:49:43 UTC 2018 x86_64
Using synchronized MPI timer
Start time skew across all tasks: 0.00 sec

Test 0 started: Fri Mar 22 12:28:11 2019
Path: /projects/ccrstaff/general/nikolays/huey/akrr_data/test/2019.03.22.15.36.10.391495
FS: 1704.7 TiB   Used FS: 48.3%   Inodes: 2635486.5 Mi   Used Inodes: 35.2%
Participating tasks: 16
task 0 on cpn-d13-16.int.ccr.buffalo.edu
task 1 on cpn-d13-16.int.ccr.buffalo.edu
task 10 on cpn-d13-17.int.ccr.buffalo.edu
task 11 on cpn-d13-17.int.ccr.buffalo.edu
task 12 on cpn-d13-16.int.ccr.buffalo.edu
task 13 on cpn-d13-16.int.ccr.buffalo.edu
task 14 on cpn-d13-17.int.ccr.buffalo.edu
task 15 on cpn-d13-17.int.ccr.buffalo.edu
task 2 on cpn-d13-17.int.ccr.buffalo.edu
task 3 on cpn-d13-17.int.ccr.buffalo.edu
task 4 on cpn-d13-16.int.ccr.buffalo.edu
task 5 on cpn-d13-16.int.ccr.buffalo.edu
task 6 on cpn-d13-17.int.ccr.buffalo.edu
task 7 on cpn-d13-17.int.ccr.buffalo.edu
task 8 on cpn-d13-16.int.ccr.buffalo.edu
task 9 on cpn-d13-16.int.ccr.buffalo.edu
Summary:
        api                = POSIX
        test filename      = testFile
        access             = single-shared-file
        pattern            = segmented (1 segment)
        ordering in a file = sequential offsets
        ordering inter file= no tasks offsets
        clients            = 16 (8 per node)
        repetitions        = 1
        xfersize           = 262144 bytes
        blocksize          = 1 MiB
        aggregate filesize = 16 MiB
Using Time Stamp 1553272091 (0x5c950d1b) for Data Signature

access    bw(MiB/s)  block(KiB) xfer(KiB)  open(s)    wr/rd(s)   close(s)   total(s)   iter
------    ---------  ---------- ---------  --------   --------   --------   --------   ----
Commencing write performance test: Fri Mar 22 12:28:11 2019
write     143.22     1024.00    256.00     0.085481   0.086161   0.108553   0.111720   0   
Commencing read performance test: Fri Mar 22 12:28:11 2019
read      9049       1024.00    256.00     0.001146   0.001161   0.000643   0.001768   0   
remove    -          -          -          -          -          -          0.002378   0   

Max Write: 143.22 MiB/sec (150.17 MB/sec)
Max Read:  9049.20 MiB/sec (9488.77 MB/sec)

Summary of all tests:
Operation   Max(MiB)   Min(MiB)  Mean(MiB)     StdDev    Mean(s) Test# #Tasks tPN reps fPP reord reordoff reordrand seed segcnt blksiz xsize aggsize API RefNum
write         143.22     143.22     143.22       0.00    0.11172 0 16 8 1 0 0 1 0 0 1 1048576 262144 16777216 POSIX 0
read         9049.20    9049.20    9049.20       0.00    0.00177 0 16 8 1 0 0 1 0 0 1 1048576 262144 16777216 POSIX 0

Finished: Fri Mar 22 12:28:11 2019
```

If it is not working modify the executed commands and copy the good ones to 
~/akrr/etc/resources/$RESOURCE/ior.app.conf.

### Setting up How to run MPI application on All Nodes with Nodes Offset

Next, we setup how to run mpirun/mpiexec on all nodes with one node offset:

**appkernel_run_env_template fragment of ior.app.conf**
```bash
#set how to run mpirun on all nodes with offset, first print all nodes after node 1 and then node 1
sed -n "$(($AKRR_CORES_PER_NODE+1)),$(($AKRR_CORES))p" all_nodes > all_nodes_offset
sed -n "1,$(($AKRR_CORES_PER_NODE))p" all_nodes >> all_nodes_offset
RUNMPI_OFFSET="mpiexec -n $AKRR_CORES -f all_nodes_offset"
```

Nearly all mpi flavours accept plain list of hosts(nodes) as a machines file, some of them uses 
different option to load that list. In this script we generate a list of all nodes (one per MPI 
process) and place to RUNMPI variable how to execute mpirun (or whatever luncher is used on your 
platform).

Adjust this section in ~/akrr/etc/resources/$RESOURCE/ior.app.conf and execute 
in interactive session, check that IOR is working:

**On remote resource**
```bash
#set how to run mpirun on all nodes with offset, first print all nodes after node 1 and then node 1
sed -n "$(($AKRR_CORES_PER_NODE+1)),$(($AKRR_CORES))p" all_nodes > all_nodes_offset
sed -n "1,$(($AKRR_CORES_PER_NODE))p" all_nodes >> all_nodes_offset
echo "all_nodes_offset:"
cat all_nodes_offset
RUNMPI_OFFSET="mpiexec -n $AKRR_CORES -f all_nodes_offset"
```

Check that IOR is working:

**On remote resource**
```bash
#let check is it working:
$RUNMPI_OFFSET $EXE -vv
```

If it is not working modify the executed commands and copy the good ones to 
~/akrr/etc/resources/$RESOURCE/ior.app.conf.

### Setting up Luster file striping (Optional) 

If you use Lustre you might want to use file striping for better parallel performance. The variables 
RESOURCE_SPECIFIC_OPTION, RESOURCE_SPECIFIC_OPTION_N_to_1 and RESOURCE_SPECIFIC_OPTION_N_to_N and  
will be passed to IOR as command line options.

RESOURCE_SPECIFIC_OPTION will be passed to all IOR execution.

RESOURCE_SPECIFIC_OPTION_N_to_1 will be passed to IOR for tests there all processes writes to a 
single file and RESOURCE_SPECIFIC_OPTION_N_to_N will be passed to IOR for tests there all processes 
writes to their own independent files.

Bellow is a fragment example from ior.app.conf which will instruct IOR to use 
striping equal to the number of nodes when all processes write to a single file.

**appkernel_run_env_template fragment of ior.app.conf**
```bash
#set striping for lustre file system
RESOURCE_SPECIFIC_OPTION_N_to_1="-O lustreStripeCount=$AKRR_NODES"
RESOURCE_SPECIFIC_OPTION_N_to_N=""
#other resource specific options
RESOURCE_SPECIFIC_OPTION=""
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

**Sample output of $AKRR_HOME/bin/akrr_ctl.sh batch_job -p -r $RESOURCE -a $APPKER -n 2**
```bash
[INFO] Creating task directory: /home/akrruser/akrr/log/data/ub-hpc/test/2019.03.22.15.36.10.391495
[INFO] Creating task directories: 
        /home/akrruser/akrr/log/data/ub-hpc/test/2019.03.22.15.36.10.391495/jobfiles
        /home/akrruser/akrr/log/data/ub-hpc/test/2019.03.22.15.36.10.391495/proc
[INFO] Creating batch job script and submitting it to remote machine
[INFO] Directory huey:/projects/ccrstaff/general/nikolays/huey/akrr_data/test/2019.03.22.15.36.10.391495 does not exists, will try to create it
[INFO] auto_walltime_limit is on, trying to estimate walltime limit...
[WARNING] One of last 5 runs have failed. Would not use autoset.
[INFO] Local copy of batch job script is /home/akrruser/akrr/log/data/ub-hpc/test/2019.03.22.15.36.10.391495/jobfiles/test.job

[INFO] Application kernel working directory on ub-hpc is /projects/ccrstaff/general/nikolays/huey/akrr_data/test/2019.03.22.15.36.10.391495
[INFO] Batch job script location on ub-hpc is /projects/ccrstaff/general/nikolays/huey/akrr_data/test/2019.03.22.15.36.10.391495/test.job
[akrruser@xdmod ~]$ akrr task new --dry-run --gen-batch-job-only -n 2 -r $RESOURCE -a $APPKER
DryRun: Should submit following to REST API (POST to scheduled_tasks) {'time_to_start': None, 'resource_param': "{'nnodes':2}", 'app': 'ior', 'repeat_in': None, 'resource': 'ub-hpc'}                                                    
[INFO] Directory /home/akrruser/akrr/log/data/ub-hpc/ior does not exist, creating it.                                
[INFO] Directory /home/akrruser/akrr/log/comptasks/ub-hpc/ior does not exist, creating it.                           
[INFO] Creating task directory: /home/akrruser/akrr/log/data/ub-hpc/ior/2019.03.22.16.36.35.793858                   
[INFO] Creating task directories:                                                                                    
        /home/akrruser/akrr/log/data/ub-hpc/ior/2019.03.22.16.36.35.793858/jobfiles                                  
        /home/akrruser/akrr/log/data/ub-hpc/ior/2019.03.22.16.36.35.793858/proc                                      
[INFO] auto_walltime_limit is on, trying to estimate walltime limit...                                               
[INFO] There are only 0 previous run, need at least 5 for walltime limit autoset                                     
[INFO] Below is content of generated batch job script:                                                               
#!/bin/bash                                                                                                          
#SBATCH --partition=general-compute                                                                                  
#SBATCH --qos=general-compute                                                                                        
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=8
#SBATCH --time=03:00:00
#SBATCH --output=/projects/ccrstaff/general/nikolays/huey/akrr_data/ior/2019.03.22.16.36.35.793858/stdout
#SBATCH --error=/projects/ccrstaff/general/nikolays/huey/akrr_data/ior/2019.03.22.16.36.35.793858/stderr
#SBATCH --constraint="CPU-L5520"
#SBATCH --exclusive


#Common commands
export AKRR_NODES=2
export AKRR_CORES=16
export AKRR_CORES_PER_NODE=8
export AKRR_NETWORK_SCRATCH="/projects/ccrstaff/general/nikolays/huey/tmp"
export AKRR_LOCAL_SCRATCH="/tmp"
export AKRR_TASK_WORKDIR="/projects/ccrstaff/general/nikolays/huey/akrr_data/ior/2019.03.22.16.36.35.793858"
export AKRR_APPKER_DIR="/projects/ccrstaff/general/nikolays/huey/appker"
export AKRR_AKRR_DIR="/projects/ccrstaff/general/nikolays/huey/akrr_data"

export AKRR_APPKER_NAME="ior"
export AKRR_RESOURCE_NAME="ub-hpc"
export AKRR_TIMESTAMP="2019.03.22.16.36.35.793858"
export AKRR_APP_STDOUT_FILE="$AKRR_TASK_WORKDIR/appstdout"

export AKRR_APPKERNEL_INPUT="/projects/ccrstaff/general/nikolays/huey/appker/inputs"
export AKRR_APPKERNEL_EXECUTABLE="/projects/ccrstaff/general/nikolays/huey/appker/execs/ior"

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



# MPI IO hints (optional)
# MPI IO hints are environment variables in the following format:
#
# 'IOR_HINT__<layer>__<hint>=<value>', where <layer> is either 'MPI'
# or 'GPFS', <hint> is the full name of the hint to be set, and <value>
# is the hint value.  E.g., 'export IOR_HINT__MPI__IBM_largeblock_io=true'
# 'export IOR_HINT__GPFS__hint=value' in mpi_io_hints


#create working dir
export AKRR_TMP_WORKDIR=`mktemp -d /projects/ccrstaff/general/nikolays/huey/tmp/ior.XXXXXXXXX`
echo "Temporary working directory: $AKRR_TMP_WORKDIR"
cd $AKRR_TMP_WORKDIR



#load application environment
#odule load hdf5
module list

#set executable location
EXE=$AKRR_APPKER_DIR/execs/ior/src/ior

#set how to run mpirun on all nodes
for node in $AKRR_NODELIST; do echo $node>>all_nodes; done
RUNMPI="mpiexec -n $AKRR_CORES -f all_nodes"

#set how to run mpirun on all nodes with offset, first print all nodes after node 1 and then node 1
sed -n "$(($AKRR_CORES_PER_NODE+1)),$(($AKRR_CORES))p" all_nodes > all_nodes_offset
sed -n "1,$(($AKRR_CORES_PER_NODE))p" all_nodes >> all_nodes_offset
RUNMPI_OFFSET="mpiexec -n $AKRR_CORES -f all_nodes_offset"


#Generate AppKer signature
appsigcheck.sh $EXE $AKRR_TASK_WORKDIR/.. > $AKRR_APP_STDOUT_FILE



#blockSize and transferSize
COMMON_TEST_PARAM="-b 200m -t 20m"
#2 level of verbosity, don't clear memory
COMMON_OPTIONS="-vv"
CACHING_BYPASS="-Z"

#list of test to perform
TESTS_LIST=("-a POSIX $RESOURCE_SPECIFIC_OPTION_N_to_1"
"-a POSIX -F $RESOURCE_SPECIFIC_OPTION_N_to_N")

#combine common parameters
COMMON_PARAM="$COMMON_OPTIONS $RESOURCE_SPECIFIC_OPTION $CACHING_BYPASS $COMMON_TEST_PARAM"


echo "Using $AKRR_TMP_WORKDIR for test...." >> $AKRR_APP_STDOUT_FILE 2>&1

#determine filesystem for file
canonicalFilename=`readlink -f $AKRR_TMP_WORKDIR`
filesystem=`awk -v canonical_path="$canonicalFilename" '{if ($2!="/" && 1==index(canonical_path, $2)) print $3 " " $1 " " $2;}' /proc/self/mounts`
echo "File System To Test: $filesystem" >> $AKRR_APP_STDOUT_FILE 2>&1
akrr_write_to_gen_info "file_system" "$filesystem"

#start the tests
akrr_write_to_gen_info "appkernel_start_time" "`date`"

#do write first
for TEST_PARAM in "${TESTS_LIST[@]}"
do
    echo "# Starting Test: $TEST_PARAM" >> $AKRR_APP_STDOUT_FILE 2>&1
    fileName=`echo ior_test_file_$TEST_PARAM |tr  '-' '_'|tr  ' ' '_'|tr  '=' '_'`
    
    #run the test
    command_to_run="$RUNMPI $EXE $COMMON_PARAM $TEST_PARAM -w -k -o $AKRR_TMP_WORKDIR/$fileName"
    echo "executing: $command_to_run" >> $AKRR_APP_STDOUT_FILE 2>&1
    $command_to_run >> $AKRR_APP_STDOUT_FILE 2>&1
done
#do read last
for TEST_PARAM in "${TESTS_LIST[@]}"
do
    echo "# Starting Test: $TEST_PARAM" >> $AKRR_APP_STDOUT_FILE 2>&1
    fileName=`echo ior_test_file_$TEST_PARAM |tr  '-' '_'|tr  ' ' '_'|tr  '=' '_'`
    
    #run the test
    command_to_run="$RUNMPI_OFFSET $EXE $COMMON_PARAM $TEST_PARAM -r -o $AKRR_TMP_WORKDIR/$fileName"
    echo "executing: $command_to_run" >> $AKRR_APP_STDOUT_FILE 2>&1
    $command_to_run >> $AKRR_APP_STDOUT_FILE 2>&1
done

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
[INFO] Creating task directory: /home/akrruser/akrr/log/data/ub-hpc/ior/2019.03.22.16.38.24.166085
[INFO] Creating task directories: 
        /home/akrruser/akrr/log/data/ub-hpc/ior/2019.03.22.16.38.24.166085/jobfiles
        /home/akrruser/akrr/log/data/ub-hpc/ior/2019.03.22.16.38.24.166085/proc
[INFO] Creating batch job script and submitting it to remote machine
[INFO] Directory huey:/projects/ccrstaff/general/nikolays/huey/akrr_data/ior does not exists, will try to create it
[INFO] Directory huey:/projects/ccrstaff/general/nikolays/huey/akrr_data/ior/2019.03.22.16.38.24.166085 does not exists, will try to create it
[INFO] auto_walltime_limit is on, trying to estimate walltime limit...
[INFO] There are only 0 previous run, need at least 5 for walltime limit autoset
[INFO] Local copy of batch job script is /home/akrruser/akrr/log/data/ub-hpc/ior/2019.03.22.16.38.24.166085/jobfiles/ior.job

[INFO] Application kernel working directory on ub-hpc is /projects/ccrstaff/general/nikolays/huey/akrr_data/ior/2019.03.22.16.38.24.166085
[INFO] Batch job script location on ub-hpc is /projects/ccrstaff/general/nikolays/huey/akrr_data/ior/2019.03.22.16.38.24.166085/ior.job```
The output contains the working directory for this task on remote resource. On remote resource get to that directory and start interactive session (request same number of nodes, in example above the script was generated for 2 nodes).
```

**On remote resource**
```bash
#get to working directory
cd /projects/ccrstaff/general/nikolays/huey/akrr_data/ior/2019.03.22.16.38.24.166085
#manually start batch job script
sbatch ior.job
```

Examine appstdout file, which contains application kernel output ([appstdout sample](AKRR_IOR_appsout_sample.md)).

If it looks ok you can move to the next step

# Perform Validation Run

On this step appkernel_validation.py utility is used to validate application kernel installation on 
the resource. It executes the application kernel and analyses its results. If it fails the problems 
need to be fixed and another round of validation (as detailed above) should be performed.

```bash
akrr app validate -n 2 -r $RESOURCE -a $APPKER 
```

See [IOR validation output sample](AKRR_IOR_appkernel_validation_sample.md)

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

Next [HPCC Deployment](AKRR_HPCC_Deployment.md)
