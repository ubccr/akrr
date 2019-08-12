## Things to perhaps look into / Small things

- In akrr.cli.resource_deploy, around line 768, there is a line that appears to do nothing bc it starts up a server but then doesn't do anything with it, so perhaps can we get rid of that line?

- Got a weird thing when setting up the openstack resource: sometimes the execs and input tars get unpacked and all the files are there, but they're all empty. Not sure what causes this, and I don't think it happens all the time, but it is possible you have to go into the openstack volume and set things up with wget manually.

- It appears the template for gamess is slightly off. Not sure if its different if running on multiple nodes or not but at least with running on one node, $AKRR_NODES and $AKRR_CORES_PER_NODE should be switched, since rungms uses the 3rd argument to determine the number of cpus (processes), so at least with one node, that would be $AKRR_CORES_PER_NODE. Unsure how it would work with multiple nodes though. Regardless, if running on one node, you would have to modify that appkernel_run_env_template for gamess.

- For Namd, I used a multicore build since everything was being run on one node, so I can just use the regular namd executable to start off things. (Check this website that explains it a bit: https://www.ks.uiuc.edu/Research/namd/2.9/ug/node79.html)
	- However it does mean I am not using charmrun in order to start things off in the Docker

### Update on how things are working (based on results file)
	- hpcc - takes about 3.5/4 mins, seems to be running on 8 cores
	- hpcg - 8 processes, takes about 1 min
	- gamess - 8 cores, takes about 2.5 mins
	- namd - running on 8 cores, takes about 2 mins (tho CPU usage for one is 800%)
	- nwchem - now working well, takes about 1.5 mins



