#!/bin/bash

# gets the number of cores of this machine
cpu_cores="$(grep ^cpu\\scores /proc/cpuinfo | uniq |  awk '{print $4}')"
if [[ "$cpu_cores" == "1" ]]; then
	echo "Detected only one core. Counting processors instead"
	cpu_cores="$(grep "processor" /proc/cpuinfo | wc -l)"
fi

echo "Number of cores detected: $cpu_cores"
echo "(used for determining what to use for -np flag in mpirun)"

hpcg_inputs_dir=$inputsLoc


usage()
{
	echo "usage: setup_run_hpcg.sh [-h] [-i] [--norun] ( [-n NODES] [-ppn PROC_PER_NODE] )"
	echo ""
	echo " Options:"
    	echo "	-h | --help			Display help text"
	#echo "	-v | --verbose			increase verbosity of output"
	echo " 	-i | --interactive		Start a bash session after the run (use with -it in docker run"
	echo "	--norun				Set if you don't want to immediately run hpcg"
	echo "	**-n NODES | --nodes NODES	Specify number of nodes hpcg will be running on"
	echo "	**-ppn PROC_PER_NODE | "
	echo "	--proc_per_node PROC_PER_NODE	Specify nymber of processes/cores per node" 
	echo "					(if not specified, number of cpu cores is used,"
	echo "					as found in /proc/cpuinfo)"
	echo "					- used to determine -np VAL for mpirun"
	echo " ** = not implemented. These options do nothing."

}

# ppn is used to set -np flag with mpirun
set_defaults()
{
	work_dir=$HOME # location where hpcg input file gets copied to
	nodes=1
	ppn=$cpu_cores
	verbose=false
	interactive=false
	run_hpcg=true
	exeName="xhpcg_avx" # determining optimal hpcg execution (checks for avx, avx2, or skx)
}

set_defaults

# counting if the processor supports avx2 or skx
countAVX2="$(grep -oc 'avx2' /proc/cpuinfo)"
countSKX="$(grep -oc 'skx' /proc/cpuinfo)"
echo "avx2: $countAVX2"
echo "skx: $countSKX"

# if find any, sets the proper executable name (can still be overriden
if [[ "$countAVX2" -gt "0" ]]; then
	exeName="xhpcg_avx2"
fi

if [[ "$countSKX" -gt "0" ]]; then
	exeName="xhpcg_skx"
fi 


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
			run_hpcg=false
			;;
		#-n | --nodes) # unsure how these would be implemented
		#	shift
		#	nodes=$1
		#	;;
		#-ppn | --proc_per_node)
		#	shift
		#	ppn=$1
		#	;;
		*)
			echo "Error: unrecognized argument"
			usage
			exit 1
			;;
	esac
	shift # to go to next argument
done

echo "nodes: $nodes"
echo "ppn: $ppn"
echo "interactive: $interactive"

# using environment variables
# setting up paths to copy file over
hpcg_input_name="hpcg.dat"
input_file_path="$hpcg_inputs_dir$hpcg_input_name"

dest_path="$work_dir/$hpcg_input_name"

echo "Input file name: $hpcg_input_name"
echo "Full path: $input_file_path"
echo "Destination path: $dest_path"

# checks if file exists
if [[ -f "$input_file_path" ]]; then
	cp $input_file_path $dest_path
	echo "$hpcc_input_name copied over to $dest_path"
else
	echo "Error: $input_file_path does not exist"
	exit 1
fi

# by default working dir is home of hpcguser
cd $work_dir
echo "work dir: $work_dir"

# source to connect up the mkl libraries
source /opt/intel/bin/compilervars.sh intel64 -platform linux
export OMP_NUM_THREADS=1 # based on HPCG Development thing

# finally sets hpcgLocation (location of hpcg executable chosen)
hpcgLoc=$binLoc/$exeName


# running hpcg and catting output
if [[ "$run_hpcg" == "true" ]]; then
	echo "Using $exeName to run hpcg"
	echo "Running hpcg..."
	$mpiLoc/mpirun -np $ppn $hpcgLoc
	echo "Complete! Outputs are in $work_dir"
	echo "cat output to standard out:"
	echo "hpcg_log ###################"
	cat hpcg_log*
	echo 
	echo ".yaml #################"
	cat *.yaml
fi


# if user sets interactive flag, starts up bash at end
if [[ "$interactive" == "true" ]]; then
	/bin/bash
fi



