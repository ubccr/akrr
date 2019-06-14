FROM nwchemorg/nwchem-qc:latest

# have to run these so we can do objcopy for the appsigcheck
RUN \
	apt-get -y update && \
	apt-get -y install binutils

ENV EXECS_LOC=/opt/appker/execs
COPY ./execs ${EXECS_LOC}

ENV INPUTS_DIR=/usr/local/appker/inputs
ENV NWCHEM_INPUTS_DIR=${INPUTS_DIR}/nwchem

COPY ./inputs/nwchem ${NWCHEM_INPUTS_DIR}/

# The path to the nwchem executable is stored in $NWCHEM_EXECUTABLE

ENV SCRIPTS_DIR=/opt/appker/scripts
COPY scripts ${SCRIPTS_DIR}

WORKDIR ${SCRIPTS_DIR}

ENTRYPOINT ["./setup_run_nwchem.sh"]
