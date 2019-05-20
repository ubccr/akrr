# AKRR Installation

AKRR support two installation ways: 
1) Global installation from RPM (on CentOS system) and 
2) In-source installation from source code, for development purposes.

## Prerequisites

Prior installing AKRR, XDMoD already should be installed. The simplest way is to 
install AKRR on same host where XDMoD was installed. AKRR needs access to XDMoD 
databases and XDMoD need access to AKRR database for results ingestion.

In case of RPM installation the dependencies would be installed automatically. Some of
the dependencies are from EPEL repository. If it was not done yet add it to repo list:

```bash
# Install EPEL if needed
yum -y install epel-release
```

The following dependencies are needed to be installed for in-source installation on CentOS:
 
```bash
# Install dependencies
yum -y install python36 python36-libs python36-bottle python36-requests \
    python36-mysql python36-typing openssl openssh-clients crontabs
```

If AKRR will use MariaDB/MySQL on the local machine install it:
```bash 
yum -y install mariadb-server  
```

## Installation on Same Host as XDMoD
### RPM Installation

Download in install AKRR RPM
```bash
sudo yum install akrr-{{ page.sw_version }}-1.noarch.rpm
```

### In Source Installation

Download tar.gz archive and uncompress it in desired installation location:
```bash
tar zxvf akrr-{{ page.sw_version }}.tar.gz
``` 

You can add bin directory from AKRR to you PATH environment variable or 
call AKRR commands with full pathname.

## Configuration
During this step AKRR will be configured and AKRR daemon will be started. 
In more details the setup script creates AKRR databases, sets new user for 
accessing these databases, creates self-signed SSL certificate for AKRR 
REST API (AKRR REST API used only internally for communication between AKRR 
and OpenXDMoD),  creates and populates AKRR database tables, followed by 
first start of AKRR daemon and creation of cronjobs for periodic log rotation 
and AKRR daemon status check.

Execute the akrr CLI with setup command. Provide the required information 
when prompted 
(the database user names / passwords):

```bash
akrr setup
```


Example of output from `akrr setup` execution:

```text
[INFO] AKRR configuration will be in /home/akrruser/akrr/etc/akrr.conf
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


no crontab for akrruser
[INPUT]: Please enter the e-mail where cron will send messages (leave empty to opt out):
nikolays@buffalo.edu
[INFO] Creating mod_akrr and user to access it
[INFO] Creating mod_appkernel and user to access it
[INFO] Setting user to access modw
[INFO] Creating directories structure.
[INFO] Generating self-signed certificate for REST-API
[INFO]     new self-signed certificate have been generated
[INFO] Generating configuration file ...
[INFO] Configuration is written to: /home/akrruser/akrr/etc/akrr.conf
[INFO] Removing access for group members and everybody for all files.
[INFO] Checking access to DBs.
[INFO] All Databases / User privileges check out!
[INFO] Creating tables and populating them with initial values.
[INFO] Starting AKRR daemon
[2019-03-12 15:04:46,393 - INFO] Directory /home/akrruser/akrr/log/data/srv does not exist, creating it.
[2019-03-12 15:04:46,393 - INFO] Writing logs to:
        /home/akrruser/akrr/log/data/srv/2019.03.12_15.04.393317.log
[2019-03-12 15:04:46,644 - INFO] following log: /home/akrruser/akrr/log/data/srv/2019.03.12_15.04.393317.log
[2019-03-12 15:04:46,511 - INFO] Starting Application Remote Runner
 [2019-03-12 15:04:46,527 - INFO] AKRR Scheduler PID is 261.
 [2019-03-12 15:04:46,538 - INFO] Starting REST-API Service
 [2019-03-12 15:04:46,540 - INFO] ####################################################################################################
 [2019-03-12 15:04:46,541 - INFO] Got into the running loop on 2019-03-12 15:04:46
 [2019-03-12 15:04:46,541 - INFO] ####################################################################################################
 
 Starting REST-API Service
 Bottle v0.12.13 server starting up (using SSLWSGIRefServer())...
 Listening on http://localhost:8091/
[2019-03-12 15:04:46,646 - INFO] 
AKRR Server successfully reached the loop.
 [INFO] Checking that AKRR daemon is running
[INFO] Beginning check of the AKRR Rest API...
[INFO] REST API is up and running!
[INFO] Installing cron entries
no crontab for akrruser
[INFO] Crontab does not have user's crontab yet
[INFO] Cron Scripts Processed!
[INFO] AKRR is set up and is running.
```

At this point AKRR should be installed and running. Now new resources can be added.

Next: [Usage](AKRR_Usage.md)
