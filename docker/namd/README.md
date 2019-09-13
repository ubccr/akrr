# Making NAMD Appkernel Docker Container

Here are logs on how a docker image for the NAMD appkernel was made.

The strategy is to compile hpcc on system with Intel compilers and copy them to docker container.

Some specs:
* NAMD version: namd/2.13
* Compilers: intel/2018.3
* MPI: intel-mpi/2018.3
* BLAS/FFW: mkl/2018.3


## Compiling NAMD binary

Usefull resources:
* [Recipe: Building NAMD on Intel® Xeon® and Intel® Xeon Phi™ Processors on a Single Node](https://software.intel.com/en-us/articles/recipe-building-namd-on-intel-xeon-and-intel-xeon-phi-processors-on-a-single-node)
* [NAMD Custom Build for Better Performance on your Modern GPU Accelerated Workstation -- Ubuntu 16.04, 18.04, CentOS 7](https://www.pugetsystems.com/labs/hpc/NAMD-Custom-Build-for-Better-Performance-on-your-Modern-GPU-Accelerated-Workstation----Ubuntu-16-04-18-04-CentOS-7-1196/)

```bash
module load intel/18.3
module load intel-mpi/2018.3
module load mkl/2018.3

CC=icc; CXX=icpc; F90=ifort; F77=ifort
export CC CXX F90 F77

mkdir -p $AKRR_APPKER_DIR/execs/namd
cd $AKRR_APPKER_DIR/execs/namd
# Download namd from:
# https://www.ks.uiuc.edu/Development/Download/download.cgi?PackageName=NAMD

# Unpack NAMD and matching Charm++ source code:
tar xzf NAMD_2.13_Source.tar.gz
export NAMD_SRC="$AKRR_APPKER_DIR/execs/namd/NAMD_2.13_Source"
cd NAMD_2.13_Source
tar xf charm-6.8.2.tar

###############################################################################
# Build and test the Charm++/Converse library (single-node multicore version):
#
cd $AKRR_APPKER_DIR/execs/namd/NAMD_2.13_Source/charm-6.8.2
# Intel recipe asked:
# Set CMK_TIMER_USE_RDTSC timer and unset another timers in file 
# src/arch/multicore-linux64/conv-mach.h
# DO NOT DO THAT timing will be off

#build multicore-linux64 iccstatic
./build charm++ multicore-linux64 iccstatic --with-production "-O3 -ip"
# test:
cd multicore-linux64-iccstatic/tests/charm++/megatest
make pgm
./pgm +p4
cd ../../../../..

# build MPI version
cd $AKRR_APPKER_DIR/execs/namd/NAMD_2.13_Source/charm-6.8.2
export MPICXX=mpiicpc
export MPICC=mpiicc
./build charm++ mpi-linux-x86_64 --with-production
cd mpi-linux-x86_64/tests/charm++/megatest
make pgm
mpiexec -n 4 ./pgm
cd ../../../../..

# build MPI-SMP version
cd $AKRR_APPKER_DIR/execs/namd/NAMD_2.13_Source/charm-6.8.2
export MPICXX=mpiicpc
export MPICC=mpiicc
./build charm++ mpi-linux-x86_64 smp --with-production
cd mpi-linux-x86_64/tests/charm++/megatest
make pgm
mpiexec -n 4 ./pgm
cd ../../../../..


# Download and install TCL and FFTW libraries:
# (cd to NAMD_2.13_Source if you're not already there)
# Using MKL instead
# wget http://www.ks.uiuc.edu/Research/namd/libraries/fftw-linux-x86_64.tar.gz
# tar xzf fftw-linux-x86_64.tar.gz
# mv linux-x86_64 fftw
# Threaded version will do
# wget http://www.ks.uiuc.edu/Research/namd/libraries/tcl8.5.9-linux-x86_64.tar.gz
# tar xzf tcl8.5.9-linux-x86_64.tar.gz
# mv tcl8.5.9-linux-x86_64 tcl
cd $AKRR_APPKER_DIR/execs/namd/NAMD_2.13_Source
wget http://www.ks.uiuc.edu/Research/namd/libraries/tcl8.5.9-linux-x86_64-threaded.tar.gz
tar xzf tcl8.5.9-linux-x86_64-threaded.tar.gz
mv tcl8.5.9-linux-x86_64-threaded tcl-threaded

###############################################################################
# Build NAMD:
#
# Get the arch/Linux-x86_64-icc-{*}.arch from $AKRR_SRC/docker/namd/makefiles
cd "${NAMD_SRC}"/arch
wget https://raw.githubusercontent.com/ubccr/akrr/master/docker/namd/makefiles/Linux-x86_64-icc-avx2.arch
wget https://raw.githubusercontent.com/ubccr/akrr/master/docker/namd/makefiles/Linux-x86_64-icc-avx.arch
wget https://raw.githubusercontent.com/ubccr/akrr/master/docker/namd/makefiles/Linux-x86_64-icc-knl.arch
wget https://raw.githubusercontent.com/ubccr/akrr/master/docker/namd/makefiles/Linux-x86_64-icc-skx.arch
wget https://raw.githubusercontent.com/ubccr/akrr/master/docker/namd/makefiles/Linux-x86_64-icc-sse.arch

# mkdir for builds
cd "${NAMD_SRC}"
mkdir smp mpi mpi-smp


# Build SMP
for march in skx knl avx2 avx sse
do 
    cd "${NAMD_SRC}"
    ./config smp/Linux-x86_64-icc-${march} --charm-arch multicore-linux64-iccstatic \
        --with-mkl --mkl-prefix $MKLROOT --tcl-prefix `pwd`/tcl-threaded \
        --charm-opts -verbose
    cd smp/Linux-x86_64-icc-${march}
    make -j 8
done
# Test
for march in skx avx2 avx sse
do 
    cd "${NAMD_SRC}/smp/Linux-x86_64-icc-${march}"
    ./namd2 +p 8 src/alanin
done

# Build MPI
for march in skx knl avx2 avx sse
do 
    cd "${NAMD_SRC}"
    ./config mpi/Linux-x86_64-icc-${march} --charm-arch mpi-linux-x86_64 \
        --with-mkl --mkl-prefix $MKLROOT --tcl-prefix `pwd`/tcl-threaded \
        --charm-opts -verbose
    cd mpi/Linux-x86_64-icc-${march}
    make -j 8
done
# Test
for march in skx avx2 avx sse
do 
    cd "${NAMD_SRC}/mpi/Linux-x86_64-icc-${march}"
    mpirun -n 8 ./namd2 src/alanin
done

# Build MPI SMP
for march in skx knl avx2 avx sse
do 
    cd "${NAMD_SRC}"
    ./config mpi-smp/Linux-x86_64-icc-${march} --charm-arch mpi-linux-x86_64-smp \
        --with-mkl --mkl-prefix $MKLROOT --tcl-prefix `pwd`/tcl-threaded \
        --charm-opts -verbose
    cd mpi-smp/Linux-x86_64-icc-${march}
    make -j 8
done
# Test
for march in skx avx2 avx sse
do 
    mpirun -n 2 ./namd2 ++ppn 2 src/alanin
done

# Build GPU
for march in skx
do
    cd "${NAMD_SRC}"
    ./config smp-cuda/Linux-x86_64-icc-${march} --charm-arch multicore-linux64-iccstatic \
        --with-mkl --mkl-prefix $MKLROOT --tcl-prefix `pwd`/tcl-threaded \
        --charm-opts -verbose --with-cuda
    cd smp-cuda/Linux-x86_64-icc-${march}
    make -j 8
done

```

```bash
# get prebuild for ref
cd $AKRR_APPKER_DIR/execs/namd
tar xzf NAMD_2.13_Linux-x86_64-multicore.tar.gz
tar xzf NAMD_2.13_Linux-x86_64-multicore-CUDA.tar.gz
```

### NAMD With FFTW

```bash
wget http://www.fftw.org/fftw-3.3.8.tar.gz
tar xzf fftw-3.3.8.tar.gz
cd fftw-3.3.8
./configure --prefix=$AKRR_APPKER_DIR/execs/libs/fftw-3.3.8_skx_agr --enable-single --disable-fortran CC=icc
make CFLAGS="-O3 -xCORE-AVX512 -fp-model fast=2 -no-prec-div -qoverride-limits" clean install
cd ..

./config Linux-x86_64-icc10 --charm-arch multicore-linux64-iccstatic \
    --with-fftw --fftw-prefix $AKRR_APPKER_DIR/execs/libs/fftw-3.3.8_skx_agr --tcl-prefix `pwd`/tcl-threaded --charm-opts -verbose
```

### NAMD Performance

|binary  | median|   sd|  n|note                                                                                                                                |
|:-------|------:|----:|--:|:-----------------------------------------------------------------------------------------------------------------------------------|
|        | ns/day|     |   | **<- Simulation Speed, ns/day**|
|generic |   6.45| 0.09| 21|Prebuild                                                                                                                            |
|skx0    |   9.72| 0.26| 21|Intel Recipe+MKL+qopt-zmm-usage=high+                                                                                               |
|skx1    |   7.33| 0.10| 21|skx1: -axCORE-AVX512                                                                                                                |
|skx2    |   7.09| 0.14| 21|skx2: -xCORE-AVX512 -qopt-zmm-usage=high                                                                                            |
|skx3    |   7.10| 0.12| 21|skx3: -xCORE-AVX512 -qopt-zmm-usage=high -DNAMD_DISABLE_SSE                                                                         |
|skx4    |   7.69| 0.15| 21|skx4: -xCORE-AVX512 & -DNAMD_KNL                                                                                                    |
|skx5    |   7.36| 0.12| 21|skx5: -xCORE-AVX512 -DNAMD_DISABLE_SSE & O3 everythere                                                                              |
|skx6    |   7.35| 0.10| 21|skx6: -xCORE-AVX512 -DNAMD_DISABLE_SSE -fp-model fast=2 -no-prec-div -qoverride-limits & O3 everythere                              |
|skx7    |   9.77| 0.28| 21|skx7: -xCORE-AVX512  -qopt-zmm-usage=high -O3 -g -fp-model fast=2 -no-prec-div -qoverride-limits -DNAMD_DISABLE_SSE&#124;-DNAMD_KNL |
|skx8    |   7.53| 0.16| 21|skx8: -xCORE-AVX512  -O3 -g -fp-model fast=2 -no-prec-div -qoverride-limits -DNAMD_DISABLE_SSE&#124;-DNAMD_KNL                      |
|skx9    |   9.66| 0.44| 21|skx9: -xCORE-AVX512  -qopt-zmm-usage=high -O3 -g  -qoverride-limits -DNAMD_DISABLE_SSE&#124;-DNAMD_KNL                              |
|skx10   |   9.58| 0.20| 21|skx10: same as skx7 but with FFTW                                                                                                   |
|skx11   |   9.83| 0.20| 21|skx11: same as skx7 + O3 everywhere                                                                                                 |
|skx12   |   9.65| 0.29| 21|skx12: same as skx9 + O3 everywhere                                                                                                 |
|skx13   |   7.63| 0.23| 15|skx13: same as skx12 without -qopt-zmm-usage=high                                                                                   |
|        |    s  |     |   | **<- Walltime, s**|
|generic | 295.91| 1.94| 21|Prebuild                                                                                                                            |
|skx0    | 183.71| 1.74| 21|Intel Recipe+MKL+qopt-zmm-usage=high+                                                                                               |
|skx1    | 239.89| 1.30| 21|skx1: -axCORE-AVX512                                                                                                                |
|skx2    | 247.94| 1.86| 21|skx2: -xCORE-AVX512 -qopt-zmm-usage=high                                                                                            |
|skx3    | 245.89| 1.45| 21|skx3: -xCORE-AVX512 -qopt-zmm-usage=high -DNAMD_DISABLE_SSE                                                                         |
|skx4    | 230.13| 1.64| 21|skx4: -xCORE-AVX512 & -DNAMD_KNL                                                                                                    |
|skx5    | 240.09| 1.86| 21|skx5: -xCORE-AVX512 -DNAMD_DISABLE_SSE & O3 everythere                                                                              |
|skx6    | 238.33| 1.60| 21|skx6: -xCORE-AVX512 -DNAMD_DISABLE_SSE -fp-model fast=2 -no-prec-div -qoverride-limits & O3 everythere                              |
|skx7    | 183.40| 1.61| 21|skx7: -xCORE-AVX512  -qopt-zmm-usage=high -O3 -g -fp-model fast=2 -no-prec-div -qoverride-limits -DNAMD_DISABLE_SSE&#124;-DNAMD_KNL |
|skx8    | 231.96| 1.96| 21|skx8: -xCORE-AVX512  -O3 -g -fp-model fast=2 -no-prec-div -qoverride-limits -DNAMD_DISABLE_SSE&#124;-DNAMD_KNL                      |
|skx9    | 184.08| 1.65| 21|skx9: -xCORE-AVX512  -qopt-zmm-usage=high -O3 -g  -qoverride-limits -DNAMD_DISABLE_SSE&#124;-DNAMD_KNL                              |
|skx10   | 186.42| 2.07| 21|skx10: same as skx7 but with FFTW                                                                                                   |
|skx11   | 183.66| 1.75| 21|skx11: same as skx7 + O3 everywhere                                                                                                 |
|skx12   | 184.53| 1.80| 21|skx12: same as skx9 + O3 everywhere                                                                                                 |
|skx13   | 231.17| 1.89| 15|skx13: same as skx12 without -qopt-zmm-usage=high                                                                                   |

Namd benchmarking on UBHPC systems:

| Machine                        | Mode                   | cores | ns/day |
|--------------------------------|------------------------|-------|--------|
| SSE (2x (CPU-L5520/CPU-L5630)) | MPI 1 node * 8 ppn     | 8     | 0.72   |
|                                | MPI 2 node * 8 ppn     | 16    | 1.40   |
|                                | MPI 4 node * 8 ppn     | 32    | 2.70   |
|                                | MPI 8 node * 8 ppn     | 64    | 5.10   |
| SSE (2xCPU-E5645)              | MPI 1 node * 12 ppn    | 12    | 1.15   |
|                                | MPI 2 node * 12 ppn    | 24    | 2.22   |
|                                | MPI 4 node * 12 ppn    | 48    | 4.30   |
|                                | MPI 8 node * 12 ppn    | 96    | 8.00   |
| SKX (2xCPU-Gold-6130)          | MT x32                 | 32    | 9.65   |
| KNL                            | MT x68                 | 68    | 4.82   |
|                                | MT x136                | 68    | 5.22   |
|                                | MT x272                | 68    | 2.73   |
|                                | 4 MPI* (32 MT + 1 COM) | 68    | 2.76   |
|                                | 4 MPI* (16 MT + 1 COM) | 68    | 7.00   |
|                                | 13 MPI* (4 MT + 1 COM) | 68    | 6.00   |
| SKX, 2xP100                    | 32xMT 2xP100           |       | 69.34  |
|                                | 32xMT 1xP100           |       | 48.88  |
| SKX, T4                        | 32xMT 1xT4             |       | 28.51  |
| SKX, 2xV100                    | 32xMT 2xV100           |       | 72.99  |
|                                | 32xMT 1xV100           |       | 57.35  |
|                                | Ppn 16 1xV100          |       | 52.57  |
|                                | Ppn 12 1xV100          |       | 50.33  |
|                                | Ppn 16 1xV100 skx opt  |       | 53.17  |
|                                | Ppn 32 2xV100          |       | 74.18  |
|                                | Ppn 32 2xV100 skx opt  |       | 74.90  |
| SKX, T4                        | Ppn 32 1xT4            |       | 30.22  |
|                                | Ppn 32 1xT4 skx opt    |       | 31.62  |


## Move binaries to docker build host

```bash
# on build host make release
cd "${NAMD_SRC}/smp/Linux-x86_64-icc-skx"
make release
mv NAMD_2.13_Linux-x86_64-multicore ../
cd ../NAMD_2.13_Linux-x86_64-multicore
mv namd2 namd2_skx

for march in knl avx2 avx sse
do 
    cp "${NAMD_SRC}/smp/Linux-x86_64-icc-${march}/namd2" namd2_${march}
done

cp ../../../NAMD_2.13_Linux-x86_64-multicore/namd2 namd2_prebuild

# on docker build host
# Copy arch opt binaries
rsync -a vortex:/projects/xdtas/nikolays/appkernels/ubhpc-skx/execs/namd/NAMD_2.13_Source/smp/NAMD_2.13_Linux-x86_64-multicore ./
# Get and unpack cuda version
tar xzf NAMD_2.13_Linux-x86_64-multicore-CUDA.tar.gz
```

## Building Docker Container

```bash
docker build -t nsimakov/namd:latest -f docker/namd/Dockerfile .
docker run --rm nsimakov/namd:latest
```
