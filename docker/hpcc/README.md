## Files for creating HPCC Docker image (uses Intel-mpi)
THIS README IS NOT COMPLETE. I used it mainly as notes while figuring things out

HPCC - High Performance Compute Competition, a benchmarking technique

Intel-mpi version used: 2018.3

### My process I used to make the binary executable for HPCC
See bottom of readme for updated version
```bash
# This process is basically the same as the AKRR_HPCC_Deployment.md process
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
# HPCC reuses makefiles from High Performance Linpack (thus do not forget to get to hpc directory)
# you can start with something close from hpl/setup directory
# or start from one of our make file
# place Make.intel64_hpcresource file to hpcc-1.4.2/hpl
cd hpl

wget https://raw.githubusercontent.com/ubccr/akrr/master/akrr/appker_repo/execs/misc/hpcc/Make.intel64_hpcresource
# edit Make.intel64_hpcresource to fit your system 
# if you have intel based system with intel compilers and intel-mpi
# most likely you don't need to change it
 
# compile hpcc in hpcc-1.5.0 root directory
cd ..
make arch=intel64_hpcresource
# if it is compiled successfully hpcc binary should appear in hpcc-1.5.0 directory

# at that point you can take the entire execs directory with binary included, (keeping it named execs)
#and you can proceed building and running the Dockerfile, assuming you put the directory 
#into the appropriate folder

# With my testing, if you'd like to really conserve space, you only need to copy the hpcc-1.5.0 in, you don't need all the libs stuff that was used to compile hpcc
```




```bash
# building the Dockerfile
docker build -t hpcc_intelmpi_centos7 .

# running it (interactively)
docker run -it hpcc_intelmpi_centos7
```

### The thought/plan

When run is being done, the user must mount the location of the input file they want to use, like so

```bash
docker run -it -v /path/to/inputs:/home/hpccuser/execs/hpcc-1.5.0/inputs hpcc_intelmpi_centos7
# if you're using hpcc inputs from this repo, the statement would be
docker run -it -v [path to akrr]/akrr/akrr/appker_repo/inputs/hpcc:/home/hpccuser/execs/hpcc-1.5.0/inputs hpcc_intelmpi_centos7 [input file to use]

```
This mount must happen, otherwise there is an error, since the script relies on inputs existing
Alternatively, if you don't want to run a file immediately, you can just not put anything and it will just put you into the directory.

NOTE: Permissions on the input directory must be correct, since the permissions are copied into the docker container. Do:

```bash
# for your inputs directory
chmod a+x [inputs dir]
 
# for all files in your inputs directory
chmod a+rw *
```

As of 5/24/19, you can do all this and the docker container will be set up with the correct input file for doing mpirun etc...

Next goal: be able to run the whole mpirun stuff from completely outside of the container just at the run instruction

## UPDATE - modifying how file system is set up

```bash
# Will be empty to allow user to mount things there
/home/hpccuser/

# location of execs directory
/opt/appker/ 
# Dockerfile has it as execsLoc for easy modification

# location of some default inputs
/usr/local/appker/inputs/hpcc/
# Dockerfile has it as inputsLoc for easy modification
# hpccLoc is the path directly to the hpcc executable, so to run it from any given directory you can do (using default example)
mpirun -np 4 $hpccLoc


```
Notes:
- the hpcc executable looks for hpccinf.txt in the directory where you are, so that needs to be present wherever you're running it
- I set up the tar and everything, so now the execs and inputs should be as described above
- The setup script in _scripts_ correctly copies over input files from the input directory to the home directory for use
	- The system: you enter the number of nodes (n) and processes per node (ppn) and then the script copies over _hpccinf.txt.[ppn]x[n]_ to the home directory as _hpccinf.txt_
