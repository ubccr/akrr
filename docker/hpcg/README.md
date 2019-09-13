# Making HPCC Appkernel Docker Container

Here are logs on how a docker image for the HPCC appkernel was made.

The strategy is to copy from or compile hpcg on system with Intel compilers and copy them to docker container.

Some specs:
* HPCG version: intel/Revision: 3.0
* Compilers: intel/2018.3
* MPI: intel-mpi/2018.3
* BLAS/FFW: mkl/2018.3

## Obtaining/Compiling HPCG binary

The HPCG binaries come with intel mkl library. But they optimized
only for avx/avx2/skx/knl. On cloud CPU can be exposed as sse2 so
we need to make that one too.

```bash
# On compilation host
# Go to executable directory
cd $AKRR_APPKER_DIR/execs

# Load modules (dependent on individual situation)
module load intel/18.3
module load intel-mpi/2018.3
module load mkl/2018.3

source $MKL/bin/mklvars.sh intel64

# hpcg lives in $MKLROOT/benchmarks/hpcg
cp -a $MKLROOT/benchmarks/hpcg ./

cp setup/Make.IMPI_IOMP_AVX2 setup/Make.IMPI_IOMP_SSE2
# change -xAVX to -xSSE2 and set xhpcg_suff to _sse2
vi setup/Make.IMPI_IOMP_SSE2
# out of source compilation is not really working
./configure My_MPI_OMP
make MKL_INCLUDE=$MKLROOT/include
# edit Makefile not to remove binary on clean
make clean
./configure IMPI_IOMP_AVX
make MKL_INCLUDE=$MKLROOT/include
make clean
```

```bash
# On docker making host

```

# Directory and files needed for HPCG Appkernel


(Optimized for Intel processors of course then)

If you do want to have your own binaries, you would need to modify the Dockerfile and script a decent bit.

## Setup of this directory
- Dockerfile - used to make the Docker image
- execs/bin - location of akrr help scripts
- inputs/hpcg - location of hpcg input to use
- scripts - location of script that sets up and runs the hpcg benchmark

