# AKRR: Creating New Application Kernel

In this tutorial we will create a new application kernel, an example that did not previously exist in the AKRR distribution.

The outline of new application kernel creation is as follows:

1. Install new application and input files on target resource
2. Add generic instructions on application kernel execution to AKRR
3. Add resource specific instructions to AKRR
4. Create a parser for new application kernel
5. Test new application kernel

## MPI-Pi, Monte-Carlo -Calculation Application Kernel

In this tutorial we will use a classic MPI-Pi calculation program as an application kernel. Reading input from a file and some timing functionality
was added to a standard mpi_pi program in order to illustrate a practical example on integration of a new application kernel.
MPI-Pi calculates pi using a Monte-Carlo method: darts are randomly thrown to a unit square target with a round unit circle dartboard on it, the
ratio of darts that hit the dartboard to the total number of darts thrown gives the ratio of areas between circle dartboard and the square target,
which is then the Monte Carlo estimate for pi.

For our MPI-Pi application kernel to resemble what one can encounter during creation of more complex application kernels we have augmented
the classical MPI-Pi program with features usually seen in much bigger programs:
1. read number of darts to throw and total number of rounds from an input file
2. print out input parameters
3. print out version number
4. timing function to measure time spend in pi calculation
5. created performance metric, Darts thrown Per Second (DaPS)

Below is MPI-Pi installation reference and output sample:

source code: [[mpi_pi_reduce.c]]

installation, compile it directly:
```bash
mpicc -o mpi_pi_reduce -O3 mpi_pi_reduce.c
```

running:
```
mpirun -n <number_of_processors> <path_to>/mpi_pi_reduce <input file>
```
input file example:
```
5000000 /* number of throws at dartboard per mpi process */
100 /* number of times "darts" is iterated */
```

output example:
```
MPI task 0 has started...
MPI task 1 has started...
MPI task 2 has started...
MPI task 3 has started...
MPI task 5 has started...
MPI task 4 has started...
version: 2015.3.9
number of throws at dartboard: 5000000
number of rounds for dartz throwing 100
After 5000000 throws, average value
of pi = 3.14172000
....
After 500000000 throws, average value
of pi = 3.14158676
Real value of PI: 3.1415926535897
Time for PI calculation: 8.011
Giga Darts Throws per Second (GDaPS): 0.374
```

For further convenience lets set RESOURCE and APPKER environment variables:
```
export RESOURCE="localhost"
export APPKER="mpipi"
```

# Installing akrr locally for developmental purposes
It is a good idea to separate your development from actual AKRR installation.

Get conda, install enviroment for akrr:
```bash
conda create --name py_akrr
conda activate py_akrr
conda install python pymysql bottle requests psutil python-dateutil mysqlclientdateutil
```

```bash
# get code
git clone https://github.com/ubccr/akrr.git
# set paths (add to .bashrc if you want)
export PATH="/<path>/akrr/bin:$PATH"
export AKRR_HOME="/<path>/akrr/devel_local"

# install akrr
akrr setup --stand-alone
# or (in order to access sql via tcp)
akrr setup --akrr-db 127.0.0.1 --stand-alone
```

