#!/bin/bash
CONT_AKRR_APPKER_DIR=${CONT_AKRR_APPKER_DIR:-/opt/appker}
INPUTS_DIR=${INPUTS_DIR:-${CONT_AKRR_APPKER_DIR}/inputs}
EXECS_DIR=${EXECS_DIR:-${CONT_AKRR_APPKER_DIR}/execs}
MPI_DIR=${MPI_DIR:-/usr/bin}

NWCHEM_INPUT_DIR=${NWCHEM_INPUT_DIR:-${INPUTS_DIR}/nwchem}
NWCHEM_INPUT_FILENAME=${NWCHEM_INPUT_FILENAME:-aump2.nw}

export PATH=${EXECS_DIR}/bin:$PATH

source "${CONT_AKRR_APPKER_DIR}/execs/bin/akrr_util.bash"

id
echo "Starting run script for running nwchem in this docker container"

# get cores count
cpu_cores="$(akrr_get_number_of_cores)"
echo "Number of processes set: ${cpu_cores}"

# get arch type
arch="$(akrr_get_arch)"
echo "CPU vectorization highest instractions: ${arch}"

# set optimal executable (run what you got)
EXE_FULL_PATH=${EXE_FULL_PATH:-${NWCHEM_EXECUTABLE}}
echo "Executable to run: ${EXE_FULL_PATH}"

# help text essentially
usage()
{
        echo "usage: setup_hpcc_inputs.sh [-h] [-i] [--norun] [-n NODES] [-ppn PROC_PER_NODE] [--pin]"
        echo "None are required."
        echo ""
        echo " Options:"
        echo "  -h | --help                     Display help text"
        echo "  -v | --verbose                  increase verbosity of output (does a set -x)"
        echo "  -i | --interactive              Start a bash session after the run (need to also do -it after docker run)"
        echo "  --norun                         Set if you don't want to immediately run hpcc "
        echo "  -n NODES | --nodes NODES        Specify number of nodes hpcc will be running on"
        echo "  -ppn PROC_PER_NODE | "
        echo "  --proc_per_node PROC_PER_NODE   Specify nymber of processes/cores per node" 
        echo "                                  (if not specified, number of cpu cores is used,"
        echo "                                  as found in /proc/cpuinfo)"
        echo "  --pin                           Turn on process pinning for mpi (I_MPI_PIN)"
        echo "  -d DEBUG_LEVEL | "
        echo "  --debug DEBUG_LEVEL             Set the mpi debug level to the given value (0-5+, default 0)"
} 

# allows script to continue if the argument passed in is a valid number
validate_number()
{
	echo "Testing entry: $1"
	# checking if the given argument is an integer
	re='^[0-9]+$'
	if ! [[ $1 =~ $re ]] ; then
   		echo "error: Entry is not an integer, as expected" >&2; exit 1
	else
		echo "Entry is valid"
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
	I_MPI_PIN=0
	I_MPI_DEBUG=0
}

echo "Setting default values for some parameters"
set_defaults

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

echo "nodes: ${nodes}"
echo "ppn: ${ppn}"
echo "interactive: ${interactive}"

echo "Validating variables to make sure they are numbers"
validate_number ${nodes}
validate_number ${ppn}
validate_number "${I_MPI_DEBUG}" I_MPI_DEBUG

echo "Determining input file"
echo "NWChem Input dir path: ${NWCHEM_INPUT_DIR}"
echo "Input file path: ${NWCHEM_INPUT_FILENAME}"

dest_path="${work_dir}"

# check if input file exists, if it does, copy it over
echo "Copying over input file to working directory"
if [[ -f "${NWCHEM_INPUT_DIR}/${NWCHEM_INPUT_FILENAME}" ]]; then
	cp ${NWCHEM_INPUT_DIR}/* ${dest_path}
	echo "${NWCHEM_INPUT_DIR}/* copied over to ${dest_path}"

	echo "scratch_dir ${work_dir}" >> "${dest_path}/${NWCHEM_INPUT_FILENAME}"
    echo "permanent_dir ${work_dir}" >> "${dest_path}/${NWCHEM_INPUT_FILENAME}"
else
	echo "Error: ${NWCHEM_INPUT_DIR}/${NWCHEM_INPUT_FILENAME} input file does not exist"
	exit 1
fi

cd $work_dir

echo "Running appsigcheck..."
${EXECS_DIR}/bin/appsigcheck.sh ${EXE_FULL_PATH}
wait

# running hpcc with mpirun, where -np is number of cores for the machine
if [[ "${run_appker}" == "true" ]]; then
	echo "Running nwchem..."
	export I_MPI_PIN
	export I_MPI_DEBUG
	mpirun -np ${cpu_cores} ${EXE_FULL_PATH} ${NWCHEM_INPUT_FILENAME}
	wait
	echo "Complete! outputs are in is in ${work_dir}"
fi

# if user sets interactive flag, starts up bash at end
if [[ "${interactive}" == "true" ]]; then
	/bin/bash
fi
















