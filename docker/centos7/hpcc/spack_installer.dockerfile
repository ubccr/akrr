# Bare OS image to run the installed executables
FROM nsimakov/appker:base

ENV APPKER=hpcc

COPY --from=spack-ubuntu-builder:hpcc --chown=ubuntu:ubuntu \
    /opt/spack-environment /opt/spack-environment
COPY --from=spack-ubuntu-builder:hpcc --chown=ubuntu:ubuntu \
    /opt/spack /opt/spack


COPY --from=spack-ubuntu-builder:hpcc --chown=ubuntu:ubuntu \
    /home/ubuntu/.bashrc /home/ubuntu/.spack /home/ubuntu/

# copying inpus, executables and scripts
COPY --chown=ubuntu:ubuntu akrr/appker_repo/inputs/hpcc $CONT_AKRR_APPKER_DIR/inputs/hpcc
COPY --chown=ubuntu:ubuntu akrr/appker_repo/execs/bin docker/hpcc/run_hpcc.sh docker/utils/ $CONT_AKRR_APPKER_DIR/execs/bin/

RUN sudo chmod a+rx /opt/appker/execs/bin/* && sudo chmod -R a+rX /opt/appker

ENTRYPOINT ["/opt/appker/execs/bin/run_hpcc.sh"]
