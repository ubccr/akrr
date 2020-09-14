#!/bin/bash
APPKER=hpcg
EXE_FILENAME=xhpcg
DEFAULT_CONFIGURATION=icc_impi
INPUT_PARAM=${INPUT_PARAM:-hpcg.dat}

copy_input()
{
    input_full_path="${INPUTS_DIR}/${APPKER}/${INPUT_PARAM}"
    # check if input file exists, if it does, copy it over
    #echo "Copying over input file to hpccinf.txt in working directory"
    if [[ -f "${input_full_path}" ]]; then
        cp "${input_full_path}" "${tmp_work_dir}/hpcg.dat"
        echo "${input_full_path} copied over to ${tmp_work_dir}"
    else
        echo "Error: ${input_full_path} does not exist"
        exit 1
    fi
}

run_appker()
{
    # running hpcc with mpirun, where -np is number of cores for the machine
    echo "Running hpcg with command:"
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
    echo "Complete! Outputs are in ${tmp_work_dir}"
	echo "cat output to standard out:"
	echo "hpcg_log ###################"
	cat hpcg_log*

	# printing out yaml in proper format (based on default hpcg.app.conf)
	for f in *.yaml
	do
		echo "====== $f Start ======"
		cat $f
		echo "====== $f End   ======"
	done
	for f in *.txt
	do
		echo "====== $f Start ======"
		cat $f
		echo "====== $f End   ======"
	done
}

source "${CONT_AKRR_APPKER_DIR}/execs/bin/akrr_docker_run_appker.sh"
