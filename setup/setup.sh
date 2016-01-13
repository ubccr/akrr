#! /usr/bin/env bash

# Setting this so that it actually exists when we call 'exit 1'
set -e

# FIND: the directory in which this script resides.
__DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )";

# INCLUDE: Logging functionality.
source ${__DIR}/utils/logging.sh

# RESET: the directory in which this script resides
__DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# DECLARE: a space delimited string that contains the scripts to be executed.
declare -r __SCRIPTS="${__DIR}/scripts/setup.py"
#scripts/akrrdb_check.py ${__DIR}/scripts/akrrgenerate_tables.py";
# ${__DIR}/scripts/akrrgenerate_templates.py

# DECLARE: Daemon script
declare -r __DAEMON_SCRIPT="${__DIR}/../src/akrrscheduler.py"

# DECLARE: the check for daemon script.
declare -r __CHECK_DAEMON_SCRIPT="${__DIR}/scripts/akrrcheck_daemon.py"

# DECLARE: Daemon script parameters
declare r __DAEMON_SCRIPT_PARAMS="start"

# DEFINE: the configuration directory
declare -r __CFG_DIR="${__DIR}/../cfg/"

# DEFINE: the default config file.
declare -r __CFG_FILE="${__CFG_DIR}/install.conf"

# DEFINE: the directory in which our template cron scripts currently reside.
declare -r __CRON_DIR="${__DIR}/cron"

# DEFINE: the directory that we'll be writing our cron files to.
declare -r __CRON_DEST_DIR="/etc/cron.d"

# DEFINE: a space delimited list of our template cron scripts.
declare -r __CRON_FILES=("template_checknrestart.sh" "template_restart.sh")

# DEFINE: a variable to hold which python executable we'll be using.
declare PYTHON_APP=""

# DEFINE: a variable to hold whether or not we've actually installed things.
declare __SUCCESS=0

# CAPTURE: the default python binary to use in case the user doesn't want to provide one.
declare -r __DEFAULT_PYTHON=$(which python)

# CAPTURE: The provided command line arguments for later use.
declare -r __ARGUMENTS="$@"

# DEFINE: the directory that AKRR will be extracted to.
declare -r __AKRR_DIR=`readlink -f ${__DIR}/..`

# DEFINE: user which will run cronjob
declare -r __AKRR_EXEC_USER=$(whoami)

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
function ensure_scripts_exist {
    for file in ${__SCRIPTS}
    do
        if [ ! -f ${file} ]
        then
            error "Unable to find $file"
            exit 1
        fi
    done
}

function determine_python_location {
    if [ -z "${PYTHON_APP}" ]
    then
        input "Please specify a path to the python binary you want to use:\n[${__DEFAULT_PYTHON}]\c"
        read python_path

        if [ -z "${python_path}" -a -z "${__DEFAULT_PYTHON}" ]
        then
            error "An installation of Python is required to continue.";
        elif [ -z "${python_path}" ]
        then
           PYTHON_APP=${__DEFAULT_PYTHON}
           echo -e "PYTHON_APP=\"${__DEFAULT_PYTHON}\"" > ${__CFG_FILE}
        else
           PYTHON_APP=${python_path}
           config_contents=$(<${__CFG_FILE})
           for line in ${config_contents}
           do
               if [[ ${line} == *PYTHON_APP* ]]
               then
                   echo -e "PYTHON_APP=${python_path}"
               else
                   echo -e "${line}"
               fi
           done >${__CFG_FILE}
        fi
    fi
    # Make sure to source the config file so that
    source ${__CFG_FILE}
}

