#! /usr/bin/env bash


# FIND: the directory in which this script resides.
declare -r __DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )";

declare -r __SRC_DIR="${__DIR}/../src/"

declare -r __DATA_DIR="${__DIR}/../data/"

declare PYTHON_APP=""

function load_environment {

    if [ -f ../cfg/install.conf ]
    then
        source ../cfg/install.conf
    else
        PYTHON_APP=`which python`
    fi

}

load_environment

cd ${__SRC_DIR}
${PYTHON_APP} akrrscheduler.py -a -o ${__DATA_DIR}checknrestart stop
${PYTHON_APP} akrrscheduler.py -a -o ${__DATA_DIR}checknrestart start

