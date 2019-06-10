#!/bin/bash


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
    	echo "usage: setup_gamess_inputs.sh [-h] [-i] [--norun] [-n NODES] [-ppn PROC_PER_NODE]"
	echo ""
    	echo " Options:"
    	echo "	-h | --help			Display help text"
	#echo "	-v | --verbose			increase verbosity of output"
	echo " 	-i | --interactive		Start a bash session after the run"
	echo "	--norun				Set if you don't want to immediately run gamess"
	echo "	-n NODES | --nodes NODES	Specify number of nodes gamess will be running on"
	echo "	-ppn PROC_PER_NODE | "
	echo "	--proc_per_node PROC_PER_NODE	Specify number of processes/cores per node" 
	echo "					(if not specified, number of cpu cores is used,"
	echo "					as found in /proc/cpuinfo)"
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
	work_dir=${HOME} # location where gamess input file gets copied to
	nodes=1
	ppn=${cpu_cores}
	verbose=false
	interactive=false
	run_gamess=true
	version=01
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
			run_gamess=false
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

gamess_input_name="c8h10-cct-mp2.inp"
input_file_path="${GAMESS_INPUTS_LOC}/${gamess_input_name}"

dest_path=${work_dir}

# output for testing
echo "Input file name: ${gamess_input_name}"
echo "Full path: ${input_file_path}"
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
if [[ -f "${GAMES_EXE_DIR}/rungms" ]]; then
	cp ${GAMES_EXE_DIR}/rungms ${dest_path}
	echo "rungms copied over to ${dest_path}"
else
	echo "Error: ${GAMES_EXE_DIR}/rungms does not exist"
	exit 1
fi


# go to working directory to run gamess
cd ${work_dir}
echo "work dir: ${work_dir}"

# to allow access for mpiexec.hydra
export PATH=${PATH}:${MPI_LOC}

echo "Running appsigcheck..."
${EXECS_LOC}/bin/appsigcheck.sh ./rungms

if [[ "${run_gamess}" == "true" ]]; then
	echo "Running gamess..."
	./rungms ${gamess_input_name} ${version} ${nodes} ${ppn}
	echo "Complete! Gamess has been run, output in ${work_dir}"
fi

# if user sets interactive flag, starts up bash at end
if [[ "${interactive}" == "true" ]]; then
	/bin/bash
fi












