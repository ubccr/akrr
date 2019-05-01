#!/bin/bash
#SBATCH --partition=general-compute 
#SBATCH --qos=general-compute
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=8
#SBATCH --time=00:30:00
#SBATCH --output=/projects/ccrstaff/general/nikolays/huey/akrr_data/mdtest/2019.05.01.19.34.55.693745/stdout
#SBATCH --error=/projects/ccrstaff/general/nikolays/huey/akrr_data/mdtest/2019.05.01.19.34.55.693745/stderr
#SBATCH --constraint="CPU-L5520"
#SBATCH --exclusive


#Common commands
export AKRR_NODES=2
export AKRR_CORES=16
export AKRR_CORES_PER_NODE=8
export AKRR_NETWORK_SCRATCH="/projects/ccrstaff/general/nikolays/huey/tmp"
export AKRR_LOCAL_SCRATCH="/tmp"
export AKRR_TASK_WORKDIR="/projects/ccrstaff/general/nikolays/huey/akrr_data/mdtest/2019.05.01.19.34.55.693745"
export AKRR_APPKER_DIR="/projects/ccrstaff/general/nikolays/huey/appker"
export AKRR_AKRR_DIR="/projects/ccrstaff/general/nikolays/huey/akrr_data"

export AKRR_APPKER_NAME="mdtest"
export AKRR_RESOURCE_NAME="ub-hpc"
export AKRR_TIMESTAMP="2019.05.01.19.34.55.693745"
export AKRR_APP_STDOUT_FILE="$AKRR_TASK_WORKDIR/appstdout"

export AKRR_APPKERNEL_INPUT="/projects/ccrstaff/general/nikolays/huey/appker/inputs"
export AKRR_APPKERNEL_EXECUTABLE="/projects/ccrstaff/general/nikolays/huey/appker/execs"

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


#create working dir
export AKRR_TMP_WORKDIR=`mktemp -d /projects/ccrstaff/general/nikolays/huey/tmp/namd.XXXXXXXXX`
echo "Temporary working directory: $AKRR_TMP_WORKDIR"
cd $AKRR_TMP_WORKDIR

case $AKRR_NODES in
1)
    ITER=20
    ;;
2)
    ITER=10
    ;;
4)
    ITER=5
    ;;
8)
    ITER=2
    ;;
*)
    ITER=1
    ;;
esac




# Load application enviroment
module load intel/18.3 intel-mpi/18.3
module list

export I_MPI_PMI_LIBRARY=/usr/lib64/libpmi.so
export I_MPI_FABRICS_LIST="tcp"

# set executable location
EXE=$AKRR_APPKER_DIR/execs/ior/src/mdtest

# set how to run app kernel
RUNMPI="srun"


#Generate AppKer signature
appsigcheck.sh $EXE $AKRR_TASK_WORKDIR/.. > $AKRR_APP_STDOUT_FILE


# Execute AppKer
akrr_write_to_gen_info "appkernel_start_time" "`date`"

echo "#Testing single directory" >> $AKRR_APP_STDOUT_FILE 2>&1
$RUNMPI $EXE -v -I 32 -z 0 -b 0 -i $ITER >> $AKRR_APP_STDOUT_FILE 2>&1

echo "#Testing single directory per process" >> $AKRR_APP_STDOUT_FILE 2>&1
$RUNMPI $EXE -v -I 32 -z 0 -b 0 -i $ITER -u >> $AKRR_APP_STDOUT_FILE 2>&1

echo "#Testing single tree directory" >> $AKRR_APP_STDOUT_FILE 2>&1
$RUNMPI $EXE -v -I 4 -z 4 -b 2 -i $ITER >> $AKRR_APP_STDOUT_FILE 2>&1
 
echo "#Testing single tree directory per process" >> $AKRR_APP_STDOUT_FILE 2>&1
$RUNMPI $EXE -v -I 4 -z 4 -b 2 -i $ITER -u >> $AKRR_APP_STDOUT_FILE 2>&1

akrr_write_to_gen_info "appkernel_end_time" "`date`"





# clean-up
cd $AKRR_TASK_WORKDIR
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
