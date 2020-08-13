## Notes on deploying gamess on singularity
Similar to other deployments

(on resource) set up cache directories
```bash
SINGULARITY_LOCALCACHEDIR=/gpfs/scratch/hoffmaps/singularity_images
SINGULARITY_CACHEDIR=/gpfs/scratch/hoffmaps/singularity_images
SINGULARITY_TMPDIR=/gpfs/scratch/hoffmaps/singularity_images

export SINGULARITY_LOCALCACHEDIR
export SINGULARITY_CACHEDIR
export SINGULARITY_TMPDIR

cd $SINGULARITY_CACHEDIR

singularity pull --docker-login docker://pshoff/akrr_benchmarks:gamess

```
Back where akrr is:

```bash
export RESOURCE=test_huey
export APPKER=gamess

# adding the resource to akrr
akrr app add -a $APPKER -r $RESOURCE

#Output 
[INFO] Generating application kernel configuration for gamess on test_huey
[INFO] Application kernel configuration for gamess on test_huey is in: 
        /home/hoffmaps/projects/akrr/etc/resources/test_huey/gamess.app.conf
```
Initial gamess.app.conf
```bash
appkernel_run_env_template = """
# Load application enviroment
module load gamess
module list

# set executable location
VERNO=01
EXE=$GAMESS_DIR/gamess.$VERNO.x

# set how to run app kernel
RUN_APPKERNEL="$AKRR_APPKER_DIR/execs/gamess/rungms $INPUT $VERNO $AKRR_NODES $AKRR_CORES_PER_NODE"
"""
```

Taking our example from the hpcc setup, change it to something like this
(Note: SINGULARITY_IMAGEDIR is wherever your singularity images are, in our case the same as the Singularity Cachedir)

```bash
appkernel_run_env_template = """

export SINGULARITY_IMAGEDIR="/gpfs/scratch/hoffmaps/singularity_images"
export I_MPI_HYDRA_BOOTSTRAP="ssh"
unset TMPDIR

# added to deal with temporary working directory error
#export SLURMTMPDIR="$AKRR_TMP_WORKDIR"
unset SLURM_JOB_ID

# set how to run app kernel ( the ppn 8 is temporary, perhaps to change to be general)
RUN_APPKERNEL="$SINGULARITY_IMAGEDIR/akrr_benchmarks_gamess.sif -ppn 8"
"""

```
Then we do the standard
```bash
akrr app validate -n 1 -a $APPKER -r $RESOURCE

```
Error's we're getting:
- permission denied on appsigcheck - that's just changing permissions on the files locally before copying them into the docker
- can't crea a file for scratch directory, was tmpdir set or something?
	- yeah looks like it looks for the SLURMTMPDIR to be the scratch, so probably want to just set that to the temp directory that we're using
	- seems like best option is doing SLURMTMPDIR=$AKRR_TMP_WORKDIR

- So gamess uses srun to start all of its processes...
	- So that's bc it sets the sched to be slurm, based on the existence of SLURM_JOB_ID, so the strat is to unset it and see what happens

- Unsetting the id didn't appear to have any negative repercussions (at least it didn't give any errors in the validation run)


