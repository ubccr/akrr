## Directory for Gamess Docker things


Right now trying to run it on ub-hpc, but getting some weird mpi error, but seems to be starting and running okay up until the error, and I'm not sure what exactly the error is.
I'm gonna try and just get the binary and try to run things on my local machine...

Here is the error I got:
```bash
===================================================================================
=   BAD TERMINATION OF ONE OF YOUR APPLICATION PROCESSES
=   PID 86375 RUNNING AT srv-p22-12.cbls.ccr.buffalo.edu
=   EXIT CODE: 24
=   CLEANING UP REMAINING PROCESSES
=   YOU CAN IGNORE THE BELOW CLEANUP MESSAGES
===================================================================================

===================================================================================
=   BAD TERMINATION OF ONE OF YOUR APPLICATION PROCESSES
=   PID 86375 RUNNING AT srv-p22-12.cbls.ccr.buffalo.edu
=   EXIT CODE: 24
=   CLEANING UP REMAINING PROCESSES
=   YOU CAN IGNORE THE BELOW CLEANUP MESSAGES
===================================================================================
   Intel(R) MPI Library troubleshooting guide:
      https://software.intel.com/node/561764
===================================================================================


```
Also don't forget to copy over the input file to where you're running the rungms thing
So I tarred up the whole games directory and such, and now I'm trying to get gamess to at least run on my computer.
So of course a lot of things need to be changed in rungms
List of things I changed (this is now their new values
```bash
set SCR=`pwd`
set USERSCR=`pwd`
set GMSPATH=/home/hoffmaps/projects/akrr/docker/gamess/execs/gamess_11Nov2017R3
```
Looks to be running fine....
It does mpiexec.hydra do do its thing

Update: seemed to complete gamess thing normally. Now to make a Dockerfile! It'll be a lot like hpcc as usual

Initial docker setup seems to be doing okay.
One added thing: I have to install csh shell, bc that's whats at the top of the rungms file.
Also, I had to delete the first thing of LD\_LIBRARY\_PATH (or rather the first time it was being used as $LD\_LIBRARY\_PATH to put on the end bc it wasn't defined or something)
Unsure if also have to have mkl, rn I'm doing fine with only mpi


Okay I think I have it more or less working, though there is something sorta weird in the output.
It says that "MPI kickoff will run GAMESS on 01 cores in 1 nodes." despite the fact that I put 6 cores per node, It does register the 6 bc it says "placing 6 of each process type onto each node" so I'm not sure what thats all about

Other than that, it seems to be running fine. Will come back to it to make some tune ups, but for now it SEEMS okay






