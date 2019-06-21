## Directory for working with Docker and HPCG image stuff
THIS README IS NOT COMPLETE. I largely used it as notes while figuring things out


Binaries I used were from Intel mkl

Slight issues I was having and how I fixed (after I installed intel mpi and mkl:

```bash
# Error
./xhpcg_avx2: error while loading shared libraries: libiomp5.so: cannot open shared object file: No such file or directory

# Fix
source /opt/intel/bin/compilervars.sh intel64 [-platform linux]
# potentially add linux too, unsure if needed but before I put linux I was getting another error
```

Things seem to be set up properly.
See Dockerfile and script for how things are set up.
So far only did the xhpc_avx hpcg file, potentially will push the others up to Docker hub eventually
Also it seems to be a bit large... perhaps because mkl is so big...?

xhpc_avx is optimized for Intel Xeon E3 for first and 2nd generation 
https://software.intel.com/en-us/mkl-linux-developer-guide-versions-of-the-intel-optimized-hpcg

Adding flexibility so that the script identifies what the optimal benchmark to use would be

Added the /scratch directory to be the place for the temporary working directory, right now doesn't clean it up at the end, perhaps want that functionality?

Most updated version: pshoff/akrr_benchmarks:hpcg - has appsigcheck and script has common practices

Older versions:
- pshoff/hpcg_benchmark:auto (06/03/19) - automatically figures out which one to use, but didn't have appsigcheck of executable
- pshoff/hpcg_benchmark:avx (05/31/19) - uses avx exclusively
- pshoff/hpcg_benchmark:avx2 (06/03/19) - uses avx2 exclusively








