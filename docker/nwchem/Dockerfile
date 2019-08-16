FROM centos:7

LABEL desc="Nwchem benchmark made ready to run"

# Installing intel-mpi, intel-mkl and making hpcguser in one Run (needed for hpcg run)
RUN \
        yum-config-manager --add-repo https://yum.repos.intel.com/mpi/setup/intel-mpi.repo && \
        rpm --import https://yum.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS-2019.PUB && \
        yum -y install intel-mpi-2018.3-051 && \
        yum-config-manager --add-repo https://yum.repos.intel.com/mkl/setup/intel-mkl.repo && \
        yum -y install intel-mkl-2018.3-051

ENV EXECS_DIR=/opt/appker/execs
COPY execs $EXECS_DIR

# absolute path to nwchem executable
ENV NWCHEM_EXECUTABLE=$EXECS_DIR/nwchem-6.8/bin/LINUX64/nwchem

# inputs for nwchem
ENV INPUTS_DIR=/opt/appker/inputs
ENV NWCHEM_INPUTS_DIR=$INPUTS_DIR/nwchem
COPY inputs $INPUTS_DIR

ENV SCRIPTS_DIR=/opt/scripts
COPY scripts $SCRIPTS_DIR/

ENV MPI_DIR=/opt/intel/impi/2018.3.222/bin64


RUN \
        mkdir /scratch && \
        chmod -R 777 /scratch && \
        chmod -R 755 $EXECS_DIR && \
        chmod -R 755 $SCRIPTS_DIR && \
        chmod -R 755 $INPUTS_DIR 

ENV LD_LIBRARY_PATH=/opt/intel/impi/2018.3.222/lib64:/opt/intel/mkl/lib/intel64

WORKDIR /scratch

ENTRYPOINT ["/opt/scripts/setup_run_nwchem.sh"]

