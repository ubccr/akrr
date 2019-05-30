## Files for creating HPCC Docker image (uses Intel-mpi)

HPCC - High Performance Compute Competition, a benchmarking technique

Intel-mpi version used: 2018.3

### My process I used to make the binary executable for HPCC
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






