These are notes on the installation/setting up of AKRR 

- There may be errors with sudo yum install akrr....rpm
	- If error is that akrr_test is not available or whatever: run the following in the top directory of AKRR:
```bash
sudo docker build -t akrr_test -f Dockerfile_run_tests .
# Then what needs to run is the make_rpm_with_docker.sh in the docker directory
```

- EPEL does not have python34-mysql or python34-typing
	- rpm of python34-typing can be found here: https://centos.pkgs.org/7/puias-unsupported-x86_64/python34-typing-3.5.2.2-3.sdl7.noarch.rpm.html

	- Eventual fix: just change all the setup things to python36 instead of python34 and no error
	- Also changed the Install file to have python36 in it

- For whatever reason, there was trouble with finding the modules when running 'akrr setup'
	- When typing akrr in terminal, it went to /usr/bin/akrr
	- Had to end up appending the entire akrr repository to the sys path with sys.append
		- (perhaps if added to path before somehow? Perhaps change the akrr file in bin to do this automatically, since that is what is copied to /usr/bin/akrr)
	- That seems to have fixed the problem
        - Want to look into that akrr file in the bin? the two directory things do not really seem to do anything
	- UPDATE: the problem was that the rpm was being made with python3.4 still, so now I am going through and updating all the files so that it is python3.6 so that HOPEFULLY it can find the right path (and so that we do not mess with python paths)

- I had to make all the other images locally (the akrr_ready_... etc docker images that Docker_run_tests uses) since the images provided were all with python34 still. To do this I based it off of the instructions in the README of akrr/docker/centos_slurm_single_host_wlm


- The image nsimakov/akrr_ready_centos_slurm_single_host_wlm:1 uses outdate python34. To use the python36 as is proper, you have to create the images yourself and run it all locally until it gets updated on the docker cloud
	- The Dockerfiles in this repo use the same image names just without the nsimakov in front
	- Recommendation: do all the image creating manually based on the readme in akrr/docker/centos_slurm_single_host_wlm, except without the nsimakov/ part at the beginning of each image


- Having some problems with setting up akrr on this machine, trying to do akrr setup but was not working properly
	- had to start mariadb service with 'service mariadb start' then I got a different error message!
	- (btw root does not need a password for logging into mysql...)

- Update: akrr setup ran to completion!
	- First I made the akrruser and gave it all the appropriate privileges in mysql with root
	- Then I ran into problems bc modw was being used (thats the XDMOD db) so I installed XDMOD too and so far it isnt yelling at me. Stay tuned!

- Update: resource ub-hpc successfully added. 
	- For head node, I used the local thing that was in my bash (where it says hoffmaps@----)
	- Based my answers off of the AKRR_Add_Resource

- Update: able to generate batch jobs decently fine it seems, but problems came when trying to do akrr resource deploy -r ub-hpc - kept saying it wasn't bash all the time - so I'll try and figure that out
	- Also I did generate some batch files and try to submit them, but ran into issues there because none of the akrr commands were recognized!! Uh oh!
	


- Update: I'm thinking I probably added the ub-hpc thing wrong. As the head node I used the local thing, and I think perhaps I should use the vortex.ccr.buffalo.edu thing... not sure
	- I'll try and do things with the ub-hpc connected to the local node, but I don't think that will be what we want, since I'm just connecting back to my own computer
		- but I was able to fix the 'bash all the time' thing, so hopefully that isn't a problem anymore for that at least
	- I'm trying to make a ub-hpc-actual that actually has me ssh to hoffmaps@vortex.ccr.buffalo.edu, but it keeps failing its pings, and I'm not sure why, since I can ssh into it fine from terminal, I'll do some of my own testing too
	
- Update: So I can't ping vortex.ccr.buffalo.edu, but I can ssh into it. Some solutions I found online but am unsure about:
	- add the server address to /etc/resolv.conf (so add 128.205.41.13 in this case) - doesn't work
	- some sort of firewall blocking things?
	- The fix to this was just to not ping when trying to get there, so I had to look at the -h for akrr resource DUH - lesson learned: look at -h for everything too




- Update: able to successfully connect to vortex.ccr.buffalo.edu, and able to run all the job things, based off of guide in repo, it all ran successfully







