# AKRR Installation

AKRR support two installation ways:

1) Global installation from RPM (on CentOS system) 

2) In-source installation from source code, for development purposes.

## Prerequisites

Prior installing AKRR, XDMoD already should be installed. The simplest way is to 
install AKRR on same host where XDMoD was installed. AKRR needs access to XDMoD 
databases and XDMoD need access to AKRR database for results ingestion.

In case of RPM installation the dependencies would be installed automatically. Some of
the dependencies are from EPEL repository. If it was not done yet add it to repo list:

```bash
# Install EPEL if needed
sudo yum -y install epel-release
```

If AKRR will use MariaDB/MySQL on the local machine install it:

```bash 
yum -y install mariadb-server mariadb
```

The following dependencies are needed to be installed for in-source installation on CentOS:
 
```bash
# Install dependencies
sudo yum -y install python36 python36-libs python36-bottle \
    python36-requests python36-mysql python36-typing \
    python36-psutil python36-dateutil python36-prettytable \
    python36-PyYAML openssl openssh-clients crontabs
```

## Installation on Same Host as XDMoD
### RPM Installation

Download in install AKRR RPM
```bash
wget https://github.com/ubccr/akrr/releases/download/v{{ page.sw_version }}/akrr-{{ page.sw_version }}-1.noarch.rpm
sudo yum install akrr-{{ page.sw_version }}-1.noarch.rpm
```

### In Source Installation

Download tar.gz archive and uncompress it in desired installation location:
```bash
wget https://github.com/ubccr/akrr/archive/v{{ page.sw_version }}.tar.gz
tar zxvf v{{ page.sw_version }}.tar.gz
``` 

Alternatively with git
```bash
git clone https://github.com/ubccr/akrr.git
cd akrr
git checkout v{{ page.sw_version }}
``` 

You can add bin directory from AKRR to you PATH environment variable or 
call AKRR commands with full pathname.

## Configuration
During this step AKRR will be configured and AKRR daemon will be started. 
In more details the setup script creates AKRR databases, sets new user for 
accessing these databases, creates self-signed SSL certificate for AKRR 
REST API (AKRR REST API used only internally for communication between AKRR 
and Open XDMoD), creates and populates AKRR database tables, followed by 
first start of AKRR daemon and creation of cronjobs for periodic log rotation 
and AKRR daemon status check.

Execute the akrr CLI with setup command. Provide the required information 
when prompted 
(the database user names / passwords):

```bash
akrr setup
```
> **Tips and Tricks**
>
> **Don't run AKRR as root**, use a regular user.
>
> Running akrr in verbose mode can help identify issues:
> ```bash
> akrr -v setup
> ```
> 

Example of output from `akrr setup` execution:

