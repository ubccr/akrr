NWChem validation output:

```text
[INFO] Validating gamess application kernel installation on ub-hpc
[INFO] ################################################################################
[INFO] Validating ub-hpc parameters from /home/akrruser/akrr/etc/resources/ub-hpc/resource.conf
[INFO] Syntax of /home/akrruser/akrr/etc/resources/ub-hpc/resource.conf is correct and all necessary parameters are present.
[INFO] Syntax of /usr/lib/python3.4/site-packages/akrr/default_conf/gamess.app.conf is correct and all necessary parameters are present.
[INFO] ################################################################################
[INFO] Validating resource accessibility. Connecting to ub-hpc.
================================================================================
[INFO] Successfully connected to ub-hpc


[INFO] Checking directory locations

[INFO] Checking: vortex:/projects/ccrstaff/general/nikolays/huey/akrr_data
[INFO] Directory exist and accessible for read/write

[INFO] Checking: vortex:/projects/ccrstaff/general/nikolays/huey/appker
[INFO] Directory exist and accessible for read/write

[INFO] Checking: vortex:/projects/ccrstaff/general/nikolays/huey/tmp
[INFO] Directory exist and accessible for read/write
[INFO] 
[INFO] Checking: vortex:/tmp
[INFO] Directory exist and accessible for read/write
[INFO] 
[INFO] ################################################################################
[INFO] Will send test job to queue, wait till it executed and will analyze the output
Will use AKRR REST API at https://localhost:8091/api/v1
[INFO] 
Submitted test job to AKRR, task_id is 3145218



================================================================================
Tast status:
Task is in scheduled_tasks queue.
It schedule to be started on 2019-05-01T16:05:30

time: 2019-05-01 16:05:30 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: None
Status info:
None

time: 2019-05-01 16:05:35 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11369048 general-c gamess.j nikolays PD       0:00      2 (Priority)
          11368921 general-c gamess.j nikolays  R      11:27      2 cpn-d16-[13-14]


time: 2019-05-01 16:05:43 


================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11369048 general-c gamess.j nikolays  R      20:10      2 cpn-d15-[13-14]


time: 2019-05-01 16:26:33 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11369048 general-c gamess.j nikolays CG      20:12      2 cpn-d15-[13-14]


time: 2019-05-01 16:26:43 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Task was completed successfully.
Status info:
Done

time: 2019-05-01 16:26:50 

================================================================================
Tast status:
Task is completed!
        status: 1
        status_info: Done

time: 2019-05-01 16:26:55 [INFO] Test job is completed analyzing output

[INFO] 
Test kernel execution summary:
status: 1
status_info: Done
processing message:
None
Local working directory for this task: /home/akrruser/akrr/log/comptasks/ub-hpc/gamess/2019.05.01.16.05.30.288233
Location of some important generated files:
        Batch job script: /home/akrruser/akrr/log/comptasks/ub-hpc/gamess/2019.05.01.16.05.30.288233/jobfiles/gamess.job
        Application kernel output: /home/akrruser/akrr/log/comptasks/ub-hpc/gamess/2019.05.01.16.05.30.288233/jobfiles/appstdout
        Batch job standard output: /home/akrruser/akrr/log/comptasks/ub-hpc/gamess/2019.05.01.16.05.30.288233/jobfiles/stdout
        Batch job standard error output: /home/akrruser/akrr/log/comptasks/ub-hpc/gamess/2019.05.01.16.05.30.288233/jobfiles/stderr
        XML processing results: /home/akrruser/akrr/log/comptasks/ub-hpc/gamess/2019.05.01.16.05.30.288233/result.xml
        Task execution logs: /home/akrruser/akrr/log/comptasks/ub-hpc/gamess/2019.05.01.16.05.30.288233/proc/log


[INFO] 
Enabling gamess on ub-hpc for execution

[INFO] Successfully enabled gamess on ub-hpc
[INFO] 
DONE, you can move to next step!
```