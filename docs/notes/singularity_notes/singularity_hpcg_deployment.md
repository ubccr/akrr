## Notes on deploying hpcg on singularity

Similar to hpcc deployment

(on resource, in this case huey)
Set up cache directories
```bash
SINGULARITY_LOCALCACHEDIR=/gpfs/scratch/hoffmaps/singularity_images
SINGULARITY_CACHEDIR=/gpfs/scratch/hoffmaps/singularity_images
SINGULARITY_TMPDIR=/gpfs/scratch/hoffmaps/singularity_images

export SINGULARITY_LOCALCACHEDIR
export SINGULARITY_CACHEDIR
export SINGULARITY_TMPDIR

cd $SINGULARITY_CACHEDIR
singularity pull --docker-login docker://pshoff/akrr_benchmarks:hpcg
```

Now back where akrr is:
```bash
export RESOURCE=test_huey
export APPKER=hpcg

# adding the resource to akrr
akrr app add -a $APPKER -r $RESOURCE

#Output:
[INFO] Generating application kernel configuration for hpcg on test_huey
[INFO] Application kernel configuration for hpcg on test_huey is in: 
        /home/hoffmaps/projects/akrr/etc/resources/test_huey/hpcg.app.conf

```
Initial hpcg.app.conf
```bash
"""
Resource specific HPCG configuration
"""

appkernel_run_env_template = """
# Load application environment
module load intel
module load intel-mpi
module load mkl
module list

# set executable location
EXE=$MKLROOT/benchmarks/hpcg/bin/xhpcg_avx

# Set how to run app kernel
export OMP_NUM_THREADS=1
RUN_APPKERNEL="mpirun $EXE"
"""
```
Taking our example from the hpcc setup, change it to something like this:

```bash
appkernel_run_env_template = """

export SINGULARITY_IMAGEDIR="/gpfs/scratch/hoffmaps/singularity_images"
export I_MPI_HYDRA_BOOTSTRAP="ssh"
unset TMPDIR

# set how to run app kernel ( the ppn 8 is temporary, perhaps to change to be general)
RUN_APPKERNEL="$SINGULARITY_IMAGEDIR/akrr_benchmarks_hpcg.sif -ppn 8"
"""
```
Remember that on huey we want the proper image at the proper path location

Then we do the standard 
```bash
akrr app validate -n 1 -a $APPKER -r $RESOURCE
```
Errors we're getting
- permission denied on appsigcheck
	- easy fix, make sure to chmod the execs dir to be 755 before you build docker image
- the cpus don't support avx instructions.... oof
	- This is probably bc the cpus on huey are really old, so they probably just cant do avx, meaning we can't really do hpcg on it... on to other things!

- Update: we'll maybe try things on preprod and on the gpu node, STAY TUNED
- Looks like on the gpu the whole avx thing would work, so we would just need to modify the job file so that it requests the gpu node



