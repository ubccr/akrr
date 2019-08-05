FROM centos:7

LABEL desc="ior benchmark"

RUN \
	yum -y update && \
	yum-config-manager --add-repo https://yum.repos.intel.com/mpi/setup/intel-mpi.repo && \
	rpm --import https://yum.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS-2019.PUB && \
	yum -y install intel-mpi-2018.3-051

ENV EXECS_DIR=/opt/appker/execs

COPY execs $EXECS_DIR

COPY ior-3.2.0 $EXECS_DIR/ior
ENV IOR_EXE_PATH=$EXECS_DIR/ior/src/ior
ENV MDTEST_EXE_PATH=$EXECS_DIR/ior/src/mdtest


ENV SCRIPTS_DIR=/opt/scripts
COPY scripts $SCRIPTS_DIR

ENV GPFS_LIB_DIR=/opt/appker/libs
COPY libs $GPFS_LIB_DIR

ENV LD_LIBRARY_PATH=$GPFS_LIB_DIR:/opt/intel/impi/2018.3.222/lib64:$GPFS_LIB_DIR/hdf5-1.8.21/lib:$GPFS_LIB_LOC/pnetcdf-1.11.1/lib


ENV MPI_DIR=/opt/intel/impi/2018.3.222/bin64

RUN \
	mkdir /scratch && \
	chmod -R 777 /scratch && \
	chmod -R 755 $EXECS_DIR && \
	chmod -R 755 $SCRIPTS_DIR

WORKDIR /scratch

ENTRYPOINT ["/opt/scripts/setup_run_ior.sh"]


