# Build stage with Spack pre-installed and ready to be used
FROM spack-ubuntu:20.04 as builder

RUN cd /opt/spack && git pull origin

ENV CONT_AKRR_APPKER_DIR=/opt/appker \
    APPKER=nwchem \
    ALL_TARGETS='x86_64 sandybridge haswell skylake_avx512'
# x86_64 sandybridge haswell
# copying inpus, executables and scripts
COPY --chown=ubuntu:ubuntu akrr/appker_repo/inputs/$APPKER $CONT_AKRR_APPKER_DIR/inputs/$APPKER

RUN sudo apt-get -yqq update \
 && sudo apt-get -yqq install --no-install-recommends python3-dev \
 && sudo rm -rf /var/lib/apt/lists/*

RUN (echo "  python:" && \
    echo "    externals:" && \
    echo "    - spec: \"python@3.8.2  arch=linux-ubuntu20.04-x86_64\"" && \
    echo "      prefix: /usr" && \
    echo "      modules: []" && \
    echo "    buildable: False") >> /home/ubuntu/.spack/packages.yaml

RUN for target in ${ALL_TARGETS}; do \
        spack install netlib-scalapack target=$target %gcc ^openblas ^openmpi \
    ;done

RUN mkdir /opt/spack-environment && cd /opt/spack-environment && \
    configuration=gcc_openblas_openmpi && \
    for target in ${ALL_TARGETS}; do \
        view=${APPKER}_${configuration}_${target} && \
        mkdir $view && cd $view && \
        spack env create -d /opt/spack-environment/$view && \
        spack env activate /opt/spack-environment/$view && \
        spack install -v nwchem target=$target %gcc ^netlib-scalapack ^openblas ^openmpi && \
        spack env deactivate && \
        spack env activate --sh -d /opt/spack-environment/$view >> /opt/spack-environment/$view/env.sh && \
        sed -r -i  's/^(export NWCHEM_NWPW_LIBRARY=.*);$/\1\/;/' /opt/spack-environment/$view/env.sh && \
        sed -r -i  's/^(export NWCHEM_BASIS_LIBRARY=.*);$/\1\/;/' /opt/spack-environment/$view/env.sh \
    ;done && \
    echo ${configuration} >> /opt/spack-environment/${APPKER}.configurations
#
RUN cd /opt/spack-environment && \
    configuration=icc_mkl_impi && \
    for target in ${ALL_TARGETS}; do \
        view=${APPKER}_${configuration}_${target} && \
        mkdir $view && cd $view && \
        spack env create -d /opt/spack-environment/$view && \
        spack env activate /opt/spack-environment/$view && \
        spack install -v nwchem target=$target %intel ^intel-mkl ^intel-mpi && \
        spack env deactivate && \
        spack env activate --sh -d /opt/spack-environment/$view >> /opt/spack-environment/$view/env.sh && \
        echo 'export MPI_DIR=/opt/intel/compilers_and_libraries_2020.2.254/linux/mpi/intel64' >> /opt/spack-environment/$view/env.sh && \
        echo 'source "${MPI_DIR}/bin/mpivars.sh"' >> /opt/spack-environment/$view/env.sh && \
        sed -r -i  's/^(export NWCHEM_NWPW_LIBRARY=.*);$/\1\/;/' /opt/spack-environment/$view/env.sh && \
        sed -r -i  's/^(export NWCHEM_BASIS_LIBRARY=.*);$/\1\/;/' /opt/spack-environment/$view/env.sh \
    ;done && \
    echo ${configuration} >> /opt/spack-environment/${APPKER}.configurations

# copying inpus, executables and scripts
COPY --chown=ubuntu:ubuntu akrr/appker_repo/inputs/$APPKER $CONT_AKRR_APPKER_DIR/inputs/$APPKER
COPY --chown=ubuntu:ubuntu akrr/appker_repo/execs/bin docker/$APPKER/run_$APPKER.sh docker/utils/ $CONT_AKRR_APPKER_DIR/execs/bin/

RUN sudo chmod a+rx /opt/appker/execs/bin/* && sudo chmod -R a+rX /opt/appker

#ENTRYPOINT ["/bin/bash", "--rcfile", "/etc/profile", "-l"]
ENTRYPOINT ["/opt/appker/execs/bin/run_nwchem.sh"]

