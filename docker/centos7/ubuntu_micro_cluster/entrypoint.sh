#!/bin/bash
echo "Reach Entry Point"
echo "$@"

echo $$ > /var/run/enrypoint.pid

trap "/sbin/shutdown.sh; exit" SIGHUP SIGINT SIGTERM

echo "Launching sshd"
/etc/init.d/ssh start

echo "Launching munge"
/etc/init.d/munge start

for var in "$@"
do  
    if [ "$var" == "mysqld" ]; then
        echo "Launching mysqld"
        /etc/init.d/mysql start
    fi
    
    if [ "$var" == "slurmdbd" ]; then
        echo "Launching slurmdbd"
        /etc/init.d/slurmdbd start
    fi
    
    if [ "$var" == "slurmctld" ]; then
        echo "Launching slurmctld"
        /etc/init.d/slurmctld start
    fi
    
    if [ "$var" == "slurmd" ]; then
        echo "Launching slurmd"
        /etc/init.d/slurmd start
    fi
    
    if [ "$var" == "bash" ]; then
        echo "Launching bash..."
        /bin/bash
    fi
done

while true; do 
    sleep 60
done
