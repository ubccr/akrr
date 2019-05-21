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





