# Should be executed from AKRR root
FROM nwchemorg/nwchem-qc:latest

# have to run these so we can do objcopy for the appsigcheck
RUN \
	apt-get -y update && \
	apt-get -y install binutils vim sudo mc

RUN useradd -m -s /bin/bash akrruser && \
    echo 'akrruser:akrruser' |chpasswd && \
    usermod -a -G sudo akrruser && \
    echo "akrruser ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# place where the executable is
ENV CONT_AKRR_APPKER_DIR=/opt/appker \
    MPI_DIR=/usr/bin

# copying inpus, executables and scripts
COPY akrr/appker_repo/inputs/nwchem $CONT_AKRR_APPKER_DIR/inputs/nwchem
COPY akrr/appker_repo/execs/bin docker/nwchem/run_nwchem.sh docker/utils/* $CONT_AKRR_APPKER_DIR/execs/bin/

RUN  chmod -R a+rX $CONT_AKRR_APPKER_DIR && \
     chmod -R a+rx $CONT_AKRR_APPKER_DIR/execs/bin

# so that the temp directory gets created there
WORKDIR /home/akrruser
USER akrruser

ENTRYPOINT ["/opt/appker/execs/bin/run_nwchem.sh"]
