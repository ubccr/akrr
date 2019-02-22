# Installation of AKRR Daemon

AKRR support two installation ways: 
1) Global installation from RPM (on CentOS system) and 
2) In-source installation from source code.


## Prerequisites

In case of RPM installation the dependencies would be installed automatically 
(add EPEL repository if needed). The following dependencies are needed to be installed
for in-source installation on CentOS:
 
 
```bash
# Install EPEL if needed
yum -y install epel-release
# Install dependencies
yum -y install python34 python34-libs python34-bottle python34-requests \
    python34-mysql python34-typing openssl openssh-clients crontabs
```

If AKRR will use MariaDB/MySQL on the local machine install it:
```bash 
yum -y install mariadb-server  
```

## Installation
### RPM Installation

Download in install AKRR RPM
```bash
yum install akrr-{{ page.sw_version }}-1.noarch.rpm
```

### In Source Installation

Download tar.gz archive and uncompress it in desired installation location:
```bash
tar zxvf akrr-{{ page.sw_version }}.tar.gz
``` 

You can add bin directory from AKRR to you PATH environment variable or 
call AKRR commands with full pathname.

## Configuration

```bash
akrr setup
```



Example input output

```text
[INFO] AKRR configuration will be in /root/akrr/etc/akrr.conf
[INFO] Before Installation continues we need to setup the database.
[INPUT]: Please specify a database user to access mod_akrr database (Used by AKRR)(This user will be created if it does not already exist):
[akrruser] 
[INPUT]: Please specify a password:
Password: 
[INPUT]: Please reenter the password:
Password: 

[INPUT]: Please provide an administrative database user (for localhost:3306) under which the installation sql script should run (This user must have privileges to create users and databases).
Username: root
[INPUT]: Please provide the password for the the user which you previously entered:
Password: 

[INPUT]: Please specify a database user to access mod_appkernel database (Used by XDMoD appkernel module, AKRR creates and syncronize resource and appkernel description)(This user will be created if it does not already exist):
[akrruser] 
[INFO] Password already entered.


[INPUT]: Please specify the user that will be connecting to the XDMoD database (modw):
[akrruser] 
[INFO] Password already entered.


[INPUT]: Please enter the e-mail where cron will send messages (leave empty to opt out):

[INFO] Creating mod_akrr and user to access it
[INFO] Creating mod_appkernel and user to access it
[INFO] Setting user to access modw
[INFO] Creating directories structure.
[INFO] Generating self-signed certificate for REST-API
[INFO]     new self-signed certificate have been generated
[INFO] Generating configuration file ...
[INFO] Configuration is written to: /root/akrr/etc/akrr.conf
[INFO] Removing access for group members and everybody for all files.
[INFO] Checking access to DBs.
[INFO] All Databases / User privileges check out!
[INFO] Creating tables and populating them with initial values.
[INFO] Starting AKRR daemon
[2019-02-22 21:59:41,351 - INFO] Directory /root/akrr/log/data/srv does not exist, creating it.
[2019-02-22 21:59:41,352 - INFO] Writing logs to:
        /root/akrr/log/data/srv/2019.02.22_21.59.352211.log
[2019-02-22 21:59:41,603 - INFO] following log: /root/akrr/log/data/srv/2019.02.22_21.59.352211.log
[2019-02-22 21:59:41,545 - INFO] Starting Application Remote Runner
 [2019-02-22 21:59:41,568 - INFO] AKRR Scheduler PID is 258.
 [2019-02-22 21:59:41,592 - INFO] Starting REST-API Service
 [2019-02-22 21:59:41,595 - INFO] ####################################################################################################
 [2019-02-22 21:59:41,596 - INFO] Got into the running loop on 2019-02-22 21:59:41
 [2019-02-22 21:59:41,596 - INFO] ####################################################################################################
 
 Starting REST-API Service
 Bottle v0.12.13 server starting up (using SSLWSGIRefServer())...
 Listening on http://localhost:8091/
[2019-02-22 21:59:41,607 - INFO] 
AKRR Server successfully reached the loop.
 [INFO] Checking that AKRR daemon is running
[INFO] Beginning check of the AKRR Rest API...
[INFO] REST API is up and running!
[INFO] Installing cron entries
no crontab for root
[INFO] Crontab does not have user's crontab yet
[INFO] Cron Scripts Processed!
[INFO] AKRR is set up and is running.
```
