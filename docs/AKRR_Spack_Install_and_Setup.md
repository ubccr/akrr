# Deploying AKRR with Spack

Spack allows automated build of packeges with all their dependencies and 
specifically targeted for HPC system. It allows architecture specific optimization
however proper triggering of "configure options" is up to Spack packege developer and
some times it is not the case.
We have addressed this issue in several packages and at
least in Fall-2020 it was working as expected for several applications used in AKRR.



# Spack Setup on HPC Resource

In principle Spack is self-sufficient and can build most of the packages 
from scratch including all dependencies.
However we want to leverage libraries and compilers already existing on the system.
Spack allows to specify the packages to use from the system, though automatic discovery
is not strong yet and would need some help.

## Install Spack on Resource

```bash
cd $AKRR_APPKER_DIR/execs
git clone https://github.com/spack/spack.git
```

## Add system wide compilers and libraries

### Compiler

From running `module avail` we see `gcc/10.2.0` package for compiler. 
To add it to Spack:

```bash
# load compiler enviroment
module load gcc/10.2.0
# Ask spack to find compiler at specific location and store it in system config
$AKRR_APPKER_DIR/execs/spack/bin/spack compiler find --scope site $(dirname $(dirname $(which gcc)))
# Examine and edit compilers.yaml
vi $AKRR_APPKER_DIR/execs/spack/etc/spack/compilers.yaml
```

In compilers.yaml we need to add `gcc/10.2.0` module to load:
```yaml
compilers:
- compiler:
    spec: gcc@10.2.0
    paths:
      cc: /<path to gcc>/bin/gcc
      cxx: /<path to gcc>/bin/g++
      f77: /<path to gcc>/bin/gfortran
      fc: /<path to gcc>/bin/gfortran
    flags: {}
    operating_system: centos8
    target: x86_64
    modules: [gcc/10.2.0]
    environment: {}
    extra_rpaths: []
```

### MPI library

Adding MPI library (`openmpi/4.0.5-gcc10.2.0` module):
```yaml
module load openmpi/4.0.5-gcc10.2.0
which mpicc
# add it manually
vi $AKRR_APPKER_DIR/execs/spack/etc/spack/packages.yaml
```

packages.yaml with openmpi/4.0.5-gcc10.2.0
```yaml
packages:
  openmpi:
    externals:
    - spec: "openmpi@4.0.5  arch=linux-centos8-zen2"
      prefix: /<path to openmpi root>
      modules: [openmpi/4.0.5-gcc10.2.0]
    buildable: False
```

### Building Tools

Often that would be enough however there are number of building tools which normally
present on the system and we don't want spack to rebuild them. 

First find their versions and locations:

```bash
which gmake
gmake -v
which cmake
cmake --version
which autoconf
autoconf --version
which automake
automake --version
which cpio
cpio --version
```

Add them to `packages.yaml`:

```yaml
  gmake:
    externals:
    - spec: "gmake@4.2.1 arch=linux-centos8-x86_64"
      prefix: /usr
    buildable: False
  cmake:
    externals:
    - spec: "cmake@3.11.4 arch=linux-centos8-x86_64"
      prefix: /usr
    buildable: False
  autoconf:
    externals:
    - spec: "autoconf@2.69 arch=linux-centos8-x86_64"
      prefix: /usr
    buildable: False
  automake:
    externals:
    - spec: "automake@1.16.1 arch=linux-centos8-x86_64"
      prefix: /usr
    buildable: False
  cpio:
    externals:
    - spec: "cpio@2.12 arch=linux-centos8-x86_64"
      prefix: /usr
    buildable: False
```

### Other Packages
Other packages. Basically we want to reuse as much libraries from system wide installation.
Below are some notes on some libraries used in appkernels.

#### parallel-hdf5

```bash
module load phdf5/1.10.7-openmpi4.0.5-gcc10.2.0
module show phdf5/1.10.7-openmpi4.0.5-gcc10.2.0
```
```yaml
  hdf5:
    externals:
    - spec: "hdf5@1.10.7 %gcc@10.2.0 arch=linux-centos8-zen2 ^openmpi@4.0.5"
      prefix: /jet/packages/spack/opt/spack/linux-centos8-zen2/gcc-10.2.0/hdf5-1.10.7-3trwysszw4lw3tazizx2if2mg6567cro
      modules: [openmpi/4.0.5-gcc10.2.0,phdf5/1.10.7-openmpi4.0.5-gcc10.2.0]
    buildable: False
```

#### parallel-netcdf

```bash
module load parallel-netcdf/1.12.1
module show parallel-netcdf/1.12.1
```
```yaml
  parallel-netcdf:
    externals:
    - spec: "parallel-netcdf@1.12.1 %gcc@10.2.0 +mpi arch=linux-centos8-zen2 ^openmpi@4.0.5"
      prefix: /jet/packages/spack/opt/spack/linux-centos8-zen/gcc-8.3.1/parallel-netcdf-1.12.1-4yiuel3fvyxrkteu5osm5mlwvkcwxhmd
      modules: [openmpi/4.0.5-gcc10.2.0,parallel-netcdf/1.12.1]
    buildable: False
```

#### fftw

```bash
module load fftw/3.3.8
module show fftw/3.3.8
```
```yaml
  fftw:
    externals:
    - spec: "fftw@3.3.8 %gcc@10.2.0 +mpi arch=linux-centos8-zen2 ^openmpi@4.0.5"
      prefix: /jet/packages/spack/opt/spack/linux-centos8-zen/gcc-8.3.1/fftw-3.3.8-bx5uvjft5olrdheauq2yqu3z5yhkmlj2
      modules: [openmpi/4.0.5-gcc10.2.0,fftw/3.3.8]
    buildable: False
```
