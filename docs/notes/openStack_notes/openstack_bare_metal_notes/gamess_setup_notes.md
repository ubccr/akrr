## Setting up gamess bare metal    

Start up an openstack instance with the volume you want to use

```bash
openstack server create --flavor c8.m16 --volume dockervolume-data --network lakeeffect-199.109.195 --key-name openstack-testing --security-group default --security-group SSH akrrtest

```

Then sftp to it with something like
```bash
sftp -i <ssh key> centos@<ip address>

```

Then you want to put the gamess executable folder thingy
Then you want to link the gamess folder to be just gamess (it usually starts as something like gamess_11Nov2017R3 or something)
Just make sure to link it (does require ssh into instance
```bash
ln -s gamess_11Nov2017R3/ gamess

```
Since rungms uses csh instead of bash, you need to install it, which can be done on the instance pretty easily with

```bash
yum -y install tcsh


```
So I used the gamess script I developed, which uses a variable GAMES_EXE_DIR so I had to set that before running the script
Also have to add the mpi location to the path so that rungms can find mpirun and such
So in the end the resulting config file looks like:
```bash
appkernel_run_env_template = """
# Load application enviroment
#module load gamess
#module list

# set executable location
VERNO=01

# so it can find where gamess is
export GAMESS_EXE_DIR=$AKRR_APPKER_DIR/execs/gamess
EXE=$GAMESS_EXE_DIR/gamess.$VERNO.x

# so it can find mpirun stuff
export PATH=$PATH:/opt/intel/impi/2018.3.222/bin64

# order of cores per node and nodes switched bc rungms works like that
# set how to run app kernel
RUN_APPKERNEL="$AKRR_APPKER_DIR/execs/gamess/rungms $INPUT $VERNO $AKRR_CORES_PER_NODE $AKRR_NODES"
"""

```

Then just validate
```bash
akrr app validate -n 1 -r openstack-no-docker -a gamess
```

You also want to probably check on openstack to make sure it's running in parallel properly


