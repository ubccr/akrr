# Directory for HPCC Appkernel Docker

This directory has all the files needed to create a Docker image for the HPCC Appkernel. The binary is not in the repository, that must be set up once you clone the repo. If you want to create the Dockerfile, you need to get the binary.

Hpcc version used when I was making the Docker: hpcc-1.5.0


## Guide to getting the HPCC binary set up from UB-HPC resource

So, you can basically follow the steps for HPCC Deployment for normal AKRR, since that gets you the binary. 

```bash
# Everything will be done in the execs directory, we'll use environment variable $EXECS_DIR
# So for example EXECS_DIR would be /path/to/proper/dir with execs being at end
# The execs directory should be from the git repo, it contains bin and misc/hpcc (05/29/19)

# Go to executable directory
cd $EXECS_DIR/execs

# Load modules (dependent on individual situation)
module load intel/18.3
module load intel-mpi/2018.3
module load mkl/2018.3
 
# We need to make bunch of interfaces to mkl library, unfortunately they are not precompiled
# Lets compile them in $EXECS_DIR/execs/libs/<interface_name>
# and install in $EXECS_DIR/execs/libs/lib
mkdir -p $EXECS_DIR/execs/libs
mkdir -p $EXECS_DIR/execs/libs/lib

# make fftw2x_cdft interface to mkl
cd $EXECS_DIR/execs/libs
cp -r $MKLROOT/interfaces/fftw2x_cdft ./
cd fftw2x_cdft
make libintel64 PRECISION=MKL_DOUBLE interface=ilp64 MKLROOT=$MKLROOT INSTALL_DIR=$EXECS_DIR/execs/libs/lib

# make FFTW C wrapper library
cd $EXECS_DIR/execs/libs
cp -r $MKLROOT/interfaces/fftw2xc ./
cd fftw2xc
make libintel64 PRECISION=MKL_DOUBLE MKLROOT=$MKLROOT INSTALL_DIR=$EXECS_DIR/execs/libs/lib

 
# get the code
cd $EXECS_DIR/execs
wget http://icl.cs.utk.edu/projectsfiles/hpcc/download/hpcc-1.5.0.tar.gz
tar xvzf hpcc-1.5.0.tar.gz
cd hpcc-1.5.0
# Prepare makefile
# HPCC reuses makefiles from High Performance Linpack (thus do not forget to get to hpl directory)
# you can start with something close from hpl/setup directory
# or start from one of our make file
# put make file into hpl directory
cd hpl

```

Up to this point everything is the same.
You could continue that deployment if you wanted.
Below is the change that (I think?) optimizes HPCC for avx and such instructions.
See original\_notes.md for some more information.
So you can use either this new make thing or the old one, it should work either way.
(Though the wget may not be accurate once this branch gets merged and such)

```bash
# now we need to get the proper make file
# the major difference is that its CCFLAGS line is
# CCFLAGS      = $(HPL_DEFS) -restrict -O3 -ansi-alias -ip -axCORE-AVX512,CORE-AVX2,AVX 
# not just -restrict and -O3
wget https://raw.githubusercontent.com/hoffmaps/akrr/intern_work/docker/hpcc/execs/misc/hpcc/Make.intel64_avxflags
# so this (in theory) checks what the optimal option is for your system of the avxs

# go back to hpcc-1.5.0 root dir
cd ..
make arch=intel64_avxflags
# then the hpcc appears in that directory
```
*Note: It should be fine if you use the normal make file that is given in the regular akrr. I just have this since I figured we should optimize it for avx instructions and such*

Now you just need to download the entire directory that has hpcc in it.

*Note: This might not be optimized in terms of space, I'm unsure exactly which files are or are not needed to run HPCC*

Then all you have to do is put the hpcc-1.5.0 into the execs directory and you should be able to build and run the Docker. If you are using a different version of hpcc you might need to change the HPCC\_EXE\_FULL\_PATH variable in the Dockerfile.

## Setup of this directoy
- Dockerfile - the thing that makes the Docker image
- execs - location of akrr scripts and hpcc binary
	- bin - location of akrr help scripts
	- misc - location of file to make the hpcc binary with (in my case)  
	- hpcc-1.5.0 - directory with the hpcc binary to run (self provided if getting this from git)
- inputs/hpcc - location of various possible inputs for hpcc
- scripts - location of run script called when docker image is run
- original\_notes.md - original notes as I was setting up the docker image - might be helpful for some more info



