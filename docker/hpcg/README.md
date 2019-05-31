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
source /opt/intel/bin/compilervars.sh intel64 [linux]
# potentially add linux too, unsure if needed but before I put linux I was getting another error


```





