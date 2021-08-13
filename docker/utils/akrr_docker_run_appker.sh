#!/usr/bin/env bash
CONT_AKRR_APPKER_DIR=${CONT_AKRR_APPKER_DIR:-/opt/appker}
INPUTS_DIR=${INPUTS_DIR:-${CONT_AKRR_APPKER_DIR}/inputs}
EXECS_DIR=${EXECS_DIR:-${CONT_AKRR_APPKER_DIR}/execs}

# source spack
# export SPACK_ROOT=${SPACK_ROOT:-/opt/spack}
# . $SPACK_ROOT/share/spack/setup-env.sh

export PATH=${EXECS_DIR}/bin:$PATH

export WORK_DIR=`pwd`

usage()
{
  cat << END
usage: <run container> [-h] [-i] [--norun] [-n NODES] [-ppn PROC_PER_NODE] [--pin]

Options:
  -h | --help           Display help text
  -v | --verbose        increase verbosity of output (does a set -x)
 	                    -it after docker run)
  -c | --configuration  Select configuration to run (by default will detect best
                        suitable)
  -lc | --list-configurations
                        list available configurations
  -view | --view        Select view to run
  -lv | --list-views
                        list available views
  --norun               Set if you don't want to immediately run hpcc
  -i | --interactive    Start a bash session after the run (need to also do
  -n NODES | --nodes NODES
                        Specify number of nodes ak will be running on (used in few cases, set ppn for number of MPI processes to use )
  -ppn PROC_PER_NODE | --proc_per_node PROC_PER_NODE
                        Specify nymber of processes/cores per node
                        (if not specified, number of cpu cores is used,
                        as found in /proc/cpuinfo)"
  -tpp TREADS_PER_PROC | --threads_per_process TREADS_PER_PROC
                        Threads per process.
  --pin                 Turn on process pinning for mpi (I_MPI_PIN)
  -d DEBUG_LEVEL | --debug DEBUG_LEVEL
                        Set the mpi debug level to the given value
                        (0-5+, default 0)
END

if [ -n "$(LC_ALL=C type -t usage_extra)" ] && [ "$(LC_ALL=C type -t usage_extra)" = function ]
then
    usage_extra
fi
}

source "${CONT_AKRR_APPKER_DIR}/execs/bin/akrr_util.bash"
source "${CONT_AKRR_APPKER_DIR}/execs/bin/akrr_docker_util.sh"
#echo "${APPKER_SPECS}"
#source "${APPKER_SPECS}"

# get cores count
cpu_cores="$(akrr_get_number_of_cores)"

# get arch type
arch="$(akrr_get_arch)"
target="$(akrr_get_arch_target)"

# setting default values for variables
set_defaults()
{
	tmp_work_dir=$(mktemp -d "${WORK_DIR}/tmp.XXXXXXXXXX") # location where input file will get copied to
	export TMPDIR=${tmp_work_dir}
	nodes=1
	ppn=${cpu_cores:-1}
	tpp=1
	verbose=false
	interactive=false
	run_appker=true
	I_MPI_PIN=0
	I_MPI_DEBUG=0
	PIN_CPU=0
}

#echo "Starting run script for running hpcc in this docker container"

#echo "Setting default values for some parameters"
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
		-tpp | --threads_per_process)
			echo "Threads Per Process, default 1 "
			shift
			tpp=${1}
			;;
		--pin)
			echo "Pin arg detected, setting I_MPI_PIN to 1"
			I_MPI_PIN=1
			PIN_CPU=1
			;;
		-d | --debug)
			echo "Debug arg detected, setting I_MPI_DEBUG to value after it"
			shift
			I_MPI_DEBUG=${1}
			;;
		-c | --configuration)
			shift
			CONFIGURATION=${1}
			;;
		-lc | --list-configurations)
			echo "Available configurations:"
			cat /opt/spack-environment/${APPKER}.configurations
			exit 1
			;;
		-view | --view)
			shift
			SPACK_VIEW=${1}
			;;
		-lv | --list-views)
			echo "Available views:"
			cd /opt/spack-environment
			ls -d ${APPKER}_*
			exit 1
			;;
		-e)
		    shift
		    ENV_VARIABLE=${1}
		    shift
			ENV_VALUE=${1}
		    export $ENV_VARIABLE=$ENV_VALUE
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

# if user sets interactive flag, starts up bash at end
if [[ "${interactive}" == "true"  && "${run_appker}" == "false" ]]; then
	echo "Launching /bin/bash"
	/bin/bash
	exit 0
fi

if [ -n "$(LC_ALL=C type -t post_arg_parse_call)" ] && [ "$(LC_ALL=C type -t post_arg_parse_call)" = function ]
then
    post_arg_parse_call
fi

echo "Number of processes set: ${cpu_cores}"
echo "CPU vectorization highest instructions: ${arch}, target: ${target}"

PACKAGE_NAME=${PACKAGE_NAME:-${APPKER}}

# set optimal executable
CONFIGURATION=${CONFIGURATION:-${DEFAULT_CONFIGURATION}}
SPACK_VIEW=${SPACK_VIEW:-${PACKAGE_NAME}_${DEFAULT_CONFIGURATION}_${target}}
source /opt/spack-environment/${SPACK_VIEW}/env.sh

EXE_FULL_PATH=${EXE_FULL_PATH:-$(which ${EXE_FILENAME})}
MPIRUN=`which mpirun`
echo "Executable to run: ${EXE_FULL_PATH}"
echo "Mpirun: ${MPIRUN}"

# echo "Validating variables to make sure they are numbers"
validate_number "${nodes}" nodes
validate_number "${ppn}" ppn
validate_number "${tpp}" tpp
validate_number "${I_MPI_DEBUG}" I_MPI_DEBUG

copy_input

# go to working directory to run hpcc
echo "Changing work directory to ${tmp_work_dir}"
cd "${tmp_work_dir}"

echo "Running appsigcheck on ${EXE_FILENAME} binary..."

"${EXECS_DIR}/bin/appsigcheck.sh" "${EXE_FULL_PATH}"
wait

export OMP_NUM_THREADS=${tpp}

if [[ "${run_appker}" == "true" ]]; then
    run_appker
fi

cd ${WORK_DIR}

# clean up if not debug 5+
if [[ "${I_MPI_DEBUG}" -lt 5 ]]
then
    rm -rf "${tmp_work_dir}"
fi

# if user sets interactive flag, starts up bash at end
if [[ "${interactive}" == "true" ]]; then
	echo "Launching /bin/bash"
	/bin/bash
fi
