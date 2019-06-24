## Notes on deployment of nwchem singularity on resource

Like before

(On resource)

```bash
SINGULARITY_LOCALCACHEDIR=/gpfs/scratch/hoffmaps/singularity_images
SINGULARITY_CACHEDIR=/gpfs/scratch/hoffmaps/singularity_images
SINGULARITY_TMPDIR=/gpfs/scratch/hoffmaps/singularity_images

export SINGULARITY_LOCALCACHEDIR
export SINGULARITY_CACHEDIR
export SINGULARITY_TMPDIR

cd $SINGULARITY_CACHEDIR

singularity pull --docker-login docker://pshoff/akrr_benchmarks:nwchem
```
Now back to akrr
```bash
export RESOURCE=test_huey
export APPKER=nwchem

# adding the resource to akrr
akrr app add -a $APPKER -r $RESOURCE

#Output
[INFO] Generating application kernel configuration for nwchem on test_huey
[INFO] Application kernel configuration for nwchem on test_huey is in: 
        /home/hoffmaps/projects/akrr/etc/resources/test_huey/nwchem.app.conf
```

Initial nwchem.app.conf
```bash
appkernel_run_env_template = """
# Load application environment
module load nwchem
module list

# make srun works with intel mpi
export I_MPI_PMI_LIBRARY=/usr/lib64/libpmi.so

# set executable location
EXE=`which nwchem`

#set how to run app kernel
RUN_APPKERNEL="srun --mpi=pmi2 $EXE $INPUT"
"""
```
Taking our example from previous setup, change it to something like this (SINGULARITY_IMAGEDIR should probably be the same as SINGULARITY_CACHEDIR as above)
```bash
appkernel_run_env_template = """

export SINGULARITY_IMAGEDIR="/gpfs/scratch/hoffmaps/singularity_images"
export I_MPI_HYDRA_BOOTSTRAP="ssh"
unset TMPDIR

# set how to run app kernel ( the ppn 8 is temporary, perhaps to change to be general)
RUN_APPKERNEL="$SINGULARITY_IMAGEDIR/akrr_benchmarks_nwchem.sif -ppn 8"
"""


```

Then we do the standard
```bash
akrr app validate -n 1 -a $APPKER -r $RESOURCE

```
Appears to work fine, maybe some errors with logging..?












