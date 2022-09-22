# Build stage with Spack pre-installed and ready to be used
FROM spack-ubuntu:20.04 as builder

RUN cd /opt/spack && git pull origin

ENV CONT_AKRR_APPKER_DIR=/opt/appker \
    APPKER=hpcg \
    ALL_TARGETS='x86_64 sandybridge haswell skylake_avx512'

# copying inpus, executables and scripts
COPY --chown=ubuntu:ubuntu akrr/appker_repo/inputs/$APPKER $CONT_AKRR_APPKER_DIR/inputs/$APPKER
COPY --chown=ubuntu:ubuntu akrr/appker_repo/execs/bin docker/$APPKER/run_$APPKER.sh docker/utils/ $CONT_AKRR_APPKER_DIR/execs/bin/

RUN mkdir /opt/spack-environment && cd /opt/spack-environment && \
    configuration=gcc_openmpi && \
    for target in ${ALL_TARGETS}; do \
        view=${APPKER}_${configuration}_${target} && \
        mkdir $view && cd $view && \
        spack env create -d /opt/spack-environment/$view && \
        spack env activate /opt/spack-environment/$view && \
        spack install hpcg target=$target %gcc ^openmpi && \
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
        spack install hpcg target=$target %intel ^intel-mpi && \
        spack env deactivate && \
        spack env activate --sh -d /opt/spack-environment/$view >> /opt/spack-environment/$view/env.sh && \
        echo 'export MPI_DIR=/opt/intel/compilers_and_libraries_2020.2.254/linux/mpi/intel64' >> /opt/spack-environment/$view/env.sh && \
        echo 'source "${MPI_DIR}/bin/mpivars.sh"' >> /opt/spack-environment/$view/env.sh \
    ;done && \
    echo ${configuration} >> /opt/spack-environment/${APPKER}.configurations

RUN SRCBINDIR=/opt/intel/compilers_and_libraries_2020/linux/mkl/benchmarks/hpcg/bin && \
    configuration=intelver_icc_imkl_impi && \
    VIEWDIR=/opt/spack-environment/hpcg_intelver_icc_imkl_impi_sandybridge && \
    mkdir $VIEWDIR  && cp $SRCBINDIR/xhpcg_avx $VIEWDIR/xhpcg && \
    echo "export PATH=$VIEWDIR:\$PATH" >> $VIEWDIR/env.sh && \
    echo 'export MPI_DIR=/opt/intel/compilers_and_libraries_2020.2.254/linux/mpi/intel64' >> $VIEWDIR/env.sh && \
    echo 'source "${MPI_DIR}/bin/mpivars.sh"' >> /opt/spack-environment/$view/env.sh \ >> $VIEWDIR/env.sh && \
    echo 'export LD_LIBRARY_PATH="/opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64_lin:${LD_LIBRARY_PATH}}"' >> $VIEWDIR/env.sh && \
    echo 'export LD_LIBRARY_PATH="/opt/intel/compilers_and_libraries_2020.2.254/linux/compiler/lib/intel64_lin:${LD_LIBRARY_PATH}}"' >> $VIEWDIR/env.sh && \
    VIEWDIR=/opt/spack-environment/hpcg_intelver_icc_imkl_impi_haswell && \
    mkdir $VIEWDIR  && cp $SRCBINDIR/xhpcg_avx2 $VIEWDIR/xhpcg && \
    echo "export PATH=$VIEWDIR:\$PATH" >> $VIEWDIR/env.sh && \
    echo 'export LD_LIBRARY_PATH="/opt/intel/compilers_and_libraries_2020.2.254/linux/mpi/intel64/libfabric/lib:${LD_LIBRARY_PATH}}"' >> $VIEWDIR/env.sh && \
    echo 'export MPI_DIR=/opt/intel/compilers_and_libraries_2020.2.254/linux/mpi/intel64' >> $VIEWDIR/env.sh && \
    echo 'source "${MPI_DIR}/bin/mpivars.sh"' >> /opt/spack-environment/$view/env.sh \ >> $VIEWDIR/env.sh && \
    echo 'export LD_LIBRARY_PATH="/opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64_lin:${LD_LIBRARY_PATH}}"' >> $VIEWDIR/env.sh && \
    echo 'export LD_LIBRARY_PATH="/opt/intel/compilers_and_libraries_2020.2.254/linux/compiler/lib/intel64_lin:${LD_LIBRARY_PATH}}"' >> $VIEWDIR/env.sh && \
    VIEWDIR=/opt/spack-environment/hpcg_intelver_icc_imkl_impi_skylake_avx512 && \
    mkdir $VIEWDIR  && cp $SRCBINDIR/xhpcg_skx $VIEWDIR/xhpcg && \
    echo "export PATH=$VIEWDIR:\$PATH" >> $VIEWDIR/env.sh && \
    echo 'export LD_LIBRARY_PATH="/opt/intel/compilers_and_libraries_2020.2.254/linux/mpi/intel64/libfabric/lib:${LD_LIBRARY_PATH}}"' >> $VIEWDIR/env.sh && \
    echo 'export MPI_DIR=/opt/intel/compilers_and_libraries_2020.2.254/linux/mpi/intel64' >> $VIEWDIR/env.sh && \
    echo 'source "${MPI_DIR}/bin/mpivars.sh"' >> /opt/spack-environment/$view/env.sh \ >> $VIEWDIR/env.sh && \
    echo 'export LD_LIBRARY_PATH="/opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64_lin:${LD_LIBRARY_PATH}}"' >> $VIEWDIR/env.sh && \
    echo 'export LD_LIBRARY_PATH="/opt/intel/compilers_and_libraries_2020.2.254/linux/compiler/lib/intel64_lin:${LD_LIBRARY_PATH}}"' >> $VIEWDIR/env.sh && \
    echo ${configuration} >> /opt/spack-environment/${APPKER}.configurations


RUN sudo chmod a+rx /opt/appker/execs/bin/* && sudo chmod -R a+rX /opt/appker

ENTRYPOINT ["/opt/appker/execs/bin/run_hpcg.sh"]
