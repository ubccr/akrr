### Notes on installing hdf5 and trying to get it to work with HDF5

First I just followed along with the installation instructions in the ior deployment

had to do 
module load intel-mpi/2018.3
module load intel/18.3

So I installed hdf5 apparently...? idk how to test that

hmmm maybe I just have to load the module...? not sure honestly
module load hdf5/1.10.1 

I'll also install parallel netcdf, then i can configure ior to work with all of those
pnetcdf doesn't appear to have a module, though there is
netcdf/4.3.3.1
and idk what to do with that
regardless imma install anyways


So i followed the installation instructions, everything seemed okay
Then I set the hdf5 and netcdf things to true in the app config
In validation run, getting error cannot open shared object file of hdf5 and such
Maybe have to set library path again?

Okay so I was dumb and I didn't add the library path stuff for the other things
But anyways, it works, the config file looks like this:
```bash
# which IO API/formats to check
testPOSIX = True
testMPIIO = False
testHDF5 = True
testNetCDF = True

# will do write test first and after that read, that minimize the caching impact from storage nodes
# require large temporary storage easily 100s GiB
doAllWritesFirst = True

appkernel_run_env_template = """
# load application environment
#module load hdf5
module load intel/18.3
module load intel-mpi/2018.3
module list

# set executable location
EXE=$AKRR_APPKER_DIR/execs/ior/src/ior

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/gpfs/scratch/hoffmaps/akrr_project/appker/vortex_bare_metal/execs/libs/hdf5-1.8.21/lib



# set how to run mpirun on all nodes
for node in $AKRR_NODELIST; do echo $node>>all_nodes; done
RUNMPI="mpiexec -n $AKRR_CORES -f all_nodes"

# set how to run mpirun on all nodes with offset, first print all nodes after node 1 and then node 1
sed -n "$(($AKRR_CORES_PER_NODE+1)),$(($AKRR_CORES))p" all_nodes > all_nodes_offset
sed -n "1,$(($AKRR_CORES_PER_NODE))p" all_nodes >> all_nodes_offset
RUNMPI_OFFSET="mpiexec -n $AKRR_CORES -f all_nodes_offset"
"""
```
Now, I just have to make this work through singularity.
Imma guess it aint gonna be as straightforward.
I know I have to take the new ior and use that to make the docker image
So far I basically just put the new ior into the docker image. It's giving me the hdf5 thing not found, I try and fix with adding the thing onto the library path


So that didn't work, instead I just went on vortex and downloaded all the hdf5 libraries to put into the docker container
now however the libimf isn't being found, so maybe I do that one too

Update: i ended up pulling just all the libs to use

