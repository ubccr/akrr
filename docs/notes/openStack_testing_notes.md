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
















