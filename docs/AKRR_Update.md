# Updating from AKRR-1.0 to AKRR-2.1

There are significant differences between the new and old versions.
The update script will update the database, config files and move logs/outputs from appkernel runs. 

> Most of developmental version in-between AKRR-1.0 to AKRR-2.0 should be able to update with these instructions. 


## Create Back-Up of MySQL Databases (Strongly Recommended)

To be on safe side make a back-up of the AKRR databases:

```shell script
mysqldump --extended-insert=FALSE -u <user> -p mod_akrr| gzip -c > mod_akrr_1.0.gz
mysqldump --extended-insert=FALSE -u <user> -p mod_appkernel| gzip -c > mod_appkernel_1.0.gz
```

## Rename Old AKRR Home directory

The update script will move updated configs and logs to new location. So if you want to keep AKRR in same directory rename old one:

```shell script
mv akrr akrr_old
```

## Installation

In the previous version AKRR was source installed. In this version RPM installation is recommended, 
in-source and using regular python methods are also possible.
 
The akrr update command should work for most combinations of older and newer installations. 

### RPM Installation
Download RPM from https://github.com/ubccr/akrr/releases and install it:

```shell script
wget https://github.com/ubccr/akrr/releases/download/v{{ page.sw_version }}/akrr-{{ page.sw_version }}-1.noarch.rpm
sudo yum install akrr-{{ page.sw_version }}-1.noarch.rpm
```


## Run Update Script

Run update script (as user which will run akrr, **don't use root** for that):

```shell script
akrr -vv update --akrr-home=<New AKRR Home, default is ~/akrr> --old-akrr-home=<Old AKRR Home>
```
> * The new AKRR home should be different from the old one
>
> * If you ran many appkernels in past it can take some time, extra verbose arguments ```-vv``` will help to 
understand what it is doing. 

During update .bashrc could be modified to include new non-standard location of ARKK_HOME or akrr executable.
In this case to continue in same terminal session reload .bashrc:

```bash
unset AKRR_HOME
source .bashrc
```

At the end it will print recommended commands to run to finish update. The most important is to run:

```bash
akrr resource deploy --overwrite -r <resource>
```

This will install new app kernel utilities. But be careful it will overwrites inputs, so keep a copy if you modified some.

The proper update of appkernels can be verified with running verificantion and test run command:

 ```bash
akrr app validate -r <resource> -a <appkernel> -n <number of nodes>
```

Now you can update the [xdmod-appkernels](https://appkernels.xdmod.org/) module for Open XDMoD.
Most likely it was already done during xdmod update, as yum would not allow for xdmod update without simultaneous 
update of xdmod-appkernels.
