```bash
[hoffmaps@dhcp-128-205-70-4 vortex_dock_sing]$ akrr app validate -n 1 -a $APPKER -r $RESOURCE
[INFO] Validating hpcg application kernel installation on vortex_dock_sing
[INFO] ################################################################################
[INFO] Validating vortex_dock_sing parameters from /home/hoffmaps/projects/akrr/etc/resources/vortex_dock_sing/resource.conf
[INFO] Syntax of /home/hoffmaps/projects/akrr/etc/resources/vortex_dock_sing/resource.conf is correct and all necessary parameters are present.
[INFO] Syntax of /home/hoffmaps/projects/akrr/akrr/default_conf/hpcg.app.conf is correct and all necessary parameters are present.
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
Submitted test job to AKRR, task_id is 3144646



================================================================================
Tast status:
Task is in scheduled_tasks queue.
It schedule to be started on 2019-06-25T14:27:10

time: 2019-06-25 14:27:10 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: None
Status info:
None

time: 2019-06-25 14:27:20 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11603124   preprod hpcg.job hoffmaps  R       0:04      1 cpn-u25-39


time: 2019-06-25 14:27:27 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11603124   preprod hpcg.job hoffmaps  R       0:09      1 cpn-u25-39


time: 2019-06-25 14:27:32 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11603124   preprod hpcg.job hoffmaps  R       0:14      1 cpn-u25-39


time: 2019-06-25 14:27:37 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11603124   preprod hpcg.job hoffmaps  R       0:19      1 cpn-u25-39


time: 2019-06-25 14:27:42 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11603124   preprod hpcg.job hoffmaps  R       0:25      1 cpn-u25-39


time: 2019-06-25 14:27:52 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11603124   preprod hpcg.job hoffmaps  R       0:30      1 cpn-u25-39


time: 2019-06-25 14:27:58 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11603124   preprod hpcg.job hoffmaps CG       0:42      1 cpn-u25-39


time: 2019-06-25 14:28:08 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Task was completed successfully.
Status info:
Done

time: 2019-06-25 14:28:14 

================================================================================
Tast status:
Task is completed!
        status: 1
        status_info: Done

time: 2019-06-25 14:28:19 [INFO] Test job is completed analyzing output

[INFO] 
Test kernel execution summary:
status: 1
status_info: Done
processing message:
None
Local working directory for this task: /home/hoffmaps/projects/akrr/log/comptasks/vortex_dock_sing/hpcg/2019.06.25.14.27.11.055819
Location of some important generated files:
        Batch job script: /home/hoffmaps/projects/akrr/log/comptasks/vortex_dock_sing/hpcg/2019.06.25.14.27.11.055819/jobfiles/hpcg.job
        Application kernel output: /home/hoffmaps/projects/akrr/log/comptasks/vortex_dock_sing/hpcg/2019.06.25.14.27.11.055819/jobfiles/appstdout
        Batch job standard output: /home/hoffmaps/projects/akrr/log/comptasks/vortex_dock_sing/hpcg/2019.06.25.14.27.11.055819/jobfiles/stdout
        Batch job standard error output: /home/hoffmaps/projects/akrr/log/comptasks/vortex_dock_sing/hpcg/2019.06.25.14.27.11.055819/jobfiles/stderr
        XML processing results: /home/hoffmaps/projects/akrr/log/comptasks/vortex_dock_sing/hpcg/2019.06.25.14.27.11.055819/result.xml
        Task execution logs: /home/hoffmaps/projects/akrr/log/comptasks/vortex_dock_sing/hpcg/2019.06.25.14.27.11.055819/proc/log


[INFO] 
Enabling hpcg on vortex_dock_sing for execution

[INFO] Successfully enabled hpcg on vortex_dock_sing
[INFO] 
DONE, you can move to next step!

```
