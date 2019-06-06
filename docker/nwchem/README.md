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


I'm back after only a day! I got gamess and namd to work more or less. The output looks decent. I still probably want to do some tuning on those to make the script a bit more concise, but that's for future me. Right now I want to look at nwchem.

So I guess for some reason now nwchem works?? At least I haven't gotten the error as above when running it, ran it with the standard mpirun -np 4 $EXE $INPUT stuff

Copied over a LOT of files from vortex, not sure if I need them all. Anyways:

Now trying to run it on my own machine, I'm getting the following error:
```bash
/home/hoffmaps/projects/akrr/docker/nwchem/execs/nwchem-6.8/bin/LINUX64/nwchem: error while loading shared libraries: libmkl_intel_ilp64.so: cannot open shared object file: No such file or directory
/home/hoffmaps/projects/akrr/docker/nwchem/execs/nwchem-6.8/bin/LINUX64/nwchem: error while loading shared libraries: libmkl_intel_ilp64.so: cannot open shared object file: No such file or directory
/home/hoffmaps/projects/akrr/docker/nwchem/execs/nwchem-6.8/bin/LINUX64/nwchem: error while loading shared libraries: libmkl_intel_ilp64.so: cannot open shared object file: No such file or directory
/home/hoffmaps/projects/akrr/docker/nwchem/execs/nwchem-6.8/bin/LINUX64/nwchem: error while loading shared libraries: libmkl_intel_ilp64.so: cannot open shared object file: No such file or directory
```
Things I found online suggested adding things to LD\_LIBRARY\_PATH but seems to have not really worked...  : https://stackoverflow.com/questions/35046753/using-mkl-error-while-loading-shared-libraries-libmkl-intel-lp64-so

Alright so I'm not sure why it works but I think it works now, I just followed advice from above and did
```bash
locate  compilervars.sh
source /adress you got from locate command/compilervars.sh intel64
source ~/.bashrc
```
Potentially have to finagle this in Docker? But regardless it now works on my system, on to the Docker! Looks like I need mkl for this one though





