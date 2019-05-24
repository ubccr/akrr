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

# copying in hpcc files
COPY execs /home/hpccuser/execs

# giving permissions and setting up path to mpi for hpccuser
RUN \
	echo "export PATH=$PATH:/opt/intel/impi/2018.3.222/bin64" >> /home/hpccuser/.bashrc && \
	chown -R hpccuser /home/hpccuser/

USER hpccuser

WORKDIR /home/hpccuser/execs/hpcc-1.5.0/

# in case we ever want to not do the input file thing
#ENTRYPOINT ["/bin/bash"]

# Starts entry script (so sets the input file for hpcc properly)
ENTRYPOINT ["/home/hpccuser/execs/hpcc-1.5.0/set_input_file.sh"]		
CMD ["nofile"] # default argument in case nothing is given


