### Notes on originally messing around and seeing how it works

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



