## mdtest deployment on openstack

do the normal thing where you get the config file ready
```bash
akrr app add -a mdtest -r open-lakeeffect-stack
```
initial config file:
```bash
appkernel_run_env_template = """
# Load application enviroment
module load intel intel-mpi
module list

export I_MPI_PMI_LIBRARY=/usr/lib64/libpmi.so

# increase verbosity of mdtest output
# export MDTEST_VERBOSE = "-v"

# set executable location
EXE=$AKRR_APPKER_DIR/execs/ior/src/mdtest

# set how to run app kernel
RUNMPI="srun"
"""
```
So here again we want to run the docker image, so we change it to now look like so:
```bash
appkernel_run_env_template = """

export I_MPI_PMI_LIBRARY=/usr/lib64/libpmi.so

# setting up docker
sudo systemctl start docker
docker pull pshoff/akrr_benchmarks:mdtest
# set executable location
EXE="docker run --rm pshoff/akrr_benchmarks:mdtest --mdtest-run"

# to get app signature
docker run --rm pshoff/akrr_benchmarks:mdtest --appsigcheck >> $AKRR_APP_STDOUT_FILE 2>&1

# set how to run app kernel - not using this bc using mpirun inside docker
RUNMPI=""
"""
```

After some adjustment of the config to use the same docker image as ior, this is the final config:
```bash
appkernel_run_env_template = """

export I_MPI_PMI_LIBRARY=/usr/lib64/libpmi.so

# setting up docker
sudo systemctl start docker
docker pull pshoff/akrr_benchmarks:ior_mdtest
# set executable location
EXE="docker run --rm pshoff/akrr_benchmarks:ior_mdtest --run-mdtest"

# to get app signature
docker run --rm pshoff/akrr_benchmarks:ior_mdtest --appsig-mdtest >> $AKRR_APP_STDOUT_FILE 2>&1

# set how to run app kernel - not using this bc using mpirun inside docker
RUNMPI=""
"""

```





