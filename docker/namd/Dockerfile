FROM centos:7

LABEL desc="namd benchmark made ready to run"

# copying executable (assumes its in namd_loc/execs
ENV EXECS_LOC=/opt/appker/execs

COPY ./namd_loc/execs $EXECS_LOC
# to get the appsigcheck thing
COPY ./execs $EXECS_LOC/

# location of namd executable
ENV NAMD_EXE_FULL_PATH=$EXECS_LOC/namd2
ENV CHARMRUN_EXE_FULL_PATH=$EXECS_LOC/charmrun

# copying over inputs to use for namd2
ENV INPUTS_LOC=/usr/local/appker/inputs
ENV NAMD_INPUTS_DIR=$INPUTS_LOC/namd
COPY ./inputs/namd $NAMD_INPUTS_DIR

ENV SCRIPTS_LOC=/opt/scripts
COPY scripts $SCRIPTS_LOC

# setting up directories and permissions
RUN \
	mkdir /scratch && \
	chmod -R 777 /scratch && \
	chmod -R 755 $EXECS_LOC && \
	chmod -R 755 $SCRIPTS_LOC && \
	chmod -R 755 $INPUTS_LOC	

WORKDIR /scratch

ENTRYPOINT ["/opt/scripts/setup_run_namd.sh"]


