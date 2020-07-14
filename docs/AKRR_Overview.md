# XDMoD: Application Kernel Performance Monitoring Module

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

The XDMoD's application kernel performance monitoring consists of two parts: 
application kernel remote runner (AKRR) and XDMoD appkernel module (`xdmod-appkernels`).

Application kernel remote runner (AKRR) executes the scheduled jobs, 
monitors their execution, processes the output, extracts performance metrics 
and exports the results to the database.

XDMoD appkernel module analyse the results of application kernels runs, provides 
visualization tools and web-base interface to control AKRR. Among analysis tools it 
has automatic anomaly detector, that analyzes the performance of all application kernels 
executed on a resource and automatically recognizes poorly performing systems. 

XDMoD should be install first, then AKRR and then `xdmod-appkernels`. In addition before 
installing `xdmod-appkernels` module, add your HPC resource to AKRR and run few appkernels 
jobs, this will help to check that `xdmod-appkernels` is working properly.

Next: [AKRR Download](AKRR_Download.md)
