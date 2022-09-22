# Bare OS image to run the installed executables
FROM nsimakov/appker:base

ENV CONT_AKRR_APPKER_DIR=/opt/appker \
    APPKER=enzo \
    ALL_TARGETS='x86_64 sandybridge haswell skylake_avx512'

COPY --from=spack-ubuntu-builder:enzo --chown=ubuntu:ubuntu \
    /opt/spack-environment /opt/spack-environment
COPY --from=spack-ubuntu-builder:enzo --chown=ubuntu:ubuntu \
    /opt/spack /opt/spack

COPY --from=spack-ubuntu-builder:enzo --chown=ubuntu:ubuntu \
    /home/ubuntu/.bashrc /home/ubuntu/.spack /home/ubuntu/

# copying inpus, executables and scripts
COPY --chown=ubuntu:ubuntu akrr/appker_repo/inputs/$APPKER $CONT_AKRR_APPKER_DIR/inputs/$APPKER
COPY --chown=ubuntu:ubuntu akrr/appker_repo/execs/bin docker/$APPKER/run_$APPKER.sh docker/utils/ $CONT_AKRR_APPKER_DIR/execs/bin/

RUN sudo chmod a+rx /opt/appker/execs/bin/* && sudo chmod -R a+rX /opt/appker

#ENTRYPOINT ["/bin/bash", "--rcfile", "/etc/profile", "-l"]
ENTRYPOINT ["/opt/appker/execs/bin/run_enzo.sh"]