# Build stage with Spack pre-installed and ready to be used
FROM spack-ubuntu:20.04 as builder

RUN cd /opt/spack && git pull origin

ENV CONT_AKRR_APPKER_DIR=/opt/appker \
    APPKER=ior \
    ALL_TARGETS='x86_64 sandybridge haswell skylake_avx512'

RUN sudo apt-get -yqq update \
 && sudo apt-get -yqq install --no-install-recommends time \
 && sudo rm -rf /var/lib/apt/lists/*

RUN mkdir /opt/spack-environment && cd /opt/spack-environment && \
    configuration=gcc_openmpi && \
    for target in ${ALL_TARGETS}; do \
        view=${APPKER}_${configuration}_${target} && \
        mkdir $view && cd $view && \
        spack env create -d /opt/spack-environment/$view && \
        spack env activate /opt/spack-environment/$view && \
        spack install ior@3.3.0rc1 +hdf5 +ncmpi target=$target ^openmpi && \
        spack env deactivate && \
        spack env activate --sh -d /opt/spack-environment/$view >> /opt/spack-environment/$view/env.sh \
    ;done && \
    echo ${configuration} >> /opt/spack-environment/${APPKER}.configurations

RUN cd /opt/spack-environment && \
    configuration=icc_impi && \
    for target in ${ALL_TARGETS}; do \
        view=${APPKER}_${configuration}_${target} && \
        mkdir $view && cd $view && \
        spack env create -d /opt/spack-environment/$view && \
        spack env activate /opt/spack-environment/$view && \
        spack install ior@3.3.0rc1 +hdf5 +ncmpi target=$target %intel^intel-mpi && \
        spack env deactivate && \
        spack env activate --sh -d /opt/spack-environment/$view >> /opt/spack-environment/$view/env.sh && \
        echo 'export MPI_DIR=/opt/intel/compilers_and_libraries_2020.2.254/linux/mpi/intel64' >> /opt/spack-environment/$view/env.sh && \
        echo 'source "${MPI_DIR}/bin/mpivars.sh"' >> /opt/spack-environment/$view/env.sh \
    ;done && \
    echo ${configuration} >> /opt/spack-environment/${APPKER}.configurations

# copying inpus, executables and scripts
COPY --chown=ubuntu:ubuntu akrr/appker_repo/execs/bin docker/ior_mdtest/run_ior_mdtest.sh docker/utils/* $CONT_AKRR_APPKER_DIR/execs/bin/

ENTRYPOINT ["/opt/appker/execs/bin/run_ior_mdtest.sh"]
