#!/bin/bash
APPKER=nwchem
EXE_FILENAME=nwchem
DEFAULT_CONFIGURATION=icc_mkl_impi
INPUT_PARAM=${INPUT_PARAM:-aump2.nw}

export NWCHEM_BASIS_LIBRARY=/opt/spack-environment/nwchem_icc_mkl_impi_skylake_avx512/.spack-env/view/share/nwchem/libraries

copy_input()
{
    # check if input file exists, if it does, copy it over
    input_full_path="${CONT_AKRR_APPKER_DIR}/inputs/nwchem/${INPUT_PARAM}"
    echo "Copying over input file to working directory"
    if [[ -f "${input_full_path}" ]]; then
        cp "${input_full_path}" ${tmp_work_dir}
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
    echo "Running nwchem..."
	export I_MPI_PIN
	export I_MPI_DEBUG
	"${MPIRUN}" -np "${ppn}" "${EXE_FULL_PATH}" "${INPUT_PARAM}"
	wait
}

source "${CONT_AKRR_APPKER_DIR}/execs/bin/akrr_docker_run_appker.sh"
