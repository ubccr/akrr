#!/bin/bash
# pass all the arguments into it
$MPI_LOC/mpiexec -n 8 $IOR_EXE_PATH "$@"
