FROM ubuntu:bionic

LABEL description="ununtu with slurm"

# install dependencies
RUN \
    apt-get update && \
    apt-get install -y vim openssh-server munge slurm-wlm slurmdbd&& \
    DEBIAN_FRONTEND=noninteractive apt-get install -y mysql-server
    
# setup sshd
RUN \
    mkdir /var/run/sshd && \
    echo 'root:root' |chpasswd && \
    echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config && \
    sed -ri 's/UsePAM yes/#UsePAM yes/g' /etc/ssh/sshd_config

EXPOSE 22

# setup munge
RUN \
    echo "secret munge key secret munge key secret munge key" >/etc/munge/munge.key && \
    /etc/init.d/munge start && \
    /etc/init.d/munge stop

EXPOSE 22

# setup mysqld
RUN \
    rm -rf /var/lib/apt/lists/* && \
    sed -i 's/^\(bind-address\s.*\)/# \1/' /etc/mysql/my.cnf && \
    sed -i 's/^\(log_error\s.*\)/# \1/' /etc/mysql/my.cnf && \
    mkdir /var/run/mysqld && \
    chown -R mysql:mysql /var/run/mysqld && \
    /etc/init.d/mysql start && \
    mysql -e 'CREATE USER IF NOT EXISTS "root"@"%";' && \
    mysql -e 'GRANT ALL PRIVILEGES ON *.* TO "root"@"%" WITH GRANT OPTION;' && \
    /etc/init.d/mysql stop


# setup slurm
COPY slurmdbd.conf slurm.conf /etc/slurm-llnl/

RUN \
    mkdir /var/run/slurm-llnl && \
    /etc/init.d/munge start && \
    /etc/init.d/mysql start && \
    /etc/init.d/slurmdbd start && \
    sacctmgr -i add cluster Name=micro Fairshare=1 QOS=normal && \
    /etc/init.d/mysql stop && \
    /etc/init.d/slurmdbd stop && \
    /etc/init.d/munge stop && \
    rm /var/log/slurm-llnl/*

EXPOSE 29002 29003
# setup entry point
COPY entrypoint.sh shutdown.sh /sbin/
ENTRYPOINT ["/sbin/entrypoint.sh"]
CMD ["mysqld","slurmdbd","slurmctld","slurmd","bash"]
