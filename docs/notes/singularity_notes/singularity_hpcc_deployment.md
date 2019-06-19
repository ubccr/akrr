## Notes on getting hpcc working on huey with singularity

The site where it describes how to use a docker image with singularity is here: https://www.sylabs.io/guides/3.2/user-guide/singularity_and_docker.html

It does talk about a cache directory that singularity uses, and I decided to make my own so that the default home directory isn't used. I put it here:

```bash
SINGULARITY_CACHEDIR=/gpfs/scratch/hoffmaps/singularity_cache
```
So that declaration should probably come before any sort of singularity work


Okay, so now lets look into deployment. It'll be a mix between Openstack and regular deployment
```bash
export RESOURCE=test_huey
export APPKER=hpcc

# adding the resource to akrr
akrr app add -a $APPKER -r $RESOURCE
```
Output:
```bash
[INFO] Generating application kernel configuration for hpcc on test_huey
[INFO] Application kernel configuration for hpcc on test_huey is in: 
        /home/hoffmaps/projects/akrr/etc/resources/test_huey/hpcc.app.conf

```
Initial hpcc.app.conf
```bash

appkernel_run_env_template = """
# Load application environment
module load intel
module load intel-mpi
module load mkl
module list

# make srun works with intel mpi
export I_MPI_PMI_LIBRARY=/usr/lib64/libpmi.so

# set how to run app kernel
RUN_APPKERNEL="srun {appkernel_dir}/{executable}"
"""

```