```text
[INFO] Creating directories structure.
[INFO] Before Installation continues we need to setup the database.
[INPUT] Please specify a database user to access mod_akrr database (Used by AKRR)(This user will be created if it does not already exist):
[akrruser]: 
[INPUT] Please specify a password:
Password: 
[INPUT] Please reenter the password:
Password: 

[INPUT] Please provide an administrative database user (for localhost:3306) under which the installation sql script should run (This user must have privileges to create users and databases).
[root]: 
[INPUT] Please provide the password for the the user which you previously entered:
Password: 

[INPUT] Please specify a database user to access mod_appkernel database (Used by XDMoD appkernel module, AKRR creates and syncronize resource and appkernel description)(This user will be created if it does not already exist):
[akrruser]: 
[INFO] Password already entered.

[INPUT] Please provide an administrative database user (for localhost:3306) under which the installation sql script should run (This user must have privileges to create users and databases).
[root]: 
[INPUT] Please provide the password for the the user which you previously entered:
Password: 

[INPUT] Please specify the user that will be connecting to the XDMoD database (modw):
[akrruser]: 
[INFO] Password already entered.

[INPUT] Please provide an administrative database user (for localhost:3306) under which the installation sql script should run (This user must have privileges to create users and databases).
[root]: 
[INPUT] Please provide the password for the the user which you previously entered:
Password: 

no crontab for centos
[INPUT] Please enter the e-mail where cron will send messages (leave empty to opt out):

[INFO] Creating mod_akrr and user to access it
[INFO] Creating mod_appkernel and user to access it
[INFO] Setting user to access modw
[INFO] Generating self-signed certificate for REST-API
[INFO]     new self-signed certificate have been generated
[INFO] Generating configuration file ...
[INFO] Configuration is written to: /home/centos/akrr/etc/akrr.conf
[INFO] Removing access for group members and everybody for all files.
[INFO] Checking access to DBs.
[INFO] All Databases / User privileges check out!
[INFO] Creating tables and populating them with initial values.
[INFO] Updating .bashrc
[INFO] AKRR is in standard location, no updates to $HOME/.bashrc
[INFO] Starting AKRR daemon
[2020-08-01 02:33:49,656 - INFO] Directory /home/centos/akrr/log/data/srv does not exist, creating it.
[2020-08-01 02:33:49,657 - INFO] Writing logs to:
        /home/centos/akrr/log/data/srv/2020.08.01_02.33.657178.log
[2020-08-01 02:33:49,910 - INFO] following log: /home/centos/akrr/log/data/srv/2020.08.01_02.33.657178.log
[2020-08-01 02:33:49,724 - INFO] Starting Application Remote Runner
 [2020-08-01 02:33:49,772 - INFO] AKRR Scheduler PID is 12989.
 [2020-08-01 02:33:49,808 - INFO] Starting REST-API Service
 [2020-08-01 02:33:49,814 - INFO] ####################################################################################################
 [2020-08-01 02:33:49,816 - INFO] Got into the running loop on 2020-08-01 02:33:49
[2020-08-01 02:33:50,138 - INFO] 
AKRR Server successfully reached the loop.
 [INFO] Checking that AKRR daemon is running
[INFO] Beginning check of the AKRR Rest API...
[INFO] REST API is up and running!
[INFO] Installing cron entries
no crontab for centos
[INFO] Crontab does not have user's crontab yet
[INFO] Crontab updated.
[INFO] AKRR is set up and is running.
```

At this point AKRR should be installed and running. During installation 
.bashrc could be modified to include non-standard location of ARKK_HOME or akrr executable.
In this case to continue in same terminal session reload .bashrc:

```bash
source .bashrc prior to continue!
```

The AKRR daemon status can be checked with:
```bash
akrr daemon status
```

```
[INFO] AKRR Server is up and it's PID is 15292
[INFO] There is no scheduled tasks
[INFO] There is no active tasks
[INFO] There is no complete tasks
[INFO] There were no tasks completed with errors.
```

Now [new resources can be added]](AKRR_Add_Resource.md).

## Tips and Tricks

### MySQL Server on a Different Host

In case if MySQL is located at different host following options to `akrr setup` command allows 
to specify MySQL server host name.

```text
  --akrr-db AKRR_DB  mod_akrr2 database location in
                     [user[:password]@]host[:port] format, missing values will
                     be asked. Default: localhost:3306
  --ak-db AK_DB      mod_appkernel database location. Usually same host as
                     XDMoD's databases host. Default: same as akrr
  --xd-db XD_DB      XDMoD modw database location. It is XDMoD's databases
                     host. Default: same as akr
```

### No Administrative Rights on MySQL Server

If there is no access with administrative rights to MySQL server from AKRR host, or a different
person administer database, ask user with administrative rights execute following:

```
CREATE DATABASE IF NOT EXISTS mod_akrr CHARACTER SET utf8;
CREATE DATABASE IF NOT EXISTS mod_appkernel CHARACTER SET utf8;

CREATE USER akrruser@'AKRR_HOSTNAME' IDENTIFIED BY 'password'

GRANT ALL ON mod_akrr.* TO akrruser@'AKRR_HOSTNAME';
GRANT ALL ON mod_appkernel.* TO akrruser@'AKRR_HOSTNAME';
GRANT SELECT ON modw.* TO akrruser@'AKRR_HOSTNAME';
```


Prior to running `akrr setup` ensure that the created user has access to DB from AKRR host.
For example by trying access mod_akrr with mysql client:

```bash
mysql -u akrruser -p -h <MYSQL_SERVER> mod_akrr
```

You might need also to add akrruser@'localhost' and add AKRR_HOSTNAME by it IP address.


Next: [Usage](AKRR_Usage.md)
