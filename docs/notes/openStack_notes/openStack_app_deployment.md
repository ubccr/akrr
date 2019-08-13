# Deploying various application kernels on OpenStack

This assumes that you have already set up OpenStack with the Docker volume, as well as set up AKRR with OpenStack.

Most setups are pretty straightforward, since you just start docker, pull the docker image, and run it.

Usually you can just run the Docker image normally, since it should identify how many cpus you have, but there are flags that allow you to specify how many processes mpirun starts.

For each of these you do the regular command to add an appkernel.
```bash
akrr app add -a $APPKER -r $OPENSTACK_RESOURCE
```

Then you just have to modify the config file that gets created.

Note that I pull from pshoff/akrr_benchmarks (my repo on docker hub) but you need to specify the appropriate Docker repo for you.

I put example config files for the corresponding Appkernels below:


### HPCC:
```bash
appkernel_run_env_template = """
sudo systemctl start docker
docker pull pshoff/akrr_benchmarks:hpcc
RUN_APPKERNEL="docker run --rm pshoff/akrr_benchmarks:hpcc"
"""
```

### HPCG:
```bash
appkernel_run_env_template = """
sudo systemctl start docker
docker pull pshoff/akrr_benchmarks:hpcg
RUN_APPKERNEL="docker run --rm pshoff/akrr_benchmarks:hpcg"
"""

```

### NAMD:
```bash
appkernel_run_env_template = """
sudo systemctl start docker
docker pull pshoff/akrr_benchmarks:namd
RUN_APPKERNEL="docker run --rm pshoff/akrr_benchmarks:namd"
"""
```

### NWChem:
```bash
appkernel_run_env_template = """
sudo systemctl start docker
docker pull pshoff/akrr_benchmarks:nwchem

# adding the shm-size 
# the cap-add to not print all the errors that are being given
RUN_APPKERNEL="docker run --rm --shm-size 8g --cap-add=SYS_PTRACE pshoff/akrr_benchmarks:nwchem"
"""
```

### GAMESS:
```bash
appkernel_run_env_template = """
# start docker daemon
sudo systemctl start docker

# get the updated images (can be skipped if you already have the image on the volume)
docker pull pshoff/akrr_benchmarks:gamess

# runs the docker image 
RUN_APPKERNEL="docker run --rm pshoff/akrr_benchmarks:gamess"
"""
```



Then you can do the validation.
```bash
akrr app validate -a $APPKER -r $OPENSTACK_RESOURCE
```

