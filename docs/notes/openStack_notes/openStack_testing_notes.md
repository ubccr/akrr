## Initial testing notes
### getting familiar with openStack

- Update: It's been a journey. I created a new directory for all the openstack testing stuff, in the projects directory in my home directory. In it there are key pairs and custom scripts

- Custom scripts: these are run when the instance is loading up, so it's used to set passwords and such, as well as do ssh stuff (I assume, will work on that)

- The script I used that was able to get me into the console online was:

```bash
#cloud-config

password: root
chpasswd: { expire: False }
ssh_pwauth: True
```
This changed the default password of the user _centos_ to root, and I was able to log in on the console online. 

- Update: to be able to ssh into it, you just need to have this in the cloud-config file that you attach to the instance when you create it

```bash
#cloud-config
ssh_pwauth: True
# I believe this allows anyone with the proper key to get in
```

Then you just type the following to ssh into the instance (centos is default user for centos7 image)
(note you have to either be in the directory with the private key or you have to give the path. This assumes you set up the instance with the proper key pair
 
```bash
ssh -i [private_key] centos@[IP Address]
```

Update 05/30/19: we're back on openstack and now we'll try to get hpcc to work on here

First Step: install Docker on the instance (I think i did this previously)

```bash
# From https://docs.docker.com/install/linux/docker-ce/centos/

sudo yum install -y yum-utils device-mapper-persistent-data lvm2
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install docker-ce docker-ce-cli containerd.io
# definitely want to add the user to the group so can just use docker by itself
sudo usermod -aG docker $(whoami) # adds current user to docker group
#sudo systemctl enable docker.service

sudo systemctl start docker

```

```bash
# Was able to get the docker image up to docker hub with
docker push pshoff/hpcc_benchmark:v02

# and then get it to the instance with
docker pull pshoff/hpcc_benchmark:v02
#seems to be running fine, though number of cores is just one, not sure about behavior

```

Trying to create new instances on openstack, keeps giving me error messages - Failed to allocate networks somehow
```bash
# error message:
Error: Failed to perform requested operation on instance "test_8cpu", the instance has an error status: Please try again later [Error: Build of instance 2a09851c-6aaa-47ea-84f2-bf9c2e5d10a8 aborted: Failed to allocate the network(s) with error No fixed IP addresses available for network: 7479b0e0-2d53-413d-8eaa-53cf1b2d9e30, not rescheduling.]. 

```

There seems to be a really weird bug where after doing the whole mpirun with hpcc anything that I cat only goes 150-160 lines before just stopping and I DON'T KNOW WHY. But the mpirun thing is the cause, bc I checked everywhere before, and everywhere after anything you cat just doesn't get to the end

Dr. Simakov took a look at it, he didn't know exactly either, so we're trying some things
1) try with counting the processors instead of the cores
2) try also just running hpcc on base, without docker

```bash
# copying over a directory into openstack using the key stuff
scp -i [path/to/key] -r execs/ centos@[IP Address]:/home/centos/execs_files
```

Note:
- It appears that everything comes out fine with the cat if we dont do -it on docker run or -i flag on the script
- If we have both, the cat doesnt work
- Trying just -it on docker run: Doesn't cat it all properly, doesn't start interactive session
- Trying just -i on script: Does cat properly, doesn't start interactive session

- Doing a bunch of runs through docker, hpcg isn't really consistent, varying in GFLOPS/s


- Looking at CPU Affinity

```bash
ps -aF
# this displays some statistics about the running processes
# PSR column shows what processor things are running on
```





