### Notes on originally messing around and seeing how it works

Singularity documentation: https://www.sylabs.io/docs/

```bash
# shows all nodes on dev clusters
sinfo -M all

#request interactive job
salloc --nodes=1

# see status of jobs
squeue -u hoffmaps

# main directory I'll be using
/gpfs/scratch/hoffmaps/akrr_project

```

Okay so I'm trying to be able to access huey by sshing right from my local machine.
https://ubccr.freshdesk.com/support/solutions/articles/13000025490-using-ssh-keys-in-linux-macos
^ Followed these directions to be able to ssh into vortex without using a password
Then I found this stackoverflow to see if I can't connect all the way to huey
https://serverfault.com/questions/337274/ssh-from-a-through-b-to-c-using-private-key-on-b
UPDATE: that thing above didn't work, but after adding in the key so that I could ssh into vortex without a password, I just made the ssh config the same as what nikolay sent and now when I do ssh huey it works
- well it works but only with the one tab... so idk how that even works then
- But at least if I run akrr in that tab then it seems to be able to connect and such
	- So don't lose that tab

so what am I entering for setting up the huey resource
```bash
[hoffmaps@dhcp-128-205-70-4 .ssh]$ akrr resource add --no-ping
[INFO] Beginning Initiation of New Resource...
[INFO] Retrieving Resources from XDMoD Database...
[INFO] Found following resources from XDMoD Database:
    resource_id  name


[INPUT]: Enter AKRR resource name:
test_huey

[INPUT]: Enter queuing system on resource (slurm, pbs or openstack): 
slurm

[INPUT]: Enter Resource head node (access node) full name (e.g. headnode.somewhere.org):
[test_huey] huey
[WARNING] Can not ping huey, but asked to ignore it.
[INPUT]: Enter username for resource access:
[hoffmaps] 
[INFO] Checking for password-less access
[INFO] Can access resource without password

[INFO] Connecting to test_huey
[INFO]               Done

[INPUT]: Enter processors (cores) per node count:
8
[INPUT]: Enter location of local scratch (visible only to single node):
[/tmp]
[INFO] Directory exist and accessible for read/write

[INPUT]: Enter location of network scratch (visible only to all nodes),used for temporary storage of app kernel input/output:
/gpfs/scratch/hoffmaps/network_scratch
[INFO] Directory exist and accessible for read/write

[INPUT]: Enter future location of app kernels input and executable files:
[/user/hoffmaps/appker/test_huey]/gpfs/scratch/hoffmaps/akrr_project
[INFO] Directory exist and accessible for read/write

[INPUT]: Enter future locations for app kernels working directories (can or even should be on scratch space):
[/gpfs/scratch/hoffmaps/network_scratch/akrr_data/test_huey]
[INFO] Directory huey:/gpfs/scratch/hoffmaps/network_scratch/akrr_data/test_huey does not exists, will try to create it
[INFO] Directory exist and accessible for read/write

[INFO] Initiating test_huey at AKRR
[INFO] Resource configuration is in /home/hoffmaps/projects/akrr/etc/resources/test_huey/resource.conf
[INFO] Initiation of new resource is completed.
    Edit batch_job_header_template variable in /home/hoffmaps/projects/akrr/etc/resources/test_huey/resource.conf
    and move to resource validation and deployment step.
    i.e. execute:
        akrr resource deploy -r test_huey

```
Then I edited the batch job header to now be
```bash
#SBATCH --partition=general-compute
#SBATCH --nodes={akrr_num_of_nodes}
#SBATCH --ntasks-per-node={akrr_ppn}
#SBATCH --time={akrr_walltime_limit}
#SBATCH --output={akrr_task_work_dir}/stdout
#SBATCH --error={akrr_task_work_dir}/stderr
#SBATCH --exclusive
#SBATCH --constraint=CPU-L5520
```
Added the constraint and set partition to be general compute

Okay I had a lot of problems with the whole ssh access thing, came back today and restarted my computer and everything. I set the ssh config to what Nikolay sent and I deleted my public key from the authorized keys on huey, then I added it back after logging out and then logging back in, so now I can ssh huey fine. WHY DID THIS NOT WORK LAST FRIDAY AARRGH

Note: when trying to deploy, make sure the akrr daemon is running
Also make sure mysql daemon is running

