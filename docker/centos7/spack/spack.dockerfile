# docker build -f spack.dockerfile -t spack-ubuntu:20.04 .
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
    LC_ALL=en_US.UTF-8                \
    ALL_TARGETS='x86_64 sandybridge haswell skylake_avx512'

RUN apt-get -yqq update \
 && apt-get -yqq install --no-install-recommends \
        build-essential \
        ca-certificates \
        curl \
        file \
        g++ \
        gcc \
        gfortran \
        git \
        gnupg2 \
        iproute2 \
        lmod \
        locales \
        lua-posix \
        make \
        python3 \
        python3-pip \
        python3-setuptools \
        tcl \
        unzip \
        sudo \
        wget \
        cpio \
        vim \
        ssh \
        autoconf automake cmake \
 && locale-gen en_US.UTF-8 \
 && pip3 install boto3 \
 && rm -rf /var/lib/apt/lists/* \
 && rm -rf /root/*.* /run/nologin

# add ubuntu user
RUN useradd -m -s /bin/bash ubuntu && \
    echo 'ubuntu:ubuntu' |chpasswd && \
    usermod -a -G sudo ubuntu && \
    echo "ubuntu ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers && \
    chown -R ubuntu:ubuntu /opt

USER ubuntu
WORKDIR /home/ubuntu

COPY --chown=ubuntu:ubuntu docker/spack/license.lic /home/ubuntu/intel-license.lic
COPY --chown=ubuntu:ubuntu docker/spack/icc-silent.cfg /home/ubuntu/icc-silent.cfg

RUN wget -O  icc.tgz http://registrationcenter-download.intel.com/akdlm/irc_nas/tec/16744/parallel_studio_xe_2020_update2_cluster_edition_online.tgz && \
    tar -xvzf icc.tgz && \
    cd parallel_studio_xe_* && \
    bash ./install.sh --silent=/home/ubuntu/icc-silent.cfg && \
    cd && \
    rm -rf parallel_studio_xe_* icc.tgz /home/ubuntu/icc-silent.cfg /home/ubuntu/intel-license.lic && \
    mkdir -p /opt/modulefiles/intel_parallel_studio_xe && \
    /usr/share/lmod/lmod/libexec/sh_to_modulefile -o /opt/modulefiles/intel_parallel_studio_xe/2020_update2.lua /opt/intel/compilers_and_libraries_2020.2.254/linux/bin/compilervars.sh intel64 && \
    echo "source /etc/profile.d/lmod.sh" >> /home/ubuntu/.bashrc && \
    echo "export MODULEPATH=/opt/modulefiles:/opt/spack/share/spack/modules:/usr/share/lmod/lmod/modulefiles" >> /home/ubuntu/.bashrc

RUN cd /opt && \
    git clone --depth=1 --branch master --single-branch \
        https://github.com/nsimakov/spack.git && \
    echo "export SPACK_ROOT=$SPACK_ROOT" >> /home/ubuntu/.bashrc && \
    echo ". \$SPACK_ROOT/share/spack/setup-env.sh" >> /home/ubuntu/.bashrc && \
    echo "source /etc/profile.d/lmod.sh\nexport MODULEPATH=/opt/modulefiles:/opt/spack/share/spack/modules:/usr/share/lmod/lmod/modulefiles\n$(cat /opt/spack/share/spack/setup-env.sh)" > /opt/spack/share/spack/setup-env.sh


RUN mkdir -p $SPACK_ROOT/opt/spack && \
    sudo ln -s $SPACK_ROOT/share/spack/docker/entrypoint.bash \
          /usr/local/bin/docker-shell \
 && sudo ln -s $SPACK_ROOT/share/spack/docker/entrypoint.bash \
          /usr/local/bin/interactive-shell \
 && sudo ln -s $SPACK_ROOT/share/spack/docker/entrypoint.bash \
          /usr/local/bin/spack-env

# add compilers and common libraries
SHELL ["docker-shell"]

RUN module load intel_parallel_studio_xe/2020_update2 && \
    cd $MKLROOT/interfaces/fftw2x_cdft && \
    make libintel64 PRECISION=MKL_DOUBLE interface=ilp64 MKLROOT=$MKLROOT && \
    cd $MKLROOT/interfaces/fftw2xc && \
    make libintel64 PRECISION=MKL_DOUBLE MKLROOT=$MKLROOT

RUN spack compiler add && \
    (echo "packages:" && \
    echo "  gmake:" && \
    echo "    externals:" && \
    echo "    - spec: \"gmake@4.2.1 arch=linux-ubuntu20.04-x86_64\"" && \
    echo "      prefix: /usr" && \
    echo "    buildable: False" && \
    echo "  cmake:" && \
    echo "    externals:" && \
    echo "    - spec: \"cmake@3.16.3 arch=linux-ubuntu20.04-x86_64\"" && \
    echo "      prefix: /usr" && \
    echo "    buildable: False" && \
    echo "  autoconf:" && \
    echo "    externals:" && \
    echo "    - spec: \"autoconf@2.69 arch=linux-ubuntu20.04-x86_64\"" && \
    echo "      prefix: /usr" && \
    echo "    buildable: False" && \
    echo "  automake:" && \
    echo "    externals:" && \
    echo "    - spec: \"automake@1.16.1 arch=linux-ubuntu20.04-x86_64\"" && \
    echo "      prefix: /usr" && \
    echo "    buildable: False" && \
    echo "  cpio:" && \
    echo "    externals:" && \
    echo "    - spec: \"cpio@2.13 arch=linux-ubuntu20.04-x86_64\"" && \
    echo "      prefix: /usr" && \
    echo "    buildable: False" && \
    echo "  m4:" && \
    echo "    externals:" && \
    echo "    - spec: \"m4@1.4.18 arch=linux-ubuntu20.04-x86_64\"" && \
    echo "      prefix: /usr" && \
    echo "    buildable: False" && \
    echo "  intel-parallel-studio:" && \
    echo "    externals:" && \
    echo "    - spec: \"intel-parallel-studio@cluster.2020.2 +mkl+mpi+ipp+tbb  arch=linux-ubuntu20.04-x86_64\"" && \
    echo "      prefix: /opt/intel/compilers_and_libraries_2020.2.254" && \
    echo "      modules: [intel_parallel_studio_xe/2020_update2]" && \
    echo "    buildable: False" && \
    echo "  intel-mkl:" && \
    echo "    externals:" && \
    echo "    - spec: \"intel-mkl@2020.2.254  arch=linux-ubuntu20.04-x86_64\"" && \
    echo "      prefix: /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl" && \
    echo "      modules: [intel_parallel_studio_xe/2020_update2]" && \
    echo "    buildable: False" && \
    echo "  intel-mpi:" && \
    echo "    externals:" && \
    echo "    - spec: \"intel-mpi@2019.8.254  arch=linux-ubuntu20.04-x86_64\"" && \
    echo "      prefix: /opt/intel/compilers_and_libraries_2020.2.254/linux/mpi/intel64" && \
    echo "      modules: [intel_parallel_studio_xe/2020_update2]" && \
    echo "    buildable: False") > /home/ubuntu/.spack/packages.yaml && \
    (echo "- compiler:" && \
    echo "    spec: intel@19.1.2.254" && \
    echo "    paths:" && \
    echo "      cc: /opt/intel/compilers_and_libraries_2020.2.254/linux/bin/intel64/icc" && \
    echo "      cxx: /opt/intel/compilers_and_libraries_2020.2.254/linux/bin/intel64/icpc" && \
    echo "      f77: /opt/intel/compilers_and_libraries_2020.2.254/linux/bin/intel64/ifort" && \
    echo "      fc: /opt/intel/compilers_and_libraries_2020.2.254/linux/bin/intel64/ifort" && \
    echo "    flags: {}" && \
    echo "    operating_system: ubuntu20.04" && \
    echo "    target: x86_64" && \
    echo "    modules: [intel_parallel_studio_xe/2020_update2]" && \
    echo "    environment: {}" && \
    echo "    extra_rpaths: []") >> /home/ubuntu/.spack/linux/compilers.yaml && \
    ln -s /opt/intel/parallel_studio_xe_2020.2.108 /opt/intel/compilers_and_libraries_2020.2.254/parallel_studio_xe && \
    mkdir /home/ubuntu/spack_mirror && \
    spack mirror add local_filesystem /home/ubuntu/spack_mirror

RUN for target in ${ALL_TARGETS}; do spack install openmpi target=$target; done
RUN for target in ${ALL_TARGETS}; do spack install openblas target=$target; done
RUN for target in ${ALL_TARGETS}; do spack install fftw@2.1.5 target=$target ^openmpi; done
RUN for target in ${ALL_TARGETS}; do spack install fftw target=$target ^openmpi; done

# pack shared libraries
# RUN cd /opt/intel/compilers_and_libraries_2020.2.254/linux/mkl/lib/intel64 && \
#     tar -czvf libs.tar.gz *.so locale
#    spack install intel-mpi%intel target=x86_64
#RUN mkdir -p /home/ubuntu/.spack \
# && cp $SPACK_ROOT/share/spack/docker/modules.yaml \
#        /home/ubuntu/.spack/modules.yaml

#WORKDIR /root
#SHELL ["docker-shell"]
#
## TODO: add a command to Spack that (re)creates the package cache
#RUN spack spec hdf5+mpi
#
#ENTRYPOINT ["/bin/bash", "/opt/spack/share/spack/docker/entrypoint.bash"]
#CMD ["interactive-shell"]
