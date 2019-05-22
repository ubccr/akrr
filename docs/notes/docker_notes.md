- Goal: get namd working with the inputs from akrr/akrr/appker_repo/inputs/namd/apoa1_nve/
	- Strategy: Simakov said something about using -v to link up the volumes and then -w to change the working directory of the docker image so tha it uses those inputs, about to try that
	- btw, the line using to run it is

```bash
docker run --rm researchcomputing/namd_212_multicore_osgvo-el6 namd2
``` 

- UPDATE: Nvidia namd found, presumably much better. Got it with

```bash
docker pull nvcr.io/hpc/namd:2.13-multinode

#Now to run it, interactivly and set up volume connection, go to directory with all the namd input files and do

docker run -v `pwd`:/root/apoa1_nve -it nvcr.io/hpc/namd:2.13-multinode

#Next step, running namd from in there
```
























