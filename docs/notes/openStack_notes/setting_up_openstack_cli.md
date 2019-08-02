## How to set up Command Line Interface with Openstack

```bash
# get pip3 first
sudo yum install python36-setuptools
sudo easy_install-3.6 pip

# then install the openstack stuff
sudo pip3 install python-cinderclient==3.6.1
sudo pip3 install python-openstackclient
sudo pip3 install git+https://github.com/ubccr/v3oidcmokeyapikey.git

# for me sudo wasn't recognizing pip so I did this:
sudo python3 -m pip install python-cinderclient==3.6.1
sudo python3 -m pip install python-openstackclient
sudo python3 -m pip install git+https://github.com/ubccr/v3oidcmokeyapikey.git

```
Then you go to the OpenStack portal: https://lakeeffect.ccr.buffalo.edu
Go to the project you want to connect to.

Top left click Project -> API Access
Then on the far right of the API Access page, click Download OpenStack RC File -> OpenStack RC File (Identity API v3)
(Name of RC file is different for everyone, depends on project. In my case it was called lakeeffect-benchmarks-openrc.sh)

The inside of this script looks like:
```bash
#!/usr/bin/env bash
unset OS_TOKEN
unset OS_AUTH_TYPE
echo "Please enter your CCR API Key: "
read -sr OS_API_KEY_INPUT
export OS_API_KEY=$OS_API_KEY_INPUT
export OS_AUTH_URL=https://lakeeffect.ccr.buffalo.edu:8770/v3
export OS_IDENTITY_API_VERSION=3
export OS_PROJECT_NAME="lakeeffect-benchmarks"
export OS_USERNAME="hoffmaps"
export OS_PROJECT_DOMAIN_NAME="lakeeffect"
export OS_INTERFACE=public
export OS_REGION_NAME="buffalo"
export OS_TOKEN=`openstack --os-auth-type v3oidcmokeyapikey --os-identity-provider ccr --os-protocol openid --os-discovery-endpoint https://sso.ccr.buffalo.edu/.well-known/openid-configuration --os-client-id ccr-os-api --os-redirect-uri https://localhost/ccrauth token issue -f value -c id`
export OS_AUTH_TYPE=v3token
```
And what it does is it gets you a token that is used to work with OpenStack from your command line.
It sets up all the variables needed to work with that project.

### Getting your CCR API Key
What you do need is the CCR API Key, which is unique to each CCR User.
To get it, go to the Identiy Management Portal, which is the link found here: https://ubccr.freshdesk.com/support/solutions/articles/13000025034-identity-management-portal

Click CCR Identity Management Portal
Log into your account.
Go to Api Keys and click "Create Api Key" for Access to CCR Openstack CLI.
Then a text box will show up with a string of letters, symbols, and numbers. 
This is the key to use when it prompts for the API Key. Save it somewhere, then click "Done".
Now the ccr-os-api key thing should say "Active" next to it.

### Finishing setup
You can either put in the api key every time you want to do things with OpenStack, or what you can do is go into the RC script and just paste the api key you got by commenting out the "asking for input" part, so that section would change to look something like this:

```bash
# old
echo "Please enter your CCR API Key: "
read -sr OS_API_KEY_INPUT
export OS_API_KEY=$OS_API_KEY_INPUT

# new
#echo "Please enter your CCR API Key: "
#read -sr OS_API_KEY_INPUT
export OS_API_KEY="my_key"
# (replace my_key with your api key)
```
Then you source it and check the available resources to see if it worked properly
```bash
# source your own script, this is just the script I was using
source lakeeffect-benchmarks-openrc.sh
openstack flavor list
openstack image list

