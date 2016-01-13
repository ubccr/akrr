#! /usr/bin/env bash

# Setting this so that it actually exists when we call 'exit 1'
set -e


__DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# INCLUDE: Logging functionality.
source ${__DIR}/utils/logging.sh

__DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# A space delimited string of programs that our script relies on.
declare -r CMDS=""

# space delimited string of the files that our script relies on. These could be different than the INSTALL_SCRIPT
declare -r FILES="${__DIR}/akrrgenerate_tables.py"

# the python install script
declare -r INSTALL_SCRIPT="${__DIR}/akrrgenerate_tables.py"

# DEFINE: the configuration directory
declare -r __CFG_DIR="cfg/"

# DEFINE: the default config file.
declare -r __CFG_FILE="cfg/install.conf"

# DEFINE: a variable to hold which python executable we'll be using.
declare python_app=""

# DEFINE: a variable to hold whether or not we've actually installed things.
declare __SUCCESS=0

# CAPTURE: the default python binary to use in case the user doesn't want to provide one.
declare -r __DEFAULT_PYTHON=$(which python)

# CAPTURE: The provided command line arguments for later use.
declare -r __ARGUMENTS="$@"

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

# Function that ensures that all of the programs listed in the CMDS variable
# are present on the PATH or the script exits.
function ensure_programs_exist {
    for cmd in ${CMDS}
    do
        declare __SUCCESS=1
        info "Searching for $cmd in PATH..."
        type -P ${cmd} >> /dev/null &&: || {
            __SUCCESS=0
            warning "$cmd not found in PATH.">&2
            echo -e "would you like to provide one? y/n [n]\c"
            read provide

            if [ ${provide} = "" ]
            then
                provide = "n"
            fi

            if [ ${provide} = "n" ]
            then
                exit 1
            elif [ ${provide} = 'y' ]
            then
                echo -e "Please enter path for $cmd\c"
                read command_path
                if [ ! ${command_path} = "" ]
                then
                    echo -e "${cmd}_app=\"$command_path\"" >> ${__CFG_FILE}
                fi
            fi
        }
        if [ ${__SUCCESS} -eq 1 ]
        then
            info "Congratulations! $cmd was found in PATH."
        fi
    done
}

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

function determine_python_location {
    if [ -z "${python_app}" ]
    then
        input "Please specify a path to the python binary you want to use:\n[${__DEFAULT_PYTHON}]\c"
        read python_path

        if [ -z "${python_path}" -a -z "${__DEFAULT_PYTHON}" ]
        then
            error "An installation of Python is required to continue.";
        elif [ -z "${python_path}" ]
        then
           python_app=${__DEFAULT_PYTHON}
           echo -e "python_app=\"${python_path}\"" >> ${__CFG_FILE}
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

function execute_install_script {
     ${python_app} ${INSTALL_SCRIPT} ${__ARGUMENTS} >&1

    # inspect the return code of the script run. Set our internal SUCCESS variable accordingly.
    if [ $? -eq 0 ]
    then
        __SUCCESS=1
    else
        __SUCCESS=0
    fi
}

# Function that will be executed when the script exist.
function clean_up {
    if [ ${__SUCCESS} -eq 0 ]
    then
        warning "Something went horribly wrong...Please Check previous messages." >&2
        error "AKRR Not Installed." >&2
    else
        info "AKRR Installed Successfully!"
    fi
}

# Ensure that the cleanup function always executes
trap "clean_up" EXIT SIGQUIT SIGKILL SIGTERM

# Make sure that we include the optional install.conf file
load_config

# Ensure that the programs we require exist
ensure_programs_exist

# Ensure that the required files are present
ensure_files_exist

# Determine where python lives on this system
determine_python_location

# Check that the python version we need exists
check_python_version

# Execute the install script
execute_install_script

# Make sure that we set the SUCCESS flag to true if we've made it this far.
__SUCCESS=1
