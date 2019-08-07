FROM centos:7

LABEL desc="namd benchmark made ready to run"

# copying executable (assumes its in namd_loc/execs
ENV EXECS_DIR=/opt/appker/execs

COPY execs $EXECS_DIR

# location of namd executable
ENV NAMD_EXE_FULL_PATH=$EXECS_DIR/namd_2.13b2-multicore/namd2
# ENV CHARMRUN_EXE_FULL_PATH=$EXECS_DIR/charmrun

# copying over inputs to use for namd2
ENV INPUTS_DIR=/usr/local/appker/inputs
ENV NAMD_INPUTS_DIR=$INPUTS_DIR/namd
COPY ./inputs/namd $NAMD_INPUTS_DIR

ENV SCRIPTS_DIR=/opt/scripts
COPY scripts $SCRIPTS_DIR

# setting up directories and permissions
RUN \
	mkdir /scratch && \
	chmod -R 777 /scratch && \
	chmod -R 755 $EXECS_DIR && \
	chmod -R 755 $SCRIPTS_DIR && \
	chmod -R 755 $INPUTS_DIR	

WORKDIR /scratch

ENTRYPOINT ["/opt/scripts/setup_run_namd.sh"]