```bash
# add local resource as shell
akrr resource add
```
output sample:
```
akrr resource add 
[INFO] Beginning Initiation of New Resource...
[INFO] Retrieving Resources from XDMoD Database...
[INFO] Found following resources from XDMoD Database:
    resource_id  name
             10  alpha                                   
             11  bravo                                   

[INPUT] Enter resource_id for import (enter None for no match):
None

[INPUT] Enter AKRR resource name:
localhost

[INPUT] Enter queuing system on resource (slurm, pbs, shell, openstack or googlecloud):
shell

[INPUT] Enter Resource head node (access node) full name (e.g. headnode.somewhere.org):
[localhost] 
[INPUT] Enter username for resource access:
[nikolays] 
[INFO] Checking for password-less access
[INFO] Can access resource without password

[INFO] Connecting to localhost
[INFO]               Done

[INPUT] Enter processors (cores) per node count:
8
[INPUT] Enter location of local scratch (visible only to single node):
[/tmp]
[INFO] Directory exist and accessible for read/write

[INPUT] Enter location of network scratch (visible only to all nodes),used for temporary storage of app kernel input/output:
/tmp
[INFO] Directory exist and accessible for read/write

[INPUT] Enter future location of app kernels input and executable files:
[/home/nikolays/appker/localhost]/home/nikolays/xdmod_wsp/akrr/devel_local/appker
[INFO] Directory localhost:/home/nikolays/xdmod_wsp/akrr/devel_local/appker does not exists, will try to create it
[INFO] Directory exist and accessible for read/write

[INPUT] Enter future locations for app kernels working directories (can or even should be on scratch space):
[/tmp/akrr_data/localhost]/home/nikolays/xdmod_wsp/akrr/devel_local/akrr_data
[INFO] Directory localhost:/home/nikolays/xdmod_wsp/akrr/devel_local/akrr_data does not exists, will try to create it
[INFO] Directory exist and accessible for read/write

[INFO] Initiating localhost at AKRR
[INFO] Resource configuration is in /home/nikolays/xdmod_wsp/akrr/devel_local/etc/resources/localhost/resource.conf
[INFO] Initiation of new resource is completed.
    Edit batch_job_header_template variable in /home/nikolays/xdmod_wsp/akrr/devel_local/etc/resources/localhost/resource.conf
    and move to resource validation and deployment step.
    i.e. execute:
        akrr resource deploy -r localhost
```


```
# edit if needed (mostly not)
vi /home/nikolays/xdmod_wsp/akrr/devel_local/etc/resources/localhost/resource.conf

# validate
akrr resource deploy -r localhost

```

## Install new application kernel executables and input files on target resource

First we need to install the application on target resource:
```
# for further convenience lets set RESOURCE and APPKER
export RESOURCE="localhost"
export APPKER="mpipi"
export AKRR_APPKER_DIR="/home/nikolays/xdmod_wsp/akrr/devel_local/appker"
export AKRR_SRC="/home/nikolays/xdmod_wsp/akrr"

# on remote resource (which is localhost in this tutorial)
# go to application kernel executable directory
# $AKRR_APPKER_DIR is appkernel_dir in config
cd $AKRR_APPKER_DIR/execs
# make new directory for application kernel executable
mkdir mpipi
cd mpipi
# get the source code
wget http://compmodel.org/mpi_pi/mpi_pi_reduce.c
# load your favorite MPI compiler
# module load intel-mpi/5.0.2
# or use system-wide
# compile mpipi
mpicc -o mpi_pi_reduce -O3 mpi_pi_reduce.c
```

The source code for mpi_pi can also be found at mpi_pi_reduce.c

Second we need to install the input file on the target resource:
```bash
# on remote resource
# go to application kernel executable directory
cd $AKRR_APPKER_DIR/inputs
#make new directory for application kernel executable
mkdir mpipi
cd mpipi
#create input file
cat > input_file << END
5000000 /* number of throws at dartboard per mpi process */
100 /* number of times "darts" is iterated */
END
```

## Add general instructions on application kernel execution to AKRR

Now we need to add instructions for the new app kernel execution (which holds for most resources):

First, initiate default configuration and template
```bash
# go to AKRR source code directory
cd $AKRR_SRC
# init default config
cd akrr/default_conf
cp template.app.conf $APPKER.app.conf
# init template for new resource deployment
cd ../../akrr/template
cp template.app.conf $APPKER.app.conf
```

Now we should have two files

* $AKRR_SRC/akrr/default_conf/mpipi.app.conf
* $AKRR_SRC/akrr/template/mpipi.app.conf

The first one is default configuration which will be read first, the second is a 
template which will be copied to $AKRR_HOME/etc/resource/<resource name>/mpipi.app.conf and read the last. The latter
should contain parameters which often are rewritten on different resources (like walltime limit)

