## Notes on Docker container with hpcc to work

- Well, I can't really find an hpcc (high performance compute challenge) image online anywhere, perhaps have to install hpcc from scratch? 
	- most hpcc images are about "High Performance Compute Clusters"

- Update: will be doing akrr hpcc test on ub-hpc, somehow compile things and then ultimately the goal is to get them in our own docker container so we can use it there


### The plan
- Transfer all the files from ub-hpc to local machine
- Start Docker image with just centos
- Get the hpcc files/executables into that container somehow
- Try and get that to work somehow
- ???
- Profit


- First I'm trying to run it locally. Of course that doesn't work, since I'm missing some shared libraries...? The error when I just try to execute it is

```bash
./hpcc: error while loading shared libraries: libmpifort.so.12: cannot open shared object file: No such file or directory

```
So the search for the libraies begins. From what I can tell there are maximum 3 libraries, sorta given in the Installing HPCC part of the AKRR_HPCC_Deployment.md file. It's based off of these lines: 

```bash
module load intel/18.3
module load intel-mpi/2018.3
module load mkl/2018.3
```
Done some snooping and (seemingly) found the mpi and mkl libraries at the link: https://software.intel.com/en-us/articles/installing-intel-free-libs-and-python-yum-repo
it tells you how to get these things, so I'm gonna try and do that now

Keeping track of what I'm doing for MKL first

```bash
# Getting the repository
sudo yum-config-manager --add-repo https://yum.repos.intel.com/mkl/setup/intel-mkl.repo

# Importing the gpg public key
sudo rpm --import https://yum.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS-2019.PUB

# yum install <COMPONENT>-<VERSION>.<UPDATE>-<BUILD_NUMBER> to install a particular version
# So since I'm trying to do mkl/2018.3, I'll do the following, based on the chart they give at the site
sudo yum install intel-mkl-2018.3-051

```
No problems happened. Now doing the same for the mpi

```bash
sudo yum-config-manager --add-repo https://yum.repos.intel.com/mpi/setup/intel-mpi.repo

sudo yum install intel-mpi-2018.3-051
```
No problems happened with the installation, but the same error is given as above, with the error loading shared libraries

Update: I was running it wrong, I believe you need to run it as follows:

```bash
mpirun -np 4 ./hpcc
```
On vortex, I only needed to load the mpi module to run hpcc successfully

I managed to get mpirun being recognized by adding the directory to the path. In my case it was

```bash
export PATH=$PATH:/opt/intel/impi/2018.3.222/bin64
```

This added all the mpi execs stuff to the path so I could do mpirun and such.
Success!

```bash
mpirun -np 4 ./hpcc
cat hpccoutf.txt
```
Gave good looking results! Next step: do it on docker.


