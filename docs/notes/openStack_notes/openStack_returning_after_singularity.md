## So coming back to this after working with singularity for a while
Just wanted to check if all the docker things were working as expected...
And of course they weren't.
No clue exactly what's going on, it seems its not even submitting the jobs and running the docker (well it did it once at the beginning for gamess, but thats it)

Looking at debug output when trying to do a validation run, it keeps printing stuff like this
```bash
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144789 HTTP/1.1" 200 338
time: 2019-07-01 11:29:20 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144789 HTTP/1.1" 404 152
```
When I ^C to stop the seemingly infinite loop, it comes back as such
```bash
  File "/home/hoffmaps/projects/akrr/bin/akrr", line 65, in <module>
    akrr.cli.CLI().run()
  File "/home/hoffmaps/projects/akrr/akrr/cli/__init__.py", line 154, in run
    return cli_args.func(cli_args)
  File "/home/hoffmaps/projects/akrr/akrr/cli/commands.py", line 369, in handler
    app_validate(args.resource, args.appkernel, int(args.nodes))
  File "/home/hoffmaps/projects/akrr/akrr/app_validate.py", line 316, in app_validate
    time.sleep(5)
```
So maybe there's something going on with that function somehow?
Anyways, I'll try setting up the whole openstack thing from the beginning, because honestly I'm not sure what else to do other than start fresh. I feel like I can't really debug it, since there's no error to follow through.
So, here we go

```bash
# just started with openstack cli, which seems to be working
source lakeeffect-xdmod-openrc.sh
openstack flavor list
openstack image list

# trying to spin-off instance
openstack server create --flavor c8.m16 --volume dockervolume --network lakeeffect-199.109.195 --security-group default --security-group SSH --key-name openstack-testing test_create_from_cl

# try to ssh into it
ssh -i openstack-testing.key centos@[ip address]
```
All that seems to be working as expected, I can make the instance and ssh into it

Now I'll try and add a new resource

```bash
[hoffmaps@dhcp-128-205-70-4 lakeeffect]$ akrr resource add --minimalistic
[INFO] Beginning Initiation of New Resource...
[INFO] Retrieving Resources from XDMoD Database...
[INFO] Found following resources from XDMoD Database:
    resource_id  name


[INPUT]: Enter AKRR resource name:
open-lakeeffect-stack

[INPUT]: Enter queuing system on resource (slurm, pbs or openstack): 
openstack

[INFO] Initiating open-lakeeffect-stack at AKRR
[INFO] Resource configuration is in /home/hoffmaps/projects/akrr/etc/resources/open-lakeeffect-stack/resource.conf
[INFO] Initiation of new resource is completed.
    Edit batch_job_header_template variable in /home/hoffmaps/projects/akrr/etc/resources/open-lakeeffect-stack/resource.conf
    and move to resource validation and deployment step.
    i.e. execute:
        akrr resource deploy -r open-lakeeffect-stack
```
Copy over the environment setter thing (I took it from old lakeeffect directory)
```bash
cd open-lakeeffect-stack
cp ../lakeeffect/lakeeffect-benchmarks-openrc.sh ./

```
Changed the resource config to have all the proper declarations: here is what mine looks like
```bash
# Resource parameters

# Processors (cores) per node
ppn = 8

# head node for remote access
remote_access_node = None
# Remote access method to the resource (default ssh)
remote_access_method = "ssh"
# Remote copy method to the resource (default scp)
remote_copy_method = "scp"

# Access authentication
ssh_username = "centos"
ssh_password = None
ssh_private_key_file = "/home/hoffmaps/projects/openstack/keypairs/openstack-testing.key"
ssh_private_key_password = None

# Scratch visible across all nodes (absolute path or/and shell environment variable)
network_scratch = "/home/centos/appker/network_scratch"
# Local scratch only locally visible (absolute path or/and shell environment variable)
local_scratch = "/home/centos/appker/network_scratch"
# Locations for app. kernels working directories (can or even should be on scratch space)
akrr_data = "/home/centos/appker/akrr_data"
# Location of executables and input for app. kernels
appkernel_dir = "/home/centos/appker/resource"

# batch options
batch_scheduler = "openstack"

# job script header
batch_job_header_template = """#!/bin/bash
"""

openstack_env_set_script = "openstack_env_set.sh"
openstack_flavor = "c8.m16"
openstack_volume = "dockervolume"
openstack_network = "lakeeffect-199.109.195"
openstack_security_group = ["default", "SSH"]
openstack_key_name = "openstack-testing"
openstack_server_name = "akrrtest"
openstack_floating_ip_attach = None

# due to current implementation (only one volume)
# the limit is 1 active task
max_number_of_active_tasks = 1


```
(Changed the openstack settings to be okay and all that)
Now I try and deploy

