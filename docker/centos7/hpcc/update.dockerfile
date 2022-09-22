# Bare OS image to run the installed executables
FROM nsimakov/appker:hpcc

# copying inpus, executables and scripts
COPY --chown=ubuntu:ubuntu akrr/appker_repo/inputs/hpcc $CONT_AKRR_APPKER_DIR/inputs/hpcc
COPY --chown=ubuntu:ubuntu akrr/appker_repo/execs/bin docker/hpcc/run_hpcc.sh docker/utils/ $CONT_AKRR_APPKER_DIR/execs/bin/

RUN sudo chmod a+rx /opt/appker/execs/bin/* && sudo chmod -R a+rX /opt/appker
