---
title: Open XDMoD Application Kernel Remote Runner Module
---

Application Kernel Performance Monitoring Module of XDMoD tool is designed to measure quality of service as well as preemptively identify
underperforming hardware and software by deploying customized, computationally lightweight “application kernels” that are run frequently (daily
to several times per week) to continuously monitor HPC system performance and reliability from the application users’ point of view. The term
“computationally-lightweight” is used to indicate that the application kernel requires relatively modest resources for a given run frequency.
Accordingly, through XDMoD, system managers have the ability to proactively monitor system performance as opposed to having to rely on users
to report failures or underperforming hardware and software.

The application kernel module of XDMoD consists of three parts. 1) the application kernel remote runner (AKRR) executes the scheduled jobs,
monitors their execution, processes the output, extracts performance metrics and exports the results to the database, 2) the application kernel
process control identifies poorly performing individual jobs, 3) the application kernel automatic anomaly detector analyzes the performance of all
application kernels executed on a particular resource and automatically recognizes poorly performing systems. Packaging-wise first one comes as
a separate installation and the last two installed within XDMoD framework.

