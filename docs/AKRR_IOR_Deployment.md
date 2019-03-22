# AKRR: Deployment of IOR Applications Kernels on a Resource

Here the deployment of ior application kernel is described. This application 
kernel is based on IOR benchmark which design to measure the performance of parallel file-systems.

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

Besides POSIX and MPIIO APIs for input-output, IOR can also test parallel HDF5 and NetCDF. You can 
choose which API to use, based on the API utilization in your center. XDMoD usually tests all of 
them. HDF5 is a popular format and many scientific HPC application use it. NetCDF is arguably a bit 
less popular and the kernel results take longer. So if you know (or strongly suspect) that nobody 
uses NetCDF on your system you might want to skip it.

### Installing HDF5

Ideally, it is preferred to use a system-wide installed parallel HDF5 library. This way 
_ior_ will also test the workability and performance of this particular library installation. HDF5 
is a popular format and are often deployed system-wide. Ensure that it was compiled with parallel 
support (for example by checking presence of h5pcc in $HDF5_HOME/bin).

Bellow is brief notes on parallel hdf5 installation,  
[http://www.hdfgroup.org/HDF5/](http://www.hdfgroup.org/HDF5/) for HDF5 installation details.

**On target resource:**
```bash
#get to application kernel executable directory
cd $AKRR_APPKER_DIR/execs

#create lib directory if needed and temporary directory for compilation
mkdir -p lib
mkdir -p lib\\tmp
cd lib\\tmp

#obtain parallel-netcdf source code
wget http://www.hdfgroup.org/ftp/HDF5/current/src/hdf5-1.8.14.tar.gz
tar xvzf hdf5-1.8.14.tar.gz
cd hdf5-1.8.14

#configure hdf5
./configure --prefix=$AKRR_APPKER_DIR/execs/lib/hdf5-1.8.14 --enable-parallel CC=\`which mpiicc\` CXX=\`which mpiicpc\`
make
 
#install
make install
cd $AKRR_APPKER_DIR/execs
 
#optionally clean-up
rm -rf $AKRR_APPKER_DIR/execs/lib/tmp/hdf5-1.8.14
```

### Installing Parallel NETCDF (optional)

IOR can also use parallel NetCDF format to test file system IO. Parallel NetCDF tends to be slower 
than other APIs and therefore significantly increases the application kernel execution time. 
Therefore, if you know that parallel NetCDF is used on your system and you want to monitor its 
performance then go ahead and add it. If you use system-wide installed library, check that it is 
parallel. Regular  serial NetCDF will not work (IOR needs the parallel version). Bellow is brief 
note on parallel-netcdf installation, refer to 
[http://trac.mcs.anl.gov/projects/parallel-netcdf](http://trac.mcs.anl.gov/projects/parallel-netcdf) 
for more details - note that currently IOR needs the linked version of parallel NetCDF, not the 
(unfortunately incompatible) NetCDF-4 parallel API.

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
#check that proper compilers are loaded
module list
Currently Loaded Modulefiles:
1) intel/14.0.2 4) tgusage/3.0 7) ant/1.9.4 10) tgresid/2.3.4
2) mvapich2/2.0/INTEL-14.0.2 5) globus/5.0.4-r1 8) java/1.7.0 11) xsede/1.0
3) gx-map/0.5.3.3-r1 6) tginfo/1.1.4 9) uberftp/2.6



#set netcdf and hdf5 enviroment
module load hdf5/1.8.12/INTEL-140-MVAPICH2-2.0
#configure IOR, note the specification of netcdf and hdf include and lib directories
./configure --with-hdf5=yes --with-ncmpi=yes CPPFLAGS="-I$AKRR_APPKER_DIR/execs/lib/pnetcdf-1.3.1/include -I/usr/local/packages/netcdf/4.2.1.1/INTEL-140-MVAPICH2-2.0/include" LDFLAGS="-L/usr/local/packages/hdf5/1.8.12/INTEL-140-MVAPICH2-2.0/lib -L$AKRR_APPKER_DIR/execs/lib/pnetcdf-1.3.1/lib"
#compile
make
 
