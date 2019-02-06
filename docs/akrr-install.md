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

## RPM Installation

Download in install AKRR RPM
```bash
yum install akrr-{{ page.sw_version }}-1.noarch.rpm
```

## In Source Installation

Download tar.gz archive and uncompress it in desired installation location:
```bash
tar zxvf akrr-{{ page.sw_version }}.tar.gz
``` 

You can add bin directory from AKRR to you PATH environment variable or 
call AKRR commands with full pathname.
