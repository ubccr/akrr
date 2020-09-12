# Build stage with Spack pre-installed and ready to be used
FROM spack-ubuntu:20.04 as builder

RUN cd /opt/spack && git pull origin

ENV CONT_AKRR_APPKER_DIR=/opt/appker \
    APPKER=hpcc \
    ALL_TARGETS='x86_64 sandybridge haswell skylake_avx512'

# copying inpus, executables and scripts
COPY --chown=ubuntu:ubuntu akrr/appker_repo/inputs/hpcc $CONT_AKRR_APPKER_DIR/inputs/hpcc
COPY --chown=ubuntu:ubuntu akrr/appker_repo/execs/bin docker/hpcc/run_hpcc.sh docker/utils/* $CONT_AKRR_APPKER_DIR/execs/bin/

#RUN for target in x86_64 sandybridge haswell skylake_avx512; do \
#    spack install hpcc target=$target ^openmpi^openblas ;\
#    done
#
#RUN for target in x86_64 sandybridge haswell skylake_avx512; do \
#    spack install hpcc target=$target fft=fftw2  ^openmpi^openblas ;\
#    done
#
#RUN for target in x86_64 sandybridge haswell skylake_avx512; do \
#    spack install hpcc target=$target fft=mkl %intel^intel-parallel-studio+mkl+mpi ;\
#    done

RUN mkdir /opt/spack-environment && cd /opt/spack-environment && \
    configuration=gcc_openmpi_openblas && \
    for target in ${ALL_TARGETS}; do \
        view=${APPKER}_${configuration}_${target} && \
        mkdir $view && cd $view && \
        spack env create -d /opt/spack-environment/$view && \
        spack env activate /opt/spack-environment/$view && \
        spack install hpcc target=$target ^openmpi^openblas && \
        spack gc -y && \
        find -L /opt/spack-environment/$view/.spack-env/view/* -type f -exec readlink -f '{}' \; | \
            xargs file -i | \
            grep 'charset=binary' | \
            grep 'x-executable\|x-archive\|x-sharedlib' | \
            awk -F: '{print $1}' | xargs strip -s && \
        spack env deactivate && \
        spack env activate --sh -d /opt/spack-environment/$view >> /opt/spack-environment/$view/env.sh \
    ;done && \
    echo ${configuration} >> /opt/spack-environment/${APPKER}.configurations

RUN cd /opt/spack-environment && \
    configuration=icc_mkl_impi && \
    for target in ${ALL_TARGETS}; do \
        view=${APPKER}_${configuration}_${target} && \
        mkdir $view && cd $view && \
        spack env create -d /opt/spack-environment/$view && \
        spack env activate /opt/spack-environment/$view && \
        spack install hpcc target=$target fft=mkl %intel^intel-mkl^intel-mpi && \
        spack gc -y && \
        find -L /opt/spack-environment/$view/.spack-env/view/* -type f -exec readlink -f '{}' \; | \
            xargs file -i | \
            grep 'charset=binary' | \
            grep 'x-executable\|x-archive\|x-sharedlib' | \
            awk -F: '{print $1}' | xargs strip -s && \
        spack env deactivate && \
        spack env activate --sh -d /opt/spack-environment/$view >> /opt/spack-environment/$view/env.sh && \
        echo 'export MPI_DIR=/opt/intel/compilers_and_libraries_2020.2.254/linux/mpi/intel64' >> /opt/spack-environment/$view/env.sh && \
        echo 'source "${MPI_DIR}/bin/mpivars.sh"' >> /opt/spack-environment/$view/env.sh \
    ;done && \
    echo ${configuration} >> /opt/spack-environment/${APPKER}.configurations
# spack install && spack gc -y



#==> Updating view at /opt/spack-environment/hpcc_openmpi_openblas_x86_64/.spack-env/view
#==> Created environment in /opt/spack-environment/hpcc_openmpi_openblas_x86_64
#==> You can activate this environment with:
#==>   spack env activate /opt/spack-environment/hpcc_openmpi_openblas_x86_64


#RUN  chmod -R a+rX $CONT_AKRR_APPKER_DIR && \
#     chmod -R a+rx $CONT_AKRR_APPKER_DIR/execs/bin $CONT_AKRR_APPKER_DIR/execs/hpcc

#RUN for target in x86_64 sandybridge haswell skylake_avx512; do spack install hpcc target=$target %intel^intel-parallel-studio+mkl+mpi; done

#RUN for target in x86_64 sandybridge haswell skylake_avx512; do spack install hpcc target=$target ^openmpi^openblas; done

#RUN for target in x86_64 sandybridge haswell skylake_avx512; do spack install hpcc fft=fftw2 target=$target ^openmpi^openblas; done


#spack install --test=root hpcc target=nehalem ^openmpi^openblas && \
#    spack install --test=root hpcc target=sandybridge ^openmpi^openblas && \
#    spack install --test=root hpcc target=haswell ^openmpi^openblas && \
#    spack install --test=root hpcc target=skylake_avx512 ^openmpi^openblas
#    #spack install --test=root hpcc target=mic_knl ^openmpi^openblas
# What we want to install and how we want to install it
# is specified in a manifest file (spack.yaml)
#RUN mkdir /opt/spack-environment \
#&&  (echo "spack:" \
#&&   echo "  specs:" \
#&&   echo "  - hpcc%gcc ^openblas ^openmpi" \
#&&   echo "  view: /opt/view" \
#&&   echo "  concretization: together" \
#&&   echo "  config:" \
#&&   echo "    install_tree: /opt/software") > /opt/spack-environment/spack.yaml
#
## Install the software, remove unecessary deps
#RUN cd /opt/spack-environment && spack env activate . && spack install --fail-fast && spack gc -y
#
## Strip all the binaries
#RUN find -L /opt/view/* -type f -exec readlink -f '{}' \; | \
#    xargs file -i | \
#    grep 'charset=binary' | \
#    grep 'x-executable\|x-archive\|x-sharedlib' | \
#    awk -F: '{print $1}' | xargs strip -s
#
## Modifications to the environment that are necessary to run
#RUN cd /opt/spack-environment && \
#    spack env activate --sh -d . >> /etc/profile.d/z10_spack_environment.sh