function check_python_version {

    info "Checking python version..."
    python_output=$(${PYTHON_APP} --version 2>&1)

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

function execute_scripts {
   for script in ${__SCRIPTS}
    do
        set +e
        ${PYTHON_APP} ${script} ${__ARGUMENTS} >&1
        
        # inspect the return code of the script run. Set our internal SUCCESS variable accordingly.
        # Exit if need be.
        if [ $? -eq 0 ]
        then
            __SUCCESS=1
        else
            __SUCCESS=0
            set -e
            exit 1;
        fi
        set -e

    done
}

function start_daemon {
    set +e
    ${PYTHON_APP} ${__DAEMON_SCRIPT} ${__DAEMON_SCRIPT_PARAMS}
    # inspect the return code of the script run. Set our internal SUCCESS variable accordingly.
    # Exit if need be.
    if [ $? -eq 0 ]
    then
        __SUCCESS=1
    else
        __SUCCESS=0
        set -e
        exit 1;
    fi
    set -e
}

function check_daemon {
    set +e
    ${PYTHON_APP} ${__CHECK_DAEMON_SCRIPT}
    # inspect the return code of the script run. Set our internal SUCCESS variable accordingly.
    # Exit if need be.
    if [ $? -eq 0 ]
    then
        __SUCCESS=1
    else
        __SUCCESS=0
        set -e
        exit 1;
    fi
    set -e
}

function find_line_in {
    local -r line=$1; shift;
    local -r file=$@;

    found=0
    for file_line in $file; do
        if [ ${line} = ${file_line} ]
        then
            found=1
        fi
    done

    if [ ${found} -eq 1 ]
    then
        echo 1
    else
        echo 0
    fi
}

function retrieve_email {
    read __AKRR_MAILTO
    if [ "${__AKRR_MAILTO}" != "" ]
    then
        echo "MAILTO=$__AKRR_MAILTO"
    else
        echo ""
    fi
}

function is_set {
    local -r value=$1; shift;
    if [ -z "${value}" ]
    then
        echo 0
    else
        echo 1
    fi
}

function install_cron_scripts {
    info "Saving current crontab..."

    local -r old_cron=`crontab -l`
    local old_cron_found=$(is_set "${old_cron}")
    local mail_to=""
    local new_cron_contents=""

    info "Installing Cron Scripts..."

    input "Please enter the e-mail where cron will send messages (leave empty to opt out):\n\c"
    mail_to=$(retrieve_email)
    mail_to_found=$(find_line_in ${mail_to} ${old_cron})

    found=0
    for file in ${__CRON_FILES[@]}
    do
        local file_contents=$(<${__CRON_DIR}/${file})

        local processed_line1="${file_contents//__AKRR_DIR/$__AKRR_DIR}"
        local processed_line="${processed_line1//__AKRR_EXEC_USER/$__AKRR_EXEC_USER}"

        local file_contents_found=$(find_line_in ${processed_line} ${old_cron})

        if [ ${file_contents_found} -eq 0 ]
        then
            found=1
            if [ -z "${new_cron_contents}" ]
            then
                new_cron_contents="${processed_line}"
            else
                new_cron_contents="${new_cron_contents}\n${processed_line}"
            fi
        fi
    done
    if [ ${found} -eq 1 ]
    then
        if [ ${found} -eq 1 -a ${mail_to_found} -eq 1 -a ${old_cron_found} -eq 1 ]
        then
            echo -e "${old_cron}\n${new_cron_contents}" > .cron_tmp
            crontab .cron_tmp
        elif [ ${found} -eq 1 -a ${mail_to_found} -eq 0 -a ${old_cron_found} -eq 0 ]
        then
            echo -e "${mail_to}\n${new_cron_contents}" > .cron_tmp
            crontab .cron_tmp
        elif [ ${found} -eq 1 -a ${mail_to_found} -eq 1 -a ${old_cron_found} -eq 0 ]
        then
            echo -e "${mail_to}\n${new_cron_contents}" > .cron_tmp
            crontab .cron_tmp
        elif [ ${found} -eq 1 -a ${mail_to_found} -eq 0 -a ${old_cron_found} -eq 1 ]
        then
            echo -e "${old_cron}\n${new_cron_contents}" > .cron_tmp
            crontab .cron_tmp
        fi

        success "Cron Scripts Processed!"
    else
        warning "All entries found. No modifications necessary."
    fi

    __SUCCESS=1
}

function update_bashrc {
    if [[ $BASH == *"bash"* ]]
    then
        info "Updating .bashrc!"
        if [ -e $HOME/.bashrc ]
        then
           if [[ `grep "\#AKRR Enviromental Varables \[Start\]" $HOME/.bashrc` == *"AKRR Enviromental Varables [Start]"* ]]
           then
               info "Updating AKRR record in $HOME/.bashrc, backing to $HOME/.bashrc_akrrbak"
               cp $HOME/.bashrc $HOME/.bashrc_akrrbak
               head -n "$(( $(grep -n '\#AKRR Enviromental Varables \[Start\]' $HOME/.bashrc_akrrbak | head -n 1 | cut -d ":" -f 1) - 1 ))" $HOME/.bashrc_akrrbak > $HOME/.bashrc
               tail -n "+$(( $(grep -n '\#AKRR Enviromental Varables \[End\]' $HOME/.bashrc_akrrbak | head -n 1 | cut -d ":" -f 1) + 1 ))" $HOME/.bashrc_akrrbak  >> $HOME/.bashrc
           fi
        fi
        info "Appending AKRR records to $HOME/.bashrc"
        echo "#AKRR Enviromental Varables [Start]" >> $HOME/.bashrc
        echo "export AKRR_HOME=\"$__AKRR_DIR\"" >> $HOME/.bashrc
        echo "export PATH=\"\$AKRR_HOME/bin:\$PATH\"" >> $HOME/.bashrc
        echo "#AKRR Enviromental Varables [End]" >> $HOME/.bashrc
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

# Ensure that the script files exist.
ensure_scripts_exist

# Determine where python lives on this system
determine_python_location

# Check that the python version we need exists
check_python_version

# Execute our scripts, in order.


execute_scripts

__SUCCESS=1
exit
# Start the daemon
start_daemon

# Check that the daemon is running
check_daemon

# Install cron scripts.
install_cron_scripts

# Add AKRR enviroment variables to .bashrc
update_bashrc

#clean_up
rm $__AKRR_DIR/*.mysql_dbs_init.sql
rm $__AKRR_DIR/cfg/akrr.src.inp.py


# Make sure that we set the SUCCESS flag to true if we've made it this far.
__SUCCESS=1