#the binary should be src/ior
ls $AKRR_APPKER_DIR/execs/ior/src/ior
```

# Generate Initiate Configuration File

Generate Initiate Configuration File:

**On AKRR server**
```bash
> python $AKRR_HOME/setup/scripts/gen_appker_on_resource_cfg.py $RESOURCE $APPKER
[INFO]: Generating application kernel configuration for xdmod.benchmark.io.ior on rush
[INFO]: Application kernel configuration for xdmod.benchmark.io.ior on SuperMIC is in: 
        /home/mikola/wsp/test/akrr/cfg/resources/rush/xdmod.benchmark.io.ior.app.inp.py
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

The most effective strategy to properly setup `xdmod.benchmark.io.ior` is to use an interactive 
session to test and define configurable parameters.

## Configuring parameters which defines how IOR will be executed

First, lets configure parameters which generally do not require an interactive debug session.

Below is a listing of the generated default configuration file located at 
$AKRR_HOME/cfg/resources/$RESOURCE/`xdmod.benchmark.io.ior`

**$AKRR_HOME/cfg/resources/$RESOURCE/xdmod.benchmark.io.ior.inp.py**
```python
#which IO API/formats to check
testPOSIX=True
testMPIIO=True
testHDF5=True
testNetCDF=True

#will do write test first and after that read, that minimize the caching impact from storage nodes
#require large temporary storage easily 100s GiB 
doAllWritesFirst=True

appKernelRunEnvironmentTemplate="""
#load application environment
module load hdf5/1.8.12/INTEL-140-MVAPICH2-2.0
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

#set striping for lustre file system
RESOURCE_SPECIFIC_OPTION_N_to_1="-O lustreStripeCount=$AKRR_NODES"
RESOURCE_SPECIFIC_OPTION_N_to_N=""
#other resource specific options
RESOURCE_SPECIFIC_OPTION=""
"""
```

`The first several lines specify which IO APIs to test:`

**Fragment of $AKRR_HOME/cfg/resources/$RESOURCE/xdmod.benchmark.io.ior.inp.py**
```python
#which IO API/formats to check
testPOSIX=True
testMPIIO=True
testHDF5=True
testNetCDF=True
```

The one which you may want to set to False is testNetCDF (see discussion above during parallel 
NetCDF library installation).

Next several lines instruct IOR application kernel to do all writes first and then do all reads:

**Fragment of $AKRR_HOME/cfg/resources/$RESOURCE/xdmod.benchmark.io.ior.inp.py**
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

## Setting up _appKernelRunEnvironmentTemplate_

Now we need to set _appKernelRunEnvironmentTemplate_ template variable.

We will do it section by section and will use interactive session on resource to test the entries.

First lets generate **test** application kernel batch job script (**not IOR script**, we will use 
this test job script to set AKRR predifined environment variable to use during entries validation):

**On AKRR Server**
```bash
> $AKRR_HOME/bin/akrr_ctl.sh batch_job -r $RESOURCE -a test -n 2
[INFO]: Local copy of batch job script is /home/mikola/wsp/test/akrr/data/SuperMIC/test/2014.12.16.12.12.51.198128/jobfiles/test.job

[INFO]: Application kernel working directory on SuperMIC is /work/xdtas/akrrdata/test/2014.12.16.12.12.51.198128
[INFO]: Batch job script location on SuperMIC is /work/xdtas/akrrdata/test/2014.12.16.12.12.51.198128/test.job
```

The output contains the working directory for this task on remote resource. On remote resource get 
to that directory and start interactive session (request same number of nodes, in example above the 
script was generated for 2 nodes).

**On remote resource**
```bash
#get to working directory
cd /work/xdtas/akrrdata/test/2014.12.16.12.12.51.198128
#check that test.job is there
ls
#start interactive session
qsub -I -l walltime=01:00:00,nodes=2:ppn=20
#wait till you get access to interactive session

#get to working directory again if not already there
cd /work/xdtas/akrrdata/test/2014.12.16.12.12.51.198128
#load everything from test.job
source test.job 
#check AKRR predifined environment variable are loaded
echo $AKRR_NODES
#output should be 2

echo $AKRR_NODELIST
#output should be space separated list of hosts 
```