```
Example output:
```text
[hoffmaps@dhcp-128-205-70-4 open-lakeeffect-stack]$ openstack flavor list
+--------+---------+-------+------+-----------+-------+-----------+
| ID     | Name    |   RAM | Disk | Ephemeral | VCPUs | Is Public |
+--------+---------+-------+------+-----------+-------+-----------+
| 101001 | c1.m1   |  1024 |   20 |         0 |     1 | True      |
| 101004 | c1.m4   |  4096 |   20 |         0 |     1 | True      |
| 102004 | c2.m4   |  4096 |   20 |         0 |     2 | True      |
| 102008 | c2.m8   |  8192 |   20 |         0 |     2 | True      |
| 104008 | c4.m8   |  8192 |   20 |         0 |     4 | True      |
| 104016 | c4.m16  | 16384 |   20 |         0 |     4 | True      |
| 108016 | c8.m16  | 16384 |   20 |         0 |     8 | True      |
| 108032 | c8.m32  | 32768 |   20 |         0 |     8 | True      |
| 116032 | c16.m32 | 32768 |   20 |         0 |    16 | True      |
| 116064 | c16.m64 | 65536 |   20 |         0 |    16 | True      |
+--------+---------+-------+------+-----------+-------+-----------+
[hoffmaps@dhcp-128-205-70-4 open-lakeeffect-stack]$ openstack image list
+--------------------------------------+----------------------------------+--------+
| ID                                   | Name                             | Status |
+--------------------------------------+----------------------------------+--------+
| eb259c93-82f1-4d9e-8318-b3546e5d02e6 | centos-7.6.1810-20190604         | active |
| 8b54ca90-c537-4e53-b2af-fe11f27f4938 | centos6-ccr-20181127-1           | active |
| 2df9cfcc-5ce1-413f-82f8-97c508ce5cf2 | centos7-ccr-20181127-1           | active |
| 6dc36647-89e7-4960-9127-36e705f2cd19 | initial_test_with_hpcc_benchmark | active |
| 3eec2848-d87a-4a74-bc75-b502776c97d7 | rhel7-20190618                   | active |
| fb903bbd-662e-462e-88f3-ef5c1209e894 | testing_with_docker_images_on_it | active |
| 17a8bcac-374c-4be0-b04c-005a847b2d10 | ubuntu1404-ccr-20181129-1        | active |
| 0847e343-cf30-4c24-a5c7-a01fb76735ee | ubuntu1604-ccr-20181127-1        | active |
| 0232b73a-1c16-4c33-96d9-3295b898ca4f | ubuntu1804-ccr-20181127-1        | active |
+--------------------------------------+----------------------------------+--------+
```
You can check these against the flavors and volumes you find in the web interface.
Remember, now the openstack commands work for that specific project you got the script from. If you want to look at a different project, you need to source a different script (same API key though).

As far as what commands you can use, refer to the Reference Docs, found here: https://docs.openstack.org/mitaka/cli-reference/


That should make everything all set to use everything through the cli, but lets create a volume, start up an instance, and ssh into it to confirm that it's all working.
Also, creating volumes and spinning up instances are pretty important in OpenStack so this is good practice.

### Initial OpenStack CLI practice

Create a volume:
```bash

openstack volume create --image centos7-ccr-20181127-1 --size 20 --description "test volume" testing_volume
# explanation:
# --image <image_name> = it uses this image as a basis (the os to use)
# --size <ssd size> = how big the volume is, aka how much storage it will have, in GiB
# --description "descrip" = not needed, but used to tell some info about the volume, perhaps what its used for
# There are other options too, but this is a good start for now, you can look at the reference for other options
# The very last phrase (testing_volume) is the name of the volume, this is what we will use when we create instances.
```
Sample Output:
```text
[hoffmaps@dhcp-128-205-70-4 open-lakeeffect-stack]$ openstack volume create --image centos7-ccr-20181127-1 --size 20 --description "test volume" testing_volume
+---------------------+--------------------------------------+
| Field               | Value                                |
+---------------------+--------------------------------------+
| attachments         | []                                   |
| availability_zone   | cbls                                 |
| bootable            | false                                |
| consistencygroup_id | None                                 |
| created_at          | 2019-08-02T15:26:51.000000           |
| description         | test volume                          |
| encrypted           | False                                |
| id                  | e6141ea7-b88d-464b-a3fa-92f5f2a869e8 |
| multiattach         | False                                |
| name                | testing_volume                       |
| properties          |                                      |
| replication_status  | None                                 |
| size                | 20                                   |
| snapshot_id         | None                                 |
| source_volid        | None                                 |
| status              | creating                             |
| type                | rbd                                  |
| updated_at          | None                                 |
| user_id             | cacbdcada640409480ea65cc804b3f32     |
+---------------------+--------------------------------------+
```

Now lets try to spin off an instance
```bash

