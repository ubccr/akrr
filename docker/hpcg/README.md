## Directory for working with Docker and HPCG image stuff

Got binaries from vortex with:
```bash
# load mkl enviroment
module load intel/18.3
module load intel-mpi/2018.3
module load mkl/2018.3

# the binaries should be in
ls $MKLROOT/benchmarks/hpcg/bin
# hpcg.dat  xhpcg_avx  xhpcg_avx2  xhpcg_knl  xhpcg_skx
# 
```
Then I downloaded the binaries and put them in the /bin directory

Slight issues I was having and how I fixed (after I installed intel mpi and mkl:

```bash
# Error
./xhpcg_avx2: error while loading shared libraries: libiomp5.so: cannot open shared object file: No such file or directory

# Fix
source /opt/intel/bin/compilervars.sh intel64 [-platform linux]
# potentially add linux too, unsure if needed but before I put linux I was getting another error
```

Things seemed to be set up properly.
See Dockerfile and script for how things are set up.
So far only did the xhpc_avx hpcg file, potentially will push the others up to Docker hub
Also it seems to be a bit large... perhaps because mkl is so big...?

xhpc_avx is optimized for Intel Xeon E3 for first and 2nd generation 
https://software.intel.com/en-us/mkl-linux-developer-guide-versions-of-the-intel-optimized-hpcg


Most updated version: pshoff/hpcg_benchmark:avx (05/31/19)








