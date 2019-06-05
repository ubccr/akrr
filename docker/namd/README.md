## Directory with all the files for the namd docker

Went to this site: https://www.ks.uiuc.edu/Development/Download/download.cgi?PackageName=NAMD
And I downloaded Linux-x86_64-multicore (64-bit Intel/AMD single node)

I then put the resulting tar in namd_loc in this directory (its in .gitignore so won't get posted to github) then I untarred it
All the executable stuff is in namd_loc/execs


Dockerfile creation was pretty straightforward.
Based it off of hpcc docker file
Copied over the executables, inputs, and scripts
then modified the entrypoint script to fit namd
It seems to run correctly without a problem, except it is taking a bit long
Other than that, this Docker image should be more or less set to go 

