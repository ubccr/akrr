## Notes on deployment of namd on openStack

Standard start - make appker and resource variables
```bash
export APPKER=namd
export RESOURCE=lakeeffect

```
Then get the initial config file
```bash
akrr app add -a $APPKER -r $RESOURCE

```
Example output
```bash
[INFO] Generating application kernel configuration for namd on lakeeffect
[INFO] Application kernel configuration for namd on lakeeffect is in: 
        /home/hoffmaps/projects/akrr/etc/resources/lakeeffect/namd.app.conf

```
Now lets look at the config file and change it so it uses the docker
```bash
# original
appkernel_run_env_template = """
#Load application environment
module load namd
export CONV_RSH=ssh

#set executable location
EXE=`which namd2`
charmrun_bin=`which charmrun`

#prepare nodelist for charmmrun
for n in $AKRR_NODELIST; do echo host $n>>nodelist; done

#set how to run app kernel
RUN_APPKERNEL="$charmrun_bin  +p$AKRR_CORES ++nodelist nodelist $EXE ./input.namd"
"""

````

New, now with docker

```bash
appkernel_run_env_template = """
sudo systemctl start docker
docker pull pshoff/akrr_benchmarks:namd

#set how to run app kernel
RUN_APPKERNEL="docker run pshoff/akrr_benchmarks:namd"
"""
```

Then we can try running the validation
```bash
akrr app validate -n 1 -r $RESOURCE -a $APPKER

```
See an example of the validation in openStack_namd_validation_example
Look at output files, and if they seem okay, you're good!








