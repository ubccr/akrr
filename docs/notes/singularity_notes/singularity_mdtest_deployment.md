### Notes on deployment for mdtest on singularity

So a lot of these notes are sorta all over the place, but here is the app conf that ended up working:

```bash
ppkernel_run_env_template = """
# Load application enviroment
#module load intel 
module load intel-mpi
module list

export I_MPI_PMI_LIBRARY=/usr/lib64/libpmi.so.3
#export I_MPI_FABRICS_LIST="tcp"

# increase verbosity of mdtest output
#export MDTEST_VERBOSE = "-v"

# setup the library paths for the singularity image
export LD_LIBRARY_PATH="/opt/appker/lib:/opt/intel/impi/2018.3.222/lib64:$LD_LIBRARY_PATH"
export PATH="$PATH:$LD_LIBRARY_PATH"

EXE=/gpfs/scratch/hoffmaps/singularity_images/akrr_benchmarks_mdtest_barebones02.sif
unset TMPDIR
$EXE --appsigcheck >> $AKRR_APP_STDOUT_FILE 2>&1

# setup singularity to run appropriately
EXE="$EXE --mdtest-run"

# set how to run app kernel
RUNMPI="mpirun"
"""
```
So in theory you already pulled the mdtest_barebones02 into the appropriate directory and can then run it.
Only issue really: it took a bit more than 5 minutes, will run it bare metal to see if there is a difference




