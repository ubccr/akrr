### Thoughts??

In akrr.cli.resource_deploy, around line 768, there is a line that appears to do nothing bc it starts up a server but then doesn't do anything with it, so perhaps can we get rid of that line?

Should check the result output? Seems like its saying only one node/one core for namd

So we want to run our own thing for nwchem, meaning doing things with volumes

So I'm looking at the volume on openstack, and hmmm, the inputs don't seem to have ANYTHING in them??
I'm gonna try just putting them in for now by getting the raws from git, but maybe this needs to be checked?
- Update, did that with wget, so now imma try it again
- Okay so its all the proper inputs looks like

## Looking into issue with games and namd - they don't seem to be running in parallel
- Looking primarily at top to see what's going on
Hpcc seems to be running in parallel - about 3.5 mins - it was less when i did -ppn 16 flag
Hpcg seems to be running in parallel - less than 5 mins
Gamess does not - only one process - takes about 20 mins
	- In the run script, when I did ./rungms, I switched {ppn} and {nodes} and that appears to have launched it in parallel, at least on local machine. - a lot better! about 5 mins
	- Uploading it to docker hub and will try to run it on openstack
Namd2 does seem to be... at least there are a bunch of processes, but still takes around 15 mins
Nwchem seems to be starting only 2 processes... but only takes about 2 mins

For Namd things
It seems I need to change how I'm running it perhaps?
```bash
# What nikolay has in github:
RUN_APPKERNEL="mpirun -n $AKRR_CORES -hostfile $PBS_NODEFILE $EXE ./input.namd"

# what I have in my script
${MPI_LOC}/mpirun ${NAMD_EXE_FULL_PATH} +p${ppn} ${work_dir}/input.namd


```
Yeah we need to use charmrun for this

UPDATE: turns out we just wanted to do the ./namd run without the whole charmrun deal bc with multicore machines we can do that, and on openstack its considered one machine, so that works fine now

### Update on how things are working (based on results file)
	- hpcc - takes about 3.5/4 mins, seems to be running on 8 cores
	- hpcg - 8 processes, takes about 1 min
	- gamess - 8 cores, takes about 2.5 mins
	- namd - running on 8 cores, takes about 2 mins (tho CPU usage for one is 800%)
	- nwchem - now working well, takes about 1.5 mins



Error I was experiencing with running ior on openstack:
Docker wouldn't run bc some weird file not found error or something, but only on openstack
what I did: I just added a yum update command in the dockerfile so it updates stuff and now it appears to work idk


