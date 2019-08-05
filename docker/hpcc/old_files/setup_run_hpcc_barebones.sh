#!/bin/bash
#set -x
# initializing some variables
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


# setting default values for variables
set_defaults()
{
	work_dir=$(mktemp -d $PWD/tmp.XXXXXXXXXX) # location where input file will get copied to
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
		--norun)
			run_hpcc=false
			;;
		-n | --nodes)
			shift
			nodes=${1}
			;;
		-ppn | --proc_per_node)
			shift
			ppn=${1}
			;;
		*)
			echo "Error: unrecognized argument"
			usage
			exit 1
			;;
	esac
	shift # to go to next argument
done

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
${EXECS_LOC}/bin/appsigcheck.sh ${HPCC_EXE_FULL_PATH}
wait

#echo "CPU Info inside container"
#cat /proc/cpuinfo

#echo "Cgroup inside container"
#${MPI_LOC}/mpirun -np ${ppn} $SCRIPTS_LOC/cat_cgroup.sh

export KMP_AFFINITY="verbose"

#export I_MPI_HYDRA_BOOTSTRAP="ssh"
# running hpcc with mpirun, where -np is number of cores for the machine
if [[ "${run_hpcc}" == "true" ]]; then
	echo "Running hpcc..."
	${HPCC_EXE_FULL_PATH}
	wait
	echo "Complete! hpccoutf.txt is in ${work_dir}"
	echo "cat output to standard out:"
	cat hpccoutf.txt
fi

