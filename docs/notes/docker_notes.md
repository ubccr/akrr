- Goal: get namd working with the inputs from akrr/akrr/appker_repo/inputs/namd/apoa1_nve/
	- Strategy: Simakov said something about using -v to link up the volumes and then -w to change the working directory of the docker image so tha it uses those inputs, about to try that
	- btw, the line using to run it is

```bash
docker run --rm researchcomputing/namd_212_multicore_osgvo-el6 namd2
``` 

























