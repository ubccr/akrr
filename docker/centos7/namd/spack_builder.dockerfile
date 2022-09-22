# Build stage with Spack pre-installed and ready to be used
FROM spack-ubuntu:20.04 as builder

RUN cd /opt/spack && git pull origin

ENV CONT_AKRR_APPKER_DIR=/opt/appker \
    APPKER=namd \
    ALL_TARGETS='x86_64 sandybridge haswell skylake_avx512'

# copying inpus, executables and scripts
COPY --chown=ubuntu:ubuntu akrr/appker_repo/inputs/$APPKER $CONT_AKRR_APPKER_DIR/inputs/$APPKER
COPY --chown=ubuntu:ubuntu akrr/appker_repo/execs/bin docker/$APPKER/run_$APPKER.sh docker/utils/ $CONT_AKRR_APPKER_DIR/execs/bin/
COPY --chown=ubuntu:ubuntu docker/namd/NAMD_2.14_Source.tar.gz /home/ubuntu/spack_mirror/namd/namd-2.14.tar.gz
COPY --chown=ubuntu:ubuntu docker/namd/NAMD_2.14_Linux-x86_64-multicore.tar.gz /home/ubuntu/spack_mirror/namd/NAMD_2.14_Linux-x86_64-multicore.tar.gz

RUN mkdir /opt/spack-environment && \
    tar zxvf /home/ubuntu/spack_mirror/namd/NAMD_2.14_Linux-x86_64-multicore.tar.gz -C /opt/spack-environment && \
    mv /opt/spack-environment/NAMD_2.14_Linux-x86_64-multicore /opt/spack-environment/namd_prebuild_multicore && \
    echo 'export PATH=/opt/spack-environment/namd_prebuild_multicore:$PATH' >> /opt/spack-environment/namd_prebuild_multicore/env.sh

RUN cd /opt/spack-environment && \
    configuration=gcc_fftw_multicore && \
    for target in ${ALL_TARGETS}; do \
        view=${APPKER}_${configuration}_${target} && \
        mkdir $view && cd $view && \
        spack env create -d /opt/spack-environment/$view && \
        spack env activate /opt/spack-environment/$view && \
        spack install namd target=$target interface=tcl fftw=3 ^tcl%gcc target=x86_64 ^openmpi ^charmpp backend=multicore ~smp && \
        spack env deactivate && \
        spack env activate --sh -d /opt/spack-environment/$view >> /opt/spack-environment/$view/env.sh \
    ;done && \
    echo ${configuration} >> /opt/spack-environment/${APPKER}.configurations

RUN cd /opt/spack-environment && \
    configuration=icc_mkl_multicore && \
    for target in ${ALL_TARGETS}; do \
        view=${APPKER}_${configuration}_${target} && \
        mkdir $view && cd $view && \
        spack env create -d /opt/spack-environment/$view && \
        spack env activate /opt/spack-environment/$view && \
        spack install namd target=$target interface=tcl fftw=mkl %intel ^tcl%gcc target=x86_64 ^intel-mkl ^charmpp backend=multicore ~smp  && \
        spack env deactivate && \
        spack env activate --sh -d /opt/spack-environment/$view >> /opt/spack-environment/$view/env.sh \
    ;done && \
    echo ${configuration} >> /opt/spack-environment/${APPKER}.configurations

RUN cd /opt/spack-environment && \
    configuration=gcc_fftw_netlrts && \
    for target in ${ALL_TARGETS}; do \
        view=${APPKER}_${configuration}_${target} && \
        mkdir $view && cd $view && \
        spack env create -d /opt/spack-environment/$view && \
        spack env activate /opt/spack-environment/$view && \
        spack install namd target=$target interface=tcl fftw=3 ^tcl%gcc target=x86_64 ^openmpi ^charmpp backend=netlrts && \
        spack env deactivate && \
        spack env activate --sh -d /opt/spack-environment/$view >> /opt/spack-environment/$view/env.sh \
    ;done && \
    echo ${configuration} >> /opt/spack-environment/${APPKER}.configurations

RUN cd /opt/spack-environment && \
    configuration=icc_mkl_netlrts && \
    for target in ${ALL_TARGETS}; do \
        view=${APPKER}_${configuration}_${target} && \
        mkdir $view && cd $view && \
        spack env create -d /opt/spack-environment/$view && \
        spack env activate /opt/spack-environment/$view && \
        spack install namd target=$target interface=tcl fftw=mkl %intel ^tcl%gcc target=x86_64 ^intel-mkl ^charmpp backend=netlrts  && \
        spack env deactivate && \
        spack env activate --sh -d /opt/spack-environment/$view >> /opt/spack-environment/$view/env.sh \
    ;done && \
    echo ${configuration} >> /opt/spack-environment/${APPKER}.configurations

RUN cd /opt/spack-environment && \
    configuration=v215_icc_mkl_multicore && \
    for target in ${ALL_TARGETS}; do \
        view=${APPKER}_${configuration}_${target} && \
        mkdir $view && cd $view && \
        spack env create -d /opt/spack-environment/$view && \
        spack env activate /opt/spack-environment/$view && \
        spack install namd@2.15a1 target=$target interface=tcl fftw=mkl %intel ^tcl%gcc target=x86_64 ^intel-mkl ^charmpp backend=multicore ~smp  && \
        spack env deactivate && \
        spack env activate --sh -d /opt/spack-environment/$view >> /opt/spack-environment/$view/env.sh \
    ;done && \
    echo ${configuration} >> /opt/spack-environment/${APPKER}.configurations

RUN cd /opt/spack-environment && \
    configuration=v215_icc_mkl_netlrts && \
    for target in ${ALL_TARGETS}; do \
        view=${APPKER}_${configuration}_${target} && \
        mkdir $view && cd $view && \
        spack env create -d /opt/spack-environment/$view && \
        spack env activate /opt/spack-environment/$view && \
        spack install namd@2.15a1 target=$target interface=tcl fftw=mkl %intel ^tcl%gcc target=x86_64 ^intel-mkl ^charmpp backend=netlrts  && \
        spack env deactivate && \
        spack env activate --sh -d /opt/spack-environment/$view >> /opt/spack-environment/$view/env.sh \
    ;done && \
    echo ${configuration} >> /opt/spack-environment/${APPKER}.configurations

COPY --chown=ubuntu:ubuntu akrr/appker_repo/inputs/$APPKER $CONT_AKRR_APPKER_DIR/inputs/$APPKER
COPY --chown=ubuntu:ubuntu akrr/appker_repo/execs/bin docker/$APPKER/run_$APPKER.sh docker/utils/ $CONT_AKRR_APPKER_DIR/execs/bin/

RUN sudo chmod a+rx /opt/appker/execs/bin/* && sudo chmod -R a+rX /opt/appker

#ENTRYPOINT ["/bin/bash", "--rcfile", "/etc/profile", "-l"]
ENTRYPOINT ["/opt/appker/execs/bin/run_namd.sh"]