- It appears that the only way to both run the python file immediately and accept arguments from the command line of docker run is using ENTRYPOINT ["python", hardcoded/path/to/scripts/setupscript]
	- If we want to use ENV $scriptsLoc we need to use the shell entrypoint format (I think)
	- If we want to pass in arguments from docker run we need to have this form of entrypoint
	- So for now I just have it as above in the Dockerfile, perhaps that can be figured out later too
- UPDATE: Current strategy being used
	- Setting working directory to the scripts place
	- Calling the python script from the entrypoint script
	- At end of entrypoint script going back to the home working directory and starting bash

End of Day Notes:
- So I got things working with the copying over script. I can send through arguments through docker run and it can copy things over pretty easily
- For tomorrow:
	- More convenience arguments for the python setup script? (see script for suggestions)
	- Option to run mpirun straightup from docker run?
	- Slight cleanup of script?
- UPDATE: Not using python anymore to read arguments, will do only bash script
- Update: made bash script, seems to be all set up with basic functionality, now need to make some new hpcc input files for 1, 2, 4, and 6 cores

- Update: Bash script works fine, added new files and made it so by default it goes for number of cores in terms of determining ppn
- Next steps:
	- Running a script to make sure about version somehow...? in execs
	- Removing execs directory bc don't want to have a binary in the git repo
	- Including instructions in this README about how to compile hpcc binary wherever it is

- Update:
	- I moved hpcc-1.5.0 back into execs, then added ./execs/hpcc-1.5.0 to the .gitignore so that we don't have the binary in the repo
	- Added the things I did to compile hpcc on vortex
	- Changed setup script to cat hpccoutf.txt after the run

- Update: changed initial script to count processors instead of cores if cores turns out to be 1

- Notes on how flags work:
	- It appears that if you want to enter into the docker container and start playing around there, you need both -it on docker run AND -i on the script
	- Having just one or the other does not start interactive session

Notes on trying to compile HPCC for avx, avx2, skx:
```bash
# similar start setup
# Go to Application Kernel executable directory
cd $AKRR_APPKER_DIR/execs
# Environment variable $AKRR_APPKER_DIR should be setup automatically during initial
# deployment to HPC resource

# Load modules
module load intel/18.3
module load intel-mpi/2018.3
module load mkl/2018.3

# We need to make bench of interfaces to mkl library, unfortunately they are not precompiled
# Lets compile them in $AKRR_APPKER_DIR/execs/libs/<interface_name>
# and install in $AKRR_APPKER_DIR/execs/libs/lib
mkdir -p $AKRR_APPKER_DIR/execs/libs
mkdir -p $AKRR_APPKER_DIR/execs/libs/lib

# make FFTW C wrapper library
cd $AKRR_APPKER_DIR/execs/libs
cp -r $MKLROOT/interfaces/fftw2x_cdft ./
cd fftw2x_cdft
make libintel64 PRECISION=MKL_DOUBLE interface=ilp64 MKLROOT=$MKLROOT INSTALL_DIR=$AKRR_APPKER_DIR/execs/libs/lib

# get the code
cd $AKRR_APPKER_DIR/execs
wget http://icl.cs.utk.edu/projectsfiles/hpcc/download/hpcc-1.5.0.tar.gz
tar xvzf hpcc-1.5.0.tar.gz
cd hpcc-1.5.0

# Prepare makefile
# HPCC reuses makefiles from High Performance Linpack (thus do not forget to get to hpc directory)
# you can start with something close from hpl/setup directory
# or start from one of our make file
# place Make.intel64_hpcresource file to hpcc-1.4.2/hpl
cd hpl




```

