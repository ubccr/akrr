FROM centos:7

LABEL description="slurm with single host WLM for various testing purposes"

# install dependencies
RUN \
    yum -y update && \
    yum -y install --setopt=tsflags=nodocs epel-release && \
    yum -y install --setopt=tsflags=nodocs \
        vim tmux mc perl-Switch\
        openssl openssh-server openssh-clients \
        mariadb-server \
        munge sudo && \
    yum clean all

WORKDIR /root

# copy slurm rpm
COPY ./centos_slurm_single_host_wlm/RPMS/x86_64/slurm*.rpm /root/

#install Slurm
RUN rpm --install \
        slurm-[0-9]*.x86_64.rpm \
        slurm-slurmctld-*.x86_64.rpm \
        slurm-slurmd-*.x86_64.rpm \
        slurm-slurmdbd-*.x86_64.rpm  && \
    rm slurm*.rpm

# copy daemons starters
COPY ./utils/cmd_setup ./utils/cmd_start ./utils/cmd_stop /usr/local/sbin/

# add users
RUN useradd -m -s /bin/bash akrruser && \
    echo 'akrruser:akrruser' |chpasswd && \
    useradd -m -s /bin/bash batchuser && \
    echo 'batchuser:batchuser' |chpasswd && \
    usermod -a -G wheel akrruser && \
    echo "akrruser ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# setup munge
RUN echo "secret munge key secret munge key secret munge key" >/etc/munge/munge.key &&\
    chown -R munge:munge /var/log/munge /run/munge /var/lib/munge /etc/munge &&\
    chmod 600 /etc/munge/munge.key &&\
    cmd_start munged &&\
    munge -n | unmunge &&\
    cmd_stop munged


# configure sshd
RUN mkdir /var/run/sshd && \
    ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key -N '' && \
    ssh-keygen -t ecdsa -f /etc/ssh/ssh_host_ecdsa_key -N '' && \
    ssh-keygen -t ed25519 -f /etc/ssh/ssh_host_ed25519_key -N '' && \
    echo 'root:root' |chpasswd && \
    echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config
# uncomment two previous line if there is a need for root access through ssh

EXPOSE 22

#configure mysqld
RUN chmod g+rw /var/lib/mysql /var/log/mariadb /var/run/mariadb && \
    mysql_install_db && \
    chown -R mysql:mysql /var/lib/mysql && \
    cmd_start mysqld && \
    mysql -e 'DELETE FROM mysql.user WHERE user NOT LIKE "root";' && \
    mysql -e 'DELETE FROM mysql.user WHERE Host NOT IN ("localhost","127.0.0.1","%");' && \
    mysql -e 'GRANT ALL PRIVILEGES ON *.* TO "root"@"%" WITH GRANT OPTION;' && \
    mysql -e 'GRANT ALL PRIVILEGES ON *.* TO "root"@"localhost" WITH GRANT OPTION;' && \
    mysql -e 'DROP DATABASE IF EXISTS test;' && \
    cmd_stop mysqld

EXPOSE 3306

# configure slurm
COPY ./centos_slurm_single_host_wlm/slurm.conf ./centos_slurm_single_host_wlm/slurmdbd.conf /etc/slurm/
RUN mkdir /var/log/slurm && \
    chmod a+r /etc/slurm/slurm.conf  /etc/slurm/slurmdbd.conf && \
    cmd_start munged && \
    cmd_start mysqld && \
    cmd_start slurmdbd && \
    sacctmgr -i add cluster Name=micro Fairshare=1 QOS=normal && \
    sacctmgr -i add account name=account1 Fairshare=1 && \
    sacctmgr -i add user name=batchuser DefaultAccount=account1 MaxSubmitJobs=1000 && \
    cmd_stop slurmdbd && \
    cmd_stop mysqld && \
    cmd_stop munged && \
    rm /var/log/slurm/*

EXPOSE 29002 29003

# setup entry point
ENTRYPOINT ["/usr/local/sbin/cmd_start"]
CMD ["self_contained_slurm_wlm", "bash"]
