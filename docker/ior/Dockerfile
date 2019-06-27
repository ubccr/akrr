FROM centos:7

LABEL desc="ior benchmark"

# installing intel-mpi to use
RUN \
        yum-config-manager --add-repo https://yum.repos.intel.com/mpi/setup/intel-mpi.repo && \
        rpm --import https://yum.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS-2019.PUB && \
        yum -y install intel-mpi-2018.3-051


ENV EXECS_LOC=/opt/appker/execs

# assuming this is what the ior main folder is
COPY ./ior-3.2.0 $EXECS_LOC/ior

# getting appsigcheck thing
COPY ./execs $EXECS_LOC/




