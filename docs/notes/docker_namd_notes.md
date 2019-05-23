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
- Update: getting an error - working on seeing what's wrong with this

```bash
CUDA initialization error on 24902da047d8: CUDA driver version is insufficient for CUDA runtime version
Charm++: standalone mode (not using charmrun)
[0] Assertion "num_devices > 0" failed in file machine-ibverbs.c line 482.
Segmentation fault (core dumped)
```
- Update: turns out there are a lot of prerequisites for this ^^ so we're going back to the first one and trying stuff out with that. I'm doing:

```bash
docker run -v `pwd`:/root/apoa1_nve -it researchcomputing/namd_212_multicore_osgvo-el6

```

- Update: was able to run namd through the docker container with the following command (executed from where the input files were)

```bash
docker run -v `pwd`:/root/apoa1_nve -w /root/apoa1_nve researchcomputing/namd_212_multicore_osgvo-el6 namd2 input.namd
```


















