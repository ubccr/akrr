## Directory with all the files for the namd docker
NOTE: Right now this docker is incorrect bc its using mpi and not charmrun like its supposed to, i'll be working on getting it working with charm

Went to this site: https://www.ks.uiuc.edu/Development/Download/download.cgi?PackageName=NAMD
And I downloaded Linux-x86_64-multicore (64-bit Intel/AMD single node)

I then put the resulting tar in namd_loc in this directory (its in .gitignore so won't get posted to github) then I untarred it
All the executable stuff is in namd_loc/execs


Dockerfile creation was pretty straightforward.
Based it off of hpcc docker file
Copied over the executables, inputs, and scripts
then modified the entrypoint script to fit namd
It seems to run correctly without a problem, except it is taking a bit long
Other than that, this Docker image should be more or less set to go, similar to other docker setups


NOTE: The cat doesn't work since the out files are binary... Perhaps also want to check on output of the whole thing, unsure how accurate it is
Also check with mpi setup, unsure if done correctly


UPDATE: Added in the appsigcheck thing, so it checks that stuff fine

## UPDATE 
So I gotta do this whole thing with charmrun somehow, NOT mpi
So that's what I'll be working on shortly to fix this

Found this website with the tar: http://charmplusplus.org/download/
Got the tar and unpacked it
Now I have to build it somehow?
```bash
# tried just building it with the standard target
./build charm++ netlrts-linux-x86_64
```
Update - so I'm not exactly sure how this charmrun stuff is working. HOWEVER i did the following command and namd2 finished within a few minutes
```bash
./namd2 +p6 ../../inputs/namd/apoa1_nve/input.namd 
```
Based on this website: https://www.ks.uiuc.edu/Research/namd/2.9/ug/node79.html
I'm not sure if it makes a difference? But we're gonna try and get this one working with akrr
Update: checked with nikolay, it makes sense.
I updated the script ot now reflect this, now when it runs namd it is
```bash
${NAMD_EXE_FULL_PATH} +p${ppn} ${work_dir}/input.namd
```
This does appear to run the things in parallel but also for some reason when I look at htop, one of them is using 600% of the cpu so idk whats up with that

- Note: currently using namd 2.12b1-multicore






