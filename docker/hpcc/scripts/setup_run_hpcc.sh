#!/bin/bash

echo "Starting run script for running hpcc in this docker container"

# initializing where the inputs are
temp="hpcc"
hpcc_inputs_dir="${INPUTS_DIR}/${temp}"

# gets the number of cores of this machine automatically
echo "Checking number of cores to determine number of processes to run"
cpu_cores="$(grep ^cpu\\scores /proc/cpuinfo | uniq |  awk '{print $4}')"
if [[ "${cpu_cores}" == "1" ]]; then
	echo "Detected only one core. Counting processors instead"
	cpu_cores="$(grep "processor" /proc/cpuinfo | wc -l)"
fi

echo "Number of processes set: ${cpu_cores}"

# help text essentially
usage()
{
    	echo "usage: setup_hpcc_inputs.sh [-h] [-i] [--norun] [-n NODES] [-ppn PROC_PER_NODE] [--pin]"
	echo "None are required."
	echo ""
    	echo " Options:"
    	echo "	-h | --help			Display help text"
	echo "	-v | --verbose			increase verbosity of output (does a set -x)"
	echo " 	-i | --interactive		Start a bash session after the run (need to also do -it after docker run)"
	echo "	--norun				Set if you don't want to immediately run hpcc "
	echo "	-n NODES | --nodes NODES	Specify number of nodes hpcc will be running on"
	echo "	-ppn PROC_PER_NODE | "
	echo "	--proc_per_node PROC_PER_NODE	Specify nymber of processes/cores per node" 
	echo "					(if not specified, number of cpu cores is used,"
	echo "					as found in /proc/cpuinfo)"
	echo "  --pin 				Turn on process pinning for mpi (I_MPI_PIN)"
	echo "  -d DEBUG_LEVEL | "
	echo "	--debug DEBUG_LEVEL		Set the mpi debug level to the given value (0-5+, default 0)"
} 

# allows script to continue if the argument passed in is a valid number
validate_number()
{
	echo "Testing entry: ${1}"
	# checking if the given argument is an integer
	re='^[0-9]+$'
	if ! [[ ${1} =~ ${re} ]] ; then
   		echo "error: Entry is not an integer, as expected" >&2; exit 1
	else
		echo "Entry is valid"
	fi
}

# setting default values for variables
set_defaults()
{
	work_dir=$(mktemp -d $PWD/tmp.XXXXXXXXXX) # location where input file will get copied to
	nodes=1
	ppn=${cpu_cores}
	verbose=false
	interactive=false
	run_hpcc=true
	I_MPI_PIN=0
	I_MPI_DEBUG=0
}

echo "Setting default values for some parameters"
set_defaults

# loop through arguments - for each to one of them
while [[ "${1}" != "" ]]; do
	case $1 in
		-h | --help)
			usage
			exit
			;;
		-v | --verbose)
			echo "Verbose arg detected, running set -x after arg processing"
			verbose=true
			;;
		-i | --interactive)
			echo "Interactive arg detected, starting bash session at end of script"
			interactive=true
			;;
		--norun)
			echo "Norun arg detected, will not run hpcc executable"
			run_hpcc=false
			;;
		-n | --nodes)
			echo "Nodes arg detected. Purely used to determine hpcc input file"
			echo "Using the docker image assumes you're working on one node"
			shift
			nodes=${1}
			;;
		-ppn | --proc_per_node)
			echo "Processes Per Node arg detected, overwriting previous processes value found from looking at number of cores"
			shift
			ppn=${1}
			;;
		--pin)
			echo "Pin arg detected, setting I_MPI_PIN to 1"
			I_MPI_PIN=1
			;;
		-d | --debug)
			echo "Debug arg detected, setting I_MPI_DEBUG to value after it"
			shift
			I_MPI_DEBUG=${1}
			;;
		*)
			echo "Error: unrecognized argument"
			usage
			exit 1
			;;
	esac
	shift # to go to next argument
done

if [[ "${verbose}" == "true" ]]; then
	set -x
fi

echo "Validating variables to make sure they are numbers"
validate_number ${nodes}
validate_number ${ppn}
validate_number ${I_MPI_DEBUG}

echo "Determining input file based on Nodes and processes per node"
# setting up paths to do the copying
temp="x"
hpcc_input_name="hpccinf.txt.${ppn}${temp}${nodes}"
hpcc_input_full_path="${hpcc_inputs_dir}/${hpcc_input_name}"

temp="hpccinf.txt"
dest_path="${work_dir}/${temp}"

# output for testing
echo "Input file name: ${hpcc_input_name}"

# check if input file exists, if it does, copy it over
echo "Copying over input file to hpccinf.txt in working directory"
if [[ -f "${hpcc_input_full_path}" ]]; then
	cp ${hpcc_input_full_path} ${dest_path}
	echo "${hpcc_input_name} copied over to ${dest_path}"
else
	echo "Error: ${hpcc_input_full_path} does not exist"
	exit 1
fi

# go to working directory to run hpcc
echo "Changing work directory to ${work_dir}"
cd ${work_dir}

echo "Running appsigcheck on HPCC binary..."
# trying to run the script thing on hpcc
source ${EXECS_DIR}/bin/akrr_util.bash
export PATH=${EXECS_DIR}/bin:$PATH

${EXECS_DIR}/bin/appsigcheck.sh ${HPCC_EXE_FULL_PATH}
wait

# running hpcc with mpirun, where -np is number of cores for the machine
if [[ "${run_hpcc}" == "true" ]]; then
	echo "Running hpcc with command:"
	echo "${MPI_DIR}/mpirun -np ${ppn} ${HPCC_EXE_FULL_PATH}"
	export I_MPI_DEBUG
	export I_MPI_PIN
	${MPI_DIR}/mpirun -np ${ppn} ${HPCC_EXE_FULL_PATH}
	wait
	echo "Complete! hpccoutf.txt is in ${work_dir}"
	echo "catting output to standard out:"
	cat hpccoutf.txt
fi


echo "End of entrypoint script. Interactive session will launch if specified."

# if user sets interactive flag, starts up bash at end
if [[ "${interactive}" == "true" ]]; then
	echo "Launching /bin/bash"
	/bin/bash
fi