Now we ready to configure _appKernelRunEnvironmentTemplate (in $AKRR_HOME/cfg/resources/Rush-debug/xdmod.benchmark.io.ior.app.inp.py)_.

### Seting up environment

In first section we set proper environment for IOR to work, we also place IOR executable location to EXE variable (binary in $EXE will be used to generate application signature):

**appKernelRunEnvironmentTemplate fragment of xdmod.benchmark.io.ior.inp.py**
```bash
#load application environment
module load hdf5/1.8.12/INTEL-140-MVAPICH2-2.0
module list

#set executable location
EXE=$AKRR_APPKER_DIR/execs/ior/src/ior
```
Make the appropriate changes for your system in 
$AKRR_HOME/cfg/resources/$RESOURCE/xdmod.benchmark.io.ior.inp.py and execute in interactive session, 
check that IOR is working:

**On remote resource**
```bash
#load application environment
module load hdf5/1.8.12/INTEL-140-MVAPICH2-2.0
module list

#set executable location
EXE=$AKRR_APPKER_DIR/execs/ior/src/ior
```

Check that IOR is working:

**On remote resource**
```bash
#let check is it working:
mpirun $EXE
```

The default file sizes for ior are quite small, so running ior with no arguments as above should 
return very quickly - unless something is wrong.

If it is not working modify the environment appropriately in 
$AKRR_HOME/cfg/resources/$RESOURCE/xdmod.benchmark.io.ior.inp.py.

### Setting up How to run MPI application on All Nodes

Next, we setup how to run mpirun/mpiexec on all nodes:

**appKernelRunEnvironmentTemplate fragment of xdmod.benchmark.io.ior.inp.py**
```bash
#set how to run mpirun on all nodes
for node in $AKRR_NODELIST; do echo $node>>all_nodes; done
RUNMPI="mpiexec -n $AKRR_CORES -f all_nodes"
```

Nearly all mpi implementations accept a plain list of hosts(nodes) as a machines file on which to 
run the MPI tasks, although the options to use that list may vary. In this script we generate a list 
of all nodes (one per MPI process) and place in the $RUNMPI environment variable how to execute 
mpirun (or whatever MPI task launcher is preferred on your platform).

Adjust this section in $AKRR_HOME/cfg/resources/$RESOURCE/xdmod.benchmark.io.ior.inp.py and again 
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
IOR-3.0.1: MPI Coordinated Test of Parallel I/O
Began: Tue Dec 16 11:34:22 2014
Command line used: /home/xdtas/appker/supermic/execs/ior/src/ior -vv
Machine: Linux smic006 2.6.32-358.23.2.el6.x86_64 #1 SMP Sat Sep 14 05:32:37 EDT 2013 x86_64
Using synchronized MPI timer
Start time skew across all tasks: 0.00 sec
Test 0 started: Tue Dec 16 11:34:22 2014
Path: /worka/work/xdtas/akrrdata/test/2014.12.16.12.12.51.198128
FS: 698.3 TiB   Used FS: 0.5%   Inodes: 699.1 Mi   Used Inodes: 0.7%
Participating tasks: 40
task 0 on smic006
task 1 on smic006
<many lines like previous>
task 9 on smic006
Summary:
        api                = POSIX
        test filename      = testFile
        access             = single-shared-file
        pattern            = segmented (1 segment)
        ordering in a file = sequential offsets
        ordering inter file= no tasks offsets
        clients            = 40 (20 per node)
        repetitions        = 1
        xfersize           = 262144 bytes
        blocksize          = 1 MiB
        aggregate filesize = 40 MiB