```bash
[hoffmaps@dhcp-128-205-70-4 open-lakeeffect-stack]$ akrr -v resource deploy -r open-lakeeffect-stack
[DEBUG] In-source installation, AKRR configuration is in /home/hoffmaps/projects/akrr/etc/akrr.conf
[INFO] Validating open-lakeeffect-stack parameters from /home/hoffmaps/projects/akrr/etc/resources/open-lakeeffect-stack/resource.conf
[INFO] Syntax of /home/hoffmaps/projects/akrr/etc/resources/open-lakeeffect-stack/resource.conf is correct and all necessary parameters are present.

Start Session
[DEBUG] which_openstack_env_set_script: /home/hoffmaps/projects/akrr/etc/resources/open-lakeeffect-stack/lakeeffect-benchmarks-openrc.sh
[DEBUG] source /home/hoffmaps/projects/akrr/etc/resources/open-lakeeffect-stack/lakeeffect-benchmarks-openrc.sh

[DEBUG] echo $OS_TOKEN
gAAAAABdGiuUncrc_kHhNNfuvasOBm_J1HicFYdMqBPZ1bqsLzGQIFt-dck1nL-mWw3ruQSoI0wclHr7egH3Sn7S-SihCKtY2Fc_lImWCgWZ1ukyS-aAHFm3AbVC7unVrapFH7cKmfOXkznE4Ozels3d2657ORT2FQiLE1ZVGcW9Kp13TVkezSl-neoHIMGggDU7sUIB0jpDwMJ-gg1pUfpR3b-L9zLCnQ

[DEBUG] server list -f json --name akrrtest
[]

[DEBUG] server create --flavor c8.m16 --volume dockervolume --network lakeeffect-199.109.195 --key-name openstack-testing --security-group default --security-group SSH akrrtest
+-----------------------------+---------------------------------------------+
| Field                       | Value                                       |
+-----------------------------+---------------------------------------------+
| OS-DCF:diskConfig           | MANUAL                                      |
| OS-EXT-AZ:availability_zone | cbls                                        |
| OS-EXT-STS:power_state      | NOSTATE                                     |
| OS-EXT-STS:task_state       | scheduling                                  |
| OS-EXT-STS:vm_state         | building                                    |
| OS-SRV-USG:launched_at      | None                                        |
| OS-SRV-USG:terminated_at    | None                                        |
| accessIPv4                  |                                             |
| accessIPv6                  |                                             |
| addresses                   |                                             |
| adminPass                   | b5pb5BymtDq3                                |
| config_drive                |                                             |
| created                     | 2019-07-01T15:49:47Z                        |
| flavor                      | c8.m16 (108016)                             |
| hostId                      |                                             |
| id                          | 0c6fcd6b-0f7f-428c-a2f5-440f2daa85ad        |
| image                       |                                             |
| key_name                    | openstack-testing                           |
| name                        | akrrtest                                    |
| progress                    | 0                                           |
| project_id                  | ef13fb8fc7aa4e9c9ecf62b08bed097a            |
| properties                  |                                             |
| security_groups             | name='a40ecec6-29fb-4734-84bf-c45cbfa495e5' |
|                             | name='b8b98905-b40d-4a44-82fa-dac23a1491ec' |
| status                      | BUILD                                       |
| updated                     | 2019-07-01T15:49:47Z                        |
| user_id                     | cacbdcada640409480ea65cc804b3f32            |
| volumes_attached            |                                             |
+-----------------------------+---------------------------------------------+

[DEBUG] server list -f json --name akrrtest
[
  {
    "ID": "0c6fcd6b-0f7f-428c-a2f5-440f2daa85ad",
    "Name": "akrrtest",
    "Status": "BUILD",
    "Networks": "",
    "Image": "",
    "Flavor": "c8.m16"
  }
]

{'ID': '0c6fcd6b-0f7f-428c-a2f5-440f2daa85ad', 'Name': 'akrrtest', 'Status': 'BUILD', 'Networks': '', 'Image': '', 'Flavor': 'c8.m16'}
[DEBUG] server list -f json --name akrrtest
[
  {
    "ID": "0c6fcd6b-0f7f-428c-a2f5-440f2daa85ad",
    "Name": "akrrtest",
    "Status": "BUILD",
    "Networks": "",
    "Image": "",
    "Flavor": "c8.m16"
  }
]

[DEBUG] server list -f json --name akrrtest
[
  {
    "ID": "0c6fcd6b-0f7f-428c-a2f5-440f2daa85ad",
    "Name": "akrrtest",
    "Status": "ACTIVE",
    "Networks": "lakeeffect-199.109.195=199.109.192.9",
    "Image": "",
    "Flavor": "c8.m16"
  }
]

[DEBUG] internal_network_ip:199.109.192.9
[DEBUG] ssh-keygen -R 199.109.192.9
Host 199.109.192.9 not found in /home/hoffmaps/.ssh/known_hosts

[DEBUG] ssh -i /home/hoffmaps/projects/openstack/keypairs/openstack-testing.key centos@199.109.192.9 "echo StArTEd_ExeCUTEtIoM_SucCeSsFully;uname -a;echo ExeCUTEd_SucCeSsFully"
ssh: connect to host 199.109.192.9 port 22: Connection refused
[DEBUG] ssh -i /home/hoffmaps/projects/openstack/keypairs/openstack-testing.key centos@199.109.192.9 "echo StArTEd_ExeCUTEtIoM_SucCeSsFully;uname -a;echo ExeCUTEd_SucCeSsFully"
ssh: connect to host 199.109.192.9 port 22: Connection refused
[DEBUG] ssh -i /home/hoffmaps/projects/openstack/keypairs/openstack-testing.key centos@199.109.192.9 "echo StArTEd_ExeCUTEtIoM_SucCeSsFully;uname -a;echo ExeCUTEd_SucCeSsFully"
The authenticity of host '199.109.192.9 (199.109.192.9)' can't be established.
ECDSA key fingerprint is SHA256:sKS3lvcUESnozREfu7n0/8K3vOAWZqAo+U2zh+F7NWA.
ECDSA key fingerprint is MD5:5c:f8:a9:c6:e3:36:7b:27:81:de:57:13:cb:bb:b6:ee.
Are you sure you want to continue connecting (yes/no)? yes
Warning: Permanently added '199.109.192.9' (ECDSA) to the list of known hosts.
StArTEd_ExeCUTEtIoM_SucCeSsFully
Linux akrrtest.novalocal 3.10.0-862.14.4.el7.x86_64 #1 SMP Wed Sep 26 15:12:11 UTC 2018 x86_64 x86_64 x86_64 GNU/Linux
ExeCUTEd_SucCeSsFully
[INFO] Validating resource accessibility. Connecting to open-lakeeffect-stack.
[DEBUG] ssh -i /home/hoffmaps/projects/openstack/keypairs/openstack-testing.key centos@199.109.192.9
[INFO] Successfully connected to open-lakeeffect-stack


[INFO] Checking if shell is BASH

[INFO] Shell is BASH

[INFO] Checking directory locations

[INFO] Checking: 199.109.192.9:/home/centos/appker/akrr_data
[INFO] Directory exist and accessible for read/write
[INFO] Checking: 199.109.192.9:/home/centos/appker/resource
[INFO] Directory exist and accessible for read/write
[INFO] Checking: 199.109.192.9:/home/centos/appker/network_scratch
[INFO] Directory exist and accessible for read/write
[INFO] Checking: 199.109.192.9:/home/centos/appker/network_scratch
[INFO] Directory exist and accessible for read/write

[INFO] Preparing to copy application signature calculator,
    app. kernel input files and 
    HPCC, IMB, IOR and Graph500 source code to remote resource

[WARNING] WARNING 1: App. kernel inputs directory /home/centos/appker/resource/inputs is present, assume they are correct.

[WARNING] WARNING 2: App. kernel executables directory /home/centos/appker/resource/execs is present, assume they are correct.
[WARNING] It should contain HPCC,IMB,IOR and Graph500 source code and app.signature calculator

[INFO] Testing app.signature calculator on headnode

[INFO] App.signature calculator is working on headnode

Start Session
[DEBUG] which_openstack_env_set_script: /home/hoffmaps/projects/akrr/etc/resources/open-lakeeffect-stack/lakeeffect-benchmarks-openrc.sh
[DEBUG] source /home/hoffmaps/projects/akrr/etc/resources/open-lakeeffect-stack/lakeeffect-benchmarks-openrc.sh

[DEBUG] echo $OS_TOKEN
gAAAAABdGivSQlwSY2u4idj8_nUmyB-H9-uuv_cVjIjh8Ajkju3K33KQOCLXxC-zoVVMJFG_aROuMV2PNL1lq1zuoW7m-KdIrf8_WvJfTjiTuwhLCy1_mIjufsGMGigCvGgRllZRyVcrsJDe2wYMqDLtRHqGgCXz1HKifEVsKjXA5mPiHvH_6ZJbcAmWYb35XfyOtflG-4nC2KVHqV1-xzHgtMiqTOTtXQ

[DEBUG] token revoke gAAAAABdGivSQlwSY2u4idj8_nUmyB-H9-uuv_cVjIjh8Ajkju3K33KQOCLXxC-zoVVMJFG_aROuMV2PNL1lq1zuoW7m-KdIrf8_WvJfTjiTuwhLCy1_mIjufsGMGigCvGgRllZRyVcrsJDe2wYMqDLtRHqGgCXz1HKifEVsKjXA5mPiHvH_6ZJbcAmWYb35XfyOtflG-4nC2KVHqV1-xzHgtMiqTOTtXQ

[DEBUG] server list -f json --name akrrtest
[
  {
    "ID": "0c6fcd6b-0f7f-428c-a2f5-440f2daa85ad",
    "Name": "akrrtest",
    "Status": "ACTIVE",
    "Networks": "lakeeffect-199.109.195=199.109.192.9",
    "Image": "",
    "Flavor": "c8.m16"
  }
]

[DEBUG] server delete akrrtest

[DEBUG] server list -f json --name akrrtest
[]

[INFO] Will send test job to queue, wait till it executed and will analyze the output
[DEBUG] Will use AKRR REST API at https://localhost:8091/api/v1
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/scheduled_tasks HTTP/1.1" 401 140
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/token HTTP/1.1" 200 94
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/scheduled_tasks HTTP/1.1" 200 5981
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "POST /api/v1/scheduled_tasks HTTP/1.1" 200 137
[INFO] 
Submitted test job to AKRR, task_id is 3144790

[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144790 HTTP/1.1" 200 349


Test status:
Task is in scheduled_tasks queue.
It schedule to be started on 2019-07-01T11:50:51

time: 2019-07-01 11:50:51 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144790 HTTP/1.1" 404 152
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144790 HTTP/1.1" 400 265
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144790 HTTP/1.1" 200 107
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144790 HTTP/1.1" 200 706


Test status:
Task is in active_tasks queue.
Status: None
Status info:
None

time: 2019-07-01 11:51:01 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144790 HTTP/1.1" 200 107
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144790 HTTP/1.1" 200 10203


Test status:
Task is in active_tasks queue.
Status: Created batch job script and have submitted it to remote queue.
Status info:
Remote job ID is 1487

time: 2019-07-01 11:51:41 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144790 HTTP/1.1" 200 107
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144790 HTTP/1.1" 200 12296


Test status:
Task is in active_tasks queue.
Status: Not in queue. Either exited with error or executed successfully. Copied all files to local machine. Deleted all files from remote machine
Status info:
Not in queue. Either exited with error or executed successfully. Copied all files to local machine. Deleted all files from remote machine

time: 2019-07-01 11:51:46 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144790 HTTP/1.1" 200 107
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144790 HTTP/1.1" 200 12058


Test status:
Task is in active_tasks queue.
Status: Task was completed successfully.
Status info:
Done

time: 2019-07-01 11:51:51 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144790 HTTP/1.1" 200 107
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144790 HTTP/1.1" 200 12060
time: 2019-07-01 11:51:56 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144790 HTTP/1.1" 404 152
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144790 HTTP/1.1" 200 15186


Test status:
Task is completed!
completed_tasks table entry:
{   'app': 'test',
    'app_param': '{}',
    'datetime_stamp': '2019.07.01.11.50.51.588624',
    'fails_to_submit_to_the_queue': 0,
    'fatal_errors_count': 0,
    'group_id': '',
    'parent_task_id': 3144790,
    'repeat_in': None,
    'resource': 'open-lakeeffect-stack',
    'resource_param': "{'nnodes':2}",
    'status': 'Done',
    'status_info': 'Done',
    'task_id': 3144790,
    'task_param': "{'test_run':True}",
    'time_activated': '2019-07-01T11:50:51',
    'time_finished': '2019-07-01T11:51:49',
    'time_submitted_to_queue': '2019-07-01T11:51:40',
    'time_to_start': '2019-07-01T11:50:51'}
akrr_xdmod_instanceinfo table entry:
{   'body': '<performance>\n'
            '    <ID>test</ID>\n'
            '    <benchmark>\n'
            '        <ID>test</ID>\n'
            '        <parameters>\n'
            '            <parameter>\n'
            '                <ID>App:ExeBinSignature</ID>\n'
            '                '
            '<value>H4sIABIsGl0CAxXLMQ7DIAwF0J1TcIJggwHTuWsOYfiJFClppaLcv8rytre+88vHWFhBxMmgFR0jMlqSbsmkSfPhnr/Qj0+4kOd9ufVZNdlWWxNSbCjEhAo2BXI2HTv7cB69yONY5ncpzv0B6DAU+G4AAAA=</value>\n'
            '            </parameter>\n'
            '            <parameter>\n'
            '                <ID>RunEnv:Nodes</ID>\n'
            '                '
            '<value>H4sIABIsGl0CA8vJT07MycgvLuECAOm1LpAKAAAA</value>\n'
            '            </parameter>\n'
            '            <parameter>\n'
            '                <ID>app</ID>\n'
            '                <value>test</value>\n'
            '            </parameter>\n'
            '            <parameter>\n'
            '                <ID>resource</ID>\n'
            '                <value>open-lakeeffect-stack</value>\n'
            '            </parameter>\n'
            '        </parameters>\n'
            '        <statistics>\n'
            '            <statistic>\n'
            '                <ID>App kernel executable exists</ID>\n'
            '                <value>1</value>\n'
            '            </statistic>\n'
            '            <statistic>\n'
            '                <ID>App kernel input exists</ID>\n'
            '                <value>1</value>\n'
            '            </statistic>\n'
            '            <statistic>\n'
            '                <ID>Network scratch directory accessible</ID>\n'
            '                <value>1</value>\n'
            '            </statistic>\n'
            '            <statistic>\n'
            '                <ID>Network scratch directory exists</ID>\n'
            '                <value>1</value>\n'
            '            </statistic>\n'
            '            <statistic>\n'
            '                <ID>Shell is BASH</ID>\n'
            '                <value>1</value>\n'
            '            </statistic>\n'
            '            <statistic>\n'
            '                <ID>Task working directory accessible</ID>\n'
            '                <value>1</value>\n'
            '            </statistic>\n'
            '            <statistic>\n'
            '                <ID>Task working directory exists</ID>\n'
            '                <value>1</value>\n'
            '            </statistic>\n'
            '            <statistic>\n'
            '                <ID>Wall Clock Time</ID>\n'
            '                <value>1.0</value>\n'
            '                <units>Second</units>\n'
            '            </statistic>\n'
            '            <statistic>\n'
            '                <ID>local scratch directory accessible</ID>\n'
            '                <value>1</value>\n'
            '            </statistic>\n'
            '            <statistic>\n'
            '                <ID>local scratch directory exists</ID>\n'
            '                <value>1</value>\n'
            '            </statistic>\n'
            '        </statistics>\n'
            '    </benchmark>\n'
            '</performance>\n',
    'collected': '2019-07-01T11:51:43',
    'committed': '2019-07-01T11:51:49',
    'cputime': 0.0,
    'executionhost': 'open-lakeeffect-stack',
    'instance_id': 3144790,
    'internal_failure': 0,
    'job_id': 1487,
    'memory': 0.0,
    'message': None,
    'ncores': None,
    'nnodes': None,
    'nodes': ';localhost;',
    'reporter': 'test',
    'reporternickname': 'test.2',
    'resource': 'open-lakeeffect-stack',
    'status': 1,
    'stderr': None,
    'walltime': 1.0}
output parsing results:
<performance>
    <ID>test</ID>
    <benchmark>
        <ID>test</ID>
        <parameters>
            <parameter>
                <ID>App:ExeBinSignature</ID>
                <value>H4sIABIsGl0CAxXLMQ7DIAwF0J1TcIJggwHTuWsOYfiJFClppaLcv8rytre+88vHWFhBxMmgFR0jMlqSbsmkSfPhnr/Qj0+4kOd9ufVZNdlWWxNSbCjEhAo2BXI2HTv7cB69yONY5ncpzv0B6DAU+G4AAAA=</value>
            </parameter>
            <parameter>
                <ID>RunEnv:Nodes</ID>
                <value>H4sIABIsGl0CA8vJT07MycgvLuECAOm1LpAKAAAA</value>
            </parameter>
            <parameter>
                <ID>app</ID>
                <value>test</value>
            </parameter>
            <parameter>
                <ID>resource</ID>
                <value>open-lakeeffect-stack</value>
            </parameter>
        </parameters>
        <statistics>
            <statistic>
                <ID>App kernel executable exists</ID>
                <value>1</value>
            </statistic>
            <statistic>
                <ID>App kernel input exists</ID>
                <value>1</value>
            </statistic>
            <statistic>
                <ID>Network scratch directory accessible</ID>
                <value>1</value>
            </statistic>
            <statistic>
                <ID>Network scratch directory exists</ID>
                <value>1</value>
            </statistic>
            <statistic>
                <ID>Shell is BASH</ID>
                <value>1</value>
            </statistic>
            <statistic>
                <ID>Task working directory accessible</ID>
                <value>1</value>
            </statistic>
            <statistic>
                <ID>Task working directory exists</ID>
                <value>1</value>
            </statistic>
            <statistic>
                <ID>Wall Clock Time</ID>
                <value>1.0</value>
                <units>Second</units>
            </statistic>
            <statistic>
                <ID>local scratch directory accessible</ID>
                <value>1</value>
            </statistic>
            <statistic>
                <ID>local scratch directory exists</ID>
                <value>1</value>
            </statistic>
        </statistics>
    </benchmark>
</performance>


time: 2019-07-01 11:52:09 


[INFO] Test job is completed analyzing output

[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144790 HTTP/1.1" 200 15186
[INFO] 
Test kernel execution summary:
status: 1
status_info: Done
processing message:
None
Local working directory for this task: /home/hoffmaps/projects/akrr/log/comptasks/open-lakeeffect-stack/test/2019.07.01.11.50.51.588624
Location of some important generated files:
        Batch job script: /home/hoffmaps/projects/akrr/log/comptasks/open-lakeeffect-stack/test/2019.07.01.11.50.51.588624/jobfiles/test.job
        Application kernel output: /home/hoffmaps/projects/akrr/log/comptasks/open-lakeeffect-stack/test/2019.07.01.11.50.51.588624/jobfiles/appstdout
        Batch job standard output: /home/hoffmaps/projects/akrr/log/comptasks/open-lakeeffect-stack/test/2019.07.01.11.50.51.588624/jobfiles/stdout
        Batch job standard error output: /home/hoffmaps/projects/akrr/log/comptasks/open-lakeeffect-stack/test/2019.07.01.11.50.51.588624/jobfiles/stderr
        XML processing results: /home/hoffmaps/projects/akrr/log/comptasks/open-lakeeffect-stack/test/2019.07.01.11.50.51.588624/result.xml
        Task execution logs: /home/hoffmaps/projects/akrr/log/comptasks/open-lakeeffect-stack/test/2019.07.01.11.50.51.588624/proc/log

[INFO] 
The output looks good.
Start Session
[DEBUG] which_openstack_env_set_script: /home/hoffmaps/projects/akrr/etc/resources/open-lakeeffect-stack/lakeeffect-benchmarks-openrc.sh
[DEBUG] source /home/hoffmaps/projects/akrr/etc/resources/open-lakeeffect-stack/lakeeffect-benchmarks-openrc.sh

[DEBUG] echo $OS_TOKEN
gAAAAABdGiwrm8BG-o5VBt6psoVPiVCs0Eoso446xjpaqaqDbXQOrUS3X81AhdMwl_e3yFwPbOAfA_hDDueS5EQf5cGBwo9lIzWgXVh-yWm46D-zSU8y-jsC-Gtm-3JEhvnaatsB5SdnZQ3PqtTffnGgxPkQyxthqc6P3P3wMulNjEBk-u6ZX4bfoJnSe-0Kvn0-TECzhfhRmbUFGDvptOHRETPE2AkT9A

[DEBUG] token revoke gAAAAABdGiuUncrc_kHhNNfuvasOBm_J1HicFYdMqBPZ1bqsLzGQIFt-dck1nL-mWw3ruQSoI0wclHr7egH3Sn7S-SihCKtY2Fc_lImWCgWZ1ukyS-aAHFm3AbVC7unVrapFH7cKmfOXkznE4Ozels3d2657ORT2FQiLE1ZVGcW9Kp13TVkezSl-neoHIMGggDU7sUIB0jpDwMJ-gg1pUfpR3b-L9zLCnQ

[DEBUG] server list -f json --name akrrtest
[]

[DEBUG] server create --flavor c8.m16 --volume dockervolume --network lakeeffect-199.109.195 --key-name openstack-testing --security-group default --security-group SSH akrrtest
+-----------------------------+---------------------------------------------+
| Field                       | Value                                       |
+-----------------------------+---------------------------------------------+
| OS-DCF:diskConfig           | MANUAL                                      |
| OS-EXT-AZ:availability_zone | cbls                                        |
| OS-EXT-STS:power_state      | NOSTATE                                     |
| OS-EXT-STS:task_state       | scheduling                                  |
| OS-EXT-STS:vm_state         | building                                    |
| OS-SRV-USG:launched_at      | None                                        |
| OS-SRV-USG:terminated_at    | None                                        |
| accessIPv4                  |                                             |
| accessIPv6                  |                                             |
| addresses                   |                                             |
| adminPass                   | 355pZw3SJPtX                                |
| config_drive                |                                             |
| created                     | 2019-07-01T15:52:19Z                        |
| flavor                      | c8.m16 (108016)                             |
| hostId                      |                                             |
| id                          | b347b031-f292-49b3-bc08-e797b3619057        |
| image                       |                                             |
| key_name                    | openstack-testing                           |
| name                        | akrrtest                                    |
| progress                    | 0                                           |
| project_id                  | ef13fb8fc7aa4e9c9ecf62b08bed097a            |
| properties                  |                                             |
| security_groups             | name='a40ecec6-29fb-4734-84bf-c45cbfa495e5' |
|                             | name='b8b98905-b40d-4a44-82fa-dac23a1491ec' |
| status                      | BUILD                                       |
| updated                     | 2019-07-01T15:52:19Z                        |
| user_id                     | cacbdcada640409480ea65cc804b3f32            |
| volumes_attached            |                                             |
+-----------------------------+---------------------------------------------+

[DEBUG] server list -f json --name akrrtest
[
  {
    "ID": "b347b031-f292-49b3-bc08-e797b3619057",
    "Name": "akrrtest",
    "Status": "BUILD",
    "Networks": "",
    "Image": "",
    "Flavor": "c8.m16"
  }
]

{'ID': 'b347b031-f292-49b3-bc08-e797b3619057', 'Name': 'akrrtest', 'Status': 'BUILD', 'Networks': '', 'Image': '', 'Flavor': 'c8.m16'}
[DEBUG] server list -f json --name akrrtest
[
  {
    "ID": "b347b031-f292-49b3-bc08-e797b3619057",
    "Name": "akrrtest",
    "Status": "BUILD",
    "Networks": "",
    "Image": "",
    "Flavor": "c8.m16"
  }
]

[DEBUG] server list -f json --name akrrtest
[
  {
    "ID": "b347b031-f292-49b3-bc08-e797b3619057",
    "Name": "akrrtest",
    "Status": "ACTIVE",
    "Networks": "lakeeffect-199.109.195=199.109.192.3",
    "Image": "",
    "Flavor": "c8.m16"
  }
]

[DEBUG] internal_network_ip:199.109.192.3
[DEBUG] ssh-keygen -R 199.109.192.3
Host 199.109.192.3 not found in /home/hoffmaps/.ssh/known_hosts

[DEBUG] ssh -i /home/hoffmaps/projects/openstack/keypairs/openstack-testing.key centos@199.109.192.3 "echo StArTEd_ExeCUTEtIoM_SucCeSsFully;uname -a;echo ExeCUTEd_SucCeSsFully"
ssh: connect to host 199.109.192.3 port 22: Connection refused
[DEBUG] ssh -i /home/hoffmaps/projects/openstack/keypairs/openstack-testing.key centos@199.109.192.3 "echo StArTEd_ExeCUTEtIoM_SucCeSsFully;uname -a;echo ExeCUTEd_SucCeSsFully"
ssh: connect to host 199.109.192.3 port 22: Connection refused
[DEBUG] ssh -i /home/hoffmaps/projects/openstack/keypairs/openstack-testing.key centos@199.109.192.3 "echo StArTEd_ExeCUTEtIoM_SucCeSsFully;uname -a;echo ExeCUTEd_SucCeSsFully"
The authenticity of host '199.109.192.3 (199.109.192.3)' can't be established.
ECDSA key fingerprint is SHA256:sKS3lvcUESnozREfu7n0/8K3vOAWZqAo+U2zh+F7NWA.
ECDSA key fingerprint is MD5:5c:f8:a9:c6:e3:36:7b:27:81:de:57:13:cb:bb:b6:ee.
Are you sure you want to continue connecting (yes/no)? yes
Warning: Permanently added '199.109.192.3' (ECDSA) to the list of known hosts.
StArTEd_ExeCUTEtIoM_SucCeSsFully
Linux akrrtest.novalocal 3.10.0-862.14.4.el7.x86_64 #1 SMP Wed Sep 26 15:12:11 UTC 2018 x86_64 x86_64 x86_64 GNU/Linux
ExeCUTEd_SucCeSsFully
[INFO] 
Adding AKRR enviroment variables to resource's .bashrc!

[DEBUG] ssh -i /home/hoffmaps/projects/openstack/keypairs/openstack-testing.key centos@199.109.192.3
[DEBUG] 
[DEBUG] Appending AKRR records to /home/centos/.bashrc

[DEBUG] 
[DEBUG] 
[DEBUG] 
[DEBUG] 
[DEBUG] 
[DEBUG] 
[DEBUG] Appending AKRR records to /home/centos/.bashrc

[INFO] Enabled open-lakeeffect-stack in mod_appkernel.resource for tasks execution and made it visible to XDMoD UI.
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/resources/open-lakeeffect-stack/on HTTP/1.1" 200 63
[INFO] Successfully enabled open-lakeeffect-stack
Start Session
[DEBUG] which_openstack_env_set_script: /home/hoffmaps/projects/akrr/etc/resources/open-lakeeffect-stack/lakeeffect-benchmarks-openrc.sh
[DEBUG] source /home/hoffmaps/projects/akrr/etc/resources/open-lakeeffect-stack/lakeeffect-benchmarks-openrc.sh

[DEBUG] echo $OS_TOKEN
gAAAAABdGixq18rdO1QBRa5X-oDWC3WCrsqIfQJCPkEWD5VtXHYYd_LOH8ZtI9be7H8G8yqIHYKJf1Gqs3UvbKkUx_WoyQKtMH9sVD3VRXXc68EYc80ruf4CuzWc_adOBFajcAGs-lnroBKzNxs2-BoVZLC002L0b4HwmmbNWBU8KOqq_aiWT4dpp4GDnVJBGvK2ZZvUCqK5LQeKWUEM8xVblHA2WLSBTw

[DEBUG] token revoke gAAAAABdGixq18rdO1QBRa5X-oDWC3WCrsqIfQJCPkEWD5VtXHYYd_LOH8ZtI9be7H8G8yqIHYKJf1Gqs3UvbKkUx_WoyQKtMH9sVD3VRXXc68EYc80ruf4CuzWc_adOBFajcAGs-lnroBKzNxs2-BoVZLC002L0b4HwmmbNWBU8KOqq_aiWT4dpp4GDnVJBGvK2ZZvUCqK5LQeKWUEM8xVblHA2WLSBTw

[DEBUG] server list -f json --name akrrtest
[
  {
    "ID": "b347b031-f292-49b3-bc08-e797b3619057",
    "Name": "akrrtest",
    "Status": "ACTIVE",
    "Networks": "lakeeffect-199.109.195=199.109.192.3",
    "Image": "",
    "Flavor": "c8.m16"
  }
]

[DEBUG] server delete akrrtest

[DEBUG] server list -f json --name akrrtest
[]


[INFO] Result:
[WARNING] There are 2 warnings.
if warnings have sense you can move to next step!

[DEBUG] token revoke gAAAAABdGiwrm8BG-o5VBt6psoVPiVCs0Eoso446xjpaqaqDbXQOrUS3X81AhdMwl_e3yFwPbOAfA_hDDueS5EQf5cGBwo9lIzWgXVh-yWm46D-zSU8y-jsC-Gtm-3JEhvnaatsB5SdnZQ3PqtTffnGgxPkQyxthqc6P3P3wMulNjEBk-u6ZX4bfoJnSe-0Kvn0-TECzhfhRmbUFGDvptOHRETPE2AkT9A
```

