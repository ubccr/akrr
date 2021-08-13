#!/bin/bash
APPKER=graph500
EXE_FILENAME=graph500_reference_bfs_sssp
DEFAULT_CONFIGURATION=icc_impi
INPUT_PARAM=${INPUT_PARAM:-23 16}

copy_input()
{
    echo "INPUT_PARAM=$INPUT_PARAM"
}

run_appker()
{
    # running hpcc with mpirun, where -np is number of cores for the machine
    echo "Running ${APPKER} with command:"
    if [[ "$ppn" == "1" ]] && [[ "$nodes" == "1" ]]
    then
        echo "${EXE_FULL_PATH}"
        "${EXE_FULL_PATH}"
    else
        echo "${MPIRUN} -np ${ppn} ${EXE_FULL_PATH} ${INPUT_PARAM}"
        export I_MPI_DEBUG
        export I_MPI_PIN
        # Set I_MPI_HYDRA_BOOTSTRAP to ssh otherwise it will use different method on HPC system
        export I_MPI_HYDRA_BOOTSTRAP="ssh"
        "${MPIRUN}" -np "${ppn}" "${EXE_FULL_PATH}" ${INPUT_PARAM}
    fi

    wait
    echo "Done!"
}

source "${CONT_AKRR_APPKER_DIR}/execs/bin/akrr_docker_run_appker.sh"
