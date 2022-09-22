#!/bin/bash
cd
echo "Running Update Test 1.0 -> 2.0"

echo "USER: $USER"
echo "CWD: " `pwd`

# rename old akrr
mv ~/akrr ~/akrr_old

# run update from 1.0
~/xdmod_wsp/akrr/bin/akrr -vv update --old-akrr-home=~/akrr_old

# now check that update work adequatly on new version too (somewhat mimic update from pre 2.0)
# mv ~/akrr ~/akrr_old2
# ~/xdmod_wsp/akrr/bin/akrr -vv update --old-akrr-home=~/akrr_old2

sudo yum install -y expect

sudo xdmod-shredder -r UBHPC -f slurm -i /root/xdmod-docker/slurm.log

sudo xdmod-ingestor

sudo yum install -y /root/xdmod-docker/xdmod-8.1.2-1.0.el7.noarch.rpm
sudo expect /home/akrruser/akrr_src/docker/update_test/xdmod-upgrade-8.1.tcl | col -b
sudo yum install -y /root/xdmod-docker/xdmod-8.5.1-1.0.el7.noarch.rpm /root/xdmod-docker/xdmod-appkernels-8.5.0-1.0.el7.noarch.rpm
sudo expect /home/akrruser/akrr_src/docker/update_test/xdmod-upgrade-8.5.tcl | col -b

# sudo xdmod-akrr-ingestor -v -s "2019-01-01 15:10:10" -c -y -m
