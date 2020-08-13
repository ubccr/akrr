## Notes for setting up namd on openstack without docker

So like before, you sftp into an openstack instance that has the volume and put in the directory that has the executable and put it in the execs directory
Can add the link too if you would like.
For me, I used namd_2.13b2-multicore since I'm only using 1 node essentially (based off of stuff on this website: https://www.ks.uiuc.edu/Research/namd/2.9/ug/node79.html)

Then I fiddled with the config file to run that namd by itself (not using charmrun bc of above)

So my config file looks like 

```bash
appkernel_run_env_template = """

export CONV_RSH=ssh
#set executable location
EXE="/home/centos/appker/resource/no_docker/execs/namd/namd2"

#set how to run app kernel
RUN_APPKERNEL="$EXE  +p$AKRR_CORES ./input.namd"
"""

```
And then it should be fine from there


