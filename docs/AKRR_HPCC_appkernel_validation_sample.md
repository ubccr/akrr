HPCC validation output:

```text
[INFO] Creating task directory: /home/akrruser/akrr/log/data/ub-hpc/hpcc/2019.03.25.16.01.28.633071
[INFO] Creating task directories: 
        /home/akrruser/akrr/log/data/ub-hpc/hpcc/2019.03.25.16.01.28.633071/jobfiles
        /home/akrruser/akrr/log/data/ub-hpc/hpcc/2019.03.25.16.01.28.633071/proc
[INFO] Creating batch job script and submitting it to remote machine
[INFO] Directory huey:/projects/ccrstaff/general/nikolays/huey/akrr_data/hpcc/2019.03.25.16.01.28.633071 does not exists, will try to create it
[INFO] auto_walltime_limit is on, trying to estimate walltime limit...
[INFO] There are only 0 previous run, need at least 5 for walltime limit autoset
[INFO] Local copy of batch job script is /home/akrruser/akrr/log/data/ub-hpc/hpcc/2019.03.25.16.01.28.633071/jobfiles/hpcc.job

[INFO] Application kernel working directory on ub-hpc is /projects/ccrstaff/general/nikolays/huey/akrr_data/hpcc/2019.03.25.16.01.28.633071
[INFO] Batch job script location on ub-hpc is /projects/ccrstaff/general/nikolays/huey/akrr_data/hpcc/2019.03.25.16.01.28.633071/hpcc.job
[akrruser@xdmod ~]$ 
[akrruser@xdmod ~]$ akrr app validate -n 2 -r $RESOURCE -a $APPKER 
[INFO] Validating hpcc application kernel installation on ub-hpc
[INFO] ################################################################################
[INFO] Validating ub-hpc parameters from /home/akrruser/akrr/etc/resources/ub-hpc/resource.conf
[INFO] Syntax of /home/akrruser/akrr/etc/resources/ub-hpc/resource.conf is correct and all necessary parameters are present.
[INFO] Syntax of /usr/lib/python3.4/site-packages/akrr/default_conf/hpcc.app.conf is correct and all necessary parameters are present.
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
Submitted test job to AKRR, task_id is 3144595



================================================================================
Tast status:
Task is in scheduled_tasks queue.
It schedule to be started on2019-03-25T16:06:34

time: 2019-03-25 16:06:34 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: None
Status info:
None

time: 2019-03-25 16:06:44 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
             10892 general-c hpcc.job nikolays  R       0:04      2 cpn-d13-[16-17]


time: 2019-03-25 16:06:51 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
             10892 general-c hpcc.job nikolays  R       0:10      2 cpn-d13-[16-17]


time: 2019-03-25 16:06:56 

...

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
             10892 general-c hpcc.job nikolays  R       5:58      2 cpn-d13-[16-17]


time: 2019-03-25 16:12:45 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
             10892 general-c hpcc.job nikolays  R       6:03      2 cpn-d13-[16-17]


time: 2019-03-25 16:12:55 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Task was completed successfully.
Status info:
Done

time: 2019-03-25 16:13:02 

================================================================================
Tast status:
Task is completed!
        status: 1
        status_info: Done

time: 2019-03-25 16:13:07 [INFO] Test job is completed analyzing output

[INFO] 
Test kernel execution summary:
status: 1
status_info: Done
processing message:
None
Local working directory for this task: /home/akrruser/akrr/log/comptasks/ub-hpc/hpcc/2019.03.25.16.06.35.347106
Location of some important generated files:
        Batch job script: /home/akrruser/akrr/log/comptasks/ub-hpc/hpcc/2019.03.25.16.06.35.347106/jobfiles/hpcc.job
        Application kernel output: /home/akrruser/akrr/log/comptasks/ub-hpc/hpcc/2019.03.25.16.06.35.347106/jobfiles/appstdout
        Batch job standard output: /home/akrruser/akrr/log/comptasks/ub-hpc/hpcc/2019.03.25.16.06.35.347106/jobfiles/stdout
        Batch job standard error output: /home/akrruser/akrr/log/comptasks/ub-hpc/hpcc/2019.03.25.16.06.35.347106/jobfiles/stderr
        XML processing results: /home/akrruser/akrr/log/comptasks/ub-hpc/hpcc/2019.03.25.16.06.35.347106/result.xml
        Task execution logs: /home/akrruser/akrr/log/comptasks/ub-hpc/hpcc/2019.03.25.16.06.35.347106/proc/log


[INFO] 
Enabling hpcc on ub-hpc for execution

[INFO] Successfully enabled hpcc on ub-hpc
[INFO] 
DONE, you can move to next step!
```