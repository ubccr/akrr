## Notes on making the docker file/image for nwchem

First just trying to make it run on ub-hpc
```bash
module load nwchem
EXE=`which nwchem`

mpirun -np 4 $EXE aump2.nw # from nwchem inputs dir
# But this gave a whole bunch of different types of errors:
[hoffmaps@vortex1:~/appker/ub-hpc-actual/inputs/nwchem]$ $EXE aump2.nw 
[0] Received an Error in Communication: (1) there must be at least two ranks per node
application called MPI_Abort(comm=0x84000000, 1) - process 0
In: PMI_Abort(1, application called MPI_Abort(comm=0x84000000, 1) - process 0)

#####################################################################

[hoffmaps@vortex1:~/appker/ub-hpc-actual/inputs/nwchem]$ /util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mpi/intel64/bin/mpirun -np 2 $EXE aump2.nw 
forrtl: severe (174): SIGSEGV, segmentation fault occurred
Image              PC                Routine            Line        Source             
nwchem             00000000031F3683  Unknown               Unknown  Unknown
libpthread-2.17.s  00007FD82367F5D0  Unknown               Unknown  Unknown
nwchem             00000000031F3267  Unknown               Unknown  Unknown
libpthread-2.17.s  00007FD82367F5D0  Unknown               Unknown  Unknown
forrtl: severe (174): SIGSEGV, segmentation fault occurred
Image              PC                Routine            Line        Source             
nwchem             00000000031F3683  Unknown               Unknown  Unknown
libpthread-2.17.s  00007F9CFC4445D0  Unknown               Unknown  Unknown
nwchem             00000000031F3267  Unknown               Unknown  Unknown
libpthread-2.17.s  00007F9CFC4445D0  Unknown               Unknown  Unknown

####################################################

mpirun -np 1 $EXE aump2.nw 
[0] Received an Error in Communication: (1) there must be at least two ranks per node
application called MPI_Abort(comm=0x84000000, 1) - process 0
In: PMI_Abort(1, application called MPI_Abort(comm=0x84000000, 1) - process 0)

===================================================================================
=   BAD TERMINATION OF ONE OF YOUR APPLICATION PROCESSES
=   PID 258840 RUNNING AT srv-p22-12.cbls.ccr.buffalo.edu
=   EXIT CODE: 9
=   CLEANING UP REMAINING PROCESSES
=   YOU CAN IGNORE THE BELOW CLEANUP MESSAGES
===================================================================================

===================================================================================
=   BAD TERMINATION OF ONE OF YOUR APPLICATION PROCESSES
=   PID 258840 RUNNING AT srv-p22-12.cbls.ccr.buffalo.edu
=   EXIT CODE: 9
=   CLEANING UP REMAINING PROCESSES
=   YOU CAN IGNORE THE BELOW CLEANUP MESSAGES
===================================================================================
   Intel(R) MPI Library troubleshooting guide:
      https://software.intel.com/node/561764
===================================================================================



```

Perhaps what need to happen is changing the Permanent and Scratch directories, in the docs about AKRR_NWChem Deployment, it says you need to set NWCHEM\_PERMANENT\_DIR and NWCHEM\_SCRATCH\_DIR in the input file. Specifically, it tells you to do this:

```bash
echo "scratch_dir $AKRR_TMP_WORKDIR" >> $INPUT
echo "permanent_dir $AKRR_TMP_WORKDIR" >> $INPUT
# so I did that
INPUT=/user/hoffmaps/appker/ub-hpc-actual/inputs/nwchem/aump2.nw
TMP_WORKDIR=/user/hoffmaps/appker/ub-hpc-actual/tmp_nwchem_workdir
echo "scratch_dir $TMP_WORKDIR" >> $INPUT
echo "permanent_dir $TMP_WORKDIR" >> $INPUT

# then I tried again
mpirun -np 4 $EXE $INPUT
# yeah nope didn't work a BIT
```
This website : http://www.nwchem-sw.org/index.php/Release65:Running
Just says to run it like regular mpirun -np 8 $EXE $INPUT
Sooo I'm not sure what to do about it rn, so I'm just gonna try and get namd working, that seems to hold more promise (06/05/19)








