# Setting up AKRR to work with Singularity images on an HPC Resource

During my (Phillip Hoffmann) internship at CCR during the Summer 2019, I worked a bit with running appkernels using singularity on the HPCC resource.

Essentially what we're doing is setting up a regular slurm resource, but then running singularity images instead of the raw binaries.

So all you need to do to set up AKRR is to set up a normal slurm resource, then you just have to modify the config files to use singularity instead of the actual binary.

However, before running any singularity images, you need to get the images onto the resource. Since you will likely have multiple singularity images that you're working with, I recommend having a designated place for them and not using your $HOME as the cache space.

So on the resource:
```bash
# directory where you want your singularity things to be (I put mine as an example)
SINGULARITY_DIR=/gpfs/scratch/hoffmaps/singularity_images 

# these are variables actually used by singularity
export SINGULARITY_LOCALCACHEDIR=$SINGULARITY_DIR
export SINGULARITY_CACHEDIR=$SINGULARITY_DIR
export SINGULARITY_TMPDIR=$SINGULARITY_DIR

# go to the directory and pull down the image
cd $SINGULARITY_DIR

# example pull
singularity pull --docker-login docker://pshoff/akrr_benchmarks:hpcc
```
In the above example, I'm pulling from the Docker hub my hpcc benchmark image. The resulting image file should then be in $SINGULARITY_DIR as akrr_benchmarks_hpcc.sif. If you're pulling from a private repo you need the Docker login to be able to access it.

You can read more about using docker with singularity here: https://www.sylabs.io/guides/3.2/user-guide/singularity_and_docker.html

Note that Docker images might not work flawlessly, because of how Singularity mounts some things automatically, more info here: https://sylabs.io/guides/3.3/user-guide/bind_paths_and_mounts.html?highlight=home

So, once you have the singularity image pulled, you can add the app to akrr the usual way, with akrr app add.

Then you just need to edit the config files. For things to work properly with singularity, you do need to set some things up first. (Note also that the below configs are using my Docker images and runningon one node only):

### HPCC:
```bash
appkernel_run_env_template = """

# wherever the singularity images are saved on the resource
export SINGULARITY_IMAGEDIR="/gpfs/scratch/hoffmaps/singularity_images"

# this allows mpirun to work properly inside the container
# so that it doesn't try and use srun (I believe)
export I_MPI_HYDRA_BOOTSTRAP="ssh" 

# so it can find the mpi libs inside the container
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/appker/lib:/opt/intel/impi/2018.3.222/lib64
# this may or may not be needed, but it can't hurt

# unset this b/c when slurm runs it it has a tmpdir that's not visible to singularity
unset TMPDIR

# set how to run app kernel
# since you may be running on nodes where it won't be as easy to detect the cpu count that you have, its best just to specify it using the -ppn flag for my Docker images.
RUN_APPKERNEL="$SINGULARITY_IMAGEDIR/akrr_benchmarks_hpcc.sif -ppn $AKRR_CORES"
"""
```

### HPCG
```bash
"""
Resource specific HPCG configuration
"""

appkernel_run_env_template = """

# location of the images (can be whatever name you choose)
export SINGULARITY_IMAGEDIR="/gpfs/scratch/hoffmaps/singularity_images"

# some of the apps give problems, since otherwise they would use srun since its a slurm system
export I_MPI_HYDRA_BOOTSTRAP="ssh"

# usually TMPDIR when its set by slurm isn't in the singularity, so this helps singularity find its own temp directory.
unset TMPDIR

#set how to run app kernel
RUN_APPKERNEL="$SINGULARITY_IMAGEDIR/akrr_benchmarks_hpcg.sif -ppn $AKRR_CORES"
"""
```

### NAMD
```bash
appkernel_run_env_template = """

# location of the images (can be whatever name you choose)
export SINGULARITY_IMAGEDIR="/gpfs/scratch/hoffmaps/singularity_images"

# some of the apps give problems, since otherwise they would use srun since its a slurm system
export I_MPI_HYDRA_BOOTSTRAP="ssh"

# usually TMPDIR when its set by slurm isn't in the singularity, so this helps singularity find its own temp directory.
unset TMPDIR

# set how to run app kernel
RUN_APPKERNEL="$SINGULARITY_IMAGEDIR/akrr_benchmarks_namd.sif -ppn $AKRR_CORES"
"""
```

### NWChem
```bash

appkernel_run_env_template = """

# location of the images (can be whatever name you choose)
export SINGULARITY_IMAGEDIR="/gpfs/scratch/hoffmaps/singularity_images"
#
# # some of the apps give problems, since otherwise they would use srun since its a slurm system
export I_MPI_HYDRA_BOOTSTRAP="ssh"
#
# # usually TMPDIR when its set by slurm isn't in the singularity, so this helps singularity find its own temp directory.
unset TMPDIR
#
# may need this to use the proper libs, unsure if needed
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/etc/libibverbs.d

# # set how to run app kernel ( the ppn 8 is temporary, perhaps to change to be general)
RUN_APPKERNEL="$SINGULARITY_IMAGEDIR/akrr_benchmarks_nwchem.sif -ppn $AKRR_CORES"
"""
```

### GAMESS
```bash
appkernel_run_env_template = """

# location of the images (can be whatever name you choose)
export SINGULARITY_IMAGEDIR="/gpfs/scratch/hoffmaps/singularity_images"

#some of the apps give problems, since otherwise they would use srun since its a slurm system
export I_MPI_HYDRA_BOOTSTRAP="ssh"

#usually TMPDIR when its set by slurm isn't in the singularity, so this helps singularity find its own temp directory.
unset TMPDIR

# if you're working with the gamess singularity, you may need to add the following, or some variation
unset SLURM_JOB_ID
# since how the rungms script works

# set how to run app kernel 
RUN_APPKERNEL="$SINGULARITY_IMAGEDIR/akrr_benchmarks_gamess.sif -ppn $AKRR_CORES"
"""
```

IOR and MDTest are a bit different