Here is example of $AKRR_SRC/akrr/default_conf/mpipi.app.conf :
```python
info = """MPI-Pi"""

walltime_limit = 40

parser = "generic_parser.py"

executable = "execs/mpipi/mpi_pi_reduce"
input_param = "inputs/mpipi/input_file"


# adding recourd about app to db
# mod_appkernel_app_kernel_def:
#    ak_def_id, name, ak_base_name, processor_unit, enabled, description, visible, control_criteria
# mod_akrr_appkernels:
#    id,name,nodes_list
# appkernel_id should be unique, next unique number is 39
appkernel_id = 39
db_setup = {
    "mod_appkernel_app_kernel_def":
        (appkernel_id, 'MPI-Pi', 'mpipi', 'node', 0,
         """Calculate Pi using MC method""", 0,
         None),
    "mod_akrr_appkernels": (appkernel_id, 'mpipi', '1;2;4;8')
}
```
Here is example of $AKRR_SRC/akrr/template/mpipi.app.conf :
```python
appkernel_run_env_template = """
# Load application environment
module load intel
module load intel-mpi
module list

# make srun works with intel mpi
export I_MPI_PMI_LIBRARY=/usr/lib64/libpmi.so

# set how to run app kernel
EXE={appkernel_dir}/{executable}
RUN_APPKERNEL="srun $EXE input_file"
"""

# nodes count where this appkernel can run by default
# num_of_nodes = [1, 2, 4, 8]
```
This file should contain parameters which final user will most likely modified.

At first we will just use the standard parser which will only give us the walltime and the nodes on which the application kernel was executed. Later
on we will customize the mpi_pi specialized parser.

## Add resource specific instruction to AKRR

Now we need to create specific instructions how to execute the app kernel on that particular resource (localhost):

``` bash
# on AKRR server machine
akrr app add -r localhost -a mpipi
# edit new config, note that it was initiated from $AKRR_SRC/akrr/template/mpipi.app.conf
vi /home/nikolays/xdmod_wsp/akrr/devel_local/etc/resources/localhost/mpipi.app.conf
```
Here is example of /home/nikolays/xdmod_wsp/akrr/devel_local/etc/resources/localhost/mpipi.app.conf :
```python
appkernel_run_env_template = """
# Load application environment

# set how to run app kernel
EXE={appkernel_dir}/{executable}
RUN_APPKERNEL="mpirun -n $AKRR_CORES $EXE input_file"
"""
```

Now we can make a first validation run

```
# check batch script, the following command will generate batch script and show it in output
akrr task new -n 1 -r localhost -a mpipi --dry-run --gen-batch-job-only

# looks good lets run it
akrr app validate -n 1 -r localhost -a mpipi
```

