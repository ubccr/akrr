## Files for creating HPCC Docker image (uses Intel-mpi)

HPCC - High Performance Compute Competition, a benchmarking technique

Intel-mpi version used: 2018.3

```bash
# building the Dockerfile
docker build -t hpcc_intelmpi_centos7 .

# running it (interactively)
docker run -it hpcc_intelmpi_centos7
```

### The thought/plan

When run is being done, the user must mount the location of the input file they want to use, like so

```bash
docker run -it -v /path/to/inputs:/home/hpccuser/execs/hpcc-1.5.0/inputs hpcc_intelmpi_centos7
# if you're using hpcc inputs from this repo, the statement would be
docker run -it -v [path to akrr]/akrr/akrr/appker_repo/inputs/hpcc:/home/hpccuser/execs/hpcc-1.5.0/inputs hpcc_intelmpi_centos7 [input file to use]

```
This mount must happen, otherwise there is an error, since the script relies on inputs existing
Alternatively, if you don't want to run a file immediately, you can just not put anything and it will just put you into the directory.

NOTE: Permissions on the input directory must be correct, since the permissions are copied into the docker container. Do:

```bash
# for your inputs directory
chmod a+x [inputs dir]
 
# for all files in your inputs directory
chmod a+rw *
```

As of 5/24/19, you can do all this and the docker container will be set up with the correct input file for doing mpirun etc...

Next goal: be able to run the whole mpirun stuff from completely outside of the container just at the run instruction




