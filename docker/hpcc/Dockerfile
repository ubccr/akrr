FROM centos:7

LABEL desc="hpcc benchmark made ready to run"

# Installing intel-mpi and making hpccuser in one Run
RUN \
	yum -y update && \
	yum -y install vim sudo && \
	yum-config-manager --add-repo https://yum.repos.intel.com/mpi/setup/intel-mpi.repo && \
	rpm --import https://yum.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS-2019.PUB && \
	yum -y install intel-mpi-2018.3-051

RUN useradd -m -s /bin/bash akrruser && \
    echo 'akrruser:akrruser' |chpasswd && \
    usermod -a -G wheel akrruser && \
    echo "akrruser ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# copy docker helpers
COPY ./docker/utils/* /usr/local/sbin/

# place where the executable is
ENV AKRR_APPKER_DIR=/opt/appker \
    EXECUTABLE=execs/hpcc/hpcc \
    MPI_DIR=/opt/intel/impi/2018.3.222/bin64

# copying inpus, executables and scripts
COPY akrr/appker_repo/inputs/hpcc $AKRR_APPKER_DIR/inputs/hpcc
COPY akrr/appker_repo/execs/bin $AKRR_APPKER_DIR/execs/bin
COPY docker/hpcc/bin/* $AKRR_APPKER_DIR/execs/hpcc/
COPY docker/hpcc/run_hpcc.sh /usr/local/bin

RUN  chmod -R a+rX $AKRR_APPKER_DIR && \
     chmod -R a+x $AKRR_APPKER_DIR/execs/bin $AKRR_APPKER_DIR/execs/hpcc /usr/local/bin

# so that the temp directory gets created there
WORKDIR /home/akrruser

# runs the setup script to start
# Just using the straightup absolute path;
ENTRYPOINT ["/usr/local/sbin/cmd_start"]
CMD ["sudo -u akrruser bash /usr/local/bin/run_hpcc.sh"]
