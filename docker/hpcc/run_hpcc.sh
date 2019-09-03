#!/bin/bash
CONT_AKRR_APPKER_DIR=${CONT_AKRR_APPKER_DIR:-/opt/appker}
INPUTS_DIR=${INPUTS_DIR:-${CONT_AKRR_APPKER_DIR}/inputs}
EXECS_DIR=${EXECS_DIR:-${CONT_AKRR_APPKER_DIR}/execs}
MPI_DIR=${MPI_DIR:-/opt/intel/impi/2018.3.222/bin64}

export PATH=${EXECS_DIR}/bin:$PATH

source "${CONT_AKRR_APPKER_DIR}/execs/bin/akrr_util.bash"
source "${MPI_DIR}/mpivars.sh"
id
echo "Starting run script for running hpcc in this docker container"

# get cores count
cpu_cores="$(akrr_get_number_of_cores)"
echo "Number of processes set: ${cpu_cores}"

# get arch type
arch="$(akrr_get_arch)"
echo "CPU vectorization highest instractions: ${arch}"

# set optimal executable
if [ "${EXECUTABLE:-x}" = "x" ]
then
    EXECUTABLE=execs/hpcc/hpcc
    if [ -x "${CONT_AKRR_APPKER_DIR}/execs/hpcc/hpcc_${arch}" ]
    then
        EXECUTABLE=execs/hpcc/hpcc_${arch}
    fi
fi
HPCC_EXE_FULL_PATH=${HPCC_EXE_FULL_PATH:-${CONT_AKRR_APPKER_DIR}/${EXECUTABLE}}
echo "Executable to run: ${HPCC_EXE_FULL_PATH}"

# help text essentially
usage()
{
  echo << END
usage: run_hpcc.sh [-h] [-i] [--norun] [-n NODES] [-ppn PROC_PER_NODE] [--pin]
None are required.

Options:
  -h | --help           Display help text
	-v | --verbose        increase verbosity of output (does a set -x)
 	-i | --interactive		Start a bash session after the run (need to also do
 	                      -it after docker run)
	--norun			         	Set if you don't want to immediately run hpcc
	-n NODES | --nodes NODES
                        Specify number of nodes hpcc will be running on
	-ppn PROC_PER_NODE | --proc_per_node PROC_PER_NODE
	                      Specify nymber of processes/cores per node
					              (if not specified, number of cpu cores is used,
					              as found in /proc/cpuinfo)"
  --pin          				Turn on process pinning for mpi (I_MPI_PIN)
  -d DEBUG_LEVEL | --debug DEBUG_LEVEL
			                  Set the mpi debug level to the given value
			                  (0-5+, default 0)
END
} 

# allows script to continue if the argument passed in is a valid number
validate_number()
{
	# checking if the given argument is an integer
	re='^[0-9]+$'
	if ! [[ ${1} =~ ${re} ]] ; then
   		echo "error: ${2:-Entry} is not an integer, as expected" >&2
   		exit 1
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
validate_number "${nodes}" nodes
validate_number "${ppn}" ppn
validate_number "${I_MPI_DEBUG}" I_MPI_DEBUG

echo "Determining input file based on Nodes and processes per node"
# setting up paths to do the copying
hpcc_input_name="hpccinf.txt.${ppn}x${nodes}"
hpcc_input_full_path="${INPUTS_DIR}/hpcc/${hpcc_input_name}"

dest_path="${work_dir}/hpccinf.txt"

# output for testing
echo "Input file name: ${hpcc_input_name}"

# check if input file exists, if it does, copy it over
echo "Copying over input file to hpccinf.txt in working directory"
if [[ -f "${hpcc_input_full_path}" ]]; then
	cp "${hpcc_input_full_path}" "${dest_path}"
	echo "${hpcc_input_name} copied over to ${dest_path}"
else
	echo "Error: ${hpcc_input_full_path} does not exist"
	exit 1
fi

# go to working directory to run hpcc
echo "Changing work directory to ${work_dir}"
cd "${work_dir}"

echo "Running appsigcheck on HPCC binary..."



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
