#! /usr/bin/env bash

###############################################################################
#  Author: Ryan Rathsam
# Created: 2014.09.19
# Description: This script will be the entry point for the 'akrr_template_generation.py' script.
###############################################################################

# Setting this so that it actually exists when we call 'exit 1'
set -e

###############################################################################
# GLOBAL VARIABLES
###############################################################################

# DEFINE: the directory in which this script lives.
declare -r __SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )";

# DEFINE: the default location of our resource templates
declare -r __DEFAULT_RESOURCE_DIR="${__SCRIPT_DIR}/../cfg/resources/";

# DEFINE: the list of queueing systems that we're going to support.
declare -r __DEFAULT_QUEUEING_SYSTEMS="pbs slurm";

# DEFINE: a space delimited string of files required by the script.
declare -r FILES="${__SCRIPT_DIR}/init_new_resource.py ${__SCRIPT_DIR}/../../cfg/akrr.inp.py ${__SCRIPT_DIR}/../../src/templates/template.pbs.inp.py ${__SCRIPT_DIR}/../../src/templates/template.slurm.inp.py"

# DEFINE: the python script that this bash script fronts.
declare -r SCRIPT="${__SCRIPT_DIR}/init_new_resource.py"

# DEFINE: the configuration directory
declare -r __CFG_DIR="${__SCRIPT_DIR}/../../cfg/"

# DEFINE: the default config file.
declare -r __CFG_FILE="${__CFG_DIR}install.conf"

# DEFINE: the default python ( aka. which python is found on the $PATH )
declare -r __DEFAULT_PYTHON=$(which python)

# DEFINE: a variable to hold which python executable we'll be using. ( this one is mutable as it could be user
#         supplied ).
declare python_app=""

# DEFINE: a variable to hold whether or not we were actually successful. ( also mutable due to it's very nature )
declare __SUCCESS=0

declare -r __ARGUMENTS="$@"

###############################################################################
# IMPORTS
###############################################################################
source ${__SCRIPT_DIR}/../utils/logging.sh

###############################################################################
# METHODS
###############################################################################

##
# Attempt to load the installation configuration file. If the directory does
# exist but the file does not, create the file. If the directory does not exist
# then freak out.
##
function load_config {
    info "Attempting to load installation configuration..."
    if [ -d ${__CFG_DIR} ]
    then
        if [ -f ${__CFG_FILE} ]
        then
            source ${__CFG_FILE}
            python_app=${PYTHON_APP}
            info "configuration loaded!"
        else
            touch ${__CFG_FILE}
            info "configuration created!"
        fi
    else
        error "unable to find config directory: $__CFG_DIR" >&2
        exit 1
    fi
}


##
# Inspect the '__SUCCESS' variable at the end of the script run to determine whether or not
# the process has completed successfully or not.
# This function will be called when any of the following signals are received: EXIT, SIGQUIT, SIGKILL, SIGTERM.
##
function clean_up {
   if [ ${__SUCCESS} -eq 0 ]
   then
       warning "Something went horribly wrong...Please check previous messages." >&2
       error "Templates Not Generated!">&2
   else
       info "Templates Generated Successfully!"
   fi
}

##
# Loops through all of the files in 'FILES' checking to see if they exist. If not then it exists after alerting the
# user to their absence.
##
function ensure_files_exist {
    for file in ${FILES}
    do
        if [ ! -f ${file} ]
        then
            error "Unable to find $file"
            exit 1
        fi
    done
}

##
# Determine which python the user wishes to use for this installation.
##
function determine_python_location {
    if [ -z "${python_app}" ]
    then
        input "Please specify a path to the python binary you want to use:\n[${__DEFAULT_PYTHON}]\c"
        read python_path

        if [ -z "${python_path}" -a -z "${__DEFAULT_PYTHON}" ]
        then
            error "An installation of Python is required to continue.";
        elif [ -z "${python_path}" -a -z "${python_app}" ]
        then
           python_app=${__DEFAULT_PYTHON}
           echo -e "python_app=\"${python_app}\"" >> ${__CFG_FILE}
        fi
    fi
}



function check_python_version {

    info "Checking python version..."
    python_output=$(${python_app} --version 2>&1)

    while IFS=' ' read -ra ADDR; do
        python_version=${ADDR[1]}

        while IFS='.' read -ra VERSION; do
            major=${VERSION[0]}
            minor=${VERSION[1]}
            micro=${VERSION[2]}

            if [ ${major} -eq 2 ]
            then
                if [ ${minor} -ge 6 ]
                then
                    info "Your python version is just right!"
                else
                    error "AKRR requires a Python version of 2.6.0+"
                fi
            else
                error "AKRR requires a Python version of 2.6.0+"
            fi
        done <<< "$python_version"

    done <<< "$python_output"
}

##
# Execute the generate_templates script.
##
function execute_script {
    # Start by executing the selected python binary, passing in the script and any command line arguments provided by
    # the user.

    ${python_app} ${SCRIPT} ${__ARGUMENTS} >&1

    # inspect the return code of the script run. Set our internal SUCCESS variable accordingly.
    if [ $? -eq 0 ]
    then
        __SUCCESS=1
    else
        __SUCCESS=0
    fi
}

function clean_up {
 if [ ${__SUCCESS} -eq 0 ]
    then
        warning "Something went horribly wrong...Please Check previous messages." >&2
        error "Templates Not Generated." >&2
    fi
}
# Ensure that the cleanup function always executes
trap "clean_up" EXIT SIGQUIT SIGKILL SIGTERM

###############################################################################
# BEGIN SCRIPT EXECUTION
###############################################################################

# Make sure that we include the optional install.conf file
load_config

# Ensure that the required files are present
ensure_files_exist

# Determine where python lives on this systemd
determine_python_location

# Check that the python version we need exists
check_python_version

# Execute the template generation script.
execute_script
