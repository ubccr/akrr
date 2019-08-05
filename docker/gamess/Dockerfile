FROM centos:7

LABEL desc="gamess benchmark made ready to run"

# installing mpi and tcsh bc rungms uses tcsh
RUN \
	yum-config-manager --add-repo https://yum.repos.intel.com/mpi/setup/intel-mpi.repo && \
	rpm --import https://yum.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS-2019.PUB && \
	yum -y install intel-mpi-2018.3-051 && \
	yum -y install tcsh 

# place where the executable is
ENV EXECS_DIR=/opt/appker/execs

# copying in gamess files
COPY execs $EXECS_DIR
# so the execs dir is /opt/appker/execs

ENV GAMESS_NAME=gamess_11Nov2017R3
# location of games path, needed in rungms
ENV GAMESS_EXE_DIR=$EXECS_DIR/$GAMESS_NAME

# location where the input for gamess will be
ENV INPUTS_DIR=/usr/local/appker/inputs
COPY ./inputs/gamess $INPUTS_DIR/gamess
ENV GAMESS_INPUTS_DIR=$INPUTS_DIR/gamess

ENV SCRIPTS_DIR=/opt/scripts
COPY scripts $SCRIPTS_DIR

ENV MPI_DIR=/opt/intel/impi/2018.3.222/bin64

# giving permissions and setting up path to mpi for gamessuser - so can just do mpirun
RUN \
	mkdir /scratch && \
	chmod -R 777 /scratch && \
	chmod -R 755 $EXECS_DIR && \
	chmod -R 755 $SCRIPTS_DIR && \
	chmod -R 755 $INPUTS_DIR


WORKDIR /scratch

# runs the setup script to start 
ENTRYPOINT ["/opt/scripts/setup_run_gamess.sh"]



