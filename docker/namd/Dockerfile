FROM centos:7

LABEL desc="hpcc benchmark made ready to run"

# Installing intel-mpi and making hpccuser in one Run
RUN \
	yum -y update && \
	yum -y install vim sudo && \
	yum-config-manager --add-repo https://yum.repos.intel.com/mkl/setup/intel-mkl.repo && \
	rpm --import https://yum.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS-2019.PUB && \
	yum -y install intel-mkl-core-rt-2018.3-222 && \
	yum clean all
# intel-mkl-2018.3-051

RUN useradd -m -s /bin/bash akrruser && \
    echo 'akrruser:akrruser' |chpasswd && \
    usermod -a -G wheel akrruser && \
    echo "akrruser ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# place where the executable is
ENV CONT_AKRR_APPKER_DIR=/opt/appker \
    MPI_DIR=/opt/intel/impi/2018.3.222/bin64

# copying inpus, executables and scripts
COPY akrr/appker_repo/inputs/namd $CONT_AKRR_APPKER_DIR/inputs/namd
COPY docker/namd/bin/NAMD_2.13_Linux-x86_64-multicore $CONT_AKRR_APPKER_DIR/execs/NAMD_2.13_Linux-x86_64-multicore
COPY docker/namd/bin/NAMD_2.13_Linux-x86_64-multicore-CUDA $CONT_AKRR_APPKER_DIR/execs/NAMD_2.13_Linux-x86_64-multicore-CUDA
COPY akrr/appker_repo/execs/bin docker/namd/run_namd.sh docker/utils/* $CONT_AKRR_APPKER_DIR/execs/bin/

RUN  chmod -R a+rX $CONT_AKRR_APPKER_DIR
# && \
#     chmod -R a+rx $CONT_AKRR_APPKER_DIR/execs/bin $CONT_AKRR_APPKER_DIR/execs/NAMD_2.13_Linux-x86_64-multicore/namd*

# so that the temp directory gets created there
WORKDIR /home/akrruser
USER akrruser

ENTRYPOINT ["/opt/appker/execs/bin/run_namd.sh"]
