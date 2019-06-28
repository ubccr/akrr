FROM centos:7

LABEL desc="ior benchmark"

# installing intel-mpi to use and mlocate for convenience
RUN \
        yum-config-manager --add-repo https://yum.repos.intel.com/mpi/setup/intel-mpi.repo && \
        rpm --import https://yum.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS-2019.PUB && \
        yum -y install intel-mpi-2018.3-051


ENV EXECS_LOC=/opt/appker/execs

COPY execs $EXECS_LOC
# assuming this is what the ior main folder is
COPY ./ior-3.2.0 $EXECS_LOC/ior
ENV MDTEST_EXE_PATH=$EXECS_LOC/ior/src/mdtest

# need to have the gpfs library (was giving error otherwise
ENV GPFS_LIB_LOC=/opt/appker/lib
COPY ./lib $GPFS_LIB_LOC

# adding path to libraries so mdtest can see them
ENV LD_LIBRARY_PATH=$GPFS_LIB_LOC:/opt/intel/impi/2018.3.222/lib64

ENV SCRIPTS_LOC=/opt/scripts
COPY scripts $SCRIPTS_LOC/

RUN \
	mkdir /scratch && \
	chmod -R 777 /scratch && \
	chmod -R 755 $EXECS_LOC && \
	chmod -R 755 $SCRIPTS_LOC

WORKDIR /scratch

# going right into it
#ENTRYPOINT ["/opt/appker/execs/ior/src/mdtest"]
ENTRYPOINT ["/opt/scripts/setup_run_mdtest.sh"]
