# Updating from AKRR-1.0 to AKRR-2.1

There are significant differences between new and old version.
The update script will update database, config files and move logs/outputs from appkernel runs. 

> Developmental version in-between AKRR-1.0 to AKRR-2.0 should be able to update with this instructions. 


## Create Back-Up of MySQL Databases

To be on safe side make a back-up of AKRR databases:

```shell script
mysqldump --extended-insert=FALSE -u <user> -p mod_akrr| gzip -c > mod_akrr_1.0.gz
mysqldump --extended-insert=FALSE -u <user> -p mod_appkernel| gzip -c > mod_appkernel_1.0.gz
```

## Rename Old AKRR Home directory (Optional)

The update doesn't do in place update and so the old AKRR home directory should be different from new one. 
If you like the old name rename it to reuse for new one.

```shell script
mv akrr akrr_old
```

## RPM Installation


New installation 
