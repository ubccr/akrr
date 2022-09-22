#!/bin/bash
APPKER=hpcc
EXE_FILENAME=hpcc
DEFAULT_CONFIGURATION=icc_mkl_impi

copy_input()
{
    # echo "Determining input file based on Nodes and processes per node"
    # setting up paths to do the copying
    hpcc_input_name="hpccinf.txt.${ppn}x${nodes}"
    hpcc_input_full_path="${INPUTS_DIR}/hpcc/${hpcc_input_name}"

    dest_path="${tmp_work_dir}/hpccinf.txt"

    # output for testing
    #echo "Input file name: ${hpcc_input_name}"

    # check if input file exists, if it does, copy it over
    #echo "Copying over input file to hpccinf.txt in working directory"
    if [[ -f "${hpcc_input_full_path}" ]]; then
        cp "${hpcc_input_full_path}" "${dest_path}"
        echo "${hpcc_input_name} copied over to ${dest_path}"
    else
        echo "Error: ${hpcc_input_full_path} does not exist"
        exit 1
    fi
}

run_appker()
{
    # running hpcc with mpirun, where -np is number of cores for the machine
    echo "Running hpcc with command:"
    if [[ "$ppn" == "1" ]] && [[ "$nodes" == "1" ]]
    then
        echo "${EXE_FULL_PATH}"
        "${EXE_FULL_PATH}"
    else
        echo "${MPIRUN} -np ${ppn} ${EXE_FULL_PATH}"
        export I_MPI_DEBUG
        export I_MPI_PIN
        # Set I_MPI_HYDRA_BOOTSTRAP to ssh otherwise it will use different method on HPC system
        export I_MPI_HYDRA_BOOTSTRAP="ssh"
        "${MPIRUN}" -np "${ppn}" "${EXE_FULL_PATH}"
    fi

    wait
    echo "Complete! hpccoutf.txt is in ${work_dir}"
    echo "catting output to standard out:"
    cat hpccoutf.txt
}

source "${CONT_AKRR_APPKER_DIR}/execs/bin/akrr_docker_run_appker.sh"