Output example:
```
[INFO] Validating mpipi application kernel installation on localhost
[INFO] ################################################################################
[INFO] Validating localhost parameters from /home/nikolays/xdmod_wsp/akrr/devel_local/etc/resources/localhost/resource.conf
[INFO] Syntax of /home/nikolays/xdmod_wsp/akrr/devel_local/etc/resources/localhost/resource.conf is correct and all necessary parameters are present.
{'appkernel_run_env_template': '\n'
                               '# Load application environment\n'
                               '# module load intel\n'
                               '# module load intel-mpi\n'
                               '# module list\n'
                               '\n'
                               '# make srun works with intel mpi\n'
                               '# export '
                               'I_MPI_PMI_LIBRARY=/usr/lib64/libpmi.so\n'
                               '\n'
                               '# set how to run app kernel\n'
                               'RUN_APPKERNEL="mpirun -n $AKRR_CORES '
                               '{appkernel_dir}/{executable}"\n',
 'name': 'mpipi',
 'nickname': 'mpipi.@nnodes@',
 'resource_specific_app_cfg_file_last_mod_time': 1658252355.1988027,
 'resource_specific_app_cfg_filename': '/home/nikolays/xdmod_wsp/akrr/devel_local/etc/resources/localhost/mpipi.app.conf'}
[INFO] Syntax of /home/nikolays/xdmod_wsp/akrr/akrr/default_conf/mpipi.app.conf is correct and all necessary parameters are present.
[INFO] ################################################################################
[INFO] Validating resource accessibility. Connecting to localhost.
================================================================================
[INFO] Successfully connected to localhost


[INFO] Checking directory locations

[INFO] Checking: localhost:/home/nikolays/xdmod_wsp/akrr/devel_local/akrr_data
[INFO] Directory exist and accessible for read/write

[INFO] Checking: localhost:/home/nikolays/xdmod_wsp/akrr/devel_local/appker
[INFO] Directory exist and accessible for read/write

[INFO] Checking: localhost:/tmp
[INFO] Directory exist and accessible for read/write
[INFO] 
[INFO] Checking: localhost:/tmp
[INFO] Directory exist and accessible for read/write
[INFO] 
[INFO] ################################################################################
[INFO] Will send test job to queue, wait till it executed and will analyze the output
Will use AKRR REST API at https://localhost:8091/api/v1
[INFO] 
Submitted test job to AKRR, task_id is 3144530



================================================================================
Tast status:
Task is in scheduled_tasks queue.
It schedule to be started on 2022-07-19T13:42:31

time: 2022-07-19 13:42:31 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Created batch job script and have submitted it to remote queue.
Status info:
Remote job ID is 82518

time: 2022-07-19 13:42:42 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Not in queue. Either exited with error or executed successfully. Copied all files to local machine. Deleted all files from remote machine
Status info:
Not in queue. Either exited with error or executed successfully. Copied all files to local machine. Deleted all files from remote machine

time: 2022-07-19 13:42:47 

================================================================================
Tast status:
Task is in active_tasks queue.
Status: Task was completed successfully.
Status info:
Done

time: 2022-07-19 13:42:52 

================================================================================
Tast status:
Task is completed!
        status: 1
        status_info: Done

time: 2022-07-19 13:42:57 [INFO] Test job is completed analyzing output

[INFO] 
Test kernel execution summary:
status: 1
status_info: Done
processing message:
None
Local working directory for this task: /home/nikolays/xdmod_wsp/akrr/devel_local/log/comptasks/localhost/mpipi/2022/07/2022.07.19.13.42.32.638320
Location of some important generated files:
        Batch job script: /home/nikolays/xdmod_wsp/akrr/devel_local/log/comptasks/localhost/mpipi/2022/07/2022.07.19.13.42.32.638320/jobfiles/mpipi.job
        Application kernel output: /home/nikolays/xdmod_wsp/akrr/devel_local/log/comptasks/localhost/mpipi/2022/07/2022.07.19.13.42.32.638320/jobfiles/appstdout
        Batch job standard output: /home/nikolays/xdmod_wsp/akrr/devel_local/log/comptasks/localhost/mpipi/2022/07/2022.07.19.13.42.32.638320/jobfiles/stdout
        Batch job standard error output: /home/nikolays/xdmod_wsp/akrr/devel_local/log/comptasks/localhost/mpipi/2022/07/2022.07.19.13.42.32.638320/jobfiles/stderr
        XML processing results: /home/nikolays/xdmod_wsp/akrr/devel_local/log/comptasks/localhost/mpipi/2022/07/2022.07.19.13.42.32.638320/result.xml
        Task execution logs: /home/nikolays/xdmod_wsp/akrr/devel_local/log/comptasks/localhost/mpipi/2022/07/2022.07.19.13.42.32.638320/proc/log


[INFO] 
Enabling mpipi on localhost for execution

[INFO] Successfully enabled mpipi on localhost
[INFO] 
DONE, you can move to next step!
```

If the last command executed successfully then even with the generic parser we already can use that app kernel

Record the location of job files directory (e.g. /home/nikolays/xdmod_wsp/akrr/devel_local/log/comptasks/localhost/mpipi/2022/07/2022.07.19.13.42.32.638320/jobfiles) we will use for parser
development.

## Create a customized parser for new application kernel

Until now we have been using a default parser which only gives walltime and the execution node names. However we want to add more
parameters and metrics to be monitored. In order to do so we need to create a customized parser.
Initialize the new parser from generic parser:

```bash
#on AKRR server, get to parsers directory
cd $AKRR_SRC/akrr/parsers
# Initiate new parser from generic parser
cp generic_parser.py mpipi_parser.py
```

Examine mpipi_parser.py. You need to modify the processAppKerOutput function to include custom output processing. The processAppKerOutput function consists of
several parts:
1. Parser initiation
2. Setting of obligatory parameters and statistics
3. Processing of application output

### Processing of application output

