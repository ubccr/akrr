# How AKRR Generate Batch Scripts

AKRR is designed with need to execute multiple application kernels on multiple HPC resources. 
The complexity of this task in part comes from
the fact that various HPC resources can be severely different in hardware and software. 
For example, HPC resources can use different queueing
systems, different vendors and versions of MPI, BLAS and others libraries. 
Furthermore, some applications can be compiled in number of way
which will affect how they should be executed (e.g. TCP/IP vs MPI). 
This makes impossible to create a single job script which will work on all
platforms. 
A large set of separate job scripts for every application kernel on every HPC resource would be unbearable to maintain. 
AKRR
addresses variability of batch job scripts by the use of templates. 

Job script is created from template for every new task.
The root template for batch job script is located at 
$AKRR_SRC/akrr/default_conf/default.resource.conf and listed bellow:

```python

```
