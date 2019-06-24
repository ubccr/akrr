FROM centos:7

LABEL desc="gamess benchmark made ready to run"

# Installing intel-mpi and making gamessuser in one Run
RUN \
	yum-config-manager --add-repo https://yum.repos.intel.com/mpi/setup/intel-mpi.repo && \
	rpm --import https://yum.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS-2019.PUB && \
	yum -y install intel-mpi-2018.3-051 && \
	yum -y install tcsh && \
	yum -y install sudo && \
	useradd -d /home/gamessuser -ms /bin/bash gamessuser && \
	usermod -aG wheel gamessuser && \
	echo "gamessuser:gamessuser" | chpasswd && \
	echo "Added gamessuser (pass: gamessuser) and installed intel-mpi"

# place where the executable is
ENV EXECS_LOC=/opt/appker/execs

# copying in gamess files
COPY execs $EXECS_LOC
# so the execs dir is /opt/appker/execs

ENV GAMESS_NAME=gamess_11Nov2017R3
# location of games path, needed in rungms
ENV GAMESS_EXE_DIR=$EXECS_LOC/$GAMESS_NAME

# location where the input for gamess will be
ENV INPUTS_LOC=/usr/local/appker/inputs
COPY ./inputs/gamess $INPUTS_LOC/gamess
ENV GAMESS_INPUTS_LOC=$INPUTS_LOC/gamess

ENV SCRIPTS_LOC=/opt/scripts
COPY scripts $SCRIPTS_LOC

ENV MPI_LOC=/opt/intel/impi/2018.3.222/bin64

# giving permissions and setting up path to mpi for gamessuser - so can just do mpirun
RUN \
	echo "export PATH=$PATH:$MPI_LOC" >> /home/gamessuser/.bashrc && \
	cd $INPUTS_LOC && \
	chown -R gamessuser $INPUTS_LOC && \
	chown -R gamessuser $EXECS_LOC && \
	chown -R gamessuser $SCRIPTS_LOC 


USER gamessuser

WORKDIR $SCRIPTS_LOC

# runs the setup script to start (this calls the python script and such
ENTRYPOINT ["./setup_run_gamess.sh"]