Like before, we mainly just care about the RUN_APPKERNEL since its all self contained
So lets change it so that it get the singularity container and runs it (don't forget to set the SINGULARITY_CACHEDIR
```bash
export SINGULARITY_CACHEDIR=/gpfs/scratch/hoffmaps/singularity_cache

RUN_APPKERNEL=<TBD> (see below)
```
Update: messing around a bit with singularity containers on huey, looks like if I get the container on the node its fine, but not if its just on the regular thing

So trying to run the singularity containers, was getting an error that said that singularity doesn't know about the whole workdir thing of docker, so we should use absolute paths in the dockerfile thing. The issue was discussed here: https://github.com/sylabs/singularity/issues/380
So Imma change the dockerfile real quick so that the entrypoint script is an absolute path.

Recommendation: have all the docker images and whatnot already pulled down so that you don't need to waste time getting them set up.

+++++++ CHECK THIS
So, I also need to change the run script for things, since the number of cores doesn't really help/isn't an accurate representation of the number of processes we need. FOR NOW, I think we'll rely on the flags for the run, setting -ppn to the appropriate number locally
*This may need to be changed in the future, unsure of the correct path to take
+++++++

So now our hpcc.app.conf looks like this:
```bash
appkernel_run_env_template = """
export SINGULARITY_CACHEDIR="/gpfs/scratch/hoffmaps/singularity_cache"

# set how to run app kernel (the ppn 8 is temporary just to get it to work, to be changed in future)
RUN_APPKERNEL="singularity run $SINGULARITY_CACHEDIR/akrr_benchmarks_hpcc.sif -ppn 8"
"""
```
Again, this is assuming we did the following on huey (or similar)
```bash
export SINGULARITY_CACHEDIR=/gpfs/scratch/hoffmaps/singularity_cache
cd $SINGULARITY_CACHEDIR
singularity pull --docker-login docker://pshoff/akrr_benchmarks:hpcc 

```
And entered the proper password and such to get the sif file

Now let's try validation run 
```bash
akrr app validate -n 1 -r test_huey -a hpcc


```
Okay this right now gives a bunch of errors. If I set it up normally on huey and just do the regular run there, it seems to go fine, but when I try and do the validation run, it doesn't work. Here's what the weird output is:

```bash
===ExeBinSignature=== ERROR: /gpfs/scratch/hoffmaps/akrr_project/execs/hpcc/hpcc is not an executable binary file
hpcc_inputs_dir: /usr/local/appker/inputs/hpcc
Number of cores detected: 4
nodes: 1
ppn: 8
interactive: false
Testing entry: 1
Entry is valid
Testing entry: 8
Entry is valid
Input file name: hpccinf.txt.8x1
Full path: /usr/local/appker/inputs/hpcc/hpccinf.txt.8x1
Destination path: /user/hoffmaps/hpccinf.txt
hpccinf.txt.8x1 copied over to /user/hoffmaps/hpccinf.txt
work dir: /user/hoffmaps
Running appsigcheck...
mktemp: failed to create file via template ‘/scratch/12434/tmp.XXXXXXXXXX’: No such file or directory
objcopy: warning: could not create temporary file whilst copying '/opt/appker/execs/hpcc-1.5.0/hpcc', (error: Read-only file system)
===ExeBinSignature=== MD5: Unable to run objcopy
mktemp: failed to create file via template ‘/scratch/12434/tmp.XXXXXXXXXX’: No such file or directory
objcopy: warning: could not create temporary file whilst copying '/lib64/libpthread.so.0', (error: Read-only file system)
===ExeBinSignature=== MD5: Unable to run objcopy
mktemp: failed to create file via template ‘/scratch/12434/tmp.XXXXXXXXXX’: No such file or directory
objcopy: warning: could not create temporary file whilst copying '/lib64/libm.so.6', (error: Read-only file system)
===ExeBinSignature=== MD5: Unable to run objcopy
mktemp: failed to create file via template ‘/scratch/12434/tmp.XXXXXXXXXX’: No such file or directory
===ExeBinSignature=== MD5: not is not an executable binary file
mktemp: failed to create file via template ‘/scratch/12434/tmp.XXXXXXXXXX’: No such file or directory
===ExeBinSignature=== MD5: not is not an executable binary file
mktemp: failed to create file via template ‘/scratch/12434/tmp.XXXXXXXXXX’: No such file or directory
objcopy: warning: could not create temporary file whilst copying '/lib64/libdl.so.2', (error: Read-only file system)
===ExeBinSignature=== MD5: Unable to run objcopy
mktemp: failed to create file via template ‘/scratch/12434/tmp.XXXXXXXXXX’: No such file or directory
objcopy: warning: could not create temporary file whilst copying '/lib64/librt.so.1', (error: Read-only file system)
===ExeBinSignature=== MD5: Unable to run objcopy
mktemp: failed to create file via template ‘/scratch/12434/tmp.XXXXXXXXXX’: No such file or directory
objcopy: warning: could not create temporary file whilst copying '/lib64/libgcc_s.so.1', (error: Read-only file system)
===ExeBinSignature=== MD5: Unable to run objcopy
mktemp: failed to create file via template ‘/scratch/12434/tmp.XXXXXXXXXX’: No such file or directory
objcopy: warning: could not create temporary file whilst copying '/lib64/libc.so.6', (error: Read-only file system)
===ExeBinSignature=== MD5: Unable to run objcopy
Running hpcc...
[mpiexec@cpn-d13-17.int.ccr.buffalo.edu] HYDU_create_process (../../utils/launch/launch.c:825): execvp error on file /usr/bin/srun (No such file or directory)
```
A couple weird things about this
	- MD5 can't run objcopy
	- There's something weird going on with the creation of a scratch directory, perhaps that's something to look at with the general template
	- Something strange is happening with mpiexec, though that should be happening in the singularity...??
	- It seems like there's something wrong with the environment variables, since its trying to copy things into /home/hoffmaps instead of /home/hpccuser like it does in Docker.
I'll look into these tomorrow

- So, it appears maybe things went wrong bc in singularity everything is root? so now just trying to run docker as if everythig is root..

- Okay so I found here: https://singularity.lbl.gov/docs-docker#troubleshooting that we shouldn't be doing anything with $HOME because that gets mounted as my home and not the home that I want (aka hpccuser home) so imma change that in the dockerfile so now instead of $HOME it'll be /home/hpccuser

- So things are sorta weird with how singularity deals with users....
- It runs the singularity as whatever user it is, but we want to run as hpccuser in the container, so I'm trying to change things up so that I run as hpccuser

- Update: so we want to set up the docker so that its able to run as any user so that we don't have to worry about switching users or anything like that

- Updated permissions so now more or less everything we would use has overarching permissions

- The objcopy issue happens when trying to run appsigcheck
- The mpiexec error happens when actually trying to execute hpcc

Also changed app conf to be this now, the cache directory thing isn't really that important
```bash
appkernel_run_env_template = """
export SINGULARITY_IMAGEDIR="/gpfs/scratch/hoffmaps/singularity_images"

# set how to run app kernel ( the ppn 8 is temporary, perhaps to change to be general)
RUN_APPKERNEL="$SINGULARITY_IMAGEDIR/akrr_benchmarks_hpcc.sif -ppn 8"
"""
```

### Trying to fix the objcopy issue:
- First I'm trying to change the permissions on the files to be 777 so everything should be readable and writable
	- Yeah that wasn't the issue. Turns out with singularity, everything enters in read only mode by default (see: http://singularity.lbl.gov/archive/docs/v2-2/create-image#read-only-vs-read-write) so now I'm setting the writable flag
	- That also didn't work..... unsure what's going on
	- The weirdest thing is that it seems to work fine if I'm just running the image in the terminal

- UPDATE: So Ben helped me a whole bunch. There was the error with the md5sum2 that just gave a bunch of weird stuff, saying it couldn't make the temp directory and stuff like that. The singularity thing ran fine when I sshed into the node and ran it, but it didn't work when I did sbatch. Turns out the problem happens with sbatch bc it sets the environment TMPDIR to be /scratch/[jobid] whereas with the salloc stuff TMPDIR wasn't set. So at the beginning of the job I just did unset TMPDIR and the md5sum2 thing worked fine/as expected












