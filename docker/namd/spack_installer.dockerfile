# Bare OS image to run the installed executables
FROM ubuntu:20.04

ENV DOCKERFILE_BASE=ubuntu            \
    DOCKERFILE_DISTRO=ubuntu          \
    DOCKERFILE_DISTRO_VERSION=20.04   \
    SPACK_ROOT=/opt/spack             \
    DEBIAN_FRONTEND=noninteractive    \
    CURRENTLY_BUILDING_DOCKER_IMAGE=1 \
    container=docker                  \
    LANGUAGE=en_US.UTF-8              \
    LANG=en_US.UTF-8                  \
    LC_ALL=en_US.UTF-8

ENV CONT_AKRR_APPKER_DIR=/opt/appker \
    APPKER=namd \
    ALL_TARGETS='x86_64 sandybridge haswell skylake_avx512'

RUN apt-get -yqq update && \
    apt-get -yqq install --no-install-recommends \
        binutils \
        lmod \
        python3 python3-pip python3-setuptools \
        sudo vim ssh wget locales cpio \
        libgfortran5 && \
    locale-gen en_US.UTF-8 && \
    rm -rf /var/lib/apt/lists/*


# add ubuntu user
RUN useradd -m -s /bin/bash ubuntu && \
    echo 'ubuntu:ubuntu' |chpasswd && \
    usermod -a -G sudo ubuntu && \
    echo "ubuntu ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers && \
    chown -R ubuntu:ubuntu /opt

USER ubuntu
WORKDIR /home/ubuntu


COPY --from=spack-ubuntu-builder:namd --chown=ubuntu:ubuntu \
    /home/ubuntu/.bashrc /home/ubuntu/.spack /home/ubuntu/

COPY --from=spack-ubuntu-builder:namd --chown=ubuntu:ubuntu \
    /opt/spack-environment /opt/spack-environment
COPY --from=spack-ubuntu-builder:namd --chown=ubuntu:ubuntu \
    /opt/spack /opt/spack
#COPY --from=spack-ubuntu-builder:namd --chown=ubuntu:ubuntu \
#    /opt/intel/compilers_and_libraries_2020.2.254/linux/mpi/intel64 /opt/intel/compilers_and_libraries_2020.2.254/linux/mpi/intel64
COPY --from=spack-ubuntu-builder:namd --chown=ubuntu:ubuntu \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64 /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64
COPY --from=spack-ubuntu-builder:namd --chown=ubuntu:ubuntu \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/compiler/lib/intel64_lin/libifcore.so.5 \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/compiler/lib/intel64_lin/libiomp5.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/compiler/lib/intel64_lin/libifcoremt.so.5 \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/compiler/lib/intel64_lin/libifport.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/compiler/lib/intel64_lin/libiompstubs5.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/compiler/lib/intel64_lin/libicaf.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/compiler/lib/intel64_lin/libqkmalloc.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/compiler/lib/intel64_lin/libifcoremt.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/compiler/lib/intel64_lin/libmpx.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/compiler/lib/intel64_lin/libiomp5_db.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/compiler/lib/intel64_lin/libirc.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/compiler/lib/intel64_lin/libsvml.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/compiler/lib/intel64_lin/libpdbx.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/compiler/lib/intel64_lin/cilk_db.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/compiler/lib/intel64_lin/libpdbx.so.5 \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/compiler/lib/intel64_lin/libcilkrts.so.5 \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/compiler/lib/intel64_lin/libifport.so.5 \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/compiler/lib/intel64_lin/libimf.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/compiler/lib/intel64_lin/libchkp.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/compiler/lib/intel64_lin/libintlc.so.5 \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/compiler/lib/intel64_lin/libirng.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/compiler/lib/intel64_lin/libcilkrts.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/compiler/lib/intel64_lin/libintlc.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/compiler/lib/intel64_lin/libifcore.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/compiler/lib/intel64_lin/libistrconv.so  \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/compiler/lib/intel64_lin/
# copying inpus, executables and scripts
COPY --chown=ubuntu:ubuntu akrr/appker_repo/inputs/$APPKER $CONT_AKRR_APPKER_DIR/inputs/$APPKER
COPY --chown=ubuntu:ubuntu akrr/appker_repo/execs/bin docker/$APPKER/run_$APPKER.sh docker/utils/ $CONT_AKRR_APPKER_DIR/execs/bin/

RUN sudo chmod a+rx /opt/appker/execs/bin/* && sudo chmod -R a+rX /opt/appker

#ENTRYPOINT ["/bin/bash", "--rcfile", "/etc/profile", "-l"]
ENTRYPOINT ["/opt/appker/execs/bin/run_namd.sh"]
