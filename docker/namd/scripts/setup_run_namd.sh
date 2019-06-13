#!/bin/bash

# name of input we want to use in inputs location
namd_cur_inputs_dir_name="apoa1_nve"
namd_input_files_dir="${NAMD_INPUTS_DIR}/${namd_cur_inputs_dir_name}"


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
    	echo "usage: setup_hpcc_inputs.sh [-h] [-i] [--norun] [-n NODES] [-ppn PROC_PER_NODE]"
	echo ""
    	echo " Options:"
    	echo "	-h | --help			Display help text"
	#echo "	-v | --verbose			increase verbosity of output"
	echo " 	-i | --interactive		Start a bash session after the run"
	echo "	--norun				Set if you don't want to immediately run hpcc"
	echo "	**-n NODES | --nodes NODES	Specify number of nodes hpcc will be running on"
	echo "	**-ppn PROC_PER_NODE | "
	echo "	--proc_per_node PROC_PER_NODE	Specify nymber of processes/cores per node" 
	echo "					(if not specified, number of cpu cores is used,"
	echo "					as found in /proc/cpuinfo)"
	echo " ** = not used. In most cases not having any arguments is fine"
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
	work_dir=${HOME} # location where hpcc input file gets copied to
	nodes=1
	ppn=${cpu_cores}
	verbose=false
	interactive=false
	run_namd=true
}

set_defaults

# loop through arguments - for each to one of them
while [[ "$1" != "" ]]; do
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
			run_namd=false
			;;
		-n | --nodes)
			shift
			nodes=$1
			;;
		-ppn | --proc_per_node)
			shift
			ppn=$1
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

input_files_path="${namd_input_files_dir}"


dest_path="${work_dir}"
echo "Input file path: ${input_files_path}"
echo "Namd Input dir path: ${NAMD_INPUTS_DIR}"

# check if input file exists, if it does, copy it over
if [[ -f "${input_files_path}/input.namd" ]]; then
	cp ${input_files_path}/* ${dest_path}
	echo "Copied everything from ${input_files_path} to ${dest_path}"
else
	echo "Error: ${input_files_path}/input.namd does not exist"
	exit 1
fi

cd $work_dir

echo "Running appsigcheck..."
${EXECS_LOC}/bin/appsigcheck.sh ${NAMD_EXE_FULL_PATH}

# running hpcc with mpirun, where -np is number of cores for the machine
if [[ "${run_namd}" == "true" ]]; then
	echo "Running namd..."
	${NAMD_EXE_FULL_PATH} +p${ppn} ${work_dir}/input.namd
	echo "Complete! outputs are in is in ${work_dir}"
	echo "Cat doesn't really work for output..."
fi

echo "End of entrypoint script. Interactive session will launch if specified."

# if user sets interactive flag, starts up bash at end
if [[ "${interactive}" == "true" ]]; then
	/bin/bash
fi












