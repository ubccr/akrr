#!/bin/bash
#AKRR Utilities

#function to test that directory/file presence
testFileDir () {
    if [ ! -e $1 ]
    then
        echo "AKRR:ERROR: $2 does not exists ($1)"
    fi
}
#function to test that directory is writable
testDirWritability () {
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
cat >> $AKRR_TASK_WORKDIR/gen.info << ENDOFFILE
"$1":"""$2""",
ENDOFFILE
}

#common tests for all appkernels
akrrPerformCommonTests () {
    #Check that app kernel launcher exists and is executable
    testFileDir "$AKRR_APPKERNEL_EXECUTABLE" "App kernel executable"
    testFileDir "$AKRR_APPKERNEL_INPUT" "App kernel input"
    
    #Test that all directories are writable
    testDirWritability "$AKRR_TASK_WORKDIR" "Task working directory"
    testDirWritability "$AKRR_NETWORK_SCRATCH" "Network scratch directory"
    testDirWritability "$AKRR_LOCAL_SCRATCH" "local scratch directory"
}

