FROM centos:7

LABEL desc="nwchem benchmark made ready to run"



# Installing intel-mpi, intel-mkl and making nwchemuser in one Run (needed for nwchem run)
RUN \
	yum-config-manager --add-repo https://yum.repos.intel.com/mpi/setup/intel-mpi.repo && \
	rpm --import https://yum.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS-2019.PUB && \
	yum -y install intel-mpi-2018.3-051 && \
	yum-config-manager --add-repo https://yum.repos.intel.com/mkl/setup/intel-mkl.repo && \
	yum -y install intel-mkl-2018.3-051 && \
	yum -y install sudo && \
	yum -y install gdb && \ 
	yum -y update && \
	useradd -d /home/nwchemuser -ms /bin/bash nwchemuser && \
	usermod -aG wheel nwchemuser && \
	echo "nwchemuser:nwchemuser" | chpasswd && \
echo "Added nwchemuser (pass: nwchemuser) and installed intel-mpi and intel-mkl"

# path to executable (aka nwchem)
ENV execsLoc=/opt/appker/execs
COPY execs $execsLoc
ENV exePath=$execsLoc/nwchem-6.8/bin/LINUX64/nwchem


# location where inputs to use are
ENV inputsLoc=/usr/local/appker/inputs
COPY ./inputs/nwchem $inputsLoc

# location of convenience scripts
ENV scriptsLoc=/opt/scripts
COPY scripts $scriptsLoc

# to be able to do mpi run and such
ENV mpiLoc=/opt/intel/impi/2018.3.222/bin64

# giving permissions and setting up path to mpi for nwchemuser - so can just do mpirun
RUN \
	echo "export PATH=$PATH:$mpiLoc" >> /home/nwchemuser/.bashrc && \
	chown -R nwchemuser:nwchemuser $inputsLoc && \
	chown -R nwchemuser:nwchemuser $execsLoc && \
	chown -R nwchemuser:nwchemuser $scriptsLoc 
	

USER nwchemuser

WORKDIR $scriptsLoc

#runs the setup script to set up the input things and run nwchem

ENTRYPOINT ["./setup_run_nwchem.sh"]

