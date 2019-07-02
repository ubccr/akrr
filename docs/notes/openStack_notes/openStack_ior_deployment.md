### Deployment of ior on openstack

Okay so first I'll try using the ior_barebones02 docker image to try and get it to work on openstack. So

```bash
akrr app add -a ior -r open-lakeeffect-stack

#Output
[INFO] Generating application kernel configuration for ior on open-lakeeffect-stack
[INFO] Application kernel configuration for ior on open-lakeeffect-stack is in: 
        /home/hoffmaps/projects/akrr/etc/resources/open-lakeeffect-stack/ior.app.conf
```
initial config for ior:
```bash
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
Now, from running ior on vortex, this is the config file from that:
```bash
[hoffmaps@dhcp-128-205-70-4 open-lakeeffect-stack]$ cat ../vortex_dock_sing/ior.app.conf 
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
module load intel
module load intel-mpi
module list

# set executable location
EXE="/gpfs/scratch/hoffmaps/singularity_images/akrr_benchmarks_ior_barebones02.sif"

 #set how to run mpirun on all nodes
export LD_LIBRARY_PATH=/opt/appker/lib:/opt/intel/impi/2018.3.222/lib64:$LD_LIBRARY_PATH
unset TMPDIR
$EXE --appsigcheck >> $AKRR_APP_STDOUT_FILE 2>&1
EXE="$EXE --ior-run"
for node in $AKRR_NODELIST; do echo $node>>all_nodes; done
RUNMPI="mpiexec -n $AKRR_CORES -f all_nodes"

# set how to run mpirun on all nodes with offset, first print all nodes after node 1 and then node 1
sed -n "$(($AKRR_CORES_PER_NODE+1)),$(($AKRR_CORES))p" all_nodes > all_nodes_offset
sed -n "1,$(($AKRR_CORES_PER_NODE))p" all_nodes >> all_nodes_offset
RUNMPI_OFFSET="mpiexec -n $AKRR_CORES -f all_nodes_offset"
"""
```
So, here is the issue: this calls an executable, but with docker we have to use the run command. So I'll make a new docker image that runs ior inside docker with the mpi exec and such, aka sorta doing what is being done in the ior.job stuff.

UPDATE ran into that pesky json error again - cannot hand out too many tokens or whatever, so it looks like the whole revoke token thing didn't really work

So I had some errors with the filesystem.... somehow with docker the directories or something couldn't be found...? Not exactly sure what was going on, but at the very least I got things working on openstack. The configuration of ior.app.conf is below along with the explanation

```bash
[hoffmaps@dhcp-128-205-70-4 open-lakeeffect-stack]$ cat ior.app.conf 
# which IO API/formats to check
testPOSIX = True
testMPIIO = False
testHDF5 = False
testNetCDF = False

# setting false up here so we can just run on one node
appkernel_requests_two_nodes_for_one = False

# will do write test first and after that read, that minimize the caching impact from storage nodes
# require large temporary storage easily 100s GiB
doAllWritesFirst = True

appkernel_run_env_template = """
sudo systemctl start docker
docker pull pshoff/akrr_benchmarks:ior_docker
EXE="docker run -v $AKRR_TMP_WORKDIR:$AKRR_TMP_WORKDIR --rm pshoff/akrr_benchmarks:ior_docker"

# set how to run mpirun on all nodes
for node in $AKRR_NODELIST; do echo $node>>all_nodes; done
# putting nothing here bc further down we don't want to use it really
RUNMPI=""

# set how to run mpirun on all nodes with offset, first print all nodes after node 1 and then node 1
sed -n "$(($AKRR_CORES_PER_NODE+1)),$(($AKRR_CORES))p" all_nodes > all_nodes_offset
sed -n "1,$(($AKRR_CORES_PER_NODE))p" all_nodes >> all_nodes_offset
# same for this run
RUNMPI_OFFSET=""
"""
```
- Deleted the stuff at the Runmpi bc that is being done in the docker container
- The EXE is just the docker run, then all the arguments get passed through to the run script, which does mpiexec.
- set the appkernel_requests_two_nodes_for_one to False, since we're treating openstack as only being one node
- This does mean that the whole offset thing is useless...
- also like the results are sorta weird bc its saying we can write 20 gb per second and that's a LOT 

The final configuration file, after adding in the appsigcheck:
```bash
# which IO API/formats to check
testPOSIX = True
testMPIIO = False
testHDF5 = False
testNetCDF = False

# setting false up here so we can just run on one node
appkernel_requests_two_nodes_for_one = False

# will do write test first and after that read, that minimize the caching impact from storage nodes
# require large temporary storage easily 100s GiB
doAllWritesFirst = True

appkernel_run_env_template = """
sudo systemctl start docker
docker pull pshoff/akrr_benchmarks:ior
EXE="docker run -v $AKRR_TMP_WORKDIR:$AKRR_TMP_WORKDIR --rm pshoff/akrr_benchmarks:ior --ior-run --proc 8"
^^
# sending over how many processes we want to run (see docker directory for more)

# to get appsig
docker run --rm pshoff/akrr_benchmarks:ior --appsigcheck >> $AKRR_APP_STDOUT_FILE 2>&1

# set how to run mpirun on all nodes
for node in $AKRR_NODELIST; do echo $node>>all_nodes; done
# putting nothing here bc further down we don't want to use it really
RUNMPI=""

# set how to run mpirun on all nodes with offset, first print all nodes after node 1 and then node 1
sed -n "$(($AKRR_CORES_PER_NODE+1)),$(($AKRR_CORES))p" all_nodes > all_nodes_offset
sed -n "1,$(($AKRR_CORES_PER_NODE))p" all_nodes >> all_nodes_offset
# same for this run
RUNMPI_OFFSET=""
"""
```




