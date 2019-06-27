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