The idea is to read application output (the output file
set from appstdout argument) and with the help of regular expressions extract the parameters and metrics which we need.
Here is a sample output form the mpipi application

```
Here is sample output:
MPI task 0 has started...
MPI task 1 has started...
MPI task 2 has started...
MPI task 3 has started...
MPI task 5 has started...
MPI task 4 has started...
version: 2015.3.9
number of throws at dartboard: 5000000
number of rounds for dartz throwing 100
After 5000000 throws, average value of pi = 3.14172000
After 10000000 throws, average value of pi = 3.14158253
....
After 495000000 throws, average value of pi = 3.14158363
After 500000000 throws, average value of pi = 3.14158676
Real value of PI: 3.1415926535897
Time for PI calculation: 8.011
Giga Darts Throws per Second (GDaPS): 0.374
```

Bellow is table of what we want to extract:

| Name                    | Units   | Parameter or Statistics | Line in output                              |
|-------------------------|---------|-------------------------|---------------------------------------------|
| App:Version             | -       | Parameter               | version: 2015.3.9                           |
| Number of Darts Throws  | -       | Parameter               | number of throws at dartboard: 5000000      |
| Number of Rounds        | -       | Parameter               | number of rounds for dartz throwing 100     |
| Time for PI Calculation | Seconds | Statistics              | Time for PI calculation: 8.011              |
| Darts Throws per Second | GDaPS   | Statistics              | Giga Darts Throws per Second (GDaPS): 0.374 |

The parser can be immediately tested on our previous run:

```bash
# on AKRR server
PYTHONPATH=$AKRR_SRC:$PYTHONPATH python $AKRR_SRC/akrr/parsers/generic_parser.py \
$AKRR_HOME/log/comptasks/localhost/mpipi/2022/07/2022.07.19.13.42.32.638320/jobfiles
# note that you might need to set PYTHONPATH
```


The output of generic parser is:

```
Parsing complete: True
Following statistics and parameter can be set as obligatory:
parser.add_must_have_parameter('App:ExeBinSignature')
parser.add_must_have_parameter('RunEnv:Nodes')

parser.add_must_have_statistic('Wall Clock Time')

Resulting XML:
<?xml version="1.0" ?>
<rep:report xmlns:rep="report">
  <body>
    <performance>
      <ID>unknown</ID>
      <benchmark>
        <ID>unknown</ID>
        <parameters>
          <parameter>
            <ID>App:ExeBinSignature</ID>
            <value>H4sIAAAAAAACAx3ISw7CIBAA0H1PMSeYoWD87V034QJkWsZIyi9Qtb29iW/5HtZO9g70Kkkoh7VEPjrtPhXvvr0Sr62Rl49EF8vC8R/O88aUaqiBtNIa1QXHG44GTxqNxrO5Gq0IEUKHXDbgDLLL8t54jgJzyNwOeIYow/ADDdY5a4EAAAA=</value>
          </parameter>
          <parameter>
            <ID>RunEnv:Nodes</ID>
            <value>H4sIAAAAAAACA8vJT07MycgvLlHIoQaLCwBCA43+UAAAAA==</value>
          </parameter>
        </parameters>
        <statistics>
          <statistic>
            <ID>Wall Clock Time</ID>
            <value>1.0</value>
            <units>Second</units>
          </statistic>
        </statistics>
      </benchmark>
    </performance>
  </body>
  <exitStatus>
    <completed>true</completed>
  </exitStatus>
</rep:report>
```
The XML at the end will be eventually dumped to DB for further ingestion by OpenXDMoD.
Now, modify the output parsing part. Note the parser.successfulRun variable it should be set to true if a measure of successful execution was
found and to false otherwise. After output processing is done you also can add parser.setMustHaveParameter and parser.setMustHaveStatistic. If
the parameters/statistics specified by such function are not set the parser will treat the run as a failure. This way we try to ensure that
all necessary metrics are set.

The final parser looks like(mpipi_parser.py):

