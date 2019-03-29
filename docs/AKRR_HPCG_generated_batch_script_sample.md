Sample Output from Running Batch Job Script Generation for HPCG

Command:
```bash
akrr task new --dry-run --gen-batch-job-only -n 2 -r $RESOURCE -a hpcg
```

Output:
```text
DryRun: Should submit following to REST API (POST to scheduled_tasks) {'repeat_in': None, 'app': 'hpcg', 'resource_param': "{'nnodes':2}", 'time_to_start': None, 'resource': 'ub-hpc-skx'}
[INFO] Creating task directory: /home/akrruser/akrr/log/data/ub-hpc-skx/hpcg/2019.03.29.13.34.04.051502
[INFO] Creating task directories: 
        /home/akrruser/akrr/log/data/ub-hpc-skx/hpcg/2019.03.29.13.34.04.051502/jobfiles
        /home/akrruser/akrr/log/data/ub-hpc-skx/hpcg/2019.03.29.13.34.04.051502/proc
[INFO] auto_walltime_limit is on, trying to estimate walltime limit...
[INFO] There are only 0 previous run, need at least 5 for walltime limit autoset
[INFO] Below is content of generated batch job script:
```
```bash
#!/bin/bash
#SBATCH --partition=skylake
#SBATCH --qos=general-compute
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=4
#SBATCH --time=00:30:00
#SBATCH --output=/projects/ccrstaff/general/nikolays/huey_slx/tmp/akrr_data/ub-hpc-skx/hpcg/2019.03.29.13.34.04.051502/stdout
#SBATCH --error=/projects/ccrstaff/general/nikolays/huey_slx/tmp/akrr_data/ub-hpc-skx/hpcg/2019.03.29.13.34.04.051502/stderr


#Common commands
export AKRR_NODES=2
export AKRR_CORES=64
export AKRR_CORES_PER_NODE=32
export AKRR_NETWORK_SCRATCH="/projects/ccrstaff/general/nikolays/huey_slx/tmp"
export AKRR_LOCAL_SCRATCH="/tmp"
export AKRR_TASK_WORKDIR="/projects/ccrstaff/general/nikolays/huey_slx/tmp/akrr_data/ub-hpc-skx/hpcg/2019.03.29.13.34.04.051502"
export AKRR_APPKER_DIR="/projects/ccrstaff/general/nikolays/huey_slx/appker"
export AKRR_AKRR_DIR="/projects/ccrstaff/general/nikolays/huey_slx/tmp/akrr_data/ub-hpc-skx"

export AKRR_APPKER_NAME="hpcg"
export AKRR_RESOURCE_NAME="ub-hpc-skx"
export AKRR_TIMESTAMP="2019.03.29.13.34.04.051502"
export AKRR_APP_STDOUT_FILE="$AKRR_TASK_WORKDIR/appstdout"

export AKRR_APPKERNEL_INPUT="/projects/ccrstaff/general/nikolays/huey_slx/appker/inputs/hpcg/hpcg.dat"
export AKRR_APPKERNEL_EXECUTABLE="/projects/ccrstaff/general/nikolays/huey_slx/appker/execs"

source "$AKRR_APPKER_DIR/execs/bin/akrr_util.bash"

#Populate list of nodes per MPI process
export AKRR_NODELIST=`srun -l --ntasks-per-node=$AKRR_CORES_PER_NODE -n $AKRR_CORES hostname -s|sort -n| awk '{printf "%s ",$2}' `

export PATH="$AKRR_APPKER_DIR/execs/bin:$PATH"

cd "$AKRR_TASK_WORKDIR"

#run common tests
akrr_perform_common_tests

#Write some info to gen.info, JSON-Like file
akrr_write_to_gen_info "start_time" "`date`"
akrr_write_to_gen_info "node_list" "$AKRR_NODELIST"


# Create working dir
export AKRR_TMP_WORKDIR=`mktemp -d /projects/ccrstaff/general/nikolays/huey_slx/tmp/ak.XXXXXXXXX`
echo "Temporary working directory: $AKRR_TMP_WORKDIR"
cd $AKRR_TMP_WORKDIR

# Copy inputs
cp /projects/ccrstaff/general/nikolays/huey_slx/appker/inputs/hpcg/hpcg.dat ./hpcg.dat

ulimit -s unlimited



# Load application environment
module load intel/18.3
module load intel-mpi/2018.3
module load mkl/2018.3
module list

# set executable location
EXE=$MKLROOT/benchmarks/hpcg/bin/xhpcg_skx
# EXE=$AKRR_APPKER_DIR/execs/hpcg-HPCG-release-3-0-0/build/bin/xhpcg

# Set how to run app kernel
export OMP_NUM_THREADS=1
RUN_APPKERNEL="mpirun $EXE"


#Generate AppKer signature
appsigcheck.sh $EXE $AKRR_TASK_WORKDIR/.. > $AKRR_APP_STDOUT_FILE


#Execute AppKer
akrr_write_to_gen_info "appkernel_start_time" "`date`"
$RUN_APPKERNEL >> $AKRR_APP_STDOUT_FILE 2>&1
akrr_write_to_gen_info "appkernel_end_time" "`date`"




akrr_write_to_gen_info "cpu_speed" "`grep 'cpu MHz' /proc/cpuinfo`"

# cat results to AKRR_APP_STDOUT_FILE
for f in *.yaml
do
    echo "====== $f Start ======"  >> $AKRR_APP_STDOUT_FILE 2>&1
    cat $f  >> $AKRR_APP_STDOUT_FILE 2>&1
    echo "====== $f End   ======" >> $AKRR_APP_STDOUT_FILE 2>&1
done
for f in *.txt
do
    echo "====== $f Start ======"  >> $AKRR_APP_STDOUT_FILE 2>&1
    cat $f  >> $AKRR_APP_STDOUT_FILE 2>&1
    echo "====== $f End   ======" >> $AKRR_APP_STDOUT_FILE 2>&1
done

cd $AKRR_TASK_WORKDIR

# Clean-up
if [ "${AKRR_DEBUG=no}" = "no" ]
then
        echo "Deleting temporary files"
        rm -rf $AKRR_TMP_WORKDIR
else
        echo "Copying temporary files"
        cp -r $AKRR_TMP_WORKDIR workdir
        rm -rf $AKRR_TMP_WORKDIR
fi



akrr_write_to_gen_info "end_time" "`date`"
```
```text
[INFO] Removing generated files from file-system as only batch job script printing was requested
```
