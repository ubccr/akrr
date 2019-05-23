## Initial testing notes
# getting familiar with openStack

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













