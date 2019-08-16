## Directory for the Nwchem docker

So this "higher up" directory has the nwchem version that is present on ub-hpc.

If you want to build this Docker by yourself, you have to provide the binary yourself.

I got my binary from UB-HPC.

It's as easy as this (on vortex):
```bash
module avail nwchem
```
```text

---------------------------------- /util/academic/modulefiles/Core -----------------------------------
   nwchem/6.0    nwchem/6.8 (D)

```
```bash
module load nwchem/6.8

echo `which nwchem`

/util/academic/nwchem/nwchem-6.8/bin/LINUX64/nwchem
```
So you just have to get the directory the binary is in. In my case I got the nwchem-6.8 directory to have all the libs and such. 

Quick note: I removed most of the src directories except for basis, since that's all that was being used in the nwchemorg docker.

Then just use sftp to get the entire nwchem-6.8 directory into execs.

## Setup of this Directory
- Dockerfile - the file that builds the Docker image for nwchem
- execs - location of nwchem binary and akrr help scripts
	- bin - akrr help scripts
	- nwchem-6.8 - directory with everything needed to run nwchem
- inputs/nwchem - location of input for nwchem
- scripts - location of setup and run script for nwchem
- nwchem_other_docker - files used by me when working with the docker from nwchemorg that was more or less scrapped
- src_real - all the extra directories I took out of the src directory in nwchem (not there on github)


