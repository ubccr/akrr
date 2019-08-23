## Setting up Docker on OpenStack volume

(You should be able to do this without the command line interface using the command line on the web interface but I found it easier to do it with the cli)

First create the volume you want to have Docker on (I called it testing_volume)

```bash
openstack volume create --image centos7-ccr-20181127-1 --size 20 --description "test volume" testing_volume
```
Spin up an instance that uses the volume:

```bash
openstack server create --flavor c8.m16 --volume testing_volume --network lakeeffect-199.109.195 --security-group default --security-group SSH --key-name openstack-testing temp_docker_test
```

Then log into the instance:

```bash
ssh -i openstack-testing.key centos@199.109.192.21
```

Once you're in the instance, you can install docker. Following the instructions here: https://docs.docker.com/install/linux/docker-ce/centos/

(Note: this is for installing docker on centos, things may be slightly different if you use other operating systems)

```bash
sudo yum install -y yum-utils \
  device-mapper-persistent-data \
  lvm2

sudo yum-config-manager \
    --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo

sudo yum install docker-ce docker-ce-cli containerd.io
# say yes to installing everything

# testing to see if it starts up properly
sudo systemctl start docker
# no errors is good

# we want to make it so anyone can use docker (specifically the centos user)

# stop docker daemon
sudo systemctl stop docker

sudo groupadd docker
sudo usermod -aG docker $USER
# so the centos user should be fine now to use docker normally
# you do need to log out and log back in for the change to take effect
```
So now that that is set up, stop and delete the instance (either web interface or server delete command).

Then start one up again and run docker commands:

```bash
openstack server create --flavor c8.m16 --volume testing_volume --network lakeeffect-199.109.195 --security-group default --security-group SSH --key-name openstack-testing test_docker

# ssh into the server
ssh -i openstack-testing.key centos@199.109.192.28 
# (note ip address might be different)

# then we just start the daemon and run the docker test image
sudo systemctl start docker
docker run hello-world

```
Sample output:
```bash
[centos@test-docker ~]$ docker run hello-world
Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
1b930d010525: Pull complete 
Digest: sha256:6540fc08ee6e6b7b63468dc3317e3303aae178cb8a45ed3123180328bcc1d20f
Status: Downloaded newer image for hello-world:latest

Hello from Docker!
This message shows that your installation appears to be working correctly.

To generate this message, Docker took the following steps:
 1. The Docker client contacted the Docker daemon.
 2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
    (amd64)
 3. The Docker daemon created a new container from that image which runs the
    executable that produces the output you are currently reading.
 4. The Docker daemon streamed that output to the Docker client, which sent it
    to your terminal.

To try something more ambitious, you can run an Ubuntu container with:
 $ docker run -it ubuntu bash

Share images, automate workflows, and more with a free Docker ID:
 https://hub.docker.com/

For more examples and ideas, visit:
 https://docs.docker.com/get-started/

```
If this completes without error, you should be fine using docker normally with that volume on OpenStack! You can do all the regular docker pull, docker push, etc commands.
Just remember every time you start up the instance you have to start the docker daemon to use docker commands.

If you want to pull from private docker repositories, you also need to set up a login/user to use every time you pull. On the instance with the volume you can do:
```bash
docker login
```
Then follow the prompts. 
After you do that the volume will be set up with that user so you can pull from any private repositories that the user has access to without needing to worry about interactively putting in username and password.


