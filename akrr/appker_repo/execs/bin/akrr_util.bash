#!/bin/bash
# AKRR Utilities

# Function to test that directory/file presence
akrr_test_file_dir () {
    if [ ! -e $1 ]
    then
        echo "AKRR:ERROR: $2 does not exists ($1)"
    fi
}
# Function to test that directory is writable
akrr_test_dir_writability () {
    if [ ! -e $1 ]
    then
        echo "AKRR:ERROR: $2 does not exists ($1)"
    else
        TESTFILE=`mktemp -q $1/testwritability.XXXXXX`
        if [ "$TESTFILE" == "" ]
        then
            echo "AKRR:ERROR: $2 is not writable ($1)"
        else
            if [ ! -f "$TESTFILE" ]
            then
                echo "AKRR:ERROR: $2 is not writable ($1)"
            else
                echo "this is test" >> "$TESTFILE"
                if [ "`cat \"$TESTFILE\"`" != "this is test" ]
                then
                    echo "AKRR:ERROR: $2 is not writable ($AKRR_TASK_WORKDIR)"
                fi
                rm "$TESTFILE"
            fi
        fi
    fi
}
# Function to print record to gen.info file
akrr_write_to_gen_info () {
cat >> $AKRR_TASK_WORKDIR/gen.info << ENDOFFILE
"$1":"""$2""",
ENDOFFILE
}

# Common tests for all appkernels
akrr_perform_common_tests () {
    #Check that app kernel launcher exists and is executable
    akrr_test_file_dir "$AKRR_APPKERNEL_EXECUTABLE" "App kernel executable"
    akrr_test_file_dir "$AKRR_APPKERNEL_INPUT" "App kernel input"

    #Test that all directories are writable
    akrr_test_dir_writability "$AKRR_TASK_WORKDIR" "Task working directory"
    akrr_test_dir_writability "$AKRR_NETWORK_SCRATCH" "Network scratch directory"
    akrr_test_dir_writability "$AKRR_LOCAL_SCRATCH" "local scratch directory"
}

akrr_get_number_of_cores () {
    # gets the number of cores of this machine automatically
    sockets="$(grep "physical\\sid" /proc/cpuinfo|sort|uniq|wc -l)"
    cores_per_sockets="$(grep ^cpu\\scores /proc/cpuinfo|sort|uniq|awk '{print $4}')"
    cores=$((sockets*cores_per_sockets))
    echo $cores
}

akrr_get_arch () {
    # return sse2, avx, avx2, skx or knl
    # skx is avx512f avx512dq avx512cd avx512bw avx512vl
    # knl is avx512f avx512pf avx512er avx512cd
    if [ "$(grep flags /proc/cpuinfo|head -n 1|awk '/avx512f/ && /avx512dq/ && /avx512cd/ && /avx512bw/ && /avx512vl/'|wc -l)" -eq "1" ]
    then
        echo "skx"
    elif [ "$(grep flags /proc/cpuinfo|head -n 1|awk '/avx512f/ && /avx512pf/ && /avx512er/ && /avx512cd/'|wc -l)" -eq "1" ]
    then
        echo "knl"
    elif [ "$(grep flags /proc/cpuinfo|head -n 1|grep avx2|wc -l)" -eq "1" ]
    then
        echo "avx2"
    elif [ "$(grep flags /proc/cpuinfo|head -n 1|grep avx|wc -l)" -eq "1" ]
    then
        echo "avx"
    elif [ "$(grep flags /proc/cpuinfo|head -n 1|grep sse2|wc -l)" -eq "1" ]
    then
        echo "sse2"
    else
        echo "unknown"
    fi
}

# Depricated camel-style format
# function to test that directory/file presence
testFileDir () {
    echo "AKRR:WARNING: testFileDir is depricated use akrr_test_file_dir"
    if [ ! -e $1 ]
    then
        echo "AKRR:ERROR: $2 does not exists ($1)"
    fi
}
# function to test that directory is writable
testDirWritability () {
    echo "AKRR:WARNING: testDirWritability is deprecated use akrr_test_dir_writability"
    if [ ! -e $1 ]
    then
        echo "AKRR:ERROR: $2 does not exists ($1)"
    else
        TESTFILE=`mktemp -q $1/testwritability.XXXXXX`
        if [ "$TESTFILE" == "" ]
        then
            echo "AKRR:ERROR: $2 is not writable ($1)"
        else
            if [ ! -f "$TESTFILE" ]
            then
                echo "AKRR:ERROR: $2 is not writable ($1)"
            else
                echo "this is test" >> "$TESTFILE"
                if [ "`cat \"$TESTFILE\"`" != "this is test" ]
                then
                    echo "AKRR:ERROR: $2 is not writable ($AKRR_TASK_WORKDIR)"
                fi
                rm "$TESTFILE"
            fi
        fi
    fi
}
#function to print record to gen.info file
writeToGenInfo () {
echo "AKRR:WARNING: writeToGenInfo is deprecated use akrr_write_to_gen_info"
cat >> $AKRR_TASK_WORKDIR/gen.info << ENDOFFILE
"$1":"""$2""",
ENDOFFILE
}

#common tests for all appkernels
akrrPerformCommonTests () {
    echo "AKRR:WARNING: akrrPerformCommonTests is deprecated use akrr_perform_common_tests"
    #Check that app kernel launcher exists and is executable
    testFileDir "$AKRR_APPKERNEL_EXECUTABLE" "App kernel executable"
    testFileDir "$AKRR_APPKERNEL_INPUT" "App kernel input"

    #Test that all directories are writable
    testDirWritability "$AKRR_TASK_WORKDIR" "Task working directory"
    testDirWritability "$AKRR_NETWORK_SCRATCH" "Network scratch directory"
    testDirWritability "$AKRR_LOCAL_SCRATCH" "local scratch directory"
}