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


```
Update: messing around a bit with singularity containers on huey, looks like if I get the container on the node its fine, but not if its just on the regular thing

So trying to run the singularity containers, was getting an error that said that singularity doesn't know about the whole workdir thing of docker, so we should use absolute paths in the dockerfile thing. The issue was discussed here: https://github.com/sylabs/singularity/issues/380
So Imma change the dockerfile real quick so that the entrypoint script is an absolute path.













