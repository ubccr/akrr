#!/bin/bash

# initial statements for testing
#echo "Arguments passed in: $@"
#echo "Number of arguments: $#"

# initializing some variables
#num_args="$#"
temp="hpcc"
hpcc_inputs_dir="${INPUTS_LOC}/${temp}"
echo "hpcc_inputs_dir: ${hpcc_inputs_dir}"

# gets the number of cores of this machine
cpu_cores="$(grep ^cpu\\scores /proc/cpuinfo | uniq |  awk '{print $4}')"
if [[ "${cpu_cores}" == "1" ]]; then
	echo "Detected only one core. Counting processors instead"
	cpu_cores="$(grep "processor" /proc/cpuinfo | wc -l)"
fi

echo "Number of cores detected: ${cpu_cores}"

# help text essentially
usage()
{
    	echo "usage: setup_hpcc_inputs.sh [-h] [-i] [--norun] [-n NODES] [-{ppn} PROC_PER_NODE]"
	echo ""
    	echo " Options:"
    	echo "	-h | --help			Display help text"
	#echo "	-v | --verbose			increase verbosity of output"
	echo " 	-i | --interactive		Start a bash session after the run"
	echo "	--norun				Set if you don't want to immediately run hpcc"
	echo "	-n NODES | --nodes NODES	Specify number of nodes hpcc will be running on"
	echo "	-ppn PROC_PER_NODE | "
	echo "	--proc_per_node PROC_PER_NODE	Specify nymber of processes/cores per node" 
	echo "					(if not specified, number of cpu cores is used,"
	echo "					as found in /proc/cpuinfo)"
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
	work_dir=${HOME} # location where hpcc input file gets copied to
	nodes=1
	ppn=${cpu_cores}
	verbose=false
	interactive=false
	run_hpcc=true
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
			verbose=true
			;;
		-i | --interactive)
			interactive=true
			;;
		--norun)
			run_hpcc=false
			;;
		-n | --nodes)
			shift
			nodes=${1}
			;;
		-ppn | --proc_per_node)
			shift
			{ppn}=${1}
			;;
		*)
			echo "Error: unrecognized argument"
			usage
			exit 1
			;;
	esac
	shift # to go to next argument
done


echo "nodes: ${nodes}"
echo "ppn: ${ppn}"
echo "interactive: ${interactive}"

#validating that they are numbers
validate_number ${nodes}
validate_number ${ppn}

# setting up paths to do the copying
temp="x"
hpcc_input_name="hpccinf.txt.${ppn}${temp}${nodes}"
hpcc_input_full_path="${hpcc_inputs_dir}/${hpcc_input_name}"

temp="hpccinf.txt"
dest_path="${work_dir}/${temp}"

# output for testing
echo "Input file name: ${hpcc_input_name}"
echo "Full path: ${hpcc_input_full_path}"
echo "Destination path: ${dest_path}"

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

echo "Running appsigcheck..."
# trying to run the script thing on hpcc
${EXECS_LOC}/bin/appsigcheck.sh ${HPCC_LOC}

# running hpcc with mpirun, where -np is number of cores for the machine
if [[ "${run_hpcc}" == "true" ]]; then
	echo "Running hpcc..."
	${MPI_LOC}/mpirun -np ${ppn} ${HPCC_LOC}
	echo "Complete! hpccoutf.txt is in ${work_dir}"
	echo "cat output to standard out:"
	cat hpccoutf.txt
fi


echo "End of entrypoint script. Interactive session will launch if specified."

# if user sets interactive flag, starts up bash at end
if [[ "${interactive}" == "true" ]]; then
	/bin/bash
fi


