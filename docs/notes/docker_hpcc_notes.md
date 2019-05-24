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

Started docker container with centos:7 on it, linked up the hpcc_files directory to /root/hpcc_files in the docker image
Then did the following process to set up intel mpi to be able to run it

```bash
# in docker image
# copying over files
cd /root
mkdir appker
cp -r hpcc_files/ appker/
cd appker/hpcc_files/
cp -r execs ../
cd ..
rm -rf hpcc_files

# so now the hpcc executable should be in the following directory
cd /root/appker/execs/hpcc-1.5.0

# installing intel mpi
yum-config-manager --add-repo https://yum.repos.intel.com/mpi/setup/intel-mpi.repo

rpm --import https://yum.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS-2019.PUB

yum -y install intel-mpi-2018.3-051

# as expected, mpirun still isn't found at this point
# add it to the path 
export PATH=$PATH:/opt/intel/impi/2018.3.222/bin64
# also added it to .bashrc for root so that it's permanently in the path


# test it on the headnode
mpirun -np 4 ./hpcc
cat hpccoutf.txt

```

Then I make a docker image from that
```bash
# in original terminal
docker commit [image_name]
# get id of image since it has <none> as its name right now
docker image ls
docker tag [image_id] hpcc_intelmpi_centos7 [optinal tag to add, default is 'latest']
```

So I was able to make things work with adjusting the image and whatnot, now I'll make one with a Dockerfile so it's better documented






