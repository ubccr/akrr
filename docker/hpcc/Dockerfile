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

# place where the executable is
ENV CONT_AKRR_APPKER_DIR=/opt/appker \
    MPI_DIR=/opt/intel/impi/2018.3.222/bin64

# copying inpus, executables and scripts
COPY akrr/appker_repo/inputs/hpcc $CONT_AKRR_APPKER_DIR/inputs/hpcc
COPY docker/hpcc/bin/* $CONT_AKRR_APPKER_DIR/execs/hpcc/
COPY akrr/appker_repo/execs/bin docker/hpcc/run_hpcc.sh docker/utils/* $CONT_AKRR_APPKER_DIR/execs/bin/

RUN  chmod -R a+rX $CONT_AKRR_APPKER_DIR && \
     chmod -R a+rx $CONT_AKRR_APPKER_DIR/execs/bin $CONT_AKRR_APPKER_DIR/execs/hpcc

# so that the temp directory gets created there
WORKDIR /home/akrruser
USER akrruser

ENTRYPOINT ["/opt/appker/execs/bin/run_hpcc.sh"]
