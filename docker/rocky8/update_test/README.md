# Update to AKRR 3.* and Rocky-Linux 8 from AKRR 2.* and CentOS7

Checking m


## Create Back-Up of MySQL Databases

To be on safe side make a back-up of the AKRR databases:

```bash
mysqldump --extended-insert=FALSE -u <user> -p mod_akrr| gzip -c > mod_akrr_2.1.1.gz
mysqldump --extended-insert=FALSE -u <user> -p mod_appkernel| gzip -c > mod_appkernel_2.1.1.gz
```

## Create Back-Up of AKRR logs

```bash
```

## 

mysql  Ver 15.1 Distrib 5.5.68-MariaDB, for Linux (x86_64) using readline 5.1

```bash
# Launch MySQL server with mod_akrr database
docker run -it --rm --name akrr3 -h akrr3 \
    -v /home/nikolays/xdmod_wsp/access_akrr/mysql_akrr3_test:/var/lib/mysql \
    -v /home/nikolays/xdmod_wsp/access_akrr/akrr/akrr_home:/home/akrruser/akrr \
    -v /home/nikolays/xdmod_wsp/akrr:/home/akrruser/akrr_src \
    -p 3371:3306 -p 2271:22 \
    nsimakov/akrr_ready:latest cmd_start sshd mysqld bash

mysql -u root -p << EOF
drop database if exists mod_appkernel;
drop database if exists mod_akrr;
create database mod_akrr;
create database mod_appkernel;
CREATE USER 'akrruser'@'localhost' IDENTIFIED BY 'akrruser';
GRANT ALL PRIVILEGES ON *.* TO 'akrruser'@'localhost' WITH GRANT OPTION;
CREATE USER 'akrruser'@'%' IDENTIFIED BY 'akrruser';
GRANT ALL PRIVILEGES ON *.* TO 'akrruser'@'%' WITH GRANT OPTION;
CREATE USER 'akrruser'@'_gateway' IDENTIFIED BY 'akrruser';
GRANT ALL PRIVILEGES ON *.* TO 'akrruser'@'_gateway' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EOF

zcat mod_akrr_2.1.1.gz | mysql -h localhost -P 3371 -u akrruser -p mod_akrr
zcat mod_appkernel_2.1.1.gz | mysql -h localhost -P 3371 -u akrruser -p mod_appkernel


```