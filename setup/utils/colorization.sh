#! /usr/bin/env bash

###############################################################################
#      Author: Ryan Rathsam
#     Created: 2014.09.19
# Description: Logging Colorization for bash scripts.
#
###############################################################################

###############################################################################
# GLOBAL VARIABLES
###############################################################################

# HEADER COLOR
declare -r HEADER="\e[1;35m";

# OK BLUE COLOR
declare -r BLUE="\e[0;34m";

# OK GREEN COLOR
declare -r GREEN="\e[1;32m";

# WARNING COLOR
declare -r WARNING="\e[1;33m";

# FAIL COLOR
declare -r FAIL="\e[1;31m";

# WHITE COLOR
declare -r WHITE="\e[1;37m";

# END COLOR
declare -r ENDC="\e[0m";

###############################################################################
# METHODS
###############################################################################

###############################################################################
# Color the provided 'msg' in red.
#
# @param msg - the text that should be colored red.
function red {
    local -r msg=$1; shift;
    local -r colored="${FAIL}${msg}${ENDC}";
    echo -e "$colored";
}

###############################################################################
# Color the provided 'msg' in yellow.
#
# @param msg - the text that should be colored yellow.
function yellow {
    local -r msg=$1; shift;
    local -r colored="${WARNING}${msg}${ENDC}";
    echo -e "$colored";
}

###############################################################################
# Color the provided 'msg' in green.
#
# @param msg - the text that should be colored green.
function green {
    local -r msg=$1; shift;
    local -r colored="${GREEN}${msg}${ENDC}";
    echo -e "$colored";
}

###############################################################################
# Color the provided 'msg' in blue.
#
# @param msg - the text that should be colored blue.
function blue {
    local -r msg=$1; shift;
    local -r colored="${BLUE}${msg}${ENDC}";
    echo -e "$colored"
}

###############################################################################
# Color the provided 'msg' as a header.
#
# @param msg - the text that should be colored as a header.
function purple {
    local -r msg=$1; shift;
    local -r colored="${HEADER}${msg}${ENDC}";
    echo -e "$colored";
}