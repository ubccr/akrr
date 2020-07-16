# Updating from AKRR-1.0 to AKRR-2.1

There are significant differences between the new and old versions.
The update script will update the database, config files and move logs/outputs from appkernel runs. 

> Developmental version in-between AKRR-1.0 to AKRR-2.0 should be able to update with these instructions. 


## Create Back-Up of MySQL Databases

To be on safe side make a back-up of the AKRR databases:

```shell script
mysqldump --extended-insert=FALSE -u <user> -p mod_akrr| gzip -c > mod_akrr_1.0.gz
mysqldump --extended-insert=FALSE -u <user> -p mod_appkernel| gzip -c > mod_appkernel_1.0.gz
```

## Rename Old AKRR Home directory (Optional)

The update doesn't do an in place update and so the old AKRR home directory should be different from new one. 
If you like the old name rename it to reuse it for the new one.

```shell script
mv akrr akrr_old
```

## Installation

In the previous version AKRR was source installed. In this version RPM installation is recommended, 
in source and using regular python methods are also possible.
 
The akrr update command should work for all combinations of older and new installations. 

### RPM Installation
Download RPM from https://github.com/ubccr/akrr/releases:

```shell script
wget https://github.com/ubccr/akrr/releases/download/v2.1.0/akrr-2.1.0-1.noarch.rpm
```

Install:
 
```shell script
sudo yum install akrr-2.1.0-1.noarch.rpm
```

## Run Update Script

Run update script (as user which will run akrr, don't use root for that):

```shell script
akrr -vv update --akrr-home=<New AKRR Home, default is ~/akrr> --old-akrr-home=<Old AKRR Home>
```

The new AKRR home should be different from the old one. The old home can be renamed, for example if it was in the default location:

```shell script
mv ~/akrr ~/akrr_old
akrr -vv update --akrr-home=~/akrr --old-akrr-home=~/akrr_old
```

At the end it will print recommended commands to run to finish update. The most important is to run:

```bash
akrr resource deploy --overwrite -r <resource>
```

This will install new app kernel utilities. But be careful it will overwrites inputs, so keep a copy if you modified some.
 
Now you can update the `xdmod-appkernels` module for Open XDMoD.
