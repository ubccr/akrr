FROM centos:7

LABEL desc="hpcc benchmark made ready to run"

# Installing intel-mpi and making hpccuser in one Run
RUN \
	yum -y update && \
	yum-config-manager --add-repo https://yum.repos.intel.com/mpi/setup/intel-mpi.repo && \
	rpm --import https://yum.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS-2019.PUB && \
	yum -y install intel-mpi-2018.3-051

# place where the executable is
ENV EXECS_DIR=/opt/appker/execs

# copying in hpcc files
COPY execs $EXECS_DIR
# so the execs dir is /opt/appker/execs


# location of executable file, since mpirun need to have the path to hpcc
ENV HPCC_EXE_FULL_PATH=$EXECS_DIR/hpcc-1.5.0/hpcc

# location where the tar will be unpacked for some default inputs for hpcc
ENV INPUTS_DIR=/usr/local/appker/inputs
COPY inputs $INPUTS_DIR

# location where convenience scripts will be (to run things using the flags and such)
ENV SCRIPTS_DIR=/opt/scripts
COPY scripts $SCRIPTS_DIR

ENV MPI_DIR=/opt/intel/impi/2018.3.222/bin64

# giving permissions to allow anyone to run things - give all permissions to everything basically
RUN \
	mkdir /scratch && \
	chmod -R 777 /scratch && \
	chmod -R 755 $EXECS_DIR && \  
	chmod -R 755 $SCRIPTS_DIR && \
	chmod -R 755 $MPI_DIR && \
	chmod -R 755 $INPUTS_DIR
	
# so that the temp directory gets created there
WORKDIR /scratch

# runs the setup script to start
# Just using the straightup absolute path;
ENTRYPOINT [ "/opt/scripts/setup_run_hpcc.sh" ]
