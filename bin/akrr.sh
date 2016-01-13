#! /usr/bin/env bash


# FIND: the directory in which this script resides.
declare -r __DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )";

declare -r __HOME_DIR="${__DIR}/../"

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

#echo "ARG:$@"
${PYTHON_APP} ${__HOME_DIR}/src/akrrscheduler.py $@

