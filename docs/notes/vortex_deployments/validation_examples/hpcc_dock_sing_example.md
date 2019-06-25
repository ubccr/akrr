### Validation of hpcc example
```bash
[hoffmaps@dhcp-128-205-70-4 vortex_dock_sing]$ akrr app validate -n 1 -a hpcc -r vortex_dock_sing
[INFO] Validating hpcc application kernel installation on vortex_dock_sing
[INFO] ################################################################################
[INFO] Validating vortex_dock_sing parameters from /home/hoffmaps/projects/akrr/etc/resources/vortex_dock_sing/resource.conf
[INFO] Syntax of /home/hoffmaps/projects/akrr/etc/resources/vortex_dock_sing/resource.conf is correct and all necessary parameters are present.
[INFO] Syntax of /home/hoffmaps/projects/akrr/akrr/default_conf/hpcc.app.conf is correct and all necessary parameters are present.
[INFO] ################################################################################
[INFO] Validating resource accessibility. Connecting to vortex_dock_sing.
================================================================================
[INFO] Successfully connected to vortex_dock_sing


[INFO] Checking directory locations

[INFO] Checking: vortex.ccr.buffalo.edu:/gpfs/scratch/hoffmaps/network_scratch/akrr_data/vortex_dock_sing
[INFO] Directory exist and accessible for read/write

[INFO] Checking: vortex.ccr.buffalo.edu:/gpfs/scratch/hoffmaps/akrr_project/appker/vortex_dock_sing
[INFO] Directory exist and accessible for read/write

[INFO] Checking: vortex.ccr.buffalo.edu:/gpfs/scratch/hoffmaps/network_scratch
[INFO] Directory exist and accessible for read/write
[INFO] 
[INFO] Checking: vortex.ccr.buffalo.edu:/tmp
[INFO] Directory exist and accessible for read/write
[INFO] 
[INFO] ################################################################################
[INFO] Will send test job to queue, wait till it executed and will analyze the output
Will use AKRR REST API at https://localhost:8091/api/v1
[INFO] 
Submitted test job to AKRR, task_id is 3144644



================================================================================
Tast status:
Task is in scheduled_tasks queue.
It schedule to be started on 2019-06-25T14:02:10

time: 2019-06-25 14:02:10 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Created batch job script and have submitted it to remote queue.
Status info:
Remote job ID is 11602987

time: 2019-06-25 14:02:20 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11602987   preprod hpcc.job hoffmaps  R       0:03      1 cpn-u25-39


time: 2019-06-25 14:02:25 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11602987   preprod hpcc.job hoffmaps  R       0:08      1 cpn-u25-39


time: 2019-06-25 14:02:30 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11602987   preprod hpcc.job hoffmaps  R       0:13      1 cpn-u25-39


time: 2019-06-25 14:02:36 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11602987   preprod hpcc.job hoffmaps  R       0:18      1 cpn-u25-39


time: 2019-06-25 14:02:41 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11602987   preprod hpcc.job hoffmaps  R       0:23      1 cpn-u25-39


time: 2019-06-25 14:02:46 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11602987   preprod hpcc.job hoffmaps  R       0:30      1 cpn-u25-39


time: 2019-06-25 14:02:51 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11602987   preprod hpcc.job hoffmaps  R       0:34      1 cpn-u25-39


time: 2019-06-25 14:02:56 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11602987   preprod hpcc.job hoffmaps  R       0:39      1 cpn-u25-39


time: 2019-06-25 14:03:01 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11602987   preprod hpcc.job hoffmaps  R       0:43      1 cpn-u25-39


time: 2019-06-25 14:03:06 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11602987   preprod hpcc.job hoffmaps  R       0:50      1 cpn-u25-39


time: 2019-06-25 14:03:11 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11602987   preprod hpcc.job hoffmaps  R       0:53      1 cpn-u25-39


time: 2019-06-25 14:03:16 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11602987   preprod hpcc.job hoffmaps  R       0:59      1 cpn-u25-39


time: 2019-06-25 14:03:21 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11602987   preprod hpcc.job hoffmaps  R       1:04      1 cpn-u25-39


time: 2019-06-25 14:03:26 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11602987   preprod hpcc.job hoffmaps  R       1:09      1 cpn-u25-39


time: 2019-06-25 14:03:31 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11602987   preprod hpcc.job hoffmaps  R       1:14      1 cpn-u25-39


time: 2019-06-25 14:03:37 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11602987   preprod hpcc.job hoffmaps  R       1:19      1 cpn-u25-39


time: 2019-06-25 14:03:42 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11602987   preprod hpcc.job hoffmaps  R       1:24      1 cpn-u25-39


time: 2019-06-25 14:03:47 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11602987   preprod hpcc.job hoffmaps  R       1:30      1 cpn-u25-39


time: 2019-06-25 14:03:52 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11602987   preprod hpcc.job hoffmaps  R       1:35      1 cpn-u25-39


time: 2019-06-25 14:03:57 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11602987   preprod hpcc.job hoffmaps  R       1:40      1 cpn-u25-39


time: 2019-06-25 14:04:02 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11602987   preprod hpcc.job hoffmaps  R       1:45      1 cpn-u25-39


time: 2019-06-25 14:04:12 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11602987   preprod hpcc.job hoffmaps  R       1:58      1 cpn-u25-39


time: 2019-06-25 14:04:21 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11602987   preprod hpcc.job hoffmaps  R       2:03      1 cpn-u25-39


time: 2019-06-25 14:04:26 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11602987   preprod hpcc.job hoffmaps  R       2:09      1 cpn-u25-39


time: 2019-06-25 14:04:31 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11602987   preprod hpcc.job hoffmaps  R       2:14      1 cpn-u25-39


time: 2019-06-25 14:04:36 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11602987   preprod hpcc.job hoffmaps  R       2:19      1 cpn-u25-39


time: 2019-06-25 14:04:41 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11602987   preprod hpcc.job hoffmaps  R       2:24      1 cpn-u25-39


time: 2019-06-25 14:04:51 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11602987   preprod hpcc.job hoffmaps  R       2:41      1 cpn-u25-39


time: 2019-06-25 14:05:04 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11602987   preprod hpcc.job hoffmaps  R       2:47      1 cpn-u25-39


time: 2019-06-25 14:05:09 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Not in queue. Either exited with error or executed successfully. Copied all files to local machine. Deleted all files from remote machine
Status info:
Not in queue. Either exited with error or executed successfully. Copied all files to local machine. Deleted all files from remote machine

time: 2019-06-25 14:05:14 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Task was completed successfully.
Status info:
Done

time: 2019-06-25 14:05:19 

================================================================================
Tast status:
Task is completed!
        status: 1
        status_info: Done

time: 2019-06-25 14:05:24 [INFO] Test job is completed analyzing output

[INFO] 
Test kernel execution summary:
status: 1
status_info: Done
processing message:
None
Local working directory for this task: /home/hoffmaps/projects/akrr/log/comptasks/vortex_dock_sing/hpcc/2019.06.25.14.02.11.071265
Location of some important generated files:
        Batch job script: /home/hoffmaps/projects/akrr/log/comptasks/vortex_dock_sing/hpcc/2019.06.25.14.02.11.071265/jobfiles/hpcc.job
        Application kernel output: /home/hoffmaps/projects/akrr/log/comptasks/vortex_dock_sing/hpcc/2019.06.25.14.02.11.071265/jobfiles/appstdout
        Batch job standard output: /home/hoffmaps/projects/akrr/log/comptasks/vortex_dock_sing/hpcc/2019.06.25.14.02.11.071265/jobfiles/stdout
        Batch job standard error output: /home/hoffmaps/projects/akrr/log/comptasks/vortex_dock_sing/hpcc/2019.06.25.14.02.11.071265/jobfiles/stderr
        XML processing results: /home/hoffmaps/projects/akrr/log/comptasks/vortex_dock_sing/hpcc/2019.06.25.14.02.11.071265/result.xml
        Task execution logs: /home/hoffmaps/projects/akrr/log/comptasks/vortex_dock_sing/hpcc/2019.06.25.14.02.11.071265/proc/log


[INFO] 
Enabling hpcc on vortex_dock_sing for execution

[INFO] Successfully enabled hpcc on vortex_dock_sing
[INFO] 
DONE, you can move to next step!
```
