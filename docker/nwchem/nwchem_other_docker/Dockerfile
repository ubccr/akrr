FROM nwchemorg/nwchem-qc:latest

# have to run these so we can do objcopy for the appsigcheck
RUN \
	apt-get -y update && \
	apt-get -y install binutils

ENV EXECS_DIR=/opt/appker/execs
COPY ./execs $EXECS_DIR

ENV INPUTS_DIR=/usr/local/appker/inputs
COPY inputs $INPUTS_DIR
ENV NWCHEM_INPUTS_DIR=$INPUTS_DIR/nwchem


# The path to the nwchem executable is stored in $NWCHEM_EXECUTABLE

ENV SCRIPTS_DIR=/opt/scripts
COPY scripts $SCRIPTS_DIR


RUN \ 
	mkdir /scratch && \
	chmod -R 777 /scratch && \
	chmod -R 755 $EXECS_DIR && \
	chmod -R 755 $SCRIPTS_DIR && \
	chmod -R 755 $INPUTS_DIR

WORKDIR /scratch

ENTRYPOINT ["/opt/scripts/setup_run_nwchem.sh"]
