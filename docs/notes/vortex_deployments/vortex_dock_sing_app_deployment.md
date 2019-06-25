## Deployment of apps using singularity images on vortex

Deployment of the singularity images all follow the same basic format

Let's first declare some general variables to be used throughout (both on resource and locally)
```bash
export RESOURCE=<resource_name>
export APPKER=<app_to_use>
# ex: hpcc, namd, hpcg, gamess, nwchem
```

## Setting up on the resource

Set up cache directories for singularity files on the resource

```bash
SINGULARITY_LOCALCACHEDIR=/gpfs/scratch/hoffmaps/singularity_images
SINGULARITY_CACHEDIR=/gpfs/scratch/hoffmaps/singularity_images
SINGULARITY_TMPDIR=/gpfs/scratch/hoffmaps/singularity_images

export SINGULARITY_LOCALCACHEDIR
export SINGULARITY_CACHEDIR
export SINGULARITY_TMPDIR

cd $SINGULARITY_CACHEDIR
```
They can be different, but in this case I'm pulling the images into SINGULARITY_CACHEDIR

```bash
# pull image down. May need docker login if its a private repo
singularity pull --docker-login docker://pshoff/akrr_benchmarks:$APPKER

# this generally results in the image akrr_benchmarks_$APPKER
```
## Setting up config files on akrr machine
Now on the akrr machine you can add the app
```bash
akrr app add -a $APPKER -r $RESOURCE
```
Sample output (using hpcc)
```bash
[INFO] Generating application kernel configuration for hpcc on vortex_dock_sing
[INFO] Application kernel configuration for hpcc on vortex_dock_sing is in: 
        /home/hoffmaps/projects/akrr/etc/resources/vortex_dock_sing/hpcc.app.conf
```
Initial hpcc.app.conf:
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
The look of this will change depending on what app you added, but for singularity it will look similar across all apps. Something like this should be fine.
```bash
appkernel_run_env_template = """

# location of the images (can be whatever name you choose)
export SINGULARITY_IMAGEDIR="/gpfs/scratch/hoffmaps/singularity_images"

# some of the apps give problems, since otherwise they would use srun since its a slurm system
export I_MPI_HYDRA_BOOTSTRAP="ssh"

# usually TMPDIR when its set by slurm isn't in the singularity, so this helps singularity find its own temp directory.
unset TMPDIR

# if you're working with the gamess singularity, you may need to add the following, or some variation
# unset SLURM_JOB_ID

# set how to run app kernel ( the ppn 8 is temporary, perhaps to change to be general)
RUN_APPKERNEL="$SINGULARITY_IMAGEDIR/akrr_benchmarks_hpcc.sif -ppn 8"
"""
```
Again, this is an example, and the RUN_APPKERNEL should be modified just to run the singularity executable and send in any arguments it might need, the -ppn 8 is because I'm focusing on 8 cores per node

After editing the config file, you can try doing dry run stuff if you want, but you can go right to validation too.
```bash
akrr app validate -n 1 -a $APPKER -r $RESOURCE
```
You may want to check on the job by sshing into the node and topping to see if things are running properly, but it should be fine, you can always analyze the output.
You can check out some of the validation examples to get a feel for what they look like.

After validation, you can start to have regularly scheduled executions with akrr task
```bash
COMING SOON....
```












