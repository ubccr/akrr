## Setting up hpcg on bare metal of openstack

For this one you do need to install intel mpi and mkl

So in Openstack volume:
```bash
        yum-config-manager --add-repo https://yum.repos.intel.com/mpi/setup/intel-mpi.repo && \
        rpm --import https://yum.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS-2019.PUB && \
        yum -y install intel-mpi-2018.3-051 && \
        yum-config-manager --add-repo https://yum.repos.intel.com/mkl/setup/intel-mkl.repo && \
        yum -y install intel-mkl-2018.3-051

```

Then, you need to find the place where the benchmarks are for hpcg. In my case they were in /opt/intel/mkl/benchmarks/hpcg/bin

Also you have to set the lib paths and identify what the libraries are to use, so the following config file was able to handle all of it well.

```bash
"""
Resource specific HPCG configuration
"""

appkernel_run_env_template = """

# counting if the processor supports avx2 or skx
hpcg_exe_name="xhpcg_avx"
count_avx2="$(grep -oc 'avx2' /proc/cpuinfo)"
count_avx512="$(grep -oc 'avx512' /proc/cpuinfo)"
echo "avx2: $count_avx2"
echo "avx512: $count_avx512"

# if find any, sets the proper executable name (can still be overriden
if [[ "$count_avx2" -gt "0" ]]; then
        hpcg_exe_name="xhpcg_avx2"
fi

if [[ "$count_avx512" -gt "0" ]]; then
        hpcg_exe_name="xhpcg_skx"
fi

# set executable location
EXE=/opt/intel/compilers_and_libraries_2018.3.222/linux/mkl/benchmarks/hpcg/bin/$hpcg_exe_name

# so it finds all necessary libraries
export LD_LIBRARY_PATH=/opt/intel/lib/intel64:/opt/intel/mkl/lib/intel64:$LD_LIBRARY_PATH

# Set how to run app kernel
export OMP_NUM_THREADS=1

# need to specify full path bc didn't add mpirun to path
RUN_APPKERNEL="/opt/intel/impi/2018.3.222/bin64/mpirun -np $AKRR_CORES $EXE"
"""
```
Also need to make sure hpcg.dat is in proper location
Run validation and check results files (stdout) to see if it found the input.
If it didn't find the input you need to get it from the git repo (I don't think its included in the tar that happens at the deploy step)