openstack server create --flavor c8.m16 \ 
  --volume testing_volume \ 
  --network lakeeffect-199.109.195 \ 
  --security-group default --security-group SSH \ 
  --key-name openstack-testing testing_instance

# Explanation
openstack server create --flavor c8.m16 \ # specify flavor (from flavor list)
  --volume testing_volume \ # specify the volume we just made
  --network lakeeffect-199.109.195 \ # network to use
  --security-group default --security-group SSH \ # configure security
  --key-name openstack-testing testing_instance # what key to use for ssh access, then the name
```
These options are also on the web interface, so if you're unsure what to put, try creating an instance through the web interface and see what the possible options are there.

Sample output:
```bash
[hoffmaps@dhcp-128-205-70-4 open-lakeeffect-stack]$ openstack server create --flavor c8.m16 --volume testing_volume  --network lakeeffect-199.109.195 --security-group default --security-group SSH --key-name openstack-testing testing_instance
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
| adminPass                   | UP5MhpdwaBDT                                |
| config_drive                |                                             |
| created                     | 2019-08-02T15:37:05Z                        |
| flavor                      | c8.m16 (108016)                             |
| hostId                      |                                             |
| id                          | 10e5ec38-ef6a-4fa0-8891-614d1e4e8fc7        |
| image                       |                                             |
| key_name                    | openstack-testing                           |
| name                        | testing_instance                            |
| progress                    | 0                                           |
| project_id                  | ef13fb8fc7aa4e9c9ecf62b08bed097a            |
| properties                  |                                             |
| security_groups             | name='a40ecec6-29fb-4734-84bf-c45cbfa495e5' |
|                             | name='b8b98905-b40d-4a44-82fa-dac23a1491ec' |
| status                      | BUILD                                       |
| updated                     | 2019-08-02T15:37:05Z                        |
| user_id                     | cacbdcada640409480ea65cc804b3f32            |
| volumes_attached            |                                             |
+-----------------------------+---------------------------------------------+

```
Check that its running
```bash
openstack server list --name testing_instance
```

Sample output:
```bash
[hoffmaps@dhcp-128-205-70-4 open-lakeeffect-stack]$ openstack server list --name testing_instance
+--------------------------------------+------------------+--------+---------------------------------------+-------+--------+
| ID                                   | Name             | Status | Networks                              | Image | Flavor |
+--------------------------------------+------------------+--------+---------------------------------------+-------+--------+
| 10e5ec38-ef6a-4fa0-8891-614d1e4e8fc7 | testing_instance | ACTIVE | lakeeffect-199.109.195=199.109.192.28 |       | c8.m16 |
+--------------------------------------+------------------+--------+---------------------------------------+-------+--------+

```
Then try to ssh into the instance

```bash
ssh -i openstack-testing.key centos@199.109.192.28
# the user may be different depending on the image you are using
# (openstack-testing.key is the full path to the private key)
```

The key should be the private key corresponding to the public key name that you used to create the instance. 
To create key pairs to use, go to the Key Pairs tab under Compute in your project. 
You can either create a new key pair or import one.
If you click "Create Key Pair" you can automatically download the private key that you can then use for the ssh command above after the -i.

Once you can ssh into the instance, you can use it as normal, any files or directories you create will be saved between instances. Being able to use ssh means you can also use the sftp command to get or put files onto the instance, and its as simple as:

```bash
sftp -i openstak-testing.key centos@199.109.192.28

```

### Possible errors
If you go away for a while not using the OpenStack command, and then you try and do some openstack command, you may run into an error like this:

```bash
Failed to validate token (HTTP 404) (Request-ID: req-5b026efc-f9f4-4eaf-93fb-04f80538d785)
```
That just means that the token that you got from sourcing the rc file has expired, you can just source that file again to get a new token and it should be fine to work again.


If you source the file too often in a short amount of time, you could get an HTTP 429 error, which means you're requesting a token too much, and the simplest fix for this is to just wait a bit before requesting a token again.

