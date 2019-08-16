# Deploying various application kernels on OpenStack

This assumes that you have already set up OpenStack with the Docker volume, as well as set up AKRR with OpenStack.

Most setups are pretty straightforward, since you just start docker, pull the docker image, and run it.

Usually you can just run the Docker image normally, since it should identify how many cpus you have, but there are flags that allow you to specify how many processes mpirun starts.

For each of these you do the regular command to add an appkernel.
```bash
akrr app add -a $APPKER -r $OPENSTACK_RESOURCE
```

Then you just have to modify the config file that gets created.

Note that I pull from pshoff/akrr_benchmarks (my repo on docker hub) but you need to specify the appropriate Docker repo for you.

I put example config files for the corresponding Appkernels below:


### HPCC:
```bash
appkernel_run_env_template = """
sudo systemctl start docker
docker pull pshoff/akrr_benchmarks:hpcc
RUN_APPKERNEL="docker run --rm pshoff/akrr_benchmarks:hpcc"
"""
```

### HPCG:
```bash
appkernel_run_env_template = """
sudo systemctl start docker
docker pull pshoff/akrr_benchmarks:hpcg
RUN_APPKERNEL="docker run --rm pshoff/akrr_benchmarks:hpcg"
"""

```

### NAMD:
```bash
appkernel_run_env_template = """
sudo systemctl start docker
docker pull pshoff/akrr_benchmarks:namd
RUN_APPKERNEL="docker run --rm pshoff/akrr_benchmarks:namd"
"""
```

### NWChem:
```bash
appkernel_run_env_template = """
sudo systemctl start docker
docker pull pshoff/akrr_benchmarks:nwchem

# adding the shm-size 
# the cap-add to not print all the errors that are being given
RUN_APPKERNEL="docker run --rm --shm-size 8g --cap-add=SYS_PTRACE pshoff/akrr_benchmarks:nwchem"
"""
```

### GAMESS:
```bash
appkernel_run_env_template = """
# start docker daemon
sudo systemctl start docker

# get the updated images (can be skipped if you already have the image on the volume)
docker pull pshoff/akrr_benchmarks:gamess

# runs the docker image 
RUN_APPKERNEL="docker run --rm pshoff/akrr_benchmarks:gamess"
"""
```

