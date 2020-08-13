HPCC validation output:

```text
[INFO] Validating hpcg application kernel installation on ub-hpc-skx
[INFO] ################################################################################
[INFO] Validating ub-hpc-skx parameters from /home/akrruser/akrr/etc/resources/ub-hpc-skx/resource.conf
[INFO] Syntax of /home/akrruser/akrr/etc/resources/ub-hpc-skx/resource.conf is correct and all necessary parameters are present.
[INFO] Syntax of /usr/lib/python3.4/site-packages/akrr/default_conf/hpcg.app.conf is correct and all necessary parameters are present.
[INFO] ################################################################################
[INFO] Validating resource accessibility. Connecting to ub-hpc-skx.
================================================================================
[INFO] Successfully connected to ub-hpc-skx


[INFO] Checking directory locations

[INFO] Checking: vortex:/projects/ccrstaff/general/nikolays/huey_slx/tmp/akrr_data/ub-hpc-skx
[INFO] Directory exist and accessible for read/write

[INFO] Checking: vortex:/projects/ccrstaff/general/nikolays/huey_slx/appker
[INFO] Directory exist and accessible for read/write

[INFO] Checking: vortex:/projects/ccrstaff/general/nikolays/huey_slx/tmp
[INFO] Directory exist and accessible for read/write
[INFO] 
[INFO] Checking: vortex:/tmp
[INFO] Directory exist and accessible for read/write
[INFO] 
[INFO] ################################################################################
[INFO] Will send test job to queue, wait till it executed and will analyze the output
Will use AKRR REST API at https://localhost:8091/api/v1
[INFO] 
Submitted test job to AKRR, task_id is 3144689



================================================================================
Tast status:
Task is in scheduled_tasks queue.
It schedule to be started on 2019-03-29T13:36:59

time: 2019-03-29 13:36:59 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: None
Status info:
None

time: 2019-03-29 13:37:09 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11163454   skylake hpcg.job nikolays  R       0:04      2 cpn-u22-[16,18]


time: 2019-03-29 13:37:15 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11163454   skylake hpcg.job nikolays  R       0:09      2 cpn-u22-[16,18]


time: 2019-03-29 13:37:21 

...

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11163454   skylake hpcg.job nikolays  R       3:18      2 cpn-u22-[16,18]


time: 2019-03-29 13:40:33 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11163454   skylake hpcg.job nikolays  R       3:24      2 cpn-u22-[16,18]


time: 2019-03-29 13:40:38 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Task was completed successfully.
Status info:
Done

time: 2019-03-29 13:40:51 

================================================================================
Tast status:
Task is completed!
        status: 1
        status_info: Done

time: 2019-03-29 13:40:56 [INFO] Test job is completed analyzing output

[INFO] 
Test kernel execution summary:
status: 1
status_info: Done
processing message:
None
Local working directory for this task: /home/akrruser/akrr/log/comptasks/ub-hpc-skx/hpcg/2019.03.29.13.36.59.905123
Location of some important generated files:
        Batch job script: /home/akrruser/akrr/log/comptasks/ub-hpc-skx/hpcg/2019.03.29.13.36.59.905123/jobfiles/hpcg.job
        Application kernel output: /home/akrruser/akrr/log/comptasks/ub-hpc-skx/hpcg/2019.03.29.13.36.59.905123/jobfiles/appstdout
        Batch job standard output: /home/akrruser/akrr/log/comptasks/ub-hpc-skx/hpcg/2019.03.29.13.36.59.905123/jobfiles/stdout
        Batch job standard error output: /home/akrruser/akrr/log/comptasks/ub-hpc-skx/hpcg/2019.03.29.13.36.59.905123/jobfiles/stderr
        XML processing results: /home/akrruser/akrr/log/comptasks/ub-hpc-skx/hpcg/2019.03.29.13.36.59.905123/result.xml
        Task execution logs: /home/akrruser/akrr/log/comptasks/ub-hpc-skx/hpcg/2019.03.29.13.36.59.905123/proc/log


[INFO] 
Enabling hpcg on ub-hpc-skx for execution

[INFO] Successfully enabled hpcg on ub-hpc-skx
[INFO] 
DONE, you can move to next step!
```