# Directory for files for ior/mdtest Docker image

This directory has the files needed for running ior and mdtest (both are contained in the same Docker)

However, it does not have the binaries or the libraries needed to run, which needs to be obtained when you.

### Getting binaries and libraries
You can follow the steps given in the IOR\_Deployment notes to compile ior (and mdtest).
Then, download the main directory, I used sftp, (ior-3.2.0) and put it in the execs here.

So your execs directory should have ior-3.2.0 and bin, which has the appsigcheck stuff. 

One thing that ior also needs is a bunch of libraries. Unsure about which ones are or are not exactly needed, but I had these libraries and it worked fine:

(In my lib directory)
```text 
libgpfs.so    libhdf5_hl.la     libhdf5_hl.so.10.2.2  libhdf5.so         libimf.so      libsvml.so
libhdf5.a     libhdf5_hl.so     libhdf5.la            libhdf5.so.10      libintlc.so.5
libhdf5_hl.a  libhdf5_hl.so.10  libhdf5.settings      libhdf5.so.10.3.2  libirng.so
```
This should all be in a new directory named lib
### In UB-HPC where to find these libraries
All the hdf5 libraries you can find in the HDF5 temp directory when you're going through the process of compiling ior (the section of installing HDF5)

```bash
# on vortex

# libgpfs.so
# using locate I found it here
/usr/lib64/libgpfs.so

# libimf.so libsvml.so libirng.so libintlc.so.5
$ module load intel/18.3
 
The Intel 18.3 compilers are in your path. This is adequate for compiling and running most codes.
Source compilervars.sh for more features including the debugger. 

$ echo $LD_LIBRARY_PATH

/util/academic/intel/18.3/lib/intel64:/util/academic/hdf5/1.8.15p1/lib:/util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mpi/intel64/lib:/util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mpi/mic/lib

$ cd /util/academic/intel/18.3/lib/intel64

# then all the libraries you need should be there...
```

To run ior or mdtest, use the flags --run-ior or --run-mdtest respectively, specify the number of processes with -ppn (used with mpiexec)

Note: running ior through Docker, since you're working on one node

For running ior/mdtest with singularity, since we want to try and run it on 2 nodes, use the Dockerfile_singularity. This is because it runs just the ior/mdtest, so you can do mpirun [singularity image] in the akrr script. 

## Setup of this Directory
- Dockerfile - to use for normal ior docker with mpirun inside              
- execs - location of the akrr help scripts and the ior/mdtest binaries
	- bin - akrr help scripts
	- ioe-3.2.0 - location of ior/mdtest binaries               
- lib - contains all the libraries needed by ior and mdtest (see above)
- Dockerfile_singularity - use this docker to make the docker to use for running it through singularity
- hdf5_pnetcdf_libs - location of hdf5 and pnetcdf from when we made the binary on ubhpc  
- original_notes.md - notes I had on getting ior and mdtest working
- scripts - the run scripts used in the different docker files



