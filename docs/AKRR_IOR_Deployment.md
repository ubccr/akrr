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

# Installing IOR


In this section the IOR installation process will be described, see also IOR benchmark documentation 
for installation details ( 
[https://github.com/hpc/ior](https://github.com/hpc/ior) ).

## Installing IOR with Spack

First install Spack and set it up to reuse system-wide packages, see [Spack Install and Setup](AKRR_Spack_Install_and_Setup.md).

```bash
# To install
$AKRR_APPKER_DIR/execs/spack/bin/spack -v install ior +hdf5 +ncmpi
```

## Manual Installation
### Installing HDF5 (optional)

It is preferred to use a system-wide installed parallel HDF5 library. This way 
_IOR_ will also test the workability and performance of this particular library installation. 
HDF5 is a popular format and are often deployed system-wide. Ensure that it was compiled with parallel 
support (for example by checking presence of h5pcc in $HDF5_HOME/bin). If there is no system-wide 
installed parallel HDF5 library than you might want to skip it.

Below are brief notes on parallel hdf5 installation,  
[http://www.hdfgroup.org/HDF5/](http://www.hdfgroup.org/HDF5/) for HDF5 installation details.

> **Note:** ior-3.2.0 does not work with hdf5-1.10.\*, so use hdf5-1.8.\* for that version or use development version of ior (3.3-dev).

**On target resource:**
```bash
#get to application kernel executable directory
cd $AKRR_APPKER_DIR/execs

#create lib directory if needed and temporary directory for compilation
mkdir -p lib
mkdir -p lib\tmp
cd lib\tmp

# obtain parallel-netcdf source code
wget https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-1.10/hdf5-1.10.6/src/hdf5-1.10.6.tar.gz
tar xvzf hdf5-1.10.6.tar.gz
cd hdf5-1.10.6

#configure hdf5
./configure --prefix=$AKRR_APPKER_DIR/execs/lib/hdf5-1.10.6 --enable-parallel CC=`which mpiicc` CXX=`which mpiicpc`
make -j 4

#install
make install
cd $AKRR_APPKER_DIR/execs

#optionally clean-up
rm -rf $AKRR_APPKER_DIR/execs/lib/tmp/hdf5-1.10.6
```

### Installing Parallel NetCDF (optional)

IOR can also use parallel NetCDF format to test file system IO. Parallel NetCDF tends to be slower 
than other APIs and therefore significantly increases the application kernel execution time. 
Therefore, if you know that parallel NetCDF is used on your system and you want to monitor its 
performance then go ahead and add it. If you use system-wide installed library, check that it is 
parallel. Regular  serial NetCDF will not work (IOR needs the parallel version). Below is brief 
note on parallel-netcdf installation, refer to 
[https://parallel-netcdf.github.io/](https://parallel-netcdf.github.io/) 
for more details - note that currently IOR needs the linked version of parallel NetCDF, not the 
(unfortunately incompatible) NetCDF-4 parallel API.

Similar to HDF5, if there is no system-wide installation and no use on the system than skip it as it
would be not that much useful.

Below are brief notes on parallel NetCDF installation,  
```bash
#get to application kernel executable directory
cd $AKRR_APPKER_DIR/execs

#create lib directory if needed and temporary directory for compilation
mkdir -p lib
mkdir -p lib/tmp
cd lib/tmp

#obtain parallel-netcdf source code
wget https://parallel-netcdf.github.io/Release/pnetcdf-1.12.1.tar.gz
tar xvzf pnetcdf-1.12.1.tar.gz
cd pnetcdf-1.12.1


#configure parallel-netcdf, specify installation location and which mpi compiler to use
./configure --prefix=$AKRR_APPKER_DIR/execs/lib/pnetcdf-1.12.1

#compile (do not use parallel compilation i.e. -j option)
make

#install
make install
cd $AKRR_APPKER_DIR/execs

#optionally clean-up
rm -rf $AKRR_APPKER_DIR/execs/lib/tmp/pnetcdf-1.12.1
```

## Installing IOR

Now we need to install IOR. Below is a sample listing of commands for IOR installation. Refer to 
IOR benchmark documentation for more installation details ( 
[https://github.com/hpc/ior](https://github.com/hpc/ior) ).

Following is done on HPC resource.

```bash
# cd to application kernel executable directory
cd $AKRR_APPKER_DIR/execs
#remove older version of ior
rm -rf ior


# Obtain latest version of IOR from our repository
# Option 1 use latest stable release (it have troubles with newer version of HDF5)
wget https://github.com/hpc/ior/releases/download/3.3.0/ior-3.3.0.tar.gz
tar -xzf ior-3.3.0.tar.gz
ln -s ior-3.3.0 ior
cd ior-3.3.0

# Option 2 using github
git clone https://github.com/hpc/ior.git
cd ior
git checkout 3.3.0rc1
./bootstrap
# load proper compilers and libs
# phdf5 and pnetcdf are optional only if you need to test hdf5 paralel library and 
# parallel netcdf  
module intel intel-mpi phdf5 pnetcdf
```

Configuration run for POSIX and MPIIO (i.e. without HDF5 and NetCDF):
```bash
./configure MPICC=mpiicc
```
> Optionally, IOR configuration with POSIX, MPIIO HDF5 and NetCDF:
> ```bash
> #set netcdf and hdf5 enviroment
> module load hdf5
> #configure IOR, note the specification of netcdf and hdf include and lib directories
> ./configure --with-hdf5=yes --with-ncmpi=yes \
>     CPPFLAGS="-I$AKRR_APPKER_DIR/execs/lib/pnetcdf-1.12.1/include -I$AKRR_APPKER_DIR/execs/lib/hdf5-1.10.6/include" \
>     LDFLAGS="-L$AKRR_APPKER_DIR/execs/lib/pnetcdf-1.12.1/lib -L$AKRR_APPKER_DIR/execs/lib/hdf5-1.10.6/lib " \
>     MPICC=mpiicc
> ```

Compilation:
```bash
# Compile
make
```

Post installation
```bash
# The binary should be src/ior
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
Using /projects/ccrstaff/general/nikolays/huey/tmp/ior.OtHKBus6G for test....
File System To Test: nfs ifs-x410.cbls.ccr.buffalo.edu:/ifs/projects /projects
# Starting Test: -a POSIX
executing: mpiexec -n 16 -f all_nodes /projects/ccrstaff/general/nikolays/huey/appker/execs/ior/src/ior -vv  -Z -b 200m -t 20m -a POSIX  -w -k -o /projects/ccrstaff/general/nikolays/huey/tmp/ior.OtHKBus6G/ior_test_file__a_POSIX
IOR-3.2.0: MPI Coordinated Test of Parallel I/O
Began               : Wed May  8 14:30:14 2019
Command line        : /projects/ccrstaff/general/nikolays/huey/appker/execs/ior/src/ior -vv -Z -b 200m -t 20m -a POSIX -w -k -o /projects/ccrstaff/general/nikolays/huey/tmp/ior.OtHKBus6G/ior_test_file__a_POSIX
Machine             : Linux cpn-d13-06.int.ccr.buffalo.edu
Start time skew across all tasks: 0.00 sec
TestID              : 0
StartTime           : Wed May  8 14:30:14 2019
Path                : /projects/ccrstaff/general/nikolays/huey/tmp/ior.OtHKBus6G
FS                  : 1704.7 TiB   Used FS: 49.3%   Inodes: 2635486.5 Mi   Used Inodes: 36.0%
Participating tasks: 16

Options:
api                 : POSIX
apiVersion          :
test filename       : /projects/ccrstaff/general/nikolays/huey/tmp/ior.OtHKBus6G/ior_test_file__a_POSIX
access              : single-shared-file
type                : independent
segments            : 1
ordering in a file  : sequential
ordering inter file : random task offset
task offset         : 1
reorder random seed : 0
tasks               : 16
clients per node    : 8
repetitions         : 1
xfersize            : 20 MiB
blocksize           : 200 MiB
aggregate filesize  : 3.12 GiB

Results:

access    bw(MiB/s)  block(KiB) xfer(KiB)  open(s)    wr/rd(s)   close(s)   total(s)   iter
------    ---------  ---------- ---------  --------   --------   --------   --------   ----
Commencing write performance test: Wed May  8 14:30:14 2019
write     104.26     204800     20480      0.309660   1.37       30.57      30.69      0
Max Write: 104.26 MiB/sec (109.33 MB/sec)

Summary of all tests:
Operation   Max(MiB)   Min(MiB)  Mean(MiB)     StdDev   Max(OPs)   Min(OPs)  Mean(OPs)     StdDev    Mean(s) Test# #Tasks tPN reps fPP reord reordoff reordrand seed segcnt   blksiz    xsize aggs(MiB)   API RefNum
write         104.26     104.26     104.26       0.00       5.21       5.21       5.21       0.00   30.69206     0     16   8    1   0     0        1         1    0      1 209715200 20971520    3200.0 POSIX      0
Finished            : Wed May  8 14:30:45 2019
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

Below is a fragment example from ior.app.conf which will instruct IOR to use 
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

**Sample output of akrr task new --dry-run --gen-batch-job-only -n 2 -r $RESOURCE -a $APPKER**
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

# Run on all nodes count 20 times (default number of runs to establish baseline)
akrr task new -r $RESOURCE -a $APPKER -n 1,2,4,8 --n-runs 20
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
