FROM centos:7

LABEL desc="namd benchmark made ready to run"


# VERY similar to hpcc - seems that we only need mpi?
# Installing intel-mpi and making namduser in one Run
RUN \
	yum-config-manager --add-repo https://yum.repos.intel.com/mpi/setup/intel-mpi.repo && \
	rpm --import https://yum.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS-2019.PUB && \
	yum -y install intel-mpi-2018.3-051 && \
	yum -y install sudo && \
	useradd -d /home/namduser -ms /bin/bash namduser && \
	usermod -aG wheel namduser && \
	echo "namduser:namduser" | chpasswd && \
echo "Added namduser (pass: namduser) and installed intel-mpi"

# copying executable (assumes its in namd_loc/execs
ENV execsLoc=/opt/appker/execs

COPY ./namd_loc/execs $execsLoc

# location of namd executable
ENV namdLoc=$execsLoc/namd2

# copying over inputs to use for namd2
ENV inputsLoc=/usr/local/appker/inputs
COPY ./inputs/apoa1_nve $inputsLoc

ENV scriptsLoc=/opt/scripts
COPY scripts $scriptsLoc


ENV mpiLoc=/opt/intel/impi/2018.3.222/bin64

RUN \
	echo "export PATH=$PATH:$mpiLoc" >> /home/namduser/.bashrc && \
	chown -R namduser $inputsLoc && \
	chown -R namduser $execsLoc && \
	chown -R namduser $scriptsLoc

USER namduser

WORKDIR $scriptsLoc

ENTRYPOINT ["./setup_run_namd.sh"]


