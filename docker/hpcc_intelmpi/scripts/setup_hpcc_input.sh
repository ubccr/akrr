#!/bin/bash

# initial statements for testing
echo "Arguments passed in: $@"
echo "Number of arguments: $#"
num_args="$#"
temp="hpcc/"
hpcc_inputs_dir="$inputsLoc$temp"
echo "hpcc_inputs_dir: " $hpcc_inputs_dir

# gets the number of cores of this machine
cpu_cores="$(grep ^cpu\\scores /proc/cpuinfo | uniq |  awk '{print $4}')"
echo "Number of cores: $cpu_cores"

# help text essentially
usage()
{
    	echo "usage: setup_hpcc.sh [-v] [-n NODES] [-ppn PROC_PER_NODE] [-h]"
	echo ""
    	echo "Options:"
    	echo "	-h | --help			Display help text"
	echo "	-v | --verbose			Increase verbosity of output"
	echo "	-n NODES | --nodes NODES	Specify number of nodes hpcc will be running on"
	echo "	-ppn PROC_PER_NODE | "
	echo "	--proc_per_node PROC_PER_NODE	Specify nymber of processes/cores per node"
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





# defaults, may change with implementation of getting number of cores from computer
nodes=1
ppn=1

if [ "$num_args" == "0" ]; then
	echo "No arguments passed in. Basing input file off of cpu cores"
	nodes=1
	ppn=$cpu_cores
fi

verbose=false

# loop through arguments
while [ "$1" != "" ]; do
	case $1 in
		-h | --help)
			usage
			exit
			;;
		-v | --verbose)
			verbose=true
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
			echo "unrecognized argument"
			usage
			exit 1
			;;
	esac
	shift # to go to next argument
done


echo "ppn: " $ppn
echo "nodes: " $nodes
echo "verbose: " $verbose

validate_number $nodes
validate_number $ppn

# setting up paths to do the copying
temp="x"
hpcc_input_name="hpccinf.txt.$ppn$temp$nodes"
input_file_path="$hpcc_inputs_dir$hpcc_input_name"

temp="/hpccinf.txt"
dest_path=$HOME$temp

echo "Input file name: $hpcc_input_name"
echo "Full path: $input_file_path"
echo "Destination path: $dest_path"

if [ -f "$input_file_path" ]; then
	cp $input_file_path $dest_path
	echo "$hpcc_input_name copied over to $dest_path"
else
	echo "Error: $input_file_path does not exist"
	exit 1
fi







echo "Hello reached the end"


