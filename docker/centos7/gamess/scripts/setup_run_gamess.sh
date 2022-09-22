#!/bin/bash

echo "Trying to detect number of processes to use"
# gets the number of cores of this machine
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
	echo "Testing entry: " $1
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
	work_dir=$(mktemp -d $PWD/tmp.XXXXXXXXXX) # location where gamess input file gets copied to
	nodes=1
	ppn=${cpu_cores}
	verbose=false
	interactive=false
	run_gamess=true
	version=01
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


#validating that they are numbers
validate_number ${nodes}
validate_number ${ppn}

gamess_input_name="c8h10-cct-mp2.inp"
input_file_path="${GAMESS_INPUTS_DIR}/${gamess_input_name}"

dest_path="${work_dir}"

# output for testing
echo "Input file name: ${gamess_input_name}"
echo "Full input path: ${input_file_path}"
echo "Destination path: ${dest_path}"

#check if input file exists, if it does, copy it over
if [[ -f "${input_file_path}" ]]; then
	cp ${input_file_path} ${dest_path}
	echo "${gamess_input_name} copied over to ${dest_path}"
else
	echo "Error: ${input_file_path} does not exist"
	exit 1
fi

# copies over the run file to the working directory
if [[ -f "${GAMESS_EXE_DIR}/rungms" ]]; then
	cp ${GAMESS_EXE_DIR}/rungms ${dest_path}
	echo "rungms copied over to ${dest_path}"
else
	echo "Error: ${GAMESS_EXE_DIR}/rungms does not exist"
	exit 1
fi


# go to working directory to run gamess
cd ${work_dir}
echo "work dir: ${work_dir}"

# to allow access for mpiexec.hydra
export PATH=${PATH}:${MPI_DIR}

# executable is in a sorta weird place
gamess_exe_full_path="${GAMESS_EXE_DIR}/gamess.${version}.x"

echo "Running appsigcheck..."
${EXECS_DIR}/bin/appsigcheck.sh ${gamess_exe_full_path}
wait

# library path to allow mpirun in rungms to find everything
export LD_LIBRARY_PATH=/opt/intel/impi/2018.3.222/bin64

if [[ "${run_gamess}" == "true" ]]; then
	echo "Running gamess..."
	export I_MPI_DEBUG
	export I_MPI_PIN
	# for rungms we have the order be version, procs per node, number nodes
	./rungms ${gamess_input_name} ${version} ${ppn} ${nodes}
	wait
	echo "Complete! Gamess has been run, output in ${work_dir}"
fi

# if user sets interactive flag, starts up bash at end
if [[ "${interactive}" == "true" ]]; then
	/bin/bash
fi