Using Time Stamp 1418751262 (0x54906d1e) for Data Signature
access    bw(MiB/s)  block(KiB) xfer(KiB)  open(s)    wr/rd(s)   close(s)   total(s)   iter
------    ---------  ---------- ---------  --------   --------   --------   --------   ----
Commencing write performance test: Tue Dec 16 11:34:22 2014
write     26.05      1024.00    256.00     0.004612   1.52       1.48       1.54       0   
Commencing read performance test: Tue Dec 16 11:34:24 2014
read      1149.09    1024.00    256.00     0.002482   0.034575   0.033708   0.034810   0   
remove    -          -          -          -          -          -          0.002008   0   
Max Write: 26.05 MiB/sec (27.31 MB/sec)
Max Read:  1149.09 MiB/sec (1204.91 MB/sec)
Summary of all tests:
Operation   Max(MiB)   Min(MiB)  Mean(MiB)     StdDev    Mean(s) Test# #Tasks tPN reps fPP reord reordoff reordrand seed segcnt blksiz xsize aggsize API RefNum
write          26.05      26.05      26.05       0.00    1.53557 0 40 20 1 0 0 1 0 0 1 1048576 262144 41943040 POSIX 0
read         1149.09    1149.09    1149.09       0.00    0.03481 0 40 20 1 0 0 1 0 0 1 1048576 262144 41943040 POSIX 0
Finished: Tue Dec 16 11:34:24 2014
```

If it is not working modify the executed commands and copy the good ones to $AKRR_HOME/cfg/resources/$RESOURCE/xdmod.benchmark.io.ior.inp.py.

### Setting up How to run MPI application on All Nodes with Nodes Offset

Next, we setup how to run mpirun/mpiexec on all nodes with one node offset:

**appKernelRunEnvironmentTemplate fragment of xdmod.benchmark.io.ior.inp.py**
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

Adjust this section in $AKRR_HOME/cfg/resources/$RESOURCE/xdmod.benchmark.io.ior.inp.py and execute 
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
$AKRR_HOME/cfg/resources/$RESOURCE/xdmod.benchmark.io.ior.inp.py.

### Setting up Luster file striping

If you use Lustre you might want to use file striping for better parallel performance. The variables 
RESOURCE_SPECIFIC_OPTION, RESOURCE_SPECIFIC_OPTION_N_to_1 and RESOURCE_SPECIFIC_OPTION_N_to_N and  
will be passed to IOR as command line options.

RESOURCE_SPECIFIC_OPTION will be passed to all IOR execution.

RESOURCE_SPECIFIC_OPTION_N_to_1 will be passed to IOR for tests there all processes writes to a 
single file and RESOURCE_SPECIFIC_OPTION_N_to_N will be passed to IOR for tests there all processes 
writes to their own independent files.

Bellow is a fragment example from xdmod.benchmark.io.ior.inp.py which will instruct IOR to use 
striping equal to the number of nodes when all processes write to a single file.

**appKernelRunEnvironmentTemplate fragment of xdmod.benchmark.io.ior.inp.py**
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
$AKRR_HOME/bin/akrr_ctl.sh batch_job -p -r $RESOURCE -a $APPKER -n 2
```

