# GAMESS-US Installation Notes

Brief notes on compilation of GAMESS-US (2018 R3 version) on UB-HPC.

Obtain code from https://www.msg.chem.iastate.edu/GAMESS/download/register/ and place it to
$AKRR_APPKER_DIR/execs

```bash
cd $AKRR_APPKER_DIR/execs/

module load intel/19.3 intel-mpi/2019.3 mkl/2019.3
source /util/academic/intel/19.3/compilers_and_libraries_2019.3.199/linux/mpi/intel64/bin/mpivars.sh
source $MKL/bin/mklvars.sh intel64

tar -xzf gamess-current.tar.gz

# configure
./config
# used config
cat /projects/ccrstaff/general/nikolays/huey/appker/execs/gamess/install.info
```
```bash
#!/bin/csh
#   compilation configuration for GAMESS
#   generated on cpn-d13-16.int.ccr.buffalo.edu
#   generated at Tue Apr 30 10:30:37 EDT 2019
setenv GMS_PATH            /projects/ccrstaff/general/nikolays/huey/appker/execs/gamess
setenv GMS_BUILD_DIR       /projects/ccrstaff/general/nikolays/huey/appker/execs/gamess
#         machine type
setenv GMS_TARGET          linux64
#         FORTRAN compiler setup
setenv GMS_FORTRAN         ifort
setenv GMS_IFORT_VERNO     19
#         mathematical library setup
setenv GMS_MATHLIB         mkl
setenv GMS_MATHLIB_PATH    /util/academic/intel/19.3/compilers_and_libraries_2019.3.199/linux/mkl/lib/intel64
setenv GMS_MKL_VERNO       12
#         parallel message passing model setup
setenv GMS_DDI_COMM        mpi
setenv GMS_MPI_LIB         impi
setenv GMS_MPI_PATH        /util/academic/intel/19.3/compilers_and_libraries_2019.3.199/linux/mpi
#         Michigan State University Coupled Cluster Build Option
setenv GMS_MSUCC           false
# Please match any manual changes to the GMS_MSUCC
# flag in /projects/ccrstaff/general/nikolays/huey/appker/execs/gamess/Makefile
# before running make
#         LIBCCHEM CPU/GPU code interface
setenv GMS_LIBCCHEM        false
#         Intel Xeon Phi build: none/knc/knl
setenv GMS_PHI             none
#         Shared memory type: sysv/posix
setenv GMS_SHMTYPE         sysv
#         SC17 SCF OpenMP support: true/false
setenv GMS_OPENMP          false
# Please match any manual changes to the GMS_OPENMP
# flag in /projects/ccrstaff/general/nikolays/huey/appker/execs/gamess/Makefile
# before running make
```

```bash
chdir ddi
./compddi >& compddi.log
# might require some editing for mpi.h location in compddi as well as MAXCPUS and MAXNODES
# dikick.x is not created from mpi runs
# mv ddikick.x ..

cd ..
./compall >& compall.log

# in lked if it can not find mpilibs
# case impi:
#   set MPILIBS="-L$GMS_MPI_PATH/lib64"
#   set MPILIBS="$MPILIBS -lmpi -lmpigf -lmpigi -lrt"
# to
# case impi:
#   set MPILIBS="-L$GMS_MPI_PATH/lib -L$GMS_MPI_PATH/lib/release"
#   set MPILIBS="$MPILIBS -lmpi -lmpigf -lmpigi -lrt"
./lked >& lked.log
```

Edit rungms

```bash
# partion of rungms
set TARGET=mpi
set SCR=`pwd`
set USERSCR=`pwd`
set GMSPATH=/projects/ccrstaff/general/nikolays/huey/appker/execs/gamess
#
``` 