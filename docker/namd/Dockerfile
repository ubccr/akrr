FROM centos:7

LABEL desc="namd benchmark made ready to run"

# Installing intel-mpi and making namduser in one Run
RUN \
	yum -y install sudo && \
	useradd -d /home/namduser -ms /bin/bash namduser && \
	usermod -aG wheel namduser && \
	echo "namduser:namduser" | chpasswd && \
echo "Added namduser (pass: namduser) and installed intel-mpi"

# copying executable (assumes its in namd_loc/execs
ENV EXECS_LOC=/opt/appker/execs

COPY ./namd_loc/execs $EXECS_LOC
# to get the appsigcheck thing
COPY ./execs $EXECS_LOC/

# location of namd executable
ENV NAMD_EXE_FULL_PATH=$EXECS_LOC/namd2

# copying over inputs to use for namd2
ENV INPUTS_LOC=/usr/local/appker/inputs
ENV NAMD_INPUTS_DIR=$INPUTS_LOC/namd
COPY ./inputs/namd $NAMD_INPUTS_DIR

ENV SCRIPTS_LOC=/opt/scripts
COPY scripts $SCRIPTS_LOC


ENV MPI_LOC=/opt/intel/impi/2018.3.222/bin64

RUN \
	echo "export PATH=$PATH:$MPI_LOC" >> /home/namduser/.bashrc && \
	chown -R namduser $INPUTS_LOC && \
	chown -R namduser $EXECS_LOC && \
	chown -R namduser $SCRIPTS_LOC

USER namduser

WORKDIR $SCRIPTS_LOC

ENTRYPOINT ["./setup_run_namd.sh"]


