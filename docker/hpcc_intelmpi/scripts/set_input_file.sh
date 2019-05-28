#!/bin/bash

# input file is argument 1 in this case if it's right after docker argument
HPCCINF=$1 

# location where hpcc is in (and where hpccinf.txt should go
HPCCDIR="/home/hpccuser/execs/hpcc-1.5.0"
cd $HPCCDIR
echo "Hpcc directory: " $HPCCDIR

INFILE="default_hpccinf.txt"
echo "If you don't want to have an input file and just use the image straightup, enter nofile or nothing at all"

# to give the option of not having an input file
if [ "$HPCCINF" = "nofile" ]
then
	echo "Entering container straightup without input file"
	/bin/bash
	exit 9999
fi

echo "You input the following file: " $HPCCINF

# checks if the given file is not the default file - need to change file name in this case
if [ "$HPCCINF" != "default" ]
then
	# checks if inputs directory exists (assumed to be mounted)
	if [ ! -d "./inputs" ]
	then
        	echo "Directory /home/hpccuser/execs/hpcc-1.5.0/inputs does not exist."
        	echo "Did you mount it properly?"
        	echo "Try running with -v /path/to/your/inputs:$HPCCDIR/inputs"
        	exit 9999
	fi
	# sets the given file to be the one being copied over
	INFILE=$HPCCINF
	cd ./inputs # assumes volume is set up properly
fi
# if its the default file don't need to go into inputs directory

# checks if the file exists and has read permissions
if [ -r "$INFILE" ]
then
	cp $INFILE $HPCCDIR/hpccinf.txt
	echo "The file $INFILE is now hpccinf.txt in the same directory as hpcc"
else
	echo "File does not exist in inputs or does not have read permissions"
	exit 9999
fi

cd $HPCCDIR

# this allows us to go back into bash (nice for debugging and such)
/bin/bash
