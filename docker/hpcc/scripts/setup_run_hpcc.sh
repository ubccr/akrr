#!/bin/bash
set -x
# initializing some variables
temp="hpcc"
hpcc_inputs_dir="${INPUTS_LOC}/${temp}"
echo "hpcc_inputs_dir: ${hpcc_inputs_dir}"

# setting default values for variables
set_defaults()
{
	work_dir=/tmp  # location where input file will get copied to
	nodes=1
	ppn=8
	verbose=false
	interactive=false
	run_hpcc=true
}

set_defaults

# loop through arguments - for each to one of them
while [[ "${1}" != "" ]]; do
	case $1 in
		-ppn | --proc_per_node)
			shift
			ppn=${1}
			;;
		*)
			echo "Error: unrecognized argument"
			usage
			exit 1
			;;
	esac
	shift # to go to next argument
done

echo "ppn: ${ppn}"

# setting up paths to do the copying
temp="x"
hpcc_input_name="hpccinf.txt.${ppn}${temp}${nodes}"
hpcc_input_full_path="${hpcc_inputs_dir}/${hpcc_input_name}"

temp="hpccinf.txt"
dest_path="${work_dir}/${temp}"

# check if input file exists, if it does, copy it over
if [[ -f "${hpcc_input_full_path}" ]]; then
	cp ${hpcc_input_full_path} ${dest_path}
	echo "${hpcc_input_name} copied over to ${dest_path}"
else
	echo "Error: ${hpcc_input_full_path} does not exist"
	exit 1
fi

# go to working directory to run hpcc
cd ${work_dir}
echo "work dir: ${work_dir}"

echo "ENVIRONMENT==================="
env
echo "ENVIRONMENT==================="



echo "Running appsigcheck..."
# trying to run the script thing on hpcc
${EXECS_LOC}/bin/appsigcheck.sh ${HPCC_EXE_FULL_PATH}

# running hpcc with mpirun, where -np is number of cores for the machine
echo "Running hpcc..."
ls -lah /usr/bin
echo "Hpcc path: ${HPCC_EXE_FULL_PATH}"
${MPI_LOC}/mpirun -np ${ppn} ${HPCC_EXE_FULL_PATH}
echo "Complete! hpccoutf.txt is in ${work_dir}"
echo "cat output to standard out:"
cat hpccoutf.txt

echo "End of entrypoint script. Interactive session will launch if specified."

