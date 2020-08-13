Setting reasonable walltime limits for appkernel tasks can help with the wait time in queue for them.
Most of application kernels uses small number of nodes and run for a short time.
This often allow the scheduler to place them in the gaps between larger jobs 
when resource are idle in wait for allocation for high priority jobs.

AKRR uses walltime from previous runs to set walltime for new tasks (with some padding). 
This increases chance of appkernels to be scheduled by backfill scheduler with affecting high priority jobs.
In case if there is a failed job among 5 previous jobs it will use default walltime which can be set in 
*$AKRR_HOME/etc/resource/<resource_name>/<appkernel_name>.conf*:

```python
# walltime_limit in minutes
walltime_limit = 30
```

The automatic walltime time determination can be turned off for all appkernels by placing following to 
*$AKRR_HOME/etc/resource/<resource_name>/resource.conf*

```python
auto_walltime_limit = False
```
