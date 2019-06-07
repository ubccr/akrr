#!/bin/bash


# have to do this to set up LD_LIBRARY_PATH I think?
source /opt/intel/bin/compilervars.sh intel64
source /opt/intel/compilers_and_libraries_2018/linux/bin/compilervars.sh intel64
source /opt/intel/compilers_and_libraries_2018.3.222/linux/bin/compilervars.sh intel64

source ~/.bashrc
ulimit -c unlimited # sets core dump to be as big as possible - perhaps for more debugging?
mpirun -np 4 $exePath $inputsLoc/aump2.nw >> temp.out

/bin/bash


