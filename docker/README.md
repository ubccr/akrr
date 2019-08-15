# Directory for Docker things for various application kernels or AKRR in general

In this directory are all the directories for the various docker images of the Application Kernels as well as some of the Docker images for AKRR otherwise

## Flags for the run script
These are the flags I added for the run scripts that is called when you run the docker image for the various appkernels.

So these are tags you can use for the hpcc, hpcg, gamess, namd, nwchem, ior, and nwchem.
(You put these at the end of the whole thing, so for example
```bash
docker run pshoff/akrr_benchmarks:hpcc -ppn 6 -v
# of course the tag might be different
```
Because of how I set up the script, only exactly the flags I give will work. (So you can't do something like -hv, you have to do -h -v)

Anyways, onto the flags and what they do:
```bash
-h | --help                     Display help text

-v | --verbose                  Increase verbosity of output (does set -x)

-i | --interactive              Start a bash session at end of script

--norun                         Set if you don't want to immediately run the binary

-n NODES | --nodes NODES        Specify number of nodes the binary will be running on (default 1)

-ppn PROC_PER_NODE |
--proc_per_node PROC_PER_NODE       Specify nymber of processes/cores per node
                                        (if not specified, number of cpu cores is used as found in /proc/cpuinfo)

--pin                           Turn on process pinning for mpi (I_MPI_PIN)

-d DEBUG_LEVEL |
--debug DEBUG_LEVEL            Set the mpi debug level (I_MPI_DEBUG) to the given value (0-5+, default 0)
```
Some things to keep in mind:

- In most cases, the --nodes option will not do anything, since the docker image assumes you're running on one node (or the openstack equivalent, one instance)
	- Really the only purpose of setting this to something other than 1 is for hpcc, since it uses the node count to choose the input file. Otherwise setting it to something won't change the end result
- If you want to start an interactive session to look into the docker image, I've found that you also need to set it for docker, so you would have to do the following:
```bash
docker run -it pshoff/akrr_benchmakrs:hpcc -i
# From my experience, only having one or the other won't properly start the interactive session
```


