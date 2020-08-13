## mdtest setup on openstack bare

Like before, you want to sftp onto the volume and put the ior directory in there (which also has mdtest) and you want to link the ior-3.2.0 to ior so that akrr can find it.

Now, mdtest also need some libraries, so you want to sftp them onto the volume as well
Then have that location in the LD_LIBRARY_PATH variable


So in the end the config file looks like

```bash
appkernel_run_env_template = """

# set executable location
EXE=$AKRR_APPKER_DIR/execs/ior/src/mdtest

# make sure all libs are found
export LD_LIBRARY_PATH=/home/centos/appker/resource/no_docker/libs

# set how to run app kernel
RUNMPI="/opt/intel/impi/2018.3.222/bin64/mpirun -np $AKRR_CORES"
"""



```


