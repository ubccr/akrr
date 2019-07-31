### Setting up ior on openstack bare

So again, you just upload the binary folder to the volume, also you want to symbolically link it so that the run script can find the executable.

You're also going to need to upload a script that clears the caches as well as the necessary libraries that ior needs (like gpfs/hdf5/etc, it'll tell you)

Now, since we can't load up modules, we do have to have some variable usage to get around that
PATH - need to update so it can find mpiexec
SCRIPT_DIR - location of clear cache script (called with sudo)
EXE - path to the executable being used (wherever you installed it)
LD_LIBRARY_PATH - path to all the libraries that ior needs to use

So in the end my config looked like:

```bash
# which IO API/formats to check
testPOSIX = True
testMPIIO = False
testHDF5 = True
testNetCDF = True

# will do write test first and after that read, that minimize the caching impact from storage nodes
# require large temporary storage easily 100s GiB
doAllWritesFirst = True

appkernel_requests_two_nodes_for_one = False


appkernel_run_env_template = """
# load application environment

# use path to be able to call mpiexec and such
export PATH=$PATH:/opt/intel/impi/2018.3.222/bin64

# location of script to clear caches
export SCRIPT_DIR=/home/centos/appker/resource/no_docker/scripts

# set executable location
EXE=$AKRR_APPKER_DIR/execs/ior/src/ior

# so ior can find the libraries needed
export LD_LIBRARY_PATH=/home/centos/appker/resource/no_docker/libs


# set how to run mpirun on all nodes
for node in $AKRR_NODELIST; do echo $node>>all_nodes; done
RUNMPI="mpiexec -n $AKRR_CORES -f all_nodes"

# set how to run mpirun on all nodes with offset, first print all nodes after node 1 and then node 1
sed -n "$(($AKRR_CORES_PER_NODE+1)),$(($AKRR_CORES))p" all_nodes > all_nodes_offset
sed -n "1,$(($AKRR_CORES_PER_NODE))p" all_nodes >> all_nodes_offset
RUNMPI_OFFSET="mpiexec -n $AKRR_CORES -f all_nodes_offset"
"""
```

Then validation seems okay
I did edit the ior default config to call sudo bash $SCRIPT_DIR/drop_caches.sh