**Sample output of $AKRR_HOME/bin/akrr_ctl.sh batch_job -p -r $RESOURCE -a $APPKER -n 2**
```bash
[INFO]: Below is content of generated batch job script:
#!/bin/bash
#PBS -l nodes=2:ppn=20
#PBS -m n
#PBS -q workq
#PBS -e stderr
#PBS -o stdout
#PBS -l walltime=03:00:00
#PBS -u xdtas
#PBS -A TG-CCR120014


#Populate list of nodes per MPI process
export AKRR_NODELIST=`cat $PBS_NODEFILE`


#Common commands
export AKRR_NODES=2
export AKRR_CORES=40
export AKRR_CORES_PER_NODE=20
export AKRR_NETWORK_SCRATCH="/work/xdtas/scratch"
export AKRR_LOCAL_SCRATCH="/tmp"
export AKRR_TASK_WORKDIR="/work/xdtas/akrrdata/xdmod.benchmark.io.ior/2014.12.16.13.39.55.613578"
export AKRR_APPKER_DIR="/home/xdtas/appker/supermic"
export AKRR_AKRR_DIR="/work/xdtas/akrrdata"

export AKRR_APPKER_NAME="xdmod.benchmark.io.ior"
export AKRR_RESOURCE_NAME="SuperMIC"
export AKRR_TIMESTAMP="2014.12.16.13.39.55.613578"
export AKRR_APP_STDOUT_FILE="$AKRR_TASK_WORKDIR/appstdout"

export AKRR_APPKERNEL_INPUT="/home/xdtas/appker/supermic/inputs"
export AKRR_APPKERNEL_EXECUTABLE="/home/xdtas/appker/supermic/execs/ior/C/IOR"

source "$AKRR_APPKER_DIR/execs/bin/akrr_util.bash"

export PATH="$AKRR_APPKER_DIR/execs/bin:$PATH"

cd "$AKRR_TASK_WORKDIR"

#run common tests
akrrPerformCommonTests

#Write some info to gen.info, JSON-Like file
writeToGenInfo "startTime" "`date`"
writeToGenInfo "nodeList" "$AKRR_NODELIST"



# MPI IO hints (optional)
# MPI IO hints are environment variables in the following format:
#
# 'IOR_HINT__<layer>__<hint>=<value>', where <layer> is either 'MPI'
# or 'GPFS', <hint> is the full name of the hint to be set, and <value>
# is the hint value.  E.g., 'export IOR_HINT__MPI__IBM_largeblock_io=true'
# 'export IOR_HINT__GPFS__hint=value' in mpi_io_hints


#create working dir
export AKRR_TMP_WORKDIR=`mktemp -d /work/xdtas/scratch/ior.XXXXXXXXX`
echo "Temporary working directory: $AKRR_TMP_WORKDIR"
cd $AKRR_TMP_WORKDIR



#load application environment
module load hdf5/1.8.12/INTEL-140-MVAPICH2-2.0
module list

#set executable location
EXE=/home/xdtas/appker/supermic/execs/ior/src/ior

#set how to run mpirun on all nodes
for node in $AKRR_NODELIST; do echo $node>>all_nodes; done
echo "all_nodes:"
cat all_nodes
RUNMPI="mpiexec -n $AKRR_CORES -f all_nodes"

#set how to run mpirun on all nodes with offset, first print all nodes after node 1 and then node 1
sed -n "$(($AKRR_CORES_PER_NODE+1)),$(($AKRR_CORES))p" all_nodes > all_nodes_offset
sed -n "1,$(($AKRR_CORES_PER_NODE))p" all_nodes >> all_nodes_offset
echo "all_nodes_offset:"
cat all_nodes_offset
RUNMPI_OFFSET="mpiexec -n $AKRR_CORES -f all_nodes_offset"

#set how to run mpirun on first node
sed -n "1,$(($AKRR_CORES_PER_NODE))p" all_nodes > first_node
echo "first_node:"
cat first_node
RUNMPI_FIRST_NODE="mpiexec -n $AKRR_CORES_PER_NODE -f first_node"

#set how to run mpirun on second node
sed -n "$(($AKRR_CORES_PER_NODE+1)),$((2*$AKRR_CORES_PER_NODE))p" all_nodes > second_node
echo "second_node:"
cat second_node
RUNMPI_SECOND_NODE="mpiexec -n $AKRR_CORES_PER_NODE -f second_node"

#set striping for lustre file system
RESOURCE_SPECIFIC_OPTION_N_to_1="-O lustreStripeCount=$AKRR_NODES"
RESOURCE_SPECIFIC_OPTION_N_to_N=""

#other resource specific options
RESOURCE_SPECIFIC_OPTION=""


#Generate AppKer signature
appsigcheck.sh $EXE $AKRR_TASK_WORKDIR/.. > $AKRR_APP_STDOUT_FILE



#blockSize and transferSize
COMMON_TEST_PARAM="-b 200m -t 20m"
#2 level of verbosity, don't clear memory
COMMON_OPTIONS="-vv"
CACHING_BYPASS="-Z"

#list of test to perform
TESTS_LIST=("-a POSIX $RESOURCE_SPECIFIC_OPTION_N_to_1"
"-a POSIX -F $RESOURCE_SPECIFIC_OPTION_N_to_N"
"-a MPIIO $RESOURCE_SPECIFIC_OPTION_N_to_1"
"-a MPIIO -c $RESOURCE_SPECIFIC_OPTION_N_to_1"
"-a MPIIO -F $RESOURCE_SPECIFIC_OPTION_N_to_N"
"-a HDF5 $RESOURCE_SPECIFIC_OPTION_N_to_1"
"-a HDF5 -c $RESOURCE_SPECIFIC_OPTION_N_to_1"
"-a HDF5 -F $RESOURCE_SPECIFIC_OPTION_N_to_N")

#combine common parameters
COMMON_PARAM="$COMMON_OPTIONS $RESOURCE_SPECIFIC_OPTION $CACHING_BYPASS $COMMON_TEST_PARAM"


echo "Using $AKRR_TMP_WORKDIR for test...." >> $AKRR_APP_STDOUT_FILE 2>&1

#determine filesystem for file
canonicalFilename=`readlink -f $AKRR_TMP_WORKDIR`
filesystem=`awk -v canonical_path="$canonicalFilename" '{if ($2!="/" && 1==index(canonical_path, $2)) print $3 " " $1 " " $2;}' /proc/self/mounts`
echo "File System To Test: $filesystem" >> $AKRR_APP_STDOUT_FILE 2>&1
writeToGenInfo "fileSystem" "$filesystem"

#start the tests
writeToGenInfo "appKerStartTime" "`date`"

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

writeToGenInfo "appKerEndTime" "`date`"




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



writeToGenInfo "endTime" "`date`"

[INFO]: Removing generated files from file-system as only batch job script printing was requested
```

