### Openstack setting up the volume

So to make things work on openstack, you have to set up a volume that akrr can use every time when running its apps. This volume also has to have docker on it.

So, first create a volume. I did it on the web interface because it's simpler that way.
You could also make it from the cli using openstack volume create.
I used a centos7 base image and made the volume 20 gb.

Then, start up an image with the volume
```bash
openstack server create --flavor c8.m16 --volume dockervolume02 --network lakeeffect-199.109.195 --security-group default --security-group SSH --key-name openstack-testing test_create_from_cl

```
Key here is to make sure you specify the right volume. In my case I'm using dockervolume02. The other parameters are just making sure its set up properly from the way my system does it. 
So, once you have the volume made, you need to install docker on it.
Log into your openstack instance
```bash
ssh -i openstack-testing.key centos@199.109.192.8
```
Now you need to install docker. Following instructions: https://docs.docker.com/install/linux/docker-ce/centos/

```bash
sudo yum install -y yum-utils \
  device-mapper-persistent-data \
  lvm2

sudo yum-config-manager \
    --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo

sudo yum install docker-ce docker-ce-cli containerd.io

sudo systemctl start docker
# now we want to make it so that any user can use docker, not just super users

# stop docker daemon
sudo systemctl stop docker

sudo groupadd docker
sudo usermod -aG docker $USER
# so the centos user should be fine now to use docker normally

```
Stopped and deleted instance
Now lets try starting up a new one and running docker commands
```bash
openstack server create --flavor c8.m16 --volume dockervolume02 --network lakeeffect-199.109.195 --security-group default --security-group SSH --key-name openstack-testing akrrtemp


sh -i openstack-testing.key centos@199.109.192.13

# success! but we do need to start the docker daemon first
sudo systemctl start docker
docker run hello-world

# so the volume with docker on it is: dockervolume
```
That should have the volume all set up with docker. 

If you want to automatically pull images from a private docker repository, you also need to set up a login/user to use every time you pull.
Just do (on the instance)
```bash
docker login
```
And follow the prompt with whatever username you want to use that has access to the private repo(s) you want to use.

Now you just need to set up the resource to use that volume when you're deploying. For more see openStack_get_akrr_working_notes.md

