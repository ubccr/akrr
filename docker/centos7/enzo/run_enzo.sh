#!/bin/bash
APPKER=enzo
EXE_FILENAME=enzo
DEFAULT_CONFIGURATION=icc_impi_optaggressive
INPUT_PARAM=${INPUT_PARAM:-ReionizationRadHydro128}

copy_input()
{
    # check if input file exists, if it does, copy it over
    input_full_path="${CONT_AKRR_APPKER_DIR}/inputs/${APPKER}/${INPUT_PARAM}"
    echo "Copying over input file to working directory"
    if [[ -d "${input_full_path}" ]]; then
        cp ${input_full_path}/* ${tmp_work_dir}
        echo "${input_full_path} copied over to ${tmp_work_dir}"
    else
        echo "Error: ${input_full_path} does not exist"
        if [[ "${interactive}" != "true" ]]; then
          exit 1
        fi
    fi
}

run_appker()
{
    echo "Running ${APPKER}..."
	export I_MPI_PIN
	export I_MPI_DEBUG

    ring_bin=`which ring`
    inits_bin=`which inits`

    #Execute AppKer
    "${MPIRUN}" -np "${ppn}" "${EXE_FULL_PATH}" -V
    $inits_bin input.inits
    "${MPIRUN}" -np "${ppn}" $ring_bin pv ParticlePositions ParticleVelocities
    wait
    "${MPIRUN}" -np "${ppn}" "${EXE_FULL_PATH}" input.enzo
    echo performance.out
    cat performance.out
	wait
}

source "${CONT_AKRR_APPKER_DIR}/execs/bin/akrr_docker_run_appker.sh"
