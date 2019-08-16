## Making a docker for the ior test

Unsure if this is possible, but lets see if we can make a docker for the ior tests...
Running the bare metal thing for ior and mdtest both went through validation, but honestly I'm not exactly sure if they're doing things correctly.
Assuming that they are, I'm gonna base it on that and see if I can't figure out how to make it work

So I did everything in ior deployment to install ior
Then I took the resulting directory and tarred it, and downloaded it onto my local machine.
I'm gonna then put it in the docker

So I set up a very barebones docker that just has the ior on it, and then that goes in place of the executable. Literally all I'm doing is replacing the EXE part of the config with the ior image, which has as its entrypoint the ior executable.

I'm not sure if any of this works on local machine bc I don't know how the whole nodelist thing would work, so I'm just trying to run it on vortex

Anyways, error I'm getting
```bash
/opt/appker/execs/ior/src/ior: error while loading shared libraries: libgpfs.so: cannot open shared object file: No such file or directory
```
Tried running just regular ior, and it worked fine, so I'm guessing its an issue inside singularity and its file system.
So far I just went to where they had the lib on vortex and downloaded it, then did
```bash
export LD_LIBRARY_PATH=`pwd` # where the lib was
```
And that gave the error
```bash
./ior: error while loading shared libraries: libgpfs.so: wrong ELF class: ELFCLASS32
```
Could be bc I downloaded the wrong one? I'm gonna try and get the one from lib64

Okay the new one works, but now I'm getting another missing library. So I'm just gonna try and get all of them from vortex and list them here
```bash
libgpfs.so # got from vortex

# in mpi libraries: /opt/intel/impi/2018.3.222/lib64
libmpifort.so.12 
# so I just added it to the LD_LIBRARY_PATH
```
When running the docker locally it didn't give any errors, so now I'll try running it on vortex

So ran it on vortex, turns out when you load the intel-mpi, it overwrites LD\_LIBRARY\_PATH, so maybe try to include it in the run script?

So in run script add
```bash
export LD_LIBRARY_PATH=/opt/appker/lib:/opt/intel/impi/2018.3.222/lib64:$LD_LIBRARY_PATH
```
Doing this before running the mpirun thing seems to make it run okay, at least in the testing phase

Now we get to the runmpi part. Doing the thing with the nodelist and stuff kept giving this error
```bash
# new text 
RUNMPI="mpiexec -n $AKRR_CORES"
$RUNMPI $EXE -vv
```
Also if I changed the nodes in all\_nodes to be the nodes I was actually on, it worked fine without errors - perhaps we can use SLURM\_JOB\_NODELIST to do this?
However that may have been a problem with the interactive session itself...? I'm not sure.
So if we just run it by adding the Library path thing (not worrying about nodelist) the validation works with the barebones singularity image

So validation cleared with ior\_barebones

Update: setting up a script so that it does appsigcheck too.
I want to do it with arguments, bc otherwise it'll run like 3 appsigchecks, so I'm gonna parse arguments, if its one argument then it does the check, with the other one it does the run

Okay, it works, only thing is that in appstdout it doesn't have the signature bc a little bit further down the job file it pipes the result of check into the out file with > instead of >> so it gets overwritten...
Perhaps need to change this? But right now barebones works okay it seems, or at least no different.

Finally was able to find where the > was: it was in default_conf/default.resource.conf.
So I changed it there, and I also did the standard unset TMPDIR in the ior.app.conf
So now the ior.app.conf looks like:
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
module load intel
module load intel-mpi
module list

# set executable location
EXE="/gpfs/scratch/hoffmaps/singularity_images/akrr_benchmarks_ior_barebones02.sif"

# setting things up to use the singularity image
export LD_LIBRARY_PATH=/opt/appker/lib:/opt/intel/impi/2018.3.222/lib64:$LD_LIBRARY_PATH
unset TMPDIR
$EXE --appsigcheck >> $AKRR_APP_STDOUT_FILE 2>&1
EXE="$EXE --ior-run"

# set how to run mpi on nodes
for node in $AKRR_NODELIST; do echo $node>>all_nodes; done
RUNMPI="mpiexec -n $AKRR_CORES -f all_nodes"

# set how to run mpirun on all nodes with offset, first print all nodes after node 1 and then node 1
sed -n "$(($AKRR_CORES_PER_NODE+1)),$(($AKRR_CORES))p" all_nodes > all_nodes_offset
sed -n "1,$(($AKRR_CORES_PER_NODE))p" all_nodes >> all_nodes_offset
RUNMPI_OFFSET="mpiexec -n $AKRR_CORES -f all_nodes_offset"
"""
```
Note the section to set up for singularity. 
Right now ior_barebones02 is the one to use, ior_barebones doesn't have the appsigcheck built in yet


## Trying to get it working with openstack.
Due to the nature of the resulting ior.job file, it seems the best strategy would be to just have the script run the executable and have all the arguments passed in to it, so that $EXE is the docker run command, and the mpi stuff is just nothing

Also looks like we need to change appkernel_requests_two_nodes_for_one to false to have this thing get run as only one node

Errors I ran into
- mpiexec not found -> fix by just doing absolute path in the script
- no such file or directory with the temporary file and such that is sent over
	- since it is using $AKRR_TMP_WORKDIR to do its thing, which of course doesnt exist in docker
	- potential solution: mount the volume somehow with -v /path:/path/in/container (done in the conf part)

- There was some error that I couldn't find the script? They talked about it here: https://github.com/moby/moby/issues/9066 maybe it has something to do with line-ending problem something? Not sure, but I removed some of the extra lines in the files and now it works again..? Anyways back to the -v flag.
- Update nope we still get the error sometimes


According to https://docs.docker.com/storage/bind-mounts/ the -v flag makes the things as a directory, so really I just need to link $AKRR_TMP_WORKDIR  to $AKRR_TMP_WORKDIR in theory

- Okay so now we are getting an error standard_init_linux.go:207: exec user process caused "no such file or directory"
- so some sort of file or directory is going haywire..? in theory the -v flag should be creating the things...
	- Actually this maybe is another one of the line endings issues...? see: https://forums.docker.com/t/standard-init-linux-go-175-exec-user-process-caused-no-such-file/20025/5
	- Unsure though bc they're saying it has to do with windows somehow? I don't know

UPDATE: So i kept getting this file directory error or whatever, so I just said alright I'm just going to rewrite the entire dockerfile line by line to see what is causing it, and I did (with slight differences) and now it works so I have no clue what the issue is, but I won't touch it now.


Update: now working with hdf5 and netcdf on openstack (i believe), basically I just re-built the ior on vortex with the right configs (according to the ior deployment) and then got all the libraries I needed into the lib folder here. I rebuilt the dockerfile and modified the config file to use the new docker and then set the things to test to be true for hdf5 and it put me through validation so wooo






