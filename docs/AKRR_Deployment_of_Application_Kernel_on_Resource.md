# Deployment of Applications Kernels on a Resource

HPC resources differ significantly in terms of the software stack. For example, 
different resources (and applications running on those resources) can utilize 
different compilers (gcc or icc) and MPI libraries (OpenMPI, MVAPICH, or a 
commercial variant). Furthermore, the same application can be compiled in a 
number of ways which can greatly vary in how they are executed. Therefore beside 
general application kernel configuration, each application kernel needs to be 
separately configured for each resource.

The overall strategy for deploying an application kernel to a resource is 
following:

1.  Install application or identify where it is already installed.
2.  Generate initial configuration file.
3.  Edit configuration file.
4.  (Optional) Generate batch job script and execute it manually, update 
configuration file as needed.
5.  Perform validation run, update configuration file as needed.
6.  Schedule regular execution of application kernel.

First, each step will be described in general as it applies to all application 
kernels and the details on example individual application kernels deployment 
will follow.

## Install Application or Identify where it is Installed

AKRR comes with two flavors of application kernels.  One is based on real-world 
applications and another is based on benchmarks. Real-world applications are 
often already installed system-wide on a resource for the use of regular users, 
here one of the purposes of application kernels is to monitor the performance of 
a standard often-used application on that resource. Benchmarks, however, are 
rarely installed system-wide and thus they need to be installed first.

## Generate Initiate Configuration File

The initial configuration file is generated with 
_akrr app add_ command. It will generate an initial 
configuration file and place it to $AKRR_HOME/cfg/resource/<app kernelname>.conf.

# Edit Configuration File

The generated configuration file is fairly generic. Here you need to specify 
proper execution environment and specify how to execute this particular 
application kernel on this particular machine/resource.  

# Generate Batch Job Script and Execute it Manually (Optional)

The purpose of this step is to ensure that the configuration lead to a correct 
(and workable) batch job script. First the batch job script is generated with 
**'akrr_ctl.sh batch_job'**. Then this script is executed in an interactive 
session (this improves the turn-around in case of errors). If the script fails 
to execute, the issues can be fixed first in that script itself and then merged 
with the configuration file.

This step is somewhat optional because it is very similar to the next step. 
However the opportunity to work in an interactive session will often improve the 
turn-around time because there is no need to stay in queue for each iteration.

# Perform Validation Run

For this step **appkernel_validation.py** utility is used to validate 
application kernel installation on particular resource. It execute the 
application kernel and analyses its results. If it fails the problems need to be 
fixed and another round of validation should be performed

# Schedule regular execution of application kernel

Finally, if validation was successful the application kernel can be submited for 
regular execution on that resource.

# Details on the Individual Application Kernels Deployment

* [NAMD Deployment](AKRR_NAMD_Deployment.md)
* [HPCC Deployment](AKRR_HPCC_Deployment.md)
* [IMB Deployment](AKRR_IMB_Deployment.md)
* [IOR Deployment](AKRR_IOR_Deployment.md)
* [HPCG Deployment](AKRR_NWChem_Deployment.md)
* [NWChem Deployment](AKRR_NWChem_Deployment.md)
* [GAMESS Deployment](AKRR_GAMESS_Deployment.md)
* [Enzo Deployment](AKRR_Enzo_Deployment.md)

* [Creating New Application Kernel](AKRR_Creating_New_Application_Kernel.md)


Next: [NAMD Deployment](AKRR_NAMD_Deployment.md)