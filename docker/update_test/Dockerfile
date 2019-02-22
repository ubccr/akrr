# Run regtest1 in docker
FROM nsimakov/akrr_ready_centos_slurm_single_host_wlm:1

LABEL description="image to test AKRR update from 1.0 to 2.0"

RUN yum install -y wget

#install xdmod
RUN wget https://github.com/ubccr/xdmod/releases/download/v8.0.0/xdmod-8.0.0-1.0.el7.noarch.rpm && \
    yum install -y  httpd php php-cli php-mysql php-gd php-mcrypt \
              gmp-devel php-gmp php-pdo php-xml \
              php-pear-MDB2 php-pear-MDB2-Driver-mysql \
              java-1.7.0-openjdk java-1.7.0-openjdk-devel \
              mariadb-server mariadb cronie logrotate \
              ghostscript php-mbstring jq && \
    yum install -y xdmod-8.0.0-1.0.el7.noarch.rpm && \
    rm xdmod-8.0.0-1.0.el7.noarch.rpm

RUN sed -i 's@;date.timezone =@date.timezone = America/New_York@g' /etc/php.ini && \
    sed -i 's@mysql.sock@mysql.sock\nmax_allowed_packet   = 16M\ngroup_concat_max_len = 16M@g' /etc/my.cnf

RUN wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2 && \
    tar xvjf phantomjs-2.1.1-linux-x86_64.tar.bz2

ADD xdmod_setup.in /root

RUN cmd_start mysqld && \
    grep -v "#" xdmod_setup.in > in && xdmod-setup < in > out && \
    cmd_stop mysqld

# install akrr
RUN yum install -y python openssl curl MySQL-python

ADD akrr_v1.0_setup.in /root

#RUN cmd_start mysqld && \
#    wget https://github.com/ubccr/akrr/releases/download/v1.0.0/akrr-1.0.0.tar.gz && \
#    tar -xzf akrr-1.0.0.tar.gz && \
#    grep -v "#" akrr_v1.0_setup.in > in && /root/akrr/setup/setup.sh < in > out && \
#    cmd_stop mysqld

COPY cmd_start /sbin/

EXPOSE 8080

ENTRYPOINT ["/sbin/cmd_start"]
CMD ["-set-no-exit-on-fail", "self_contained_slurm_wlm", "httpd", "akrr_v1", "bash"]
