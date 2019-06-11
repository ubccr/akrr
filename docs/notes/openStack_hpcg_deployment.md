## Notes on deploying hpcg on openstack

Like hpcc we'll define resource and appker

```bash
export RESOURCE=lakeeffect
export APPKER=hpcg

```
We have hpcg in a docker already, so we just need to edit the config too look at that.
So lets make the initial config firle:

```bash
akrr app add -a $APPKER -r $RESOURCE

```

Sample output:
```bash
[INFO] Generating application kernel configuration for hpcg on lakeeffect
[INFO] Application kernel configuration for hpcg on lakeeffect is in: 
        /home/hoffmaps/projects/akrr/etc/resources/lakeeffect/hpcg.app.conf

```
Now let's edit the config file.
Originally it looks like this:
```bash
# /home/hoffmaps/projects/akrr/etc/resources/lakeeffect/hpcg.app.conf
"""
Resource specific HPCG configuration
"""

appkernel_run_env_template = """
# Load application environment
module load intel
module load intel-mpi
module load mkl
module list

# set executable location
EXE=$MKLROOT/benchmarks/hpcg/bin/xhpcg_avx

# Set how to run app kernel
export OMP_NUM_THREADS=1
RUN_APPKERNEL="mpirun $EXE"
"""
```

We want to edit this so it calls the docker
So the new config file is this:
```bash
appkernel_run_env_template = """
sudo systemctl start docker
RUN_APPKERNEL="docker run --rm pshoff/akrr_benchmarks:hpcg"

"""

```

Once we edit the config for hpcg to use the docker, we can perform the validation run
```bash
akrr app validate -n 1 -r $RESOURCE -a $APPKER

```
OOP Looks like there was an error processing the output - bc the yaml output is in docker and of course doesn't get copied over
I think perhaps my strategy is just changing up the docker file so that printing out the *.yaml has the same format as given in the config, namely with the  === *.yaml Start === and end and such.

Okay I did that, turns out theres still an error, I think its with the yaml module itself, since the error happens with import yaml, and it gives a ModuleNotFoundError

- So I'm gonna try to remove pyyaml and reinstall it
```bash
sudo yum remove python36-PyYAML
sudo pip3 install python-cinderclient==3.6.1
sudo pip3 install python-openstackclient
sudo pip3 install git+https://github.com/ubccr/v3oidcmokeyapikey.git

```
No didn't really work...
I'm gonna try moving the import yaml thing up to the top of the file of hpcg_parser.py

I've tried re-installing pyyaml and printing out information, to no avail.Now I'm just getting weird errors, like that json error

```bash

[ERROR] ('Can not connect to lakeeffect\nProbably invalid credential, see full error report below', 'Start Session\n\nTraceback (most recent call last):\n  File "/home/hoffmaps/projects/akrr/akrr/app_validate.py", line 129, in app_validate\n    openstack_server.create()\n  File "/home/hoffmaps/projects/akrr/akrr/util/openstack.py", line 137, in create\n    if self.is_server_running():\n  File "/home/hoffmaps/projects/akrr/akrr/util/openstack.py", line 114, in is_server_running\n    out = json.loads(out.strip())\n  File "/usr/lib64/python3.6/json/__init__.py", line 354, in loads\n    return _default_decoder.decode(s)\n  File "/usr/lib64/python3.6/json/decoder.py", line 339, in decode\n    obj, end = self.raw_decode(s, idx=_w(s, 0).end())\n  File "/usr/lib64/python3.6/json/decoder.py", line 357, in raw_decode\n    raise JSONDecodeError("Expecting value", s, err.value) from None\njson.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n')
Traceback (most recent call last):
  File "/home/hoffmaps/projects/akrr/bin/akrr", line 65, in <module>
    akrr.cli.CLI().run()
  File "/home/hoffmaps/projects/akrr/akrr/cli/__init__.py", line 154, in run
    return cli_args.func(cli_args)
  File "/home/hoffmaps/projects/akrr/akrr/cli/commands.py", line 369, in handler
    app_validate(args.resource, args.appkernel, int(args.nodes))
  File "/home/hoffmaps/projects/akrr/akrr/app_validate.py", line 145, in app_validate
    raise e
  File "/home/hoffmaps/projects/akrr/akrr/app_validate.py", line 129, in app_validate
    openstack_server.create()
  File "/home/hoffmaps/projects/akrr/akrr/util/openstack.py", line 137, in create
    if self.is_server_running():
  File "/home/hoffmaps/projects/akrr/akrr/util/openstack.py", line 114, in is_server_running
    out = json.loads(out.strip())
  File "/usr/lib64/python3.6/json/__init__.py", line 354, in loads
    return _default_decoder.decode(s)
  File "/usr/lib64/python3.6/json/decoder.py", line 339, in decode
    obj, end = self.raw_decode(s, idx=_w(s, 0).end())
  File "/usr/lib64/python3.6/json/decoder.py", line 357, in raw_decode
    raise JSONDecodeError("Expecting value", s, err.value) from None
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```
UPDATE: The Json error thing happens when something goes wrong with connecting to the resource in app_validate, probably some sort of error with sshing or something?

Update: Now without changing anything (that I know of) the Json error is no more, but still having issues with the whole import yaml thingy



