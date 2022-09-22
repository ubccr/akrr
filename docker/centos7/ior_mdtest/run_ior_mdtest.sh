#!/bin/bash
PACKAGE_NAME=ior
APPKER=ior
EXE_FILENAME=ior
DEFAULT_CONFIGURATION=icc_impi


#set striping for lustre file system
RESOURCE_SPECIFIC_OPTION_N_to_1=""
RESOURCE_SPECIFIC_OPTION_N_to_N=""

#other resource specific options
RESOURCE_SPECIFIC_OPTION=""

#blockSize and transferSize
COMMON_TEST_PARAM="-b 200m -t 20m"

IOR_EXTRA="-M 80%"

#2 level of verbosity, don't clear memory
COMMON_OPTIONS="-vv -e -Y"
CACHING_BYPASS="-Z"

#list of test to perform
TESTS_LIST=("-a POSIX $RESOURCE_SPECIFIC_OPTION_N_to_1"
"-a POSIX -F $RESOURCE_SPECIFIC_OPTION_N_to_N"
"-a MPIIO $RESOURCE_SPECIFIC_OPTION_N_to_1"
"-a MPIIO -c $RESOURCE_SPECIFIC_OPTION_N_to_1"
"-a MPIIO -F $RESOURCE_SPECIFIC_OPTION_N_to_N"
"-a HDF5 $RESOURCE_SPECIFIC_OPTION_N_to_1"
"-a HDF5 -c $RESOURCE_SPECIFIC_OPTION_N_to_1"
"-a HDF5 -F $RESOURCE_SPECIFIC_OPTION_N_to_N"
"-a NCMPI $RESOURCE_SPECIFIC_OPTION_N_to_1"
"-a NCMPI -c $RESOURCE_SPECIFIC_OPTION_N_to_1")

usage_extra()
{
    cat << END
 -e APPKER [ior|mdtest] which app to rum ior or mdtest (ior by default)
END
}

post_arg_parse_call()
{
    if [[ "$APPKER" == "ior" ]]
    then
        EXE_FILENAME=ior
    elif [[ "$APPKER" == "mdtest" ]]
    then
        EXE_FILENAME=mdtest
    fi
}

copy_input()
{
    AKRR_TMP_WORKDIR=${tmp_work_dir}
    #determine filesystem for file
    canonicalFilename=`readlink -f $AKRR_TMP_WORKDIR`
    filesystem=`awk -v canonical_path="$canonicalFilename" '{if ($2!="/" && 1==index(canonical_path, $2)) print $3 " " $1 " " $2;}' /proc/self/mounts`
    echo "File System To Test: $filesystem"
}

run_appker_ior()
{
    echo "Running ior"
    AKRR_CORES=${ppn}

    RUNMPI="${MPIRUN} -np ${AKRR_CORES}"
    RUNMPI_OFFSET="${MPIRUN} -np ${AKRR_CORES}"

    AKRR_TMP_WORKDIR=${tmp_work_dir}
    EXE=${EXE_FULL_PATH}
    echo "Using $AKRR_TMP_WORKDIR for test...."

    #combine common parameters
    COMMON_PARAM="$COMMON_OPTIONS $IOR_EXTRA $RESOURCE_SPECIFIC_OPTION $CACHING_BYPASS $COMMON_TEST_PARAM"

    #determine filesystem for file
    canonicalFilename=`readlink -f $AKRR_TMP_WORKDIR`
    filesystem=`awk -v canonical_path="$canonicalFilename" '{if ($2!="/" && 1==index(canonical_path, $2)) print $3 " " $1 " " $2;}' /proc/self/mounts`
    echo "File System To Test: $filesystem"

    #do write first
    for TEST_PARAM in "${TESTS_LIST[@]}"
    do
        echo "# Starting Test: $TEST_PARAM"
        fileName=`echo ior_test_file_$TEST_PARAM |tr  '-' '_'|tr  ' ' '_'|tr  '=' '_'`

        #run the tests
        command_to_run="$RUNMPI $EXE $COMMON_PARAM $TEST_PARAM -w -k -o $AKRR_TMP_WORKDIR/$fileName"
        echo "executing: $command_to_run"
        $command_to_run
        sudo /usr/bin/time sync
    done

    if [[ -f /writable_proc/sys/vm/drop_caches ]]
    then
        sudo sh -c "/usr/bin/echo 3 > /writable_proc/sys/vm/drop_caches"
    elif [[ -f /proc/sys/vm/drop_caches ]]
    then
        sudo sh -c "/usr/bin/echo 3 > /proc/sys/vm/drop_caches"
    fi

    #do read last
    for TEST_PARAM in "${TESTS_LIST[@]}"
    do
        echo "# Starting Test: $TEST_PARAM"
        fileName=`echo ior_test_file_$TEST_PARAM |tr  '-' '_'|tr  ' ' '_'|tr  '=' '_'`

        #run the tests
        command_to_run="$RUNMPI_OFFSET $EXE $COMMON_PARAM $TEST_PARAM -r -o $AKRR_TMP_WORKDIR/$fileName"
        echo "executing: $command_to_run"
        $command_to_run
    done
}
run_appker_mdtest()
{
    echo "Running mdtest"
    AKRR_NODES=1
    AKRR_CORES=${ppn}

    RUNMPI="${MPIRUN} -np ${AKRR_CORES}"

    AKRR_TMP_WORKDIR=${tmp_work_dir}
    EXE=${EXE_FULL_PATH}
    echo "Using $AKRR_TMP_WORKDIR for test...."

    case $AKRR_NODES in
    1)
        ITER=20
        ;;
    2)
        ITER=10
        ;;
    4)
        ITER=5
        ;;
    8)
        ITER=2
        ;;
    *)
        ITER=1
        ;;
    esac

    echo "#Testing single directory"
    $RUNMPI $EXE $MDTEST_VERBOSE -I 32 -z 0 -b 0 -i $ITER

    echo "#Testing single directory per process"
    $RUNMPI $EXE $MDTEST_VERBOSE -I 32 -z 0 -b 0 -i $ITER -u

    echo "#Testing single tree directory"
    $RUNMPI $EXE $MDTEST_VERBOSE -I 4 -z 4 -b 2 -i $ITER

    echo "#Testing single tree directory per process"
    $RUNMPI $EXE $MDTEST_VERBOSE -I 4 -z 4 -b 2 -i $ITER -u

}
run_appker()
{
    export I_MPI_DEBUG
    export I_MPI_PIN

    # Set I_MPI_HYDRA_BOOTSTRAP to ssh otherwise it will use different method on HPC system
    export I_MPI_HYDRA_BOOTSTRAP="ssh"
    # running hpcc with mpirun, where -np is number of cores for the machine



    if [[ "$APPKER" == "ior" ]]
    then
        run_appker_ior
    elif [[ "$APPKER" == "mdtest" ]]
    then
        run_appker_mdtest
    else
        echo "UNKNOWN APP $APPKER"
    fi
}

source "${CONT_AKRR_APPKER_DIR}/execs/bin/akrr_docker_run_appker.sh"