Looking for things that might show how to compile hpcc for avx vs avx2 vs skx:
Best thing so far (doesn't give clear answer but its something):
https://www.chpc.utah.edu/documentation/white_papers/skylake.pdf
Found this in the thing above:

For the Skylake and Broadwell, we have built HPCC 1.5.0 with Intel 2017.4 compilers and 
corresponding Intel MKL and MPI using the following compiler optimization flags: 
-O3 -ansi-alias -ip -axCORE-AVX512,CORE-AVX2,AVX,SSE4.2 -restrict

Of course this does not work with the 'make' that we are doing

Update: I think perhaps we need to go into the Make.intel64_hpcresource and change the Compilers/linkers - Optimization flags portion, so I'm going to try that now

It did seem to change something... since the old hpcc is 63M and the new one is 64M
So I made a couple binaries
hpcc\_[with extension]
	- coreAVX[2 | 512] - compiled with flags $(HPL_DEFS) -restrict -O3 -axCORE-AVX[2 | 512]
	- mAVX[2| 512] - compiled with flags $(HPL_DEFS) -restrict -O3 -mavx -mno-avx2 -mno-avx512f (or proper ones 

- the ansi-alias and -ip i don't know what they're doing, but maybe i'll try them later too
- It seems that -axCORE-AVX does not work with ax - trying -axAVX : that seems to work!
- For AVX, -axCORE-AVX2 did work, as did -axCORE-AVX512
- For some reason when I make it multiple times in the same directory, it doesn't actually care about the CCFLAGS, so I'm just making a new execs directory and doing all the building every time for each individual one 
- The mno options above failed with all sorts of combinations, so I'll just specify the -mavx and such instead, hopefully I don't need to disable

- mavx2 did not work, suggested I use -march=core-avx2, check out this website it gave some more info
https://software.intel.com/en-us/articles/performance-tools-for-software-developers-intel-compiler-options-for-sse-generation-and-processor-specific-optimizations
- ^^^ Yeah this website is the bomb, it also gives the options that I used for the core stuff

Lets take a look at the flags used in the paper:

```bash
# the flags used were:
-O3 -ansi-alias -ip -axCORE-AVX512,CORE-AVX2,AVX,SSE4.2 -restrict

```
Lets look at what these mean

__-O3__ : turns on a bunch of optimizations to try and improve performance or code size (see https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html)

__-ansi-alias__ : enables the use of ANSI aliasing rules in optimizations, so if your code follows ansi aliasability rules, the compiler can optimize more aggressively (see https://software.intel.com/en-us/cpp-compiler-developer-guide-and-reference-ansi-alias-qansi-alias and https://www.ibm.com/support/knowledgecenter/en/SSLTBW_2.3.0/com.ibm.zos.v2r3.cbcpx01/optalias.htm

__-ip__ : enables additional interprocedural optimizations for single-file compilation. (see https://software.intel.com/en-us/cpp-compiler-developer-guide-and-reference-ip-qip and https://en.wikipedia.org/wiki/Interprocedural_optimization)

__-axCORE-AVX512,CORE-AVX2,AVX,SSE4.2__ : check at execution time what the best code path is for that processor, so AVX512 will be chosen for processors that support it, and AVX will be chosen for processors that support that but not AVX2 or AVX512 (see https://software.intel.com/en-us/articles/performance-tools-for-software-developers-intel-compiler-options-for-sse-generation-and-processor-specific-optimizations) 

__-restrict__ : enables pointer disambiguation to further optimize (see https://software.intel.com/en-us/node/734225 and https://en.wikipedia.org/wiki/Restrict)






- So -mavx2 is instead -march=core-avx2, and -mavx512 is instead -march=avx512

- Do we want to do some sort of march or mtune to tune things?

- Also looks like -msse2 is the default on Linux, perhaps revise the input?


This website seems to give some information regarding the various flags to potentially enable avx
https://gcc.gnu.org/onlinedocs/gcc/x86-Options.html


## Updated notes on how to compile HPCC so that it has AVX stuff
```bash

s process is basically the same as the AKRR_HPCC_Deployment.md process
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


###Most updated docker image: pshoff/hpcc_benchmark:v03 (05/30/19)
###Older images: 
- hpcc_test:v01 (05/29/19) 
- hpcc_test:v02 (05/30/19) - Doesn't have the check for 1 core that v03 has