Next generate the script on resource:
```bash
> $AKRR_HOME/bin/akrr_ctl.sh batch_job -r $RESOURCE -a $APPKER -n 2
[INFO]: Local copy of batch job script is /home/mikola/wsp/test/akrr/data/SuperMIC/xdmod.benchmark.io.ior/2014.12.16.13.43.05.851076/jobfiles/xdmod.benchmark.io.ior.job

[INFO]: Application kernel working directory on SuperMIC is /work/xdtas/akrrdata/xdmod.benchmark.io.ior/2014.12.16.13.43.05.851076
[INFO]: Batch job script location on SuperMIC is /work/xdtas/akrrdata/xdmod.benchmark.io.ior/2014.12.16.13.43.05.851076/xdmod.benchmark.io.ior.job
```
The output contains the working directory for this task on remote resource. On remote resource get to that directory and start interactive session (request same number of nodes, in example above the script was generated for 2 nodes).

**On remote resource**
```bash
#get to working directory
cd /work/xdtas/akrrdata/xdmod.benchmark.io.ior/2014.12.16.13.43.05.851076
#check that xdmod.benchmark.io.ior.job is there
ls
#start interactive session
qsub -I -l walltime=01:00:00,nodes=2:ppn=20
#wait till you get access to interactive session

#get to working directory again if you was not redirected there
cd /work/xdtas/akrrdata/xdmod.benchmark.io.ior/2014.12.16.13.43.05.851076
#run ior application kernel
bash xdmod.benchmark.io.ior.job
```

Examine appstdout file, which contains application kernel output:

