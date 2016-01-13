#! /usr/bin/env bash

###############################################################################
#      Author: Ryan Rathsam
#     Created: 2014.09.19
# Description: Logging for bash scripts.
#
###############################################################################

###############################################################################
# GLOBAL VARIABLES
###############################################################################

# DEFINE: the directory in which this script currently residesx
__DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# INCLUDE: the colorization util library.
source ${__DIR}/colorization.sh

# RE-DEFINE: the directory in which this script currently residesx
__DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

###############################################################################
# METHODS
###############################################################################

##
# Log an 'error' to stdout in the format: [ERROR]: error_msg
##
function error {
    local -r msg=$1; shift;
    local -r result="[$(red "ERROR")]: $msg";
    echo -e "$result";
}

##
# Log a 'warning' to stdout in the format: [WARNING]: warning_msg
##
function warning {
    local -r msg=$1; shift;
    local -r result="[$(yellow "WARNING")]: $msg";
    echo -e "$result";
}

##
# Log an 'informational' message to stdout in the format: [INFO]: msg
##
function info {
    local -r msg=$1; shift;
    local -r result="[$(green "INFO")]: $msg";
    echo -e "$result";
}

##
# Log a 'debug' message to stdout in the format: [DEBUG]: msg
##
function debug {
    loca l -r msg=$1; shift;
    local -r result="[$(blue "DEBUG")]: $msg";
    echo -e "$result";local -r msg=$1; shift;
}

##
# Write out an 'input' message to stdout in the format: [INPUT]: msg
##
function input {
     local -r msg=$1; shift;
     local -r result="[$(purple "INPUT")]: $msg";
     echo -e "$result";
}

##
# Write out a 'success' message to stdout in the format: [SUCCESS]: msg
##
function success {
    local -r msg=$1; shift;
    local -r result="[$(green "SUCCESS")]: $msg";
    echo -e "$result";
}