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

COPY --from=spack-ubuntu:20.04 --chown=ubuntu:ubuntu \
    /home/ubuntu/.bashrc /home/ubuntu/.spack /home/ubuntu/

# COPY --from=spack-ubuntu:20.04 --chown=ubuntu:ubuntu \
#     /opt/spack-environment /opt/spack-environment
COPY --from=spack-ubuntu:20.04 --chown=ubuntu:ubuntu \
    /opt/spack /opt/spack

COPY --from=spack-ubuntu-builder:nwchem --chown=ubuntu:ubuntu \
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

COPY --from=spack-ubuntu:20.04 --chown=ubuntu:ubuntu \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/mpi/intel64 /opt/intel/compilers_and_libraries_2020.2.254/linux/mpi/intel64

# COPY --from=spack-ubuntu:20.04 --chown=ubuntu:ubuntu \
#     /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64 /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64

COPY --from=spack-ubuntu:20.04 \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64/libmkl_avx2.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64/libmkl_avx512_mic.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64/libmkl_avx512.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64/libmkl_avx.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64/libmkl_blacs_intelmpi_ilp64.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64/libmkl_blacs_intelmpi_lp64.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64/libmkl_blacs_openmpi_ilp64.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64/libmkl_blacs_openmpi_lp64.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64/libmkl_blacs_sgimpt_ilp64.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64/libmkl_blacs_sgimpt_lp64.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64/libmkl_cdft_core.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64/libmkl_core.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64/libmkl_def.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64/libmkl_gf_ilp64.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64/libmkl_gf_lp64.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64/libmkl_gnu_thread.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64/libmkl_intel_ilp64.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64/libmkl_intel_lp64.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64/libmkl_intel_thread.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64/libmkl_mc3.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64/libmkl_mc.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64/libmkl_pgi_thread.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64/libmkl_rt.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64/libmkl_scalapack_ilp64.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64/libmkl_scalapack_lp64.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64/libmkl_sequential.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64/libmkl_tbb_thread.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64/libmkl_vml_avx2.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64/libmkl_vml_avx512_mic.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64/libmkl_vml_avx512.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64/libmkl_vml_avx.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64/libmkl_vml_cmpt.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64/libmkl_vml_def.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64/libmkl_vml_mc2.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64/libmkl_vml_mc3.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64/libmkl_vml_mc.so \
    /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64/

# copying inpus, executables and scripts
COPY --chown=ubuntu:ubuntu akrr/appker_repo $CONT_AKRR_APPKER_DIR
COPY --chown=ubuntu:ubuntu docker/utils/ $CONT_AKRR_APPKER_DIR/execs/bin/