```python
# Generic Parser
import re
import os
import sys
from akrr.parsers.akrrappkeroutputparser import AppKerOutputParser


def process_appker_output(appstdout=None, stdout=None, stderr=None, geninfo=None, proclog=None, 
                          resource_appker_vars=None):
    # set App Kernel Description
    if resource_appker_vars is not None and 'app' in resource_appker_vars and 'name' in resource_appker_vars['app']:
        akname = resource_appker_vars['app']['name']
    else:
        akname = 'unknown'

    # initiate parser
    parser = AppKerOutputParser(
        name=akname
    )
    # set obligatory parameters and statistics
    # set common parameters and statistics (App:ExeBinSignature and RunEnv:Nodes)
    parser.add_common_must_have_params_and_stats()
    # set app kernel custom sets
    parser.add_must_have_parameter('App:ExeBinSignature')
    parser.add_must_have_parameter('App:Version')
    parser.add_must_have_parameter('Number of Darts Throws')
    parser.add_must_have_parameter('Number of Rounds')
    parser.add_must_have_parameter('RunEnv:Nodes')

    parser.add_must_have_statistic('Darts Throws per Second')
    parser.add_must_have_statistic('Time for PI Calculation')
    parser.add_must_have_statistic('Wall Clock Time')

    # parse common parameters and statistics
    parser.parse_common_params_and_stats(appstdout, stdout, stderr, geninfo)

    if hasattr(parser, 'appKerWallClockTime'):
        parser.set_statistic("Wall Clock Time", parser.appKerWallClockTime.total_seconds(), "Second")

    # Here can be custom output parsing
    # read output
    lines = []
    if os.path.isfile(appstdout):
        fin = open(appstdout, "rt")
        lines = fin.readlines()
        fin.close()

    # process the output
    parser.successfulRun = False
    j = 0
    while j < len(lines):
        m = re.search(r'version:\s+(.+)', lines[j])
        if m:
            parser.set_parameter('App:Version', m.group(1))

        m = re.search(r'number of throws at dartboard:\s+(\d+)', lines[j])
        if m:
            parser.set_parameter('Number of Darts Throws', m.group(1))

        m = re.search(r'number of rounds for dartz throwing\s+(\d+)', lines[j])
        if m:
            parser.set_parameter('Number of Rounds', m.group(1))

        m = re.search(r'Time for PI calculation:\s+([0-9.]+)', lines[j])
        if m:
            parser.set_statistic("Time for PI Calculation", m.group(1), "Seconds")

        m = re.search(r'Giga Darts Throws per Second \(GDaPS\):\s+([0-9.]+)', lines[j])
        if m:
            parser.set_statistic("Darts Throws per Second", m.group(1), "GDaPS")

        m = re.search(r'Giga Darts Throws per Second', lines[j])
        if m:
            parser.successfulRun = True

        j += 1

    if __name__ == "__main__":
        # output for testing purpose
        print(("Parsing complete:", parser.parsing_complete(verbose=True)))
        print("Following statistics and parameter can be set as obligatory:")
        parser.print_params_stats_as_must_have()
        print("\nResulting XML:")
        print((parser.get_xml()))

    # return complete XML otherwise return None
    return parser.get_xml()


if __name__ == "__main__":
    """stand alone testing"""
    jobdir = sys.argv[1]
    print("Proccessing Output From", jobdir)
    process_appker_output(appstdout=os.path.join(jobdir, "appstdout"), geninfo=os.path.join(jobdir, "gen.info"))
```


Now we can have the mpipi application kernel use mpipi_parser.py. Modify the parser variable in $AKRR_SRC/akrr/default_conf/mpipi.app.conf :
```python
info = """MPI-Pi"""

walltime_limit = 40

parser = "mpipi_parser.py"
...
```

```
# run new appkernel
akrr app validate -n 1 -r localhost -a mpipi
```

Finally we need to copy the resource specific application kernel configuration to the template directory to reuse it in the future for deployment on a
different resource
```
# on AKRR server
cd $AKRR_SRC/akrr/appker_repo/inputs
# make new directory for application kernel input
mkdir -p mpipi
# copy input
cp $AKRR_APPKER_DIR/inputs/mpipi/input_file mpipi

#pack input.tar.gz
cd $AKRR_SRC/akrr/appker_repo
tar -zcvf input.tar.gz input
```

## Deployment of Application Kernel on a Different Resource
Done as any other appkernel now.
