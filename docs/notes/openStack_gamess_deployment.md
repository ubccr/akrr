## Notes on deploying gamess to openstack

Let's first make the standard resource and appker standardized (modify for your purposes)
```bash
export RESOURCE=lakeeffect
export APPKER=gamess
```
Generate Initial Config File
```bash
akrr app add -a $APPKER -r $RESOURCE
```

Sample output:
```bash
[INFO] Generating application kernel configuration for gamess on lakeeffect
[INFO] Application kernel configuration for gamess on lakeeffect is in: 
        /home/hoffmaps/projects/akrr/etc/resources/lakeeffect/gamess.app.conf

```
Editing the config file now, since we are using Docker and not the actual games executable
Originally the executable is:

```bash
appkernel_run_env_template = """
# Load application enviroment
module load gamess
module list

# set executable location
VERNO=01
EXE=$GAMESS_DIR/gamess.$VERNO.x

# set how to run app kernel
RUN_APPKERNEL="$AKRR_APPKER_DIR/execs/gamess/rungms $INPUT $VERNO $AKRR_NODES $AKRR_CORES_PER_NODE"
"""

```
New run just has the docker image

```bash
appkernel_run_env_template = """
sudo systemctl start docker
docker pull pshoff/akrr_benchmarks:gamess

# set how to run app kernel
RUN_APPKERNEL="docker run --rm pshoff/akrr_benchmarks:gamess"
"""
```
Now we just try the validation run
```bash
akrr app validate -n 1 -r $RESOURCE -a $APPKER
```
Example validation file is in openStack_gamess_validation_example