So it appears deployment went okay. We didn't get the infinite loop with the https things

Now, lets try and deploy something
```bash
akrr app add -r open-lakeeffect-stack -a hpcg

```
We want to edit the config to use the docker image (so new one is below):
```bash
appkernel_run_env_template = """
sudo systemctl start docker
docker pull pshoff/akrr_benchmarks:hpcg
RUN_APPKERNEL="docker run --rm pshoff/akrr_benchmarks:hpcg"
"""
```
Then we can try the validation
```bash
[hoffmaps@dhcp-128-205-70-4 open-lakeeffect-stack]$ akrr -v app validate -n 1 -r open-lakeeffect-stack -a hpcg
[INFO] Validating hpcg application kernel installation on open-lakeeffect-stack
[DEBUG] In-source installation, AKRR configuration is in /home/hoffmaps/projects/akrr/etc/akrr.conf
[INFO] ################################################################################
[INFO] Validating open-lakeeffect-stack parameters from /home/hoffmaps/projects/akrr/etc/resources/open-lakeeffect-stack/resource.conf
[DEBUG] In-source installation, AKRR configuration is in /home/hoffmaps/projects/akrr/etc/akrr.conf
[INFO] Syntax of /home/hoffmaps/projects/akrr/etc/resources/open-lakeeffect-stack/resource.conf is correct and all necessary parameters are present.
[INFO] Syntax of /home/hoffmaps/projects/akrr/akrr/default_conf/hpcg.app.conf is correct and all necessary parameters are present.
[INFO] ################################################################################
[INFO] Validating resource accessibility. Connecting to open-lakeeffect-stack.
[DEBUG] which_openstack_env_set_script: /home/hoffmaps/projects/akrr/etc/resources/open-lakeeffect-stack/lakeeffect-benchmarks-openrc.sh
[DEBUG] source /home/hoffmaps/projects/akrr/etc/resources/open-lakeeffect-stack/lakeeffect-benchmarks-openrc.sh

[DEBUG] echo $OS_TOKEN
gAAAAABdGi3ZHlC8fNxvtWzXgWErQSsy28YOp2KByaDj2y7x0M6qGvr0xerRpeEEakfNkLdDW_ZkcY-ksDbi4a0t7SitNmlJyJ6dsBZkrYJBot2YghZn8iVod0U2FNfy2Z3CThkvxJEqrQUL1nZwrXCQ7WHrEab2Fdopp0bHHKwaSE1ZSAMgx74Kbueox7Up7T-2jWGpraWehBt9C4Diaf_Vb7TK1ClMEQ

[DEBUG] server list -f json --name akrrtest
[]

[DEBUG] server create --flavor c8.m16 --volume dockervolume --network lakeeffect-199.109.195 --key-name openstack-testing --security-group default --security-group SSH akrrtest
+-----------------------------+---------------------------------------------+
| Field                       | Value                                       |
+-----------------------------+---------------------------------------------+
| OS-DCF:diskConfig           | MANUAL                                      |
| OS-EXT-AZ:availability_zone | cbls                                        |
| OS-EXT-STS:power_state      | NOSTATE                                     |
| OS-EXT-STS:task_state       | scheduling                                  |
| OS-EXT-STS:vm_state         | building                                    |
| OS-SRV-USG:launched_at      | None                                        |
| OS-SRV-USG:terminated_at    | None                                        |
| accessIPv4                  |                                             |
| accessIPv6                  |                                             |
| addresses                   |                                             |
| adminPass                   | 353dDtgRYizD                                |
| config_drive                |                                             |
| created                     | 2019-07-01T15:59:27Z                        |
| flavor                      | c8.m16 (108016)                             |
| hostId                      |                                             |
| id                          | b026c94b-df67-48e1-bbe9-fa0739653a92        |
| image                       |                                             |
| key_name                    | openstack-testing                           |
| name                        | akrrtest                                    |
| progress                    | 0                                           |
| project_id                  | ef13fb8fc7aa4e9c9ecf62b08bed097a            |
| properties                  |                                             |
| security_groups             | name='a40ecec6-29fb-4734-84bf-c45cbfa495e5' |
|                             | name='b8b98905-b40d-4a44-82fa-dac23a1491ec' |
| status                      | BUILD                                       |
| updated                     | 2019-07-01T15:59:27Z                        |
| user_id                     | cacbdcada640409480ea65cc804b3f32            |
| volumes_attached            |                                             |
+-----------------------------+---------------------------------------------+

[DEBUG] server list -f json --name akrrtest
[
  {
    "ID": "b026c94b-df67-48e1-bbe9-fa0739653a92",
    "Name": "akrrtest",
    "Status": "BUILD",
    "Networks": "",
    "Image": "",
    "Flavor": "c8.m16"
  }
]

[DEBUG] server list -f json --name akrrtest
[
  {
    "ID": "b026c94b-df67-48e1-bbe9-fa0739653a92",
    "Name": "akrrtest",
    "Status": "BUILD",
    "Networks": "",
    "Image": "",
    "Flavor": "c8.m16"
  }
]

[DEBUG] server list -f json --name akrrtest
[
  {
    "ID": "b026c94b-df67-48e1-bbe9-fa0739653a92",
    "Name": "akrrtest",
    "Status": "ACTIVE",
    "Networks": "lakeeffect-199.109.195=199.109.192.15",
    "Image": "",
    "Flavor": "c8.m16"
  }
]

[DEBUG] internal_network_ip:199.109.192.15
[DEBUG] ssh-keygen -R 199.109.192.15
Host 199.109.192.15 not found in /home/hoffmaps/.ssh/known_hosts

[DEBUG] ssh -i /home/hoffmaps/projects/openstack/keypairs/openstack-testing.key centos@199.109.192.15 "echo StArTEd_ExeCUTEtIoM_SucCeSsFully;uname -a;echo ExeCUTEd_SucCeSsFully"
[DEBUG] ssh -i /home/hoffmaps/projects/openstack/keypairs/openstack-testing.key centos@199.109.192.15 "echo StArTEd_ExeCUTEtIoM_SucCeSsFully;uname -a;echo ExeCUTEd_SucCeSsFully"
[DEBUG] ssh -i /home/hoffmaps/projects/openstack/keypairs/openstack-testing.key centos@199.109.192.15
================================================================================
[INFO] Successfully connected to open-lakeeffect-stack


[INFO] Checking directory locations

[INFO] Checking: 199.109.192.15:/home/centos/appker/akrr_data
[INFO] Directory exist and accessible for read/write

[INFO] Checking: 199.109.192.15:/home/centos/appker/resource
[INFO] Directory exist and accessible for read/write

[INFO] Checking: 199.109.192.15:/home/centos/appker/network_scratch
[INFO] Directory exist and accessible for read/write
[INFO] 
[INFO] Checking: 199.109.192.15:/home/centos/appker/network_scratch
[INFO] Directory exist and accessible for read/write
[INFO] 
[DEBUG] server list -f json --name akrrtest
[
  {
    "ID": "b026c94b-df67-48e1-bbe9-fa0739653a92",
    "Name": "akrrtest",
    "Status": "ACTIVE",
    "Networks": "lakeeffect-199.109.195=199.109.192.15",
    "Image": "",
    "Flavor": "c8.m16"
  }
]

[DEBUG] server delete akrrtest

[DEBUG] server list -f json --name akrrtest
[]

[INFO] ################################################################################
[INFO] Will send test job to queue, wait till it executed and will analyze the output
Will use AKRR REST API at https://localhost:8091/api/v1
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/scheduled_tasks HTTP/1.1" 401 140
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/token HTTP/1.1" 200 94
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/scheduled_tasks HTTP/1.1" 200 5981
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "POST /api/v1/scheduled_tasks HTTP/1.1" 200 137
[INFO] 
Submitted test job to AKRR, task_id is 3144791

[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144791 HTTP/1.1" 200 349


================================================================================
Tast status:
Task is in scheduled_tasks queue.
It schedule to be started on 2019-07-01T12:00:05

time: 2019-07-01 12:00:05 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144791 HTTP/1.1" 404 152
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144791 HTTP/1.1" 400 265
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144791 HTTP/1.1" 200 107
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144791 HTTP/1.1" 200 707


================================================================================
Tast status:
Task is in active_tasks queue.
Status: None
Status info:
None

time: 2019-07-01 12:00:16 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144791 HTTP/1.1" 200 107
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144791 HTTP/1.1" 200 10883


================================================================================
Tast status:
Task is in active_tasks queue.
Status: start_openstack_server ... Done
Status info:
start_openstack_server ... Done

time: 2019-07-01 12:00:58 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144791 HTTP/1.1" 200 107
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144791 HTTP/1.1" 200 11814


================================================================================
Tast status:
Task is in active_tasks queue.
Status: Still in queue. Either waiting or running
Status info:
  PID TTY          TIME CMD
 1445 ?        00:00:00 bash

time: 2019-07-01 12:01:03 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144791 HTTP/1.1" 200 107
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144791 HTTP/1.1" 200 12706
time: 2019-07-01 12:01:08 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144791 HTTP/1.1" 200 107
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144791 HTTP/1.1" 200 13598
time: 2019-07-01 12:01:13 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144791 HTTP/1.1" 200 107
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144791 HTTP/1.1" 200 14490
time: 2019-07-01 12:01:18 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144791 HTTP/1.1" 200 107
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144791 HTTP/1.1" 200 15382
time: 2019-07-01 12:01:24 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144791 HTTP/1.1" 200 107
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144791 HTTP/1.1" 200 16274
time: 2019-07-01 12:01:29 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144791 HTTP/1.1" 200 107
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144791 HTTP/1.1" 200 17166
time: 2019-07-01 12:01:34 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144791 HTTP/1.1" 200 107
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144791 HTTP/1.1" 200 18058
time: 2019-07-01 12:01:39 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144791 HTTP/1.1" 200 107
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144791 HTTP/1.1" 200 18950
time: 2019-07-01 12:01:44 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144791 HTTP/1.1" 200 107
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144791 HTTP/1.1" 200 19842
time: 2019-07-01 12:01:49 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144791 HTTP/1.1" 200 107
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144791 HTTP/1.1" 200 20734
time: 2019-07-01 12:01:54 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144791 HTTP/1.1" 200 107
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144791 HTTP/1.1" 200 21626
time: 2019-07-01 12:01:59 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144791 HTTP/1.1" 200 107
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144791 HTTP/1.1" 200 22518
time: 2019-07-01 12:02:04 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144791 HTTP/1.1" 200 107
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144791 HTTP/1.1" 200 23410
time: 2019-07-01 12:02:09 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144791 HTTP/1.1" 200 107
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144791 HTTP/1.1" 200 24302
time: 2019-07-01 12:02:14 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144791 HTTP/1.1" 200 107
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144791 HTTP/1.1" 200 25194
time: 2019-07-01 12:02:19 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144791 HTTP/1.1" 200 107
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144791 HTTP/1.1" 200 26086
time: 2019-07-01 12:02:25 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144791 HTTP/1.1" 200 107
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144791 HTTP/1.1" 200 26978
time: 2019-07-01 12:02:30 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144791 HTTP/1.1" 200 107
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144791 HTTP/1.1" 200 27870
time: 2019-07-01 12:02:35 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144791 HTTP/1.1" 200 107
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144791 HTTP/1.1" 200 28762
time: 2019-07-01 12:02:40 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144791 HTTP/1.1" 200 107
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144791 HTTP/1.1" 200 29654
time: 2019-07-01 12:02:45 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144791 HTTP/1.1" 200 107
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144791 HTTP/1.1" 200 30546
time: 2019-07-01 12:02:50 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144791 HTTP/1.1" 200 107
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144791 HTTP/1.1" 200 31438
time: 2019-07-01 12:02:55 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144791 HTTP/1.1" 200 107
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144791 HTTP/1.1" 200 32330
time: 2019-07-01 12:03:00 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144791 HTTP/1.1" 200 107
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144791 HTTP/1.1" 200 33222
time: 2019-07-01 12:03:05 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144791 HTTP/1.1" 200 107
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144791 HTTP/1.1" 200 34114
time: 2019-07-01 12:03:10 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144791 HTTP/1.1" 200 107
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144791 HTTP/1.1" 200 35006
time: 2019-07-01 12:03:15 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144791 HTTP/1.1" 200 107
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144791 HTTP/1.1" 200 37079


================================================================================
Tast status:
Task is in active_tasks queue.
Status: Not in queue. Either exited with error or executed successfully. Copied all files to local machine. Deleted all files from remote machine
Status info:
Not in queue. Either exited with error or executed successfully. Copied all files to local machine. Deleted all files from remote machine

time: 2019-07-01 12:03:20 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144791 HTTP/1.1" 200 107
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144791 HTTP/1.1" 200 37104


================================================================================
Tast status:
Task is in active_tasks queue.
Status: Task was completed successfully.
Status info:
Done

time: 2019-07-01 12:03:26 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144791 HTTP/1.1" 200 107
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144791 HTTP/1.1" 200 37107
time: 2019-07-01 12:03:31 [DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/active_tasks/3144791 HTTP/1.1" 404 152
[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144791 HTTP/1.1" 200 53531


================================================================================
Tast status:
Task is completed!
completed_tasks table entry:
{   'app': 'hpcg',
    'app_param': '{}',
    'datetime_stamp': '2019.07.01.12.00.06.078458',
    'fails_to_submit_to_the_queue': 0,
    'fatal_errors_count': 0,
    'group_id': '',
    'parent_task_id': 3144791,
    'repeat_in': None,
    'resource': 'open-lakeeffect-stack',
    'resource_param': "{'nnodes':1}",
    'status': 'Done',
    'status_info': 'Done',
    'task_id': 3144791,
    'task_param': "{'test_run':True}",
    'time_activated': '2019-07-01T12:00:06',
    'time_finished': '2019-07-01T12:03:25',
    'time_submitted_to_queue': '2019-07-01T12:00:57',
    'time_to_start': '2019-07-01T12:00:05'}
akrr_xdmod_instanceinfo table entry:
{   'body': '<performance>\n'
            '    <ID>HPCG</ID>\n'
            '    <benchmark>\n'
            '        <ID>HPCG</ID>\n'
            '        <parameters>\n'
            '            <parameter>\n'
            '                <ID>App:ExeBinSignature</ID>\n'
            '                '
            '<value>H4sIAMouGl0CA7WUTW/bMAyG7/0VvhewKUrUR8/bcRjQPxBQFNUaSRzDcYfs309pss7nortRhB68r/ih78/PP5+fuuH1dNRBdFpP54Hnea/LwPtl2RVeeXid5WVAMKmH0IPpDfYAPfh2jI7i0PfdeO6m09rx1OlF5W3lfNAujxMvv7s6HvThxzd66sRzKNFyQK0AbB0xJUcph2CZMHXDaV6HcVr1MMjpODdwOe94KrvDmBdeRj3vmo/Y2x4Rh8M4vV2G4/4wZJ3k9cjL/nwz25SHyzXa8a/LTRuCUY6eYuGamo/AEaMxJjtAb4p+SvvvxXbMN9a7azy2PPXn0026KueADkON2RFAhGjAR2diKhbUf/rZG9V2dbqeW3r3ntodZu8+LCi6wMVbcIxYCprskxoEG2OqvtT/Y2F9XZTLh4lYkgFGTkmIYkIMhK5Vw2hV4iJfbUJOi/6rQBZPJlowxVm0Nreeo8fqpZZc5ZPi87ht+7vwPMrl0mTbmtwnr3qyyUgrvLpiKDjXJhFUYgtN4i9Urqdl3Uq3gievVCOWjFlrAdRMJCEGF9pIfqH0Vjbn7KJxgQgcErkQTRU1reTsW7VNd2VudDlcwTtHCWMJNTWkFIW2LFliYIFEKXKBDXd/541DmwBzFhFQSyCmlgqpQIBqpbi44eaPmezhbhZ8W4PkoRqyaj050pKUk2v72nq3gc9rkcfHK+vvwgGoddS1Lc6iYDA4rcklHwxilrxhjxtMYkUxNqiq4faDmiyQNWRvC0pzs8FeRHbnzVMZQ+OoCgpC+zmLpaDVgyFJqc3zBpWb4sMfOz6kDOQFAAA=</value>\n'
            '            </parameter>\n'
            '            <parameter>\n'
            '                <ID>App:Version</ID>\n'
            '                <value>n104-8p-1t version V3.0</value>\n'
            '            </parameter>\n'
            '            <parameter>\n'
            '                <ID>Input:Distributed Processes</ID>\n'
            '                <value>8</value>\n'
            '            </parameter>\n'
            '            <parameter>\n'
            '                <ID>Input:Global Problem Dimensions Nx</ID>\n'
            '                <value>208</value>\n'
            '            </parameter>\n'
            '            <parameter>\n'
            '                <ID>Input:Global Problem Dimensions Ny</ID>\n'
            '                <value>208</value>\n'
            '            </parameter>\n'
            '            <parameter>\n'
            '                <ID>Input:Global Problem Dimensions Nz</ID>\n'
            '                <value>208</value>\n'
            '            </parameter>\n'
            '            <parameter>\n'
            '                <ID>Input:Local Domain Dimensions Nx</ID>\n'
            '                <value>104</value>\n'
            '            </parameter>\n'
            '            <parameter>\n'
            '                <ID>Input:Local Domain Dimensions Ny</ID>\n'
            '                <value>104</value>\n'
            '            </parameter>\n'
            '            <parameter>\n'
            '                <ID>Input:Local Domain Dimensions Nz</ID>\n'
            '                <value>104</value>\n'
            '            </parameter>\n'
            '            <parameter>\n'
            '                <ID>Input:Number of Coarse Grid Levels</ID>\n'
            '                <value>3</value>\n'
            '            </parameter>\n'
            '            <parameter>\n'
            '                <ID>Input:Threads per processes</ID>\n'
            '                <value>1</value>\n'
            '            </parameter>\n'
            '            <parameter>\n'
            '                <ID>RunEnv:CPU Speed</ID>\n'
            '                <value>2399.996</value>\n'
            '                <units>MHz</units>\n'
            '            </parameter>\n'
            '            <parameter>\n'
            '                <ID>RunEnv:Nodes</ID>\n'
            '                '
            '<value>H4sIAMkuGl0CA8vJT07MycgvLuECAOm1LpAKAAAA</value>\n'
            '            </parameter>\n'
            '            <parameter>\n'
            '                <ID>app</ID>\n'
            '                <value>hpcg</value>\n'
            '            </parameter>\n'
            '            <parameter>\n'
            '                <ID>resource</ID>\n'
            '                <value>open-lakeeffect-stack</value>\n'
            '            </parameter>\n'
            '        </parameters>\n'
            '        <statistics>\n'
            '            <statistic>\n'
            '                <ID>App kernel executable exists</ID>\n'
            '                <value>1</value>\n'
            '            </statistic>\n'
            '            <statistic>\n'
            '                <ID>App kernel input exists</ID>\n'
            '                <value>0</value>\n'
            '            </statistic>\n'
            '            <statistic>\n'
            '                <ID>Floating-Point Performance, Raw DDOT</ID>\n'
            '                <value>26.7584</value>\n'
            '                <units>GFLOP/s</units>\n'
            '            </statistic>\n'
            '            <statistic>\n'
            '                <ID>Floating-Point Performance, Raw MG</ID>\n'
            '                <value>10.8708</value>\n'
            '                <units>GFLOP/s</units>\n'
            '            </statistic>\n'
            '            <statistic>\n'
            '                <ID>Floating-Point Performance, Raw SpMV</ID>\n'
            '                <value>8.99097</value>\n'
            '                <units>GFLOP/s</units>\n'
            '            </statistic>\n'
            '            <statistic>\n'
            '                <ID>Floating-Point Performance, Raw Total</ID>\n'
            '                <value>9.92526</value>\n'
            '                <units>GFLOP/s</units>\n'
            '            </statistic>\n'
            '            <statistic>\n'
            '                <ID>Floating-Point Performance, Raw WAXPBY</ID>\n'
            '                <value>9.87888</value>\n'
            '                <units>GFLOP/s</units>\n'
            '            </statistic>\n'
            '            <statistic>\n'
            '                <ID>Floating-Point Performance, Total</ID>\n'
            '                <value>9.85149</value>\n'
            '                <units>GFLOP/s</units>\n'
            '            </statistic>\n'
            '            <statistic>\n'
            '                <ID>Memory Bandwidth, Read</ID>\n'
            '                <value>61.1473</value>\n'
            '                <units>GB/s</units>\n'
            '            </statistic>\n'
            '            <statistic>\n'
            '                <ID>Memory Bandwidth, Total</ID>\n'
            '                <value>75.2783</value>\n'
            '                <units>GB/s</units>\n'
            '            </statistic>\n'
            '            <statistic>\n'
            '                <ID>Memory Bandwidth, Write</ID>\n'
            '                <value>14.131</value>\n'
            '                <units>GB/s</units>\n'
            '            </statistic>\n'
            '            <statistic>\n'
            '                <ID>Network scratch directory accessible</ID>\n'
            '                <value>1</value>\n'
            '            </statistic>\n'
            '            <statistic>\n'
            '                <ID>Network scratch directory exists</ID>\n'
            '                <value>1</value>\n'
            '            </statistic>\n'
            '            <statistic>\n'
            '                <ID>Setup Time</ID>\n'
            '                <value>0.638408</value>\n'
            '                <units>Seconds</units>\n'
            '            </statistic>\n'
            '            <statistic>\n'
            '                <ID>Task working directory accessible</ID>\n'
            '                <value>1</value>\n'
            '            </statistic>\n'
            '            <statistic>\n'
            '                <ID>Task working directory exists</ID>\n'
            '                <value>1</value>\n'
            '            </statistic>\n'
            '            <statistic>\n'
            '                <ID>Wall Clock Time</ID>\n'
            '                <value>62.0</value>\n'
            '                <units>Second</units>\n'
            '            </statistic>\n'
            '            <statistic>\n'
            '                <ID>local scratch directory accessible</ID>\n'
            '                <value>1</value>\n'
            '            </statistic>\n'
            '            <statistic>\n'
            '                <ID>local scratch directory exists</ID>\n'
            '                <value>1</value>\n'
            '            </statistic>\n'
            '        </statistics>\n'
            '    </benchmark>\n'
            '</performance>\n',
    'collected': '2019-07-01T12:03:19',
    'committed': '2019-07-01T12:03:25',
    'cputime': 0.0,
    'executionhost': 'open-lakeeffect-stack',
    'instance_id': 3144791,
    'internal_failure': 0,
    'job_id': 1445,
    'memory': 0.0,
    'message': None,
    'ncores': None,
    'nnodes': None,
    'nodes': ';localhost;',
    'reporter': 'hpcg',
    'reporternickname': 'hpcg.1',
    'resource': 'open-lakeeffect-stack',
    'status': 1,
    'stderr': None,
    'walltime': 62.0}
output parsing results:
<performance>
    <ID>HPCG</ID>
    <benchmark>
        <ID>HPCG</ID>
        <parameters>
            <parameter>
                <ID>App:ExeBinSignature</ID>
                <value>H4sIAMouGl0CA7WUTW/bMAyG7/0VvhewKUrUR8/bcRjQPxBQFNUaSRzDcYfs309pss7nortRhB68r/ih78/PP5+fuuH1dNRBdFpP54Hnea/LwPtl2RVeeXid5WVAMKmH0IPpDfYAPfh2jI7i0PfdeO6m09rx1OlF5W3lfNAujxMvv7s6HvThxzd66sRzKNFyQK0AbB0xJUcph2CZMHXDaV6HcVr1MMjpODdwOe94KrvDmBdeRj3vmo/Y2x4Rh8M4vV2G4/4wZJ3k9cjL/nwz25SHyzXa8a/LTRuCUY6eYuGamo/AEaMxJjtAb4p+SvvvxXbMN9a7azy2PPXn0026KueADkON2RFAhGjAR2diKhbUf/rZG9V2dbqeW3r3ntodZu8+LCi6wMVbcIxYCprskxoEG2OqvtT/Y2F9XZTLh4lYkgFGTkmIYkIMhK5Vw2hV4iJfbUJOi/6rQBZPJlowxVm0Nreeo8fqpZZc5ZPi87ht+7vwPMrl0mTbmtwnr3qyyUgrvLpiKDjXJhFUYgtN4i9Urqdl3Uq3gievVCOWjFlrAdRMJCEGF9pIfqH0Vjbn7KJxgQgcErkQTRU1reTsW7VNd2VudDlcwTtHCWMJNTWkFIW2LFliYIFEKXKBDXd/541DmwBzFhFQSyCmlgqpQIBqpbi44eaPmezhbhZ8W4PkoRqyaj050pKUk2v72nq3gc9rkcfHK+vvwgGoddS1Lc6iYDA4rcklHwxilrxhjxtMYkUxNqiq4faDmiyQNWRvC0pzs8FeRHbnzVMZQ+OoCgpC+zmLpaDVgyFJqc3zBpWb4sMfOz6kDOQFAAA=</value>
            </parameter>
            <parameter>
                <ID>App:Version</ID>
                <value>n104-8p-1t version V3.0</value>
            </parameter>
            <parameter>
                <ID>Input:Distributed Processes</ID>
                <value>8</value>
            </parameter>
            <parameter>
                <ID>Input:Global Problem Dimensions Nx</ID>
                <value>208</value>
            </parameter>
            <parameter>
                <ID>Input:Global Problem Dimensions Ny</ID>
                <value>208</value>
            </parameter>
            <parameter>
                <ID>Input:Global Problem Dimensions Nz</ID>
                <value>208</value>
            </parameter>
            <parameter>
                <ID>Input:Local Domain Dimensions Nx</ID>
                <value>104</value>
            </parameter>
            <parameter>
                <ID>Input:Local Domain Dimensions Ny</ID>
                <value>104</value>
            </parameter>
            <parameter>
                <ID>Input:Local Domain Dimensions Nz</ID>
                <value>104</value>
            </parameter>
            <parameter>
                <ID>Input:Number of Coarse Grid Levels</ID>
                <value>3</value>
            </parameter>
            <parameter>
                <ID>Input:Threads per processes</ID>
                <value>1</value>
            </parameter>
            <parameter>
                <ID>RunEnv:CPU Speed</ID>
                <value>2399.996</value>
                <units>MHz</units>
            </parameter>
            <parameter>
                <ID>RunEnv:Nodes</ID>
                <value>H4sIAMkuGl0CA8vJT07MycgvLuECAOm1LpAKAAAA</value>
            </parameter>
            <parameter>
                <ID>app</ID>
                <value>hpcg</value>
            </parameter>
            <parameter>
                <ID>resource</ID>
                <value>open-lakeeffect-stack</value>
            </parameter>
        </parameters>
        <statistics>
            <statistic>
                <ID>App kernel executable exists</ID>
                <value>1</value>
            </statistic>
            <statistic>
                <ID>App kernel input exists</ID>
                <value>0</value>
            </statistic>
            <statistic>
                <ID>Floating-Point Performance, Raw DDOT</ID>
                <value>26.7584</value>
                <units>GFLOP/s</units>
            </statistic>
            <statistic>
                <ID>Floating-Point Performance, Raw MG</ID>
                <value>10.8708</value>
                <units>GFLOP/s</units>
            </statistic>
            <statistic>
                <ID>Floating-Point Performance, Raw SpMV</ID>
                <value>8.99097</value>
                <units>GFLOP/s</units>
            </statistic>
            <statistic>
                <ID>Floating-Point Performance, Raw Total</ID>
                <value>9.92526</value>
                <units>GFLOP/s</units>
            </statistic>
            <statistic>
                <ID>Floating-Point Performance, Raw WAXPBY</ID>
                <value>9.87888</value>
                <units>GFLOP/s</units>
            </statistic>
            <statistic>
                <ID>Floating-Point Performance, Total</ID>
                <value>9.85149</value>
                <units>GFLOP/s</units>
            </statistic>
            <statistic>
                <ID>Memory Bandwidth, Read</ID>
                <value>61.1473</value>
                <units>GB/s</units>
            </statistic>
            <statistic>
                <ID>Memory Bandwidth, Total</ID>
                <value>75.2783</value>
                <units>GB/s</units>
            </statistic>
            <statistic>
                <ID>Memory Bandwidth, Write</ID>
                <value>14.131</value>
                <units>GB/s</units>
            </statistic>
            <statistic>
                <ID>Network scratch directory accessible</ID>
                <value>1</value>
            </statistic>
            <statistic>
                <ID>Network scratch directory exists</ID>
                <value>1</value>
            </statistic>
            <statistic>
                <ID>Setup Time</ID>
                <value>0.638408</value>
                <units>Seconds</units>
            </statistic>
            <statistic>
                <ID>Task working directory accessible</ID>
                <value>1</value>
            </statistic>
            <statistic>
                <ID>Task working directory exists</ID>
                <value>1</value>
            </statistic>
            <statistic>
                <ID>Wall Clock Time</ID>
                <value>62.0</value>
                <units>Second</units>
            </statistic>
            <statistic>
                <ID>local scratch directory accessible</ID>
                <value>1</value>
            </statistic>
            <statistic>
                <ID>local scratch directory exists</ID>
                <value>1</value>
            </statistic>
        </statistics>
    </benchmark>
</performance>


time: 2019-07-01 12:03:43 [INFO] Test job is completed analyzing output

[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "GET /api/v1/tasks/3144791 HTTP/1.1" 200 53531
[INFO] 
Test kernel execution summary:
status: 1
status_info: Done
processing message:
None
Local working directory for this task: /home/hoffmaps/projects/akrr/log/comptasks/open-lakeeffect-stack/hpcg/2019.07.01.12.00.06.078458
Location of some important generated files:
        Batch job script: /home/hoffmaps/projects/akrr/log/comptasks/open-lakeeffect-stack/hpcg/2019.07.01.12.00.06.078458/jobfiles/hpcg.job
        Application kernel output: /home/hoffmaps/projects/akrr/log/comptasks/open-lakeeffect-stack/hpcg/2019.07.01.12.00.06.078458/jobfiles/appstdout
        Batch job standard output: /home/hoffmaps/projects/akrr/log/comptasks/open-lakeeffect-stack/hpcg/2019.07.01.12.00.06.078458/jobfiles/stdout
        Batch job standard error output: /home/hoffmaps/projects/akrr/log/comptasks/open-lakeeffect-stack/hpcg/2019.07.01.12.00.06.078458/jobfiles/stderr
        XML processing results: /home/hoffmaps/projects/akrr/log/comptasks/open-lakeeffect-stack/hpcg/2019.07.01.12.00.06.078458/result.xml
        Task execution logs: /home/hoffmaps/projects/akrr/log/comptasks/open-lakeeffect-stack/hpcg/2019.07.01.12.00.06.078458/proc/log


[INFO] 
Enabling hpcg on open-lakeeffect-stack for execution

[DEBUG] Starting new HTTPS connection (1): localhost:8091
[DEBUG] https://localhost:8091 "PUT /api/v1/resources/open-lakeeffect-stack/on HTTP/1.1" 200 63
[INFO] Successfully enabled hpcg on open-lakeeffect-stack
[INFO] 
DONE, you can move to next step!

[DEBUG] token revoke gAAAAABdGi3ZHlC8fNxvtWzXgWErQSsy28YOp2KByaDj2y7x0M6qGvr0xerRpeEEakfNkLdDW_ZkcY-ksDbi4a0t7SitNmlJyJ6dsBZkrYJBot2YghZn8iVod0U2FNfy2Z3CThkvxJEqrQUL1nZwrXCQ7WHrEab2Fdopp0bHHKwaSE1ZSAMgx74Kbueox7Up7T-2jWGpraWehBt9C4Diaf_Vb7TK1ClMEQ
```
So that says that it worked.
Will try again to check if its actually running in parallel

So I'm gonna try and validate each of them, maybe I just wasn't waiting long enough for the others.
So the list:
- hpcg - working as expected (~ 1 min run)
- hpcc - working as expected (~ 3.5 min run)
- gamess - working as expected (~ 2.5 min run)
- namd - working as expected (~ 2.5 min run)
- nwchem - working as expected (~ 1.5 min run) 

For nwchem we need a special setup thats different than the usual:
```bash
appkernel_run_env_template = """
sudo systemctl start docker
docker pull pshoff/akrr_benchmarks:nwchem

# the cap-add to not print all the errors that are being given
RUN_APPKERNEL="docker run --rm --shm-size 8g --cap-add=SYS_PTRACE pshoff/akrr_benchmarks:nwchem"
# to have correct input things
sed -i -e "s/scratch_dir/#/g" $INPUT
sed -i -e "s/permanent_dir/#/g" $INPUT
"""

```



