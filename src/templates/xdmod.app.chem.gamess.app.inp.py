appKernelRunEnvironmentTemplate="""
#Load application enviroment
module load gamess/v20120501r1
module list

#set executable location
VERNO=01
EXE=$GAMESS_DIR/gamess.$VERNO.x

#create scratch directory if needed
mkdir -p /scratch/xdtas

#prepare hostnames list
export GMX_NODELIST=`scontrol show hostname $SLURM_NODELIST| awk -v vv=$AKRR_CORES_PER_NODE '{{print $1 ":cpus=" vv}}'`

#set how to run app kernel
RUN_APPKERNEL="/projects/ccrstaff/general/appker/edge12core/execs/gamess/rungms $INPUT $VERNO $AKRR_CORES"
"""



