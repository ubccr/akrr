FROM centos:7

LABEL desc="ior benchmark"

RUN \
	yum-config-manager --add-repo https://yum.repos.intel.com/mpi/setup/intel-mpi.repo && \
	rpm --import https://yum.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS-2019.PUB && \
	yum -y install intel-mpi-2018.3-051

ENV EXECS_LOC=/opt/appker/execs

COPY execs $EXECS_LOC

COPY ior-3.2.0 $EXECS_LOC/ior
ENV IOR_EXE_PATH=$EXECS_LOC/ior/src/ior
ENV MDTEST_EXE_PATH=$EXECS_LOC/ior/src/mdtest


ENV SCRIPTS_LOC=/opt/scripts
COPY scripts $SCRIPTS_LOC

ENV GPFS_LIB_LOC=/opt/appker/lib
COPY lib $GPFS_LIB_LOC

ENV LD_LIBRARY_PATH=/opt/intel/impi/2018.3.222/lib64:$GPFS_LIB_LOC

ENV MPI_LOC=/opt/intel/impi/2018.3.222/bin64

RUN \
	mkdir /scratch && \
	chmod -R 777 /scratch && \
	chmod -R 755 $EXECS_LOC && \
	chmod -R 755 $SCRIPTS_LOC

WORKDIR /scratch

ENTRYPOINT ["/opt/scripts/setup_run_ior.sh"]


