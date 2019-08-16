# Directory for Gamess Appkernel Docker

This directory has all the files needed to create a Docker image for the Gamess Appkernel.
The binary is not on the repository, that must be set up once you clone the repo.
If you want to create the Docker yourself, you need to get the binary.
See setup of this Docker directory at bottom of Readme
Version of Gamess used when I was working with this Docker: gamess\_11Nov2017R3


## Guide to getting the Gamess binary set up from UB-HPC resource:

__On resource__
```bash
# check if gamess is available
module avail gamess
```
```text
---------------------------------- /util/academic/modulefiles/Core -----------------------------------
   gamess/5dec2014R1-ddi    gamess/5dec2014R1    gamess/11Nov2017R3    gamess/18Aug2016R1 (D)
```

For the Dockerfile in the git repo, gamess/11Nov2017R3 was used. Any version can be used, but the name of the version would have to be changed in the Dockerfile (change the GAMESS\_NAME variable). 

We'll be getting the binary from the resource, so really you just need a temporary directory to work with the files that you can access later with sftp from your machine, so cd to whatever directory you want to store the binary for now.

Find the location of the binary.
```bash
module show gamess/11Nov2017R3
```
```text
whatis(" GAMESS")
prepend_path("PATH","/util/academic/gamess/11Nov2017R3/impi/gamess")
load("intel/18.1")
load("intel-mpi/2018.1")
load("mkl/2018.1")
```
Check the directory that's added to the PATH:
```bash
ls /util/academic/gamess/11Nov2017R3/impi/gamess
```
You should see a bunch of files and libraries, most importantly the gamess executable, gamess.01.x, or something similar. 

In normal AKRR usage, we would only need the rungms script into a different directory, but in this case we want the entire directory so we can put it into our Docker image.
So, from the temporary directory, lets copy everything into that.
```bash
cp -r /util/academic/gamess/11Nov2017R3/impi/gamess ./
```
In my case it copied as just gamess, I changed the directory name to gamess\_11Nov2017R3 to distinguish it.
*Note: I copied the entire directory. You likely don't need everything in it, but I don't know gamess well enough to know what is or isn't needed. This has room for optimizing in terms of space*

So now you have the gamess executable in a directory. You now need to get it on the machine with the Dockerfile into the execs directory.
I used sftp.

__On Dockerfile Machine__
```bash
cd execs 
# this is the execs directory in the gamess Docker directory

sftp vortex.ccr.buffalo.edu
# now you're on the resource where the gamess directory is
# go to the directory where you made the gamess directory
# then do a get
get -r gamess_11Nov2017R3
# (this may take a little bit, potentially think about tarring?)
```
So once you have all that downloaded into your execs directory, you need to modify the rungms script.
Specifically towards the beginning (~line 64), you need to change 3 values:
```bash
# old values
set SCR=/gpfs/scratch/$USER
set USERSCR=/gpfs/scratch/$USER/scr
set GMSPATH=/util/academic/gamess/11Nov2017R3/impi/gamess

# new values
set SCR=`pwd`                                                                       
set USERSCR=`pwd`                                                               
set GMSPATH=$GAMESS_EXE_DIR 
```
This is because the Docker script goes to the place where we want to run it from. 
Then the GMSPATH is the directory where the gamess executable is, which for the Docker is in GAMESS\_EXE\_DIR.

Once you change the rungms script, you should be good to build and run the Docker.
Just running it with the regular docker run command will run gamess and display the results to the standard output.
There are flags that you can pass in to take some control over it.


## Setup of this Docker directory
- Dockerfile - creates the Docker image to use
- execs - location of akrr help scripts and gamess binary
	- bin - has the akkr help scripts
	- gamess\_11Nov2017R3 - directory with all the gamess things, including rungms and the gamess binary. If you are getting this from git directly, you need to get this yourself.
- inputs/gamess - location of gamess input file (c8h10-cct-mp2.inp)
- scripts - location of entrypoint script that runs when the gamess docker is launched
- original\_notes.md - my original notes on setting up the docker for gamess (not too helpful, but its there)



