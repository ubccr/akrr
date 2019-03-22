IOR validation output:

```text
[INFO] Validating ior application kernel installation on ub-hpc
[INFO] ################################################################################
[INFO] Validating ub-hpc parameters from /home/akrruser/akrr/etc/resources/ub-hpc/resource.conf
[INFO] Syntax of /home/akrruser/akrr/etc/resources/ub-hpc/resource.conf is correct and all necessary parameters are present.
[INFO] Syntax of /usr/lib/python3.4/site-packages/akrr/default_conf/ior.app.conf is correct and all necessary parameters are present.
[INFO] ################################################################################
[INFO] Validating resource accessibility. Connecting to ub-hpc.
================================================================================
[INFO] Successfully connected to ub-hpc


[INFO] Checking directory locations

[INFO] Checking: huey:/projects/ccrstaff/general/nikolays/huey/akrr_data
[INFO] Directory exist and accessible for read/write

[INFO] Checking: huey:/projects/ccrstaff/general/nikolays/huey/appker
[INFO] Directory exist and accessible for read/write

[INFO] Checking: huey:/projects/ccrstaff/general/nikolays/huey/tmp
[INFO] Directory exist and accessible for read/write
[INFO] 
[INFO] Checking: huey:/tmp
[INFO] Directory exist and accessible for read/write
[INFO] 
[INFO] ################################################################################
[INFO] Will send test job to queue, wait till it executed and will analyze the output
Will use AKRR REST API at https://localhost:8091/api/v1
[INFO] 
Submitted test job to AKRR, task_id is 3144557



================================================================================
Tast status:
Task is in scheduled_tasks queue.
It schedule to be started on2019-03-22T18:09:16

time: 2019-03-22 18:09:16 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: None
Status info:
None

time: 2019-03-22 18:09:26 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
             10859 general-c  ior.job nikolays  R       0:04      2 cpn-d13-[16-17]


time: 2019-03-22 18:09:33 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
             10859 general-c  ior.job nikolays  R       0:55      2 cpn-d13-[16-17]


time: 2019-03-22 18:10:24 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Not in queue. Either exited with error or executed successfully. Copied all files to local machine. Deleted all files from remote machine
Status info:
Not in queue. Either exited with error or executed successfully. Copied all files to local machine. Deleted all files from remote machine

time: 2019-03-22 18:10:29 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Task was completed successfully.
Status info:
Done

time: 2019-03-22 18:10:34 

================================================================================
Tast status:
Task is completed!
        status: 1
        status_info: Done

time: 2019-03-22 18:10:39 [INFO] Test job is completed analyzing output

[INFO] 
Test kernel execution summary:
status: 1
status_info: Done
processing message:
None
Local working directory for this task: /home/akrruser/akrr/log/comptasks/ub-hpc/ior/2019.03.22.18.09.17.306954
Location of some important generated files:
        Batch job script: /home/akrruser/akrr/log/comptasks/ub-hpc/ior/2019.03.22.18.09.17.306954/jobfiles/ior.job
        Application kernel output: /home/akrruser/akrr/log/comptasks/ub-hpc/ior/2019.03.22.18.09.17.306954/jobfiles/appstdout
        Batch job standard output: /home/akrruser/akrr/log/comptasks/ub-hpc/ior/2019.03.22.18.09.17.306954/jobfiles/stdout
        Batch job standard error output: /home/akrruser/akrr/log/comptasks/ub-hpc/ior/2019.03.22.18.09.17.306954/jobfiles/stderr
        XML processing results: /home/akrruser/akrr/log/comptasks/ub-hpc/ior/2019.03.22.18.09.17.306954/result.xml
        Task execution logs: /home/akrruser/akrr/log/comptasks/ub-hpc/ior/2019.03.22.18.09.17.306954/proc/log


[INFO] 
Enabling ior on ub-hpc for execution

[INFO] Successfully enabled ior on ub-hpc
[INFO] 
DONE, you can move to next step!
```