### IOR:
It's a bit more complicated for IOR since we want to clear caches in between runs, so you set things up slightly differently:
```bash

# which IO API/formats to check                                                                       
testPOSIX = True                                                                                      
testMPIIO = False                                                                                     
testHDF5 = True                                                                                       
testNetCDF = True                                                                                     
                                                                                                      
# setting false up here so we can just run on one node                                                
appkernel_requests_two_nodes_for_one = False                                                          
                                                                                                      
# will do write test first and after that read, that minimize the caching impact from storage nodes   
# require large temporary storage easily 100s GiB                                                     
doAllWritesFirst = True                                                                               
                                                                                                      
appkernel_run_env_template = """                                                                      
set -x                                                                                                
sudo systemctl start docker                                                                           
                                                                                                      
export DOCKER_IMAGE=pshoff/akrr_benchmarks:ior_mdtest                                                 
docker pull $DOCKER_IMAGE                                                                             
EXE="docker run -v $AKRR_TMP_WORKDIR:$AKRR_TMP_WORKDIR --rm $DOCKER_IMAGE --run-ior -ppn $AKRR_CORES" 
                                                                                                      
free -h                                                                                               
# to get appsig                                                                                       
docker run --rm $DOCKER_IMAGE --ior-appsig >> $AKRR_APP_STDOUT_FILE 2>&1                              
                                                                                                      
echo "sync; echo 3 > /proc/sys/vm/drop_caches" > drop_caches.sh                                       
export SCRIPT_DIR=`pwd`                                                                               

# set how to run mpirun on all nodes
for node in $AKRR_NODELIST; do echo $node>>all_nodes; done
# putting nothing here bc further down we don't want to use it really
RUNMPI=""

# set how to run mpirun on all nodes with offset, first print all nodes after node 1 and then node 1
sed -n "$(($AKRR_CORES_PER_NODE+1)),$(($AKRR_CORES))p" all_nodes > all_nodes_offset
sed -n "1,$(($AKRR_CORES_PER_NODE))p" all_nodes >> all_nodes_offset
# same for this run
RUNMPI_OFFSET=""
"""


# new variable so you can clear caches
runIORTestsWriteReadCyclic = """
for TEST_PARAM in "${{TESTS_LIST[@]}}"
do
    echo "# Starting Test: $TEST_PARAM" >> $AKRR_APP_STDOUT_FILE 2>&1
    fileName=`echo ior_test_file_$TEST_PARAM |tr  '-' '_'|tr  ' ' '_'|tr  '=' '_'`

    #run the test
    command_to_run="$RUNMPI $EXE $COMMON_PARAM $TEST_PARAM -o $AKRR_TMP_WORKDIR/$fileName"
    
    echo "Before cache clear:"
    free -h
    sudo bash $SCRIPT_DIR/drop_caches.sh
    echo "After cache clear:"
    free -h
    echo "executing: $command_to_run" >> $AKRR_APP_STDOUT_FILE 2>&1
    $command_to_run >> $AKRR_APP_STDOUT_FILE 2>&1
    done
"""

runIORTestsAllWritesFirst = """
#do write first
for TEST_PARAM in "${{TESTS_LIST[@]}}"
do
    echo "# Starting Test: $TEST_PARAM" >> $AKRR_APP_STDOUT_FILE 2>&1
    fileName=`echo ior_test_file_$TEST_PARAM |tr  '-' '_'|tr  ' ' '_'|tr  '=' '_'`

    #run the test
    command_to_run="$RUNMPI $EXE $COMMON_PARAM $TEST_PARAM -w -k -o $AKRR_TMP_WORKDIR/$fileName"

    echo "Before cache clear:"
    free -h
    sudo bash $SCRIPT_DIR/drop_caches.sh
    echo "After cache clear:"
    free -h
    
    echo "executing: $command_to_run" >> $AKRR_APP_STDOUT_FILE 2>&1
    $command_to_run >> $AKRR_APP_STDOUT_FILE 2>&1
done
#do read last
for TEST_PARAM in "${{TESTS_LIST[@]}}"
do
    echo "# Starting Test: $TEST_PARAM" >> $AKRR_APP_STDOUT_FILE 2>&1
    fileName=`echo ior_test_file_$TEST_PARAM |tr  '-' '_'|tr  ' ' '_'|tr  '=' '_'`

    # run test
    command_to_run="$RUNMPI_OFFSET $EXE $COMMON_PARAM $TEST_PARAM -r -o $AKRR_TMP_WORKDIR/$fileName"

    echo "Before cache clear:"
    free -h
    sudo bash $SCRIPT_DIR/drop_caches.sh
    echo "After cache clear:"
    free -h
    
    echo "executing: $command_to_run" >> $AKRR_APP_STDOUT_FILE 2>&1
    $command_to_run >> $AKRR_APP_STDOUT_FILE 2>&1
done
"""


runIORTestsWriteReadCyclicOneNode = """
for TEST_PARAM in "${{TESTS_LIST[@]}}"
do
    echo "# Starting Test: $TEST_PARAM" >> $AKRR_APP_STDOUT_FILE 2>&1
    fileName=`echo ior_test_file_$TEST_PARAM |tr  '-' '_'|tr  ' ' '_'|tr  '=' '_'`

    #run the test
    command_to_run="$RUNMPI $EXE $COMMON_PARAM $TEST_PARAM -w -k -o $AKRR_TMP_WORKDIR/$fileName"

    echo "Before cache clear:"
    free -h
    sudo bash $SCRIPT_DIR/drop_caches.sh
    echo "After cache clear:"
    free -h

    echo "executing: $command_to_run" >> $AKRR_APP_STDOUT_FILE 2>&1
    $command_to_run >> $AKRR_APP_STDOUT_FILE 2>&1

    command_to_run="$RUNMPI_OFFSET $EXE $COMMON_PARAM $TEST_PARAM -r -o $AKRR_TMP_WORKDIR/$fileName"

    echo "Before cache clear:"
    free -h
    sudo bash $SCRIPT_DIR/drop_caches.sh
    echo "After cache clear:"
    free -h

    echo "executing: $command_to_run" >> $AKRR_APP_STDOUT_FILE 2>&1
    $command_to_run >> $AKRR_APP_STDOUT_FILE 2>&1
done
"""

runIORTestsAllWritesFirstOneNode = """
#do write first
for TEST_PARAM in "${{TESTS_LIST[@]}}"
do
    echo "# Starting Test: $TEST_PARAM" >> $AKRR_APP_STDOUT_FILE 2>&1
    fileName=`echo ior_test_file_$TEST_PARAM |tr  '-' '_'|tr  ' ' '_'|tr  '=' '_'`

    #run the tests
    command_to_run="$RUNMPI $EXE $COMMON_PARAM $TEST_PARAM -w -k -o $AKRR_TMP_WORKDIR/$fileName"

    #clearing cache
    echo "Before cache clear:"
    free -h
    sudo bash $SCRIPT_DIR/drop_caches.sh
    echo "After cache clear:"
    free -h

    echo "executing: $command_to_run" >> $AKRR_APP_STDOUT_FILE 2>&1
    $command_to_run >> $AKRR_APP_STDOUT_FILE 2>&1
done
#do read last
for TEST_PARAM in "${{TESTS_LIST[@]}}"
do
    echo "# Starting Test: $TEST_PARAM" >> $AKRR_APP_STDOUT_FILE 2>&1
    fileName=`echo ior_test_file_$TEST_PARAM |tr  '-' '_'|tr  ' ' '_'|tr  '=' '_'`

    #run the tests
    command_to_run="$RUNMPI_OFFSET $EXE $COMMON_PARAM $TEST_PARAM -r -o $AKRR_TMP_WORKDIR/$fileName"
    
    # clearing cache
    echo "Before cache clear:"
    free -h
    sudo bash $SCRIPT_DIR/drop_caches.sh
    echo "After cache clear:"
    free -h


    echo "executing: $command_to_run" >> $AKRR_APP_STDOUT_FILE 2>&1
    $command_to_run >> $AKRR_APP_STDOUT_FILE 2>&1
done
"""
```
Notice how it's calling drop_caches.sh (see the ior docker directory scripts for what it might look like)
 
### MDTest:
Also slightly different since it's using the ior_mdtest docker
```bash
appkernel_run_env_template = """

export I_MPI_PMI_LIBRARY=/usr/lib64/libpmi.so

# setting up docker
sudo systemctl start docker
export DOCKER_IMAGE=pshoff/akrr_benchmarks:ior_mdtest
docker pull $DOCKER_IMAGE
# set executable location
EXE="docker run --rm $DOCKER_IMAGE -ppn $AKRR_CORES --run-mdtest"

# to get app signature
docker run --rm $DOCKER_IMAGE--mdtest-appsig >> $AKRR_APP_STDOUT_FILE 2>&1

# set how to run app kernel - not using this bc using mpirun inside docker
RUNMPI=""
"""


```

Then you can do the validation.
```bash
akrr app validate -a $APPKER -r $OPENSTACK_RESOURCE
```

