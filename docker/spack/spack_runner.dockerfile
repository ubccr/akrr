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

RUN apt-get -yqq update && \
    apt-get -yqq install --no-install-recommends \
        sudo vim ssh wget locales cpio && \
    locale-gen en_US.UTF-8 && \
    rm -rf /var/lib/apt/lists/* && \
    wget http://registrationcenter-download.intel.com/akdlm/irc_nas/tec/16815/l_mpi-rt_2019.8.254.tgz && \
    tar zxvf l_mpi-rt_2019.8.254.tgz && \
    ./l_mpi-rt_2019.8.254/install.sh -s ./l_mpi-rt_2019.8.254/silent.cfg --accept_eula && \
    rm -rf l_mpi-rt_2019.8.254*

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

# add ubuntu user
RUN useradd -m -s /bin/bash ubuntu && \
    echo 'ubuntu:ubuntu' |chpasswd && \
    usermod -a -G sudo ubuntu && \
    echo "ubuntu ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers && \
    chown -R ubuntu:ubuntu /opt

USER ubuntu
WORKDIR /home/ubuntu

