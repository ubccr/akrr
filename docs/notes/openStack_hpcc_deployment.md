## Deployment of HPCC benchmark for Openstack

```bash
export RESOURCE=lakeeffect
export APPKER=hpcc

# adding the resource to akrr
akrr app add -a $APPKER -r $RESOURCE

```
Sample output:
```bash
[INFO] Generating application kernel configuration for hpcc on lakeeffect
[INFO] Application kernel configuration for hpcc on lakeeffect is in: 
        /home/hoffmaps/projects/akrr/etc/resources/lakeeffect/hpcc.app.conf
```
So on openStack we don't have to worry about loading up modules and such, we just want to run the dockerfile
So take a look at hpcc.app.conf
```bash
appkernel_run_env_template = """
# Load application environment
module load intel
module load intel-mpi
module load mkl
module list

# make srun works with intel mpi
export I_MPI_PMI_LIBRARY=/usr/lib64/libpmi.so

# set how to run app kernel
RUN_APPKERNEL="srun {appkernel_dir}/{executable}"
"""

```
We really only care about the RUN_APPKERNEL, so everything else can be commented out or removed
```bash
RUN_APPKERNEL="docker run pshoff/akrr_benchmarks:hpcc"
```

Perform validation run - only 1 node
```bash
akrr app validate -n 1 -r $RESOURCE -a $APPKER 
```
So this gave a whole bunch of errors, then gave me errors when handling those errors
I think it could have to do with the whole remote access node? so I gave it a name in the resource.conf for lakeeffect instead of just None, then I re-deployed resource
- Yeah that didn't work
Nikolay suggested a workaround for now, namely to spin up an instance before the ssh happens, then delete it after
	- (see resource_deploy for how to spin up a resource first, about at line 744)
	- The error when doing the validation happens at about line 123 in app_validate.py, so putting the instance spin up thing in right before that

The following code blocks were added:
```python
# (Around line 124 of akrr.app_validate.py)
#### ADDED BY PHILLIP HOFFMANN TO SPIN UP INSTANCE BEFORE SSH        
if resource['batch_scheduler'].lower() == "openstack":
	# Start instance if it is cloud
        openstack_server = akrr.util.openstack.OpenStackServer(resource=resource)
        resource['openstack_server'] = openstack_server
        openstack_server.create()
        resource['remote_access_node'] = openstack_server.ip
#### ADDED BY PHILLIP HOFFMANN

# (Around line 184 of akrr.app_validate.py
#### ADDED BY PHILLIP HOFFMANN TO DELETE OPENSTACK INSTANCE AFTER TESTS
if resource['batch_scheduler'].lower() == "openstack":
        # delete instance if it is cloud
        akrr.util.openstack.OpenStackServer(resource=resource)
        resource['openstack_server'].delete()
        resource['remote_access_node'] = None
#### ADDED BY PHILLIP HOFFMANN



```
Okay that appears to allow us to connect to the resource
Now we are getting errors in terms of connecting to the docker daemon.
For now I'm gonna put this in the config, but might consider putting it in resource.conf file header?
```bash
# put at start of hpcc.app.conf
sudo systemctl start docker
```bash

- Update: okay docker is started now, but the docker hub repo was private so I made it public to see if at least the docker thing works

- Update: it completed successfully, seems we have everything we need, I'll check it all over again tomorrow, but it appears hpcc works
- Yeah everything appears to be working as normal, no weird things other than a logging error, but I don't think that really affects anything

- UPDATE: Editing the place that calls the docker run to remove container on exit, so the hpcc.app.conf is now this:
```bash
appkernel_run_env_template = """
sudo systemctl start docker

# set how to run app kernel
RUN_APPKERNEL="docker run --rm pshoff/akrr_benchmarks:hpcc"
"""
```





