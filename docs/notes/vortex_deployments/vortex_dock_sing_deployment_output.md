```bash
[hoffmaps@dhcp-128-205-70-4 vortex_dock_sing]$ akrr resource deploy -r vortex_dock_sing
[INFO] Validating vortex_dock_sing parameters from /home/hoffmaps/projects/akrr/etc/resources/vortex_dock_sing/resource.conf
[INFO] Syntax of /home/hoffmaps/projects/akrr/etc/resources/vortex_dock_sing/resource.conf is correct and all necessary parameters are present.

[INFO] Validating resource accessibility. Connecting to vortex_dock_sing.
[INFO] Successfully connected to vortex_dock_sing


[INFO] Checking if shell is BASH

[INFO] Shell is BASH

[INFO] Checking directory locations

[INFO] Checking: vortex.ccr.buffalo.edu:/gpfs/scratch/hoffmaps/network_scratch/akrr_data/vortex_dock_sing
[INFO] Directory exist and accessible for read/write
[INFO] Checking: vortex.ccr.buffalo.edu:/gpfs/scratch/hoffmaps/akrr_project/appker/vortex_dock_sing
[INFO] Directory exist and accessible for read/write
[INFO] Checking: vortex.ccr.buffalo.edu:/gpfs/scratch/hoffmaps/network_scratch
[INFO] Directory exist and accessible for read/write
[INFO] Checking: vortex.ccr.buffalo.edu:/tmp
[INFO] Directory exist and accessible for read/write

[INFO] Preparing to copy application signature calculator,
    app. kernel input files and 
    HPCC, IMB, IOR and Graph500 source code to remote resource

[WARNING] WARNING 1: App. kernel inputs directory /gpfs/scratch/hoffmaps/akrr_project/appker/vortex_dock_sing/inputs is present, assume they are correct.

[WARNING] WARNING 2: App. kernel executables directory /gpfs/scratch/hoffmaps/akrr_project/appker/vortex_dock_sing/execs is present, assume they are correct.
[WARNING] It should contain HPCC,IMB,IOR and Graph500 source code and app.signature calculator

[INFO] Testing app.signature calculator on headnode

[INFO] App.signature calculator is working on headnode

[INFO] Will send test job to queue, wait till it executed and will analyze the output
[INFO] 
Submitted test job to AKRR, task_id is 3144643



Test status:
Task is in scheduled_tasks queue.
It schedule to be started on 2019-06-25T13:36:41

time: 2019-06-25 13:36:41 

Test status:
Task is in active_tasks queue.
Status: None
Status info:
None

time: 2019-06-25 13:36:51 

Test status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11602764   preprod test.job hoffmaps CG       0:04      2 cpn-u26-31-[01-02]


time: 2019-06-25 13:37:08 

Test status:
Task is in active_tasks queue.
Status: Task was completed successfully.
Status info:
Done

time: 2019-06-25 13:37:14 

Test status:
Task is completed!
        status: 1
        status_info: Done

time: 2019-06-25 13:37:19 


[INFO] Test job is completed analyzing output

[INFO] 
Test kernel execution summary:
status: 1
status_info: Done
processing message:
None
Local working directory for this task: /home/hoffmaps/projects/akrr/log/comptasks/vortex_dock_sing/test/2019.06.25.13.36.42.473322
Location of some important generated files:
        Batch job script: /home/hoffmaps/projects/akrr/log/comptasks/vortex_dock_sing/test/2019.06.25.13.36.42.473322/jobfiles/test.job
        Application kernel output: /home/hoffmaps/projects/akrr/log/comptasks/vortex_dock_sing/test/2019.06.25.13.36.42.473322/jobfiles/appstdout
        Batch job standard output: /home/hoffmaps/projects/akrr/log/comptasks/vortex_dock_sing/test/2019.06.25.13.36.42.473322/jobfiles/stdout
        Batch job standard error output: /home/hoffmaps/projects/akrr/log/comptasks/vortex_dock_sing/test/2019.06.25.13.36.42.473322/jobfiles/stderr
        XML processing results: /home/hoffmaps/projects/akrr/log/comptasks/vortex_dock_sing/test/2019.06.25.13.36.42.473322/result.xml
        Task execution logs: /home/hoffmaps/projects/akrr/log/comptasks/vortex_dock_sing/test/2019.06.25.13.36.42.473322/proc/log

[INFO] 
The output looks good.

[INFO] 
Adding AKRR enviroment variables to resource's .bashrc!

[INFO] Enabled vortex_dock_sing in mod_appkernel.resource for tasks execution and made it visible to XDMoD UI.
[INFO] Successfully enabled vortex_dock_sing

[INFO] Result:
[WARNING] There are 2 warnings.
if warnings have sense you can move to next step!
```