**On remote resource, appstdout content**
```bash
===ExeBinSignature=== DYNLIB: Glibc 2.12
<many lines like previous>
===ExeBinSignature=== MD5: a6e6262120f548dc3a4486ac3df13863 \*/home/xdtas/appker/supermic/execs/ior/src/ior
<many lines like previous>
Using /work/xdtas/scratch/ior.xnUWSQf0V for test....
File System To Test: lustre 172.17.40.34@o2ib:172.17.40.35@o2ib:/smic /worka
# Starting Test: -a POSIX -O lustreStripeCount=2
executing: mpiexec -n 40 -f all_nodes /home/xdtas/appker/supermic/execs/ior/src/ior -vv  -Z -b 200m -t 20m -a POSIX -O lustreStripeCount=2 -w -k -o /work/xdtas/scratch/ior.xnUWSQf0V/ior_test_file__a_POSIX__O_lustreStripeCount_2
IOR-3.0.1: MPI Coordinated Test of Parallel I/O

Began: Tue Dec 16 12:44:13 2014
Command line used: /home/xdtas/appker/supermic/execs/ior/src/ior -vv -Z -b 200m -t 20m -a POSIX -O lustreStripeCount=2 -w -k -o /work/xdtas/scratch/ior.xnUWSQf0V/ior_test_file__a_POSIX__O_lustreStripeCount_2
Machine: Linux smic001 2.6.32-358.23.2.el6.x86_64 #1 SMP Sat Sep 14 05:32:37 EDT 2013 x86_64
Using synchronized MPI timer
Start time skew across all tasks: 0.00 sec

Test 0 started: Tue Dec 16 12:44:13 2014
Path: /worka/work/xdtas/scratch/ior.xnUWSQf0V
FS: 698.3 TiB   Used FS: 0.5%   Inodes: 699.1 Mi   Used Inodes: 0.7%
Participating tasks: 40
task 0 on smic001
task 1 on smic001
<many lines like previous>
task 9 on smic001
Summary:
        api                = POSIX
        test filename      = /work/xdtas/scratch/ior.xnUWSQf0V/ior_test_file__a_POSIX__O_lustreStripeCount_2
        access             = single-shared-file
        pattern            = segmented (1 segment)
        ordering in a file = sequential offsets
        ordering inter file= random task offsets >= 1, seed=0
        clients            = 40 (20 per node)
        repetitions        = 1
        xfersize           = 20 MiB
        blocksize          = 200 MiB
        aggregate filesize = 7.81 GiB
        Lustre stripe size = Use default
              stripe count = 2
Using Time Stamp 1418755453 (0x54907d7d) for Data Signature

access    bw(MiB/s)  block(KiB) xfer(KiB)  open(s)    wr/rd(s)   close(s)   total(s)   iter
------    ---------  ---------- ---------  --------   --------   --------   --------   ----
Commencing write performance test: Tue Dec 16 12:44:13 2014
write     508.93     204800     20480      0.005252   15.72      11.85      15.72      0   

Max Write: 508.93 MiB/sec (533.65 MB/sec)

Summary of all tests:
Operation   Max(MiB)   Min(MiB)  Mean(MiB)     StdDev    Mean(s) Test# #Tasks tPN reps fPP reord reordoff reordrand seed segcnt blksiz xsize aggsize API RefNum
write         508.93     508.93     508.93       0.00   15.71921 0 40 20 1 0 0 1 1 0 1 209715200 20971520 8388608000 POSIX 0

Finished: Tue Dec 16 12:44:28 2014
# Starting Test: -a POSIX -F 
 
...
<many output similar to previous>
...

Finished: Tue Dec 16 12:47:42 2014
```

If it looks ok you can move to the next step

# Perform Validation Run

On this step appkernel_validation.py utility is used to validate application kernel installation on 
the resource. It executes the application kernel and analyses its results. If it fails the problems 
need to be fixed and another round of validation (as detailed above) should be performed.

```bash
python $AKRR_HOME/setup/scripts/appkernel_validation.py -n 2 $RESOURCE $APPKER
```

**appkernel_validation.py Sample output**

DONE, you can move to next step!

# Schedule regular execution of application kernel.

Now this application kernel can be submitted for regular execution:

```bash
#Perform a test run on all nodes count
python $AKRR_HOME/src/akrrctl.py new_task -r $RESOURCE -a $APPKER -n 1,2,4,8

#Start daily execution from today on nodes 1,2,4,8 and distribute execution time between 1:00 and 5:00
python $AKRR_HOME/src/akrrctl.py new_task -r $RESOURCE -a $APPKER -n 1,2,4,8 -t0 "01:00" -t1 "05:00" -p 1
```

see [Scheduling and Rescheduling Application Kernels](6259267.html) and 
[Setup Walltime Limit](Setup-Walltime-Limit_6259272.html) for more details

# FAQ


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
