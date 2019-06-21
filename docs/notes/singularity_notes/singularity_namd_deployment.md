## notes on deploying namd with singularity

Seems to work okay with the test script I've done

On resource
```bash
SINGULARITY_LOCALCACHEDIR=/gpfs/scratch/hoffmaps/singularity_images
SINGULARITY_CACHEDIR=/gpfs/scratch/hoffmaps/singularity_images
SINGULARITY_TMPDIR=/gpfs/scratch/hoffmaps/singularity_images

export SINGULARITY_LOCALCACHEDIR
export SINGULARITY_CACHEDIR
export SINGULARITY_TMPDIR

cd $SINGULARITY_CACHEDIR
singularity pull --docker-login docker://pshoff/akrr_benchmarks:namd


```
Now where you have akrr

```bash
export RESOURCE=test_huey
export APPKER=namd

# adding the resource to akrr
akrr app add -a $APPKER -r $RESOURCE

#Output:
[INFO] Generating application kernel configuration for namd on test_huey
[INFO] Application kernel configuration for namd on test_huey is in: 
        /home/hoffmaps/projects/akrr/etc/resources/test_huey/namd.app.conf


```
Initial namd.app.conf
```bash
appkernel_run_env_template = """
#Load application environment
module load namd
export CONV_RSH=ssh

#set executable location
EXE=`which namd2`
charmrun_bin=`which charmrun`

#prepare nodelist for charmmrun
for n in $AKRR_NODELIST; do echo host $n>>nodelist; done

#set how to run app kernel
RUN_APPKERNEL="$charmrun_bin  +p$AKRR_CORES ++nodelist nodelist $EXE ./input.namd"
"""

```
Change it to set it up for singularity (based on hpcc template sorta)
New namd.app.conf
```bash
appkernel_run_env_template = """

export SINGULARITY_IMAGEDIR="/gpfs/scratch/hoffmaps/singularity_images"
export I_MPI_HYDRA_BOOTSTRAP="ssh"
unset TMPDIR

# set how to run app kernel ( the ppn 8 is temporary, perhaps to change to be general)
RUN_APPKERNEL="$SINGULARITY_IMAGEDIR/akrr_benchmarks_namd.sif -ppn 8"
"""
```

Then we do the standard
```bash
akrr app validate -n 1 -a $APPKER -r $RESOURCE
```






