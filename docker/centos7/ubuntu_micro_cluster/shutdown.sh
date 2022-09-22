#!/bin/bash

/etc/init.d/slurmctld stop
/etc/init.d/slurmdbd stop
/etc/init.d/slurmd stop
/etc/init.d/mysql stop
/etc/init.d/munge stop
/etc/init.d/ssh stop

if [ -f /var/run/enrypoint.pid ]; then
    kill -9 `cat /var/run/enrypoint.pid`
fi
