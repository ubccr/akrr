Application Kernels Remote Runner (AKRR)
=========================================

AKRR is a tool used in XDMoD's Application Kernel Performance Monitoring Module.

Application Kernel Performance Monitoring Module of XDMoD tool is designed to 
measure quality of service as well as preemptively identify underperforming 
hardware and software by deploying customized, computationally lightweight 
“application kernels” that are run on a regular basis (daily to several times per week) 
to continuously monitor HPC system performance and reliability from the 
application users’ point of view. The term “computationally-lightweight” is used 
to indicate that the application kernel requires relatively modest resources for 
a given run frequency. Accordingly, through XDMoD, system managers have the 
ability to proactively monitor system performance as opposed to having to rely 
on users to report failures or underperforming hardware and software.

* [Overview](docs/index.md)
* [Download](docs/AKRR_Download.md)
* [Installation](docs/AKRR_Install.md)
* [Update](docs/AKRR_Update.md)
* [Usage](docs/AKRR_Usage.md)
  * [Add HPC resource](docs/AKRR_Add_Resource.md)
  * [Deployment of Application Kernels on Resource](docs/AKRR_Deployment_of_Application_Kernel_on_Resource.md)
    * [NAMD Deployment](docs/AKRR_NAMD_Deployment.md)
    * [IMB Deployment](docs/AKRR_IMB_Deployment.md)
    * [IOR Deployment](docs/AKRR_IOR_Deployment.md)
    * [HPCC Deployment](docs/AKRR_HPCC_Deployment.md)
    * [HPCG Deployment](docs/AKRR_HPCG_Deployment.md)
    * [NWChem Deployment](docs/AKRR_NWChem_Deployment.md)
    * [GAMESS Deployment](docs/AKRR_GAMESS_Deployment.md)
    * [Enzo Deployment](docs/AKRR_Enzo_Deployment.md)    
    * [Creating New Application Kernel](docs/AKRR_Creating_New_Application_Kernel.md)
  * [Adding OpenStack Resource and Application Kernels Deployment](docs/AKRR_Add_OpenStack_Resource_and_AppKernels.md.md)
  * [Scheduling and Rescheduling Application Kernels](docs/AKRR_Tasks_Scheduling.md)
  * [Setting Walltime Limit](docs/AKRR_Walltimelimit_Setting.md)
