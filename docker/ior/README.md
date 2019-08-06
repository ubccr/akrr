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

/util/academic/hdf5/1.8.15p1/lib

### In UB-HPC where to find these libraries
All the hdf5 libraries you can find in the HDF5 temp directory when you're going through the process of compiling ior (the section of installing HDF5)

```bash
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

# then libimf.so and libsvml.so was there
```