```bash
sudo service mariadb start
akrr daemon start
```
Sample output from deployment

```bash
$ akrr resource deploy -r test_huey

[INFO] Validating test_huey parameters from /home/hoffmaps/projects/akrr/etc/resources/test_huey/resource.conf
[INFO] Syntax of /home/hoffmaps/projects/akrr/etc/resources/test_huey/resource.conf is correct and all necessary parameters are present.

[INFO] Validating resource accessibility. Connecting to test_huey.
[INFO] Successfully connected to test_huey


[INFO] Checking if shell is BASH

[INFO] Shell is BASH

[INFO] Checking directory locations

[INFO] Checking: huey:/gpfs/scratch/hoffmaps/network_scratch/akrr_data/test_huey
[INFO] Directory exist and accessible for read/write
[INFO] Checking: huey:/gpfs/scratch/hoffmaps/akrr_project
[INFO] Directory exist and accessible for read/write
[INFO] Checking: huey:/gpfs/scratch/hoffmaps/network_scratch
[INFO] Directory exist and accessible for read/write
[INFO] Checking: huey:/tmp
[INFO] Directory exist and accessible for read/write

[INFO] Preparing to copy application signature calculator,
    app. kernel input files and 
    HPCC, IMB, IOR and Graph500 source code to remote resource

[WARNING] WARNING 1: App. kernel inputs directory /gpfs/scratch/hoffmaps/akrr_project/inputs is present, assume they are correct.

[WARNING] WARNING 2: App. kernel executables directory /gpfs/scratch/hoffmaps/akrr_project/execs is present, assume they are correct.
[WARNING] It should contain HPCC,IMB,IOR and Graph500 source code and app.signature calculator

[INFO] Testing app.signature calculator on headnode

[INFO] App.signature calculator is working on headnode

[INFO] Will send test job to queue, wait till it executed and will analyze the output
[INFO] 
Submitted test job to AKRR, task_id is 3144590



Test status:
Task is in scheduled_tasks queue.
It schedule to be started on 2019-06-17T09:54:22

time: 2019-06-17 09:54:22 

Test status:
Task is in active_tasks queue.
Status: None
Status info:
None

time: 2019-06-17 09:54:32 

Test status:
Task is in active_tasks queue.
Status: Created batch job script and have submitted it to remote queue.
Status info:
Remote job ID is 12429

time: 2019-06-17 09:54:41 

Test status:
Task is in active_tasks queue.
Status: Task was completed successfully.
Status info:
Done

time: 2019-06-17 09:54:47 

Test status:
Task is completed!
        status: 1
        status_info: Done

time: 2019-06-17 09:54:52 


[INFO] Test job is completed analyzing output

[INFO] 
Test kernel execution summary:
status: 1
status_info: Done
processing message:
None
Local working directory for this task: /home/hoffmaps/projects/akrr/log/comptasks/test_huey/test/2019.06.17.09.54.23.257560
Location of some important generated files:
        Batch job script: /home/hoffmaps/projects/akrr/log/comptasks/test_huey/test/2019.06.17.09.54.23.257560/jobfiles/test.job
        Application kernel output: /home/hoffmaps/projects/akrr/log/comptasks/test_huey/test/2019.06.17.09.54.23.257560/jobfiles/appstdout
        Batch job standard output: /home/hoffmaps/projects/akrr/log/comptasks/test_huey/test/2019.06.17.09.54.23.257560/jobfiles/stdout
        Batch job standard error output: /home/hoffmaps/projects/akrr/log/comptasks/test_huey/test/2019.06.17.09.54.23.257560/jobfiles/stderr
        XML processing results: /home/hoffmaps/projects/akrr/log/comptasks/test_huey/test/2019.06.17.09.54.23.257560/result.xml
        Task execution logs: /home/hoffmaps/projects/akrr/log/comptasks/test_huey/test/2019.06.17.09.54.23.257560/proc/log

[INFO] 
The output looks good.

[INFO] 
Adding AKRR enviroment variables to resource's .bashrc!

[INFO] Enabled test_huey in mod_appkernel.resource for tasks execution and made it visible to XDMoD UI.
[INFO] Successfully enabled test_huey

[INFO] Result:
[WARNING] There are 2 warnings.
if warnings have sense you can move to next step!

```
Note: may have to set up the directories on the resource manually, should examine them to make sure they're all good









