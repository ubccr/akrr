## Notes on deployment for Nwchem on openstack

Like before, make the standard variables

```bash
export APPKER=nwchem
export RESOURCE=lakeeffect

```
Then make the initial config

```bash
akrr app add -a $APPKER -r $RESOURCE

```
Sample output:
```bash
[INFO] Generating application kernel configuration for nwchem on lakeeffect
[INFO] Application kernel configuration for nwchem on lakeeffect is in: 
        /home/hoffmaps/projects/akrr/etc/resources/lakeeffect/nwchem.app.conf
```
Initial config file:
```bash
appkernel_run_env_template = """
# Load application environment
module load nwchem
module list

# make srun works with intel mpi
export I_MPI_PMI_LIBRARY=/usr/lib64/libpmi.so

# set executable location
EXE=`which nwchem`

#set how to run app kernel
RUN_APPKERNEL="srun --mpi=pmi2 $EXE $INPUT"
"""
```
Now we want to just use Docker instead.
Slightly different than other benchmarks, for this we're using someone else's docker image
New config file:
```bash
appkernel_run_env_template = """
sudo systemctl start docker
docker pull nwchemorg/nwchem-qc

# Temporary until we figure out exactly which one we want to run
brary_tests/CH4_STO6G_FCI/ch4_sto6g_fci.nw
# connecting it to a volume...
RUN_APPKERNEL="docker run --rm -v $AKRR_TMP_WORKDIR:/opt/data nwchemorg/nwchem-qc aump2.nw"
"""
```
In this case we want to run aump2.nw
Then run the validation
```bash
akrr app validate -n 1 -r $RESOURCE -a $APPKER
```

Validation example is in openStack_nwchem_validation_example

UPDATE: so docker runs as root, and the nwchem docker we are running is trying to make files in one of our directories. It appears that the directory created with the deployment (network_scratch) only has rwx for the owner, so give that directory rw for all users..?
- Actually it might be that you need to give access with the created temp directory
- I gave all the proper permissions I believe, but its still giving me the error that it can't make files..
- Okay so DUH the issue was that the scratch and permanent directory don't exist inside of the docker, so i believe they can just be commented out, those lines.
- So my fix for now is just to have a short little if statement in the config that checks if its openstack, and if it is openstack, then we just replace the temp directories with comments

So I added this to the nwchem.app.conf in the resources
```bash
export IS_OPENSTACK=true
```
I think bc of how the configs are set up, this following bit also needs to go into the nwchem.app.conf, maybe even just the sed parts, since there's no place to have something there
 
```bash
if [[ "$IS_OPENSTACK" == "true" ]]; then
	sed -i -e "s/scratch_dir/#/g" $INPUT
	sed -i -e "s/permanent_dir/#/g" $INPUT
fi
```

So my nwchem.app.conf is now:
```bash
appkernel_run_env_template = """
sudo systemctl start docker
docker pull nwchemorg/nwchem-qc
# Temporary until we figure out exactly which one we want to run
# connecting it to a volume...
RUN_APPKERNEL="docker run -v $AKRR_TMP_WORKDIR:/opt/data nwchemorg/nwchem-qc aump2.nw"
sed -i -e "s/scratch_dir/#/g" $INPUT
sed -i -e "s/permanent_dir/#/g" $INPUT
"""
```
Okay that makes it run fine, but now we run into a similar error as before, where the variable geometry is referenced before assignment, and I'm not exactly sure what's going on

The plan: im gonna spin up an instance and run the docker and see if I can't find anything out

Update: wasn't able to figure out what the error was with the geometry, Nikolay figured out it has to do with how big the shared memory thing is, so we're editing how much memory is being shared, and you can do that with the --shm-size flag on docker run
```bash
# new RUN_APPKERNEL
RUN_APPKERNEL="docker run --rm --shm-size 8g -v $AKRR_TMP_WORKDIR:/opt/data nwchemorg/nwchem-qc aump2.nw"
```
Update: I made a dockerfile from their docker image so that it runs based on the number of cpu/cores not just 2, so now the app config looks like this:

```bash
appkernel_run_env_template = """
sudo systemctl start docker
docker pull pshoff/akrr_benchmarks:nwchem
# Temporary until we figure out exactly which one we want to run
# connecting it to a volume...

# the cap-add to not print all the errors that are being given
RUN_APPKERNEL="docker run --rm --shm-size 8g --cap-add=SYS_PTRACE pshoff/akrr_benchmarks:nwchem"
sed -i -e "s/scratch_dir/#/g" $INPUT
sed -i -e "s/permanent_dir/#/g" $INPUT
"""
```
So this incorporates the shared memory size and also gets rid of the printing of all those errors
yep! seems to be working well now






