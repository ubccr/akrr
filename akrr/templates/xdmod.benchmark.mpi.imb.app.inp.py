appKernelRunEnvironmentTemplate="""
#Load application enviroment
module load intel/13.0
module load intel-mpi/4.1.0
module list

export I_MPI_PMI_LIBRARY=/usr/lib64/libpmi.so

ulimit -s unlimited

#set how to run mpi applications, one process per node
RUNMPI="srun --ntasks-per-node=1 -n {akrrNNodes}"
"""
