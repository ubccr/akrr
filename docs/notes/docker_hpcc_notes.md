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






