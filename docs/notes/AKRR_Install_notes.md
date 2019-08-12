## Notes on setting up of AKRR and connecting it with ub-hpc 

- There may be errors with sudo yum install akrr....rpm
	- If error is that akrr_test is not available or whatever: run the following in the top directory of AKRR:
```bash
sudo docker build -t akrr_test -f Dockerfile_run_tests .
# Then what needs to run is the make_rpm_with_docker.sh in the docker directory
```

Should be fixed but in case there are errors, just make sure that everything is using python36, not python34.

So when you make the Docker images for the setup, everything should be python36. Check the README of akrr/docker/centos_slurm_single_host_wlm. Possible that the Docker images already have pytho36, but if you're getting errors you may want to try and make them locally to make sure you have python36.


Trying to get it set up with a resource: when it says how to connect to head node, you want to put the address that you would use normally to ssh (for example for ub-ccr, the address would be vortex.ccr.buffalo.edu as the head node)


Its possible that the resource doesn't do pinging properly (idk why) but if you can ssh into it normally, then you could try creating the resource with the --no-ping option and it might give you a warning but it should be fine.




