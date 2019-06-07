FROM centos:7

LABEL desc="HPCG benchmark made ready to run"

# Installing intel-mpi, intel-mkl and making hpcguser in one Run (needed for hpcg run)
RUN \
	yum-config-manager --add-repo https://yum.repos.intel.com/mpi/setup/intel-mpi.repo && \
	rpm --import https://yum.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS-2019.PUB && \
	yum -y install intel-mpi-2018.3-051 && \
	yum-config-manager --add-repo https://yum.repos.intel.com/mkl/setup/intel-mkl.repo && \
	yum -y install intel-mkl-2018.3-051 && \
	yum -y install sudo && \
	useradd -d /home/hpcguser -ms /bin/bash hpcguser && \
	usermod -aG wheel hpcguser && \
	echo "hpcguser:hpcguser" | chpasswd && \
	echo "Added hpcguser (pass: hpcguser) and installed intel-mpi and intel-mkl"

# name of executable that this Docker will have - NOT USED IN FAVOR OF DETERMINING THAT DURING STARTUP
#ENV EXE_NAME=xhpcg_avx2

# where the mkl stuff is, which also has the hpcg things
ENV MKL_DIR=/opt/intel/compilers_and_libraries_2018.3.222/linux/mkl

# location of binary executable to run
ENV HPCG_BIN_LOC=$MKL_DIR/benchmarks/hpcg/bin

# path to executable file for mpirun - NOT USED IN FAVOR OF DETERMINING THAT DURING STARTUP
#ENV HPCG_EXE_LOC=$HPCG_BIN_LOC/$EXE_NAME

# location where any inputs to hpcg will be (in this case mainly only one)
ENV INPUTS_LOC=/usr/local/appker/inputs
COPY inputs $INPUTS_LOC

# location of convenience scripts
ENV scriptsLoc=/opt/scripts
COPY scripts $scriptsLoc

# to be able to just say mpirun in interactive (also for script)
ENV mpiLoc=/opt/intel/impi/2018.3.222/bin64

# giving permissions and setting up path to mpi for hpccuser - so can just do mpirun
RUN \
	echo "export PATH=$PATH:$mpiLoc" >> /home/hpcguser/.bashrc && \
	chown -R hpcguser $INPUTS_LOC && \
	chown -R hpcguser $HPCG_BIN_LOC && \
	chown -R hpcguser $scriptsLoc 
	

USER hpcguser

WORKDIR $scriptsLoc

#runs the setup script to set up the input things and run hpcg

ENTRYPOINT ["./setup_run_hpcg.sh"]







