#!/bin/bash
APPKER=namd
EXE_FILENAME=namd2
DEFAULT_CONFIGURATION=icc_mkl_multicore
INPUT_PARAM=${INPUT_PARAM:-apoa1_nve}

copy_input()
{
    # check if input file exists, if it does, copy it over
    input_full_path="${CONT_AKRR_APPKER_DIR}/inputs/namd/${INPUT_PARAM}"
    echo "Copying over input file to working directory"
    if [[ -d "${input_full_path}" ]]; then
        cp "${input_full_path}"/* ${tmp_work_dir}
        echo "${input_full_path} copied over to $(tmp_work_dir)"
    else
        echo "Error: ${input_full_path} does not exist"
        if [[ "${interactive}" != "true" ]]; then
          exit 1
        fi
    fi
}

run_appker()
{
    if [[ "$PIN_CPU" == "1" ]]
    then
        CPUAFFINITY="+setcpuaffinity"
    else
        CPUAFFINITY=""
    fi

    CMD="${EXE_FULL_PATH} +p ${ppn} ${CPUAFFINITY} +showcpuaffinity input.namd"
    echo "Running namd with command: $CMD"
    $CMD

    wait
}

source "${CONT_AKRR_APPKER_DIR}/execs/bin/akrr_docker_run_appker.sh"
