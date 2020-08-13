## Setting up hpcc on openstack without docker


First start up openstack server with volume you want

```bash
openstack server create --flavor c8.m16 --volume dockervolume-data --network lakeeffect-199.109.195 --key-name openstack-testing --security-group default --security-group SSH akrrtest

```

Then we need to get hpcc on there.
So I want to use the same binary, so imma try and get the binary on there.
Done with sftp, using -i for the key pair and then putting the directory there.

Don't forget also to add a symbolic link hpcc-->hpcc-1.5.0
```bash
ln -s hpcc-1.5.0/ hpcc

```



Also have to install intel mpi stuff for mpirun and such

```bash
# may need to switch to root user here
yum-config-manager --add-repo https://yum.repos.intel.com/mpi/setup/intel-mpi.repo
rpm --import https://yum.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS-2019.PUB
yum -y install intel-mpi-2018.3-051


```

Then once the binary is there, just add in the hpcc app
```bash
akrr app add -a hpcc -r openstack-no-docker


```
So origninally hpcc is gonna be using srun for a normal hpc thing
So we gotta change it to be for mpirun

So new config is like this
```bash
appkernel_run_env_template = """

# assuming one node so using akrr cores
RUN_APPKERNEL="/opt/intel/impi/2018.3.222/bin64/mpirun -np $AKRR_CORES {appkernel_dir}/{executable}"
"""
```
Then just run the validation
```bash
akrr app validate -a hpcc -r openstack-no-docker -n 1

```
Seems to be working fine then

