#!/bin/bash
# name of input we want to use in inputs location
nwchem_input_files_dir=${NWCHEM_INPUTS_DIR}
input_file_name="aump2.nw"


# gets the number of cores of this machine (used for later mpirun -np flag
cpu_cores="$(grep ^cpu\\scores /proc/cpuinfo | uniq |  awk '{print $4}')"
if [[ "${cpu_cores}" == "1" ]]; then
	echo "Detected only one core. Counting processors instead"
	cpu_cores="$(grep "processor" /proc/cpuinfo | wc -l)"
fi

echo "Number of cores detected: ${cpu_cores}"

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
	work_dir=$(mktemp -d $PWD/tmp.XXXXXXXXXX) # location where hpcc input file gets copied to
	nodes=1
	ppn=${cpu_cores}
	verbose=false
	interactive=false
	run_namd=true
	I_MPI_PIN=0
}

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


echo "nodes: ${nodes}"
echo "ppn: ${ppn}"
echo "interactive: ${interactive}"

validate_number ${nodes}
validate_number ${ppn}

input_files_path="${nwchem_input_files_dir}"

dest_path="${work_dir}"
echo "Input file path: ${input_files_path}"
echo "Namd Input dir path: ${nwchem_input_files_dir}"

if [[ -f "${input_files_path}/${input_file_name}" ]]; then
	cp ${input_files_path}/* ${dest_path}

else
	echo "Error: ${input_files_path}/${input_file_name} input file does not exist"
	exit 1
fi


cd $work_dir
export LD_LIBRARY_PATH=/opt/intel/impi/2018.3.222/lib64:/opt/intel/mkl/lib/intel64

echo "Running appsigcheck..."
${EXECS_DIR}/bin/appsigcheck.sh ${NWCHEM_EXECUTABLE}
wait


# running hpcc with mpirun, where -np is number of cores for the machine
if [[ "${run_namd}" == "true" ]]; then
	echo "Running namd..."
	export I_MPI_PIN
	export I_MPI_DEBUG
	${MPI_DIR}/mpirun -np ${ppn} ${NWCHEM_EXECUTABLE} ${input_file_name}
	wait
	echo "Complete! outputs are in is in ${work_dir}"
fi


# if user sets interactive flag, starts up bash at end
if [[ "${interactive}" == "true" ]]; then
	/bin/bash
fi
















