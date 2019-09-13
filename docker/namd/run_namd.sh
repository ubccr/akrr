#!/bin/bash
CONT_AKRR_APPKER_DIR=${CONT_AKRR_APPKER_DIR:-/opt/appker}
INPUT_PARAM=${INPUT_PARAM:-inputs/namd/apoa1_nve}
EXECS_DIR=${EXECS_DIR:-${CONT_AKRR_APPKER_DIR}/execs}

export PATH=${EXECS_DIR}/bin:$PATH

source "${CONT_AKRR_APPKER_DIR}/execs/bin/akrr_util.bash"
source /opt/intel/compilers_and_libraries_2018.3.222/linux/mkl/bin/mklvars.sh intel64

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
    EXECUTABLE=execs/NAMD_2.13_Linux-x86_64-multicore/namd2_prebuild
    if [ -x "${CONT_AKRR_APPKER_DIR}/execs/NAMD_2.13_Linux-x86_64-multicore/namd2_${arch}" ]
    then
        EXECUTABLE=execs/NAMD_2.13_Linux-x86_64-multicore/namd2_${arch}
    fi
fi
EXE_FULL_PATH=${EXE_FULL_PATH:-${CONT_AKRR_APPKER_DIR}/${EXECUTABLE}}
echo "Executable to run: ${EXE_FULL_PATH}"

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
  --pin          				Turn on process pinning
  -d | --debug
			                  Set debug mode
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
	work_dir=$(mktemp -d "$(pwd)/tmp.XXXXXXXXXX") # location where input file will get copied to
	export TMPDIR=${work_dir}
	nodes=1
	ppn=${cpu_cores}
	verbose=false
	interactive=false
	run_appker=true
	CPUAFFINITY=""
	DEBUG=0
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
			run_appker=false
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
			echo "Pin arg detected, adding +setcpuaffinity"
			CPUAFFINITY="setcpuaffinity"
			;;
		-d | --debug)
			echo "Debug arg detected, would not remove work_dir"
			DEBUG=1
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

input_full_path="${CONT_AKRR_APPKER_DIR}/${INPUT_PARAM}"

# go to working directory to run hpcc
echo "Changing work directory to ${work_dir}"
cd
cd "${work_dir}"

# check if input file exists, if it does, copy it over
echo "Copying over input file to working directory"
if [[ -d "${input_full_path}" ]]; then
	cp "${input_full_path}"/* .
	echo "${input_full_path} copied over to $(pwd)"
else
	echo "Error: ${input_full_path} does not exist"
	if [[ "${interactive}" != "true" ]]; then
	  exit 1
	fi
fi

echo "Running appsigcheck on HPCC binary..."

"${EXECS_DIR}/bin/appsigcheck.sh" "${EXE_FULL_PATH}"
wait

# running hpcc with mpirun, where -np is number of cores for the machine
if [[ "${run_appker}" == "true" ]]; then
  CMD="${EXE_FULL_PATH} +p ${ppn} ${CPUAFFINITY} input.namd"
  echo "Running namd with command: $CMD"
  $CMD

  wait
fi

# clean up if not debug 5+
if [[ "${DEBUG}" == "0" ]]
then
    rm -rf "${work_dir}"
    export TMPDIR=/tmp
fi

# if user sets interactive flag, starts up bash at end
if [[ "${interactive}" == "true" ]]; then
	echo "Launching /bin/bash"
	/bin/bash
fi
