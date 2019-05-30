FROM centos:7

LABEL desc="hpcc benchmark made ready to run"



# Installing intel-mpi and making hpccuser in one Run
RUN \
	yum-config-manager --add-repo https://yum.repos.intel.com/mpi/setup/intel-mpi.repo && \
	rpm --import https://yum.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS-2019.PUB && \
	yum -y install intel-mpi-2018.3-051 && \
	yum -y install sudo && \
	useradd -d /home/hpccuser -ms /bin/bash hpccuser && \
	usermod -aG wheel hpccuser && \
	echo "hpccuser:hpccuser" | chpasswd && \
	echo "Added hpccuser (pass: hpccuser) and installed intel-mpi"

# place where the executable is
ENV execsLoc=/opt/appker/execs

# copying in hpcc files
COPY execs $execsLoc
# so the execs dir is /opt/appker/execs


# location of executable file, since mpirun need to have the path to hpcc
ENV hpccLoc=$execsLoc/hpcc-1.5.0/hpcc

# location where the tar will be unpacked for some default inputs for hpcc
ENV inputsLoc=/usr/local/appker/inputs/
COPY hpcc_inputsV2.tar.gz $inputsLoc

# location where convenience scripts will be (to run things using the flags and such)
ENV scriptsLoc=/opt/scripts
COPY scripts $scriptsLoc

ENV mpiLoc=/opt/intel/impi/2018.3.222/bin64

# giving permissions and setting up path to mpi for hpccuser - so can just do mpirun
RUN \
	echo "export PATH=$PATH:$mpiLoc" >> /home/hpccuser/.bashrc && \
	cd $inputsLoc && \
	tar -xzvf $inputsLoc/hpcc_inputsV2.tar.gz && \
	chown -R hpccuser $inputsLoc/hpcc && \
	chown -R hpccuser $execsLoc && \
	chown -R hpccuser $scriptsLoc  # only doing this temporarily to finagle python script


USER hpccuser

WORKDIR $scriptsLoc

# runs the setup script to start (this calls the python script and such
ENTRYPOINT ["./setup_hpcc_input.sh"]

