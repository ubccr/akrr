# Making HPCC Appkernel Docker Container

Here are logs on how a docker image for the HPCC appkernel was made.

The strategy is to compile hpcc on system with Intel compilers and copy them to docker container.

Some specs:
* HPCC version: hpcc/1.5.0
* Compilers: intel/2018.3
* MPI: intel-mpi/2018.3
* BLAS/FFW: mkl/2018.3


## Compiling HPCC binary

So, you can basically follow the steps for HPCC Deployment for normal AKRR, since that gets you the binary. 

```bash
# Everything will be done in the execs directory, we'll use environment variable $EXECS_DIR
# So for example EXECS_DIR would be /path/to/proper/dir with execs being at end
# The execs directory should be from the git repo, it contains bin and misc/hpcc (05/29/19)

# Go to executable directory
cd $AKRR_APPKER_DIR/execs

# Load modules (dependent on individual situation)
module load intel/18.3
module load intel-mpi/2018.3
module load mkl/2018.3
 
# We need to make bunch of interfaces to mkl library, unfortunately they are not precompiled
# Lets compile them in $EXECS_DIR/execs/libs/<interface_name>
# and install in $EXECS_DIR/execs/libs/lib
mkdir -p $AKRR_APPKER_DIR/execs/libs
mkdir -p $AKRR_APPKER_DIR/execs/libs/lib

# make fftw2x_cdft interface to mkl
cd $AKRR_APPKER_DIR/execs/libs
cp -r $MKLROOT/interfaces/fftw2x_cdft ./
cd fftw2x_cdft
make libintel64 PRECISION=MKL_DOUBLE interface=ilp64 MKLROOT=$MKLROOT INSTALL_DIR=$AKRR_APPKER_DIR/execs/libs/lib

# make FFTW C wrapper library
cd $AKRR_APPKER_DIR/execs/libs
cp -r $MKLROOT/interfaces/fftw2xc ./
cd fftw2xc
make libintel64 PRECISION=MKL_DOUBLE MKLROOT=$MKLROOT INSTALL_DIR=$AKRR_APPKER_DIR/execs/libs/lib

 
# get the code
cd $AKRR_APPKER_DIR/execs
wget http://icl.cs.utk.edu/projectsfiles/hpcc/download/hpcc-1.5.0.tar.gz
tar xvzf hpcc-1.5.0.tar.gz
cd hpcc-1.5.0
# Prepare makefile
# HPCC reuses makefiles from High Performance Linpack (thus do not forget to get to hpl directory)
# you can start with something close from hpl/setup directory
# or start from one of our make file
# put make file into hpl directory
cd hpl
# now we need to get the proper make file
# the major difference is that its CCFLAGS line is
# CCFLAGS      = $(HPL_DEFS) -restrict -O3 -ansi-alias -ip -xCORE-AVX512 
# not just -restrict and -O3
wget https://raw.githubusercontent.com/ubccr/akrr/master/docker/hpcc/execs/misc/hpcc/Make.intel64_skx

# go back to hpcc-1.5.0 root dir
cd ..
make arch=intel64_skx
mv hpcc hpcc_skx
make arch=intel64_skx clean

# now same for avx2
cd hpl
wget https://raw.githubusercontent.com/ubccr/akrr/master/docker/hpcc/makefiles/Make.intel64_avx2
cd ..
make arch=intel64_avx2
mv hpcc hpcc_avx2
make arch=intel64_avx2 clean
# now same for avx
cd hpl
wget https://raw.githubusercontent.com/ubccr/akrr/master/docker/hpcc/makefiles/Make.intel64_avx
cd ..
make arch=intel64_avx
mv hpcc hpcc_avx
make arch=intel64_avx clean
# now same for sse2
cd hpl
wget https://raw.githubusercontent.com/ubccr/akrr/master/docker/hpcc/makefiles/Make.intel64_sse2
cd ..
make arch=intel64_sse2
mv hpcc hpcc_sse2
make arch=intel64_sse2 clean

# optimized for multiple architectures
cd hpl
Make.intel64_multarch
wget https://raw.githubusercontent.com/ubccr/akrr/master/docker/hpcc/makefiles/Make.intel64_multarch
cd ..
make arch=intel64_multarch

# then the hpcc appears in that directory
cd ..
ln -s hpcc-1.5.0 hpcc
```

Copy binaries to $(AKRR_SRC)/docker/hpcc/bin
```bash
mkdir $(AKRR_SRC)/docker/hpcc/bin
cd $(AKRR_SRC)/docker/hpcc/bin
scp $USER@hpcresource:$AKRR_APPKER_DIR/execs/hpcc/hpcc* ./
```

## Building Docker Container

```bash
# in $(AKRR_SRC) directory
docker build
```
- Dockerfile - the thing that makes the Docker image
- execs - location of akrr scripts and hpcc binary
	- bin - location of akrr help scripts
	- misc - location of file to make the hpcc binary with (in my case)  
	- hpcc-1.5.0 - directory with the hpcc binary to run (self provided if getting this from git)
- inputs/hpcc - location of various possible inputs for hpcc
- scripts - location of run script called when docker image is run
- original\_notes.md - original notes as I was setting up the docker image - might be helpful for some more info



