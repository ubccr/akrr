```bash
[hoffmaps@dhcp-128-205-70-4 vortex_bare_metal]$ akrr resource deploy -r vortex_bare_metal
[INFO] Validating vortex_bare_metal parameters from /home/hoffmaps/projects/akrr/etc/resources/vortex_bare_metal/resource.conf
[INFO] Syntax of /home/hoffmaps/projects/akrr/etc/resources/vortex_bare_metal/resource.conf is correct and all necessary parameters are present.

[INFO] Validating resource accessibility. Connecting to vortex_bare_metal.
[INFO] Successfully connected to vortex_bare_metal


[INFO] Checking if shell is BASH

[INFO] Shell is BASH

[INFO] Checking directory locations

[INFO] Checking: vortex.ccr.buffalo.edu:/gpfs/scratch/hoffmaps/network_scratch/akrr_data/vortex_bare_metal
[INFO] Directory exist and accessible for read/write
[INFO] Checking: vortex.ccr.buffalo.edu:/gpfs/scratch/hoffmaps/akrr_project/appker/vortex_bare_metal
[INFO] Directory exist and accessible for read/write
[INFO] Checking: vortex.ccr.buffalo.edu:/gpfs/scratch/hoffmaps/network_scratch
[INFO] Directory exist and accessible for read/write
[INFO] Checking: vortex.ccr.buffalo.edu:/tmp
[INFO] Directory exist and accessible for read/write

[INFO] Preparing to copy application signature calculator,
    app. kernel input files and 
    HPCC, IMB, IOR and Graph500 source code to remote resource

[INFO] Copying app. kernel input tarball to /gpfs/scratch/hoffmaps/akrr_project/appker/vortex_bare_metal
UPDATED: March 6, 2015

You are accessing a University at Buffalo (UB) - Center for Computational Research (CCR)
computer system that is provided for CCR-authorized users only.  By using this system
(which consists of any device attached to this machine, including compute nodes,
remote visualization software and hardware, storage and database resources), you have
implicitly agreed to abide by the highest standards of responsibility to your
colleagues -- the students, faculty, staff, and external users who share this environment.
You are required to comply with ALL University at Buffalo policies
(http://www.buffalo.edu/ubit/policies/it-policies-a-to-z/computer-and-network-use.html),
as well as state and federal laws concerning appropriate use of information technology.

- CCR is not responsible for the loss or misuse of data on our systems.

- CCR systems are NOT HIPAA-compliant.  Storage of any personally identifiable Protected
Health Information (PHI) on our systems is a violation of the Health Insurance Portability
and Accountability Act (HIPAA) of 1996 Privacy and Security Rules.  If in doubt, contact
CCR before transferring your data.

- All CCR systems are monitored for administrative and security reasons. Use of this system
constitutes consent to this monitoring for these purposes.

By continuing to use this system you indicate your awareness of and consent to these terms
and conditions of use.  Non-compliance of these terms is considered a breach of University
policy and may result in disciplinary and/or legal action.

LOG OFF IMMEDIATELY if you do not agree to the conditions stated in this warning.

inputs.tar.gz                                 100% 5715KB  35.8MB/s   00:00    
[INFO] Unpacking app. kernel input files to /gpfs/scratch/hoffmaps/akrr_project/appker/vortex_bare_metal/inputs
[INFO] App. kernel input files are in /gpfs/scratch/hoffmaps/akrr_project/appker/vortex_bare_metal/inputs

[INFO] Copying app. kernel execs tarball to /gpfs/scratch/hoffmaps/akrr_project/appker/vortex_bare_metal
It contains HPCC,IMB,IOR and Graph500 source code and app.signature calculator
UPDATED: March 6, 2015

You are accessing a University at Buffalo (UB) - Center for Computational Research (CCR)
computer system that is provided for CCR-authorized users only.  By using this system
(which consists of any device attached to this machine, including compute nodes,
remote visualization software and hardware, storage and database resources), you have
implicitly agreed to abide by the highest standards of responsibility to your
colleagues -- the students, faculty, staff, and external users who share this environment.
You are required to comply with ALL University at Buffalo policies
(http://www.buffalo.edu/ubit/policies/it-policies-a-to-z/computer-and-network-use.html),
as well as state and federal laws concerning appropriate use of information technology.

- CCR is not responsible for the loss or misuse of data on our systems.

- CCR systems are NOT HIPAA-compliant.  Storage of any personally identifiable Protected
Health Information (PHI) on our systems is a violation of the Health Insurance Portability
and Accountability Act (HIPAA) of 1996 Privacy and Security Rules.  If in doubt, contact
CCR before transferring your data.

- All CCR systems are monitored for administrative and security reasons. Use of this system
constitutes consent to this monitoring for these purposes.

By continuing to use this system you indicate your awareness of and consent to these terms
and conditions of use.  Non-compliance of these terms is considered a breach of University
policy and may result in disciplinary and/or legal action.

LOG OFF IMMEDIATELY if you do not agree to the conditions stated in this warning.

execs.tar.gz                                  100% 4457     1.7MB/s   00:00    
[INFO] Unpacking HPCC,IMB,IOR and Graph500 source code and app.signature calculator files to /gpfs/scratch/hoffmaps/akrr_project/appker/vortex_bare_metal/execs
[INFO] HPCC,IMB,IOR and Graph500 source code and app.signature calculator are in /gpfs/scratch/hoffmaps/akrr_project/appker/vortex_bare_metal/execs

[INFO] Testing app.signature calculator on headnode

[INFO] App.signature calculator is working on headnode

[INFO] Will send test job to queue, wait till it executed and will analyze the output
[INFO] 
Submitted test job to AKRR, task_id is 3144655



Test status:
Task is in scheduled_tasks queue.
It schedule to be started on 2019-06-25T16:11:49

time: 2019-06-25 16:11:49 

Test status:
Task is in active_tasks queue.
Status: None
Status info:
None

time: 2019-06-25 16:11:59 

Test status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11603557   preprod test.job hoffmaps CG       0:03      2 cpn-u26-31-[01-02]


time: 2019-06-25 16:12:05 

Test status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          11603557   preprod test.job hoffmaps CG       0:03      1 cpn-u26-31-02


time: 2019-06-25 16:12:16 

Test status:
Task is in active_tasks queue.
Status: Task was completed successfully.
Status info:
Done

time: 2019-06-25 16:12:21 

Test status:
Task is completed!
        status: 1
        status_info: Done

time: 2019-06-25 16:12:26 


[INFO] Test job is completed analyzing output

[INFO] 
Test kernel execution summary:
status: 1
status_info: Done
processing message:
None
Local working directory for this task: /home/hoffmaps/projects/akrr/log/comptasks/vortex_bare_metal/test/2019.06.25.16.11.50.635490
Location of some important generated files:
        Batch job script: /home/hoffmaps/projects/akrr/log/comptasks/vortex_bare_metal/test/2019.06.25.16.11.50.635490/jobfiles/test.job
        Application kernel output: /home/hoffmaps/projects/akrr/log/comptasks/vortex_bare_metal/test/2019.06.25.16.11.50.635490/jobfiles/appstdout
        Batch job standard output: /home/hoffmaps/projects/akrr/log/comptasks/vortex_bare_metal/test/2019.06.25.16.11.50.635490/jobfiles/stdout
        Batch job standard error output: /home/hoffmaps/projects/akrr/log/comptasks/vortex_bare_metal/test/2019.06.25.16.11.50.635490/jobfiles/stderr
        XML processing results: /home/hoffmaps/projects/akrr/log/comptasks/vortex_bare_metal/test/2019.06.25.16.11.50.635490/result.xml
        Task execution logs: /home/hoffmaps/projects/akrr/log/comptasks/vortex_bare_metal/test/2019.06.25.16.11.50.635490/proc/log

[INFO] 
The output looks good.

[INFO] 
Adding AKRR enviroment variables to resource's .bashrc!

[INFO] Enabled vortex_bare_metal in mod_appkernel.resource for tasks execution and made it visible to XDMoD UI.
[INFO] Successfully enabled vortex_bare_metal

[INFO] Result:
[INFO] 
DONE, you can move to next step!
```
