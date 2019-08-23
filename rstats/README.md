## Directory where I'll be doing all the playing with r and statistics and whatnot

So, working with the script for getting the data with R...

We have to take a look at the database itself to see what tables we need to use

Initial results/thoughts:
- looks like the singularity approach is performing the same or slightly better even than bare metal. Potentially want to look into that? - maybe has to do with mpi version? singularity uses 2018.3, the default may not be that

- with nwchem, examining the appstdout files, there is a slight difference in the job information between bare metal and singularity - towards start of file, slightly different version...?
- with hpcg, bare_metal didn't even find the right input, so there's bigger differences there, but I just put the input into the proper directory for hpcg, so it should be running okay (as of 11:40 on 07/09/19)
- mdtest, can't see a substantial difference between the appstdout files other than some of the extra stuff from my script that I run
- gamess, singularity used version 11 Nov 2017 (R3) whereas bare metal was using 18 Aug 2016 (R1)
	- alright i checked out the rungms script and for whatever reason, even the 11Nov2017R3 version of the script just runs the 18Aug2016R1 version... WHY?? So even if you're loading the 2017 module, you're gonna be running the 2016 version. Maybe um fix?   
	- submitted a ticket and they fixed it to now be the proper gamess version
	- as of 7/10/19 10:45 it is correct
- namd - no real differences noted in namd appstdout
- hpcc - no real differences noted in appstdout in terms of setup 

- ior - I set it up just like normal, set it up so that it does mpirun on the sif file, and boy the singularity thing goes a LOT slower, by a factor of 10 almost
	- But running it again, its sorta comparable - maybe different cpus?
	- yeah pretty sure it was bc of the cpu

