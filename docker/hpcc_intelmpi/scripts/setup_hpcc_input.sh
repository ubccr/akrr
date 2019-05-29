#!/bin/bash

# initial statements for testing
echo "Arguments passed in: " $@
echo "Number of arguments: " $#

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

# defaults, may change with implementation of getting number of cores from computer
nodes=1
ppn=1

verbose=false


echo $0
while [ "$1" != "" ]; do
	case $1 in
		-h | --help)
			usage
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
			;;


	esac
	shift # to go to next argument
done



