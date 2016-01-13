#! /usr/bin/env bash

###############################################################################
#      Author: Ryan Rathsam
#     Created: 2014.10.08
# Description: AKRR Main Installation Script. Responsible for setting up the top
#              level directories and unpacking the akrr tarball into the correct
#              location.
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

# DEFINE: a variable to determine whether or not the install process was a success.
declare __SUCCESS=0

# FIND: the directory in which this script resides.
declare -r __DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )";

# DEFINE: the directory that the akrr tarball should be unpacked to.
#declare -r __AKRR_DIR="akrr"

# DEFINE: the directories that need to be created.
declare -r __REQ_DIRS="${__DIR}/../data ${__DIR}/../comptasks ${__AKRR_DIR}";

# DEFINE: the files that this script depends on
declare -r __FILES="${__DIR}/akrr.src.tar.gz"

# DEFINE: the tarball
declare -r __TARBALL="akrr.src.tar.gz"

# DEFINE: The replacement string that will be used to sub in the AKRR SQL username.
declare -r __AKRR_USER_FIND="__AKRR_USER"

# DEFINE: the replacement string that will be used to sub in the AKRR SQL user's password.
declare -r __AKRR_PASSWORD_FIND="__AKRR_USER_PASSWORD"

declare -r __AKRR_MODW_USER_FIND="__AKRR_MODW_USER"

declare -r __AKRR_MODW_PASSWORD_FIND="__AKRR_MODW_USER_PASSWORD"

declare -r __AKRR_REST_RW_PASSWORD_FIND="__AKRR_REST_RW_PASSWORD"

declare -r __AKRR_REST_RO_PASSWORD_FIND="__AKRR_REST_RO_PASSWORD"


# DEFINE: the file name used for the install sql script.
declare -r __INSTALL_SQL_FILE="mysql_dbs_init.sql"

# DEFINE: the default sql user to create for AKRR
declare -r __DEFAULT_AKRR_USER="akrruser"

declare -r __DEFAULT_AKRR_MODW_USER="akrruser"

declare __AKRR_USER_NAME=""

declare __AKRR_USER_PASSWORD=""

declare __AKRR_HOST=""

declare __AKRR_PORT=""

declare __AKRR_MODW_USER_NAME=""

declare __AKRR_MODW_USER_PASSWORD=""

declare __AKRR_MODW_HOST=""

declare __AKRR_MODW_port=""

# DEFINE: the directory that AKRR will be extracted to.
declare -r __AKRR_DIR=`readlink -f ${__DIR}/../..`

# DEFINE: the location that the setup script will be located at.
declare -r __SETUP_SCRIPT="${__AKRR_DIR}/setup/setup.sh"

# DECLARE: a variable to hold the contents of the bootstrap sql script so that we can write it back out.
declare __SQL_SCRIPT=""

# DEFINE:
declare -r __AKRR_CFG_DIR="${__AKRR_DIR}/cfg"

declare -r __AKRR_SRC_CFG_FILE="${__AKRR_CFG_DIR}/akrr.src.inp.py"

declare -r __AKRR_CFG_FILE="${__AKRR_CFG_DIR}/akrr.inp.py"
###############################################################################
# COLORIZATION METHODS
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

###############################################################################
# LOGGING METHODS
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

###############################################################################
# INSTALLATION METHODS
###############################################################################

function modify_install_sql {
    local -r local_sql_file="${__DIR}/${__INSTALL_SQL_FILE}"

    local -r sql_script_contents=$(<${local_sql_file})

    process_contents_with_password="${sql_script_contents//${__AKRR_PASSWORD_FIND}/${__AKRR_USER_PASSWORD}}"
    process_contents="${process_contents_with_password//${__AKRR_USER_FIND}/${__AKRR_USER_NAME}}"
    process_modw_contents_with_password="${process_contents//${__AKRR_MODW_PASSWORD_FIND}/${__AKRR_MODW_USER_PASSWORD}}"
    process_modw_contents="${process_modw_contents_with_password//${__AKRR_MODW_USER_FIND}/${__AKRR_MODW_USER_NAME}}"


    echo "$process_modw_contents"
}

function read_akrr_creds {

    info "Before Installation continues we need to setup the database."

    input "Please specify a database user for AKRR (This user will be created if it does not already exist): \n[${__DEFAULT_AKRR_USER}]\c :"
    read __AKRR_USER_NAME

    if [ -z "$__AKRR_USER_NAME" ]
    then
        __AKRR_USER_NAME=${__DEFAULT_AKRR_USER}
    fi

    while true
    do
        input "Please specify a password for the AKRR database user: \n\c :"
        read -s password
        echo
        input "Please reenter password: \n\c :"
        read -s password2
        echo
        [ "$password" = "$password2" ] && break
        error "Entered passwords do not match. Please try again"
    done
    __AKRR_USER_PASSWORD=$password
}

function read_modw_creds {
    input "Please specify the user that will be connecting to the XDMoD database (modw): \n[${__DEFAULT_AKRR_USER}]\c :"
    read __AKRR_MODW_USER_NAME

    if [ -z "$__AKRR_MODW_USER_NAME" ]
    then
        __AKRR_MODW_USER_NAME=${__DEFAULT_AKRR_MODW_USER}
    fi

    if [ "$__AKRR_MODW_USER_NAME" = "$__AKRR_USER_NAME" ]
    then
        info "Same user as for AKRR database user, will set same password"
        __AKRR_MODW_USER_PASSWORD=$__AKRR_USER_PASSWORD
    else
        while true
        do
            input "Please specify the password:\n\c :"
            read -s password
            echo
            input "Please reenter password: \n\c :"
            read -s password2
            echo
            [ "$password" = "$password2" ] && break
            error "Entered passwords do not match. Please try again"
        done
        __AKRR_MODW_USER_PASSWORD=$password
    fi
}

function generate_modified_sql {
    local -r script_counter=$((`ls *.sql 2>/dev/null | wc -w 2>/dev/null`+1));

    local -r modified_sql=$(modify_install_sql)
    local -r new_sql_file_name="${script_counter}.${__INSTALL_SQL_FILE}"
    echo -e "${modified_sql}">"${new_sql_file_name}"
    info "Your script has been saved to [${new_sql_file_name}]"

    __SQL_SCRIPT="${new_sql_file_name}"

}

function execute_sql_script {
    local -r script_name=$1; shift;

    input "Please provide an administrative database user under which the installation sql script should
run (This user must have privileges to create users and databases):"
    read install_user

    input "Please provide the password for the the user which you previously entered:"
    read -s install_user_password

    if [ -z "$install_user" ]
    then
        error "You must provide a user to execute the sql install script."
        __SUCCESS=0
        exit 1
    fi

    if [ -z "$install_user_password" ]
    then
        error "You must provide a password to be used in the execution of the sql install script."
        __SUCCESS=0
        exit 1
    fi

    status=$(mysql -u ${install_user} -p${install_user_password} < ${script_name} 2>&1)

    if [[ $status == *ERROR* ]]
    then
        error "Can not execute the sql install script: $status"
        __SUCCESS=0
        exit 1
    fi
}

function generate_self_signed_certificate {
    info "Generating self-signed certificate for REST-API"
    #openssl genrsa -des3 -passout pass:x -out ${__AKRR_CFG_DIR}/server.pass.key 2048
    #openssl rsa -passin pass:x -in ${__AKRR_CFG_DIR}/server.pass.key -out ${__AKRR_CFG_DIR}/server.key
    #rm ${__AKRR_CFG_DIR}/server.pass.key
    #openssl req -new -key ${__AKRR_CFG_DIR}/server.key -out ${__AKRR_CFG_DIR}/server.csr
    #openssl x509 -req -days 36500 -in ${__AKRR_CFG_DIR}/server.csr -signkey ${__AKRR_CFG_DIR}/server.key -out ${__AKRR_CFG_DIR}/server.crt
    openssl req \
        -new \
        -newkey rsa:4096 \
        -days 365 \
        -nodes \
        -x509 \
        -subj "/C=US/ST=Denial/L=Springfield/O=Dis/CN=localhost" \
        -keyout ${__AKRR_CFG_DIR}/server.key \
        -out ${__AKRR_CFG_DIR}/server.cert
    cp ${__AKRR_CFG_DIR}/server.key ${__AKRR_CFG_DIR}/server.pem
    cat ${__AKRR_CFG_DIR}/server.cert >> ${__AKRR_CFG_DIR}/server.pem
    info "New self-signed certificate have been generated"
}

function generate_settings_file {
    echo -e "${__AKRR_SRC_CFG_FILE}"

    info "Generating Settings File..."
    local -r config_file_contents=$(<${__AKRR_SRC_CFG_FILE})

    process_contents_with_password="${config_file_contents//${__AKRR_PASSWORD_FIND}/${__AKRR_USER_PASSWORD}}"
    process_contents="${process_contents_with_password//${__AKRR_USER_FIND}/${__AKRR_USER_NAME}}"
    process_modw_contents_with_password="${process_contents//${__AKRR_MODW_PASSWORD_FIND}/${__AKRR_MODW_USER_PASSWORD}}"
    process_modw_contents="${process_modw_contents_with_password//${__AKRR_MODW_USER_FIND}/${__AKRR_MODW_USER_NAME}}"

    #random password for rest api
    __AKRR_REST_RW_PASSWORD=$(head /dev/urandom | tr -dc A-Z-a-z-0-9 | head -c${1:-16})
    __AKRR_REST_RO_PASSWORD=$(head /dev/urandom | tr -dc A-Z-a-z-0-9 | head -c${1:-16})
    
    process_rest_api_rw_password="${process_modw_contents//${__AKRR_REST_RW_PASSWORD_FIND}/${__AKRR_REST_RW_PASSWORD}}"
    process_rest_api_ro_password="${process_rest_api_rw_password//${__AKRR_REST_RO_PASSWORD_FIND}/${__AKRR_REST_RO_PASSWORD}}"


    echo -e "${process_rest_api_ro_password}">${__AKRR_CFG_FILE}

    info "Settings written to: ${__AKRR_CFG_FILE}"
}

function set_permission_on_files {
    info "Removing access for group members and everybody for all files as it might contain sensetive information."
    chmod -R g-rwx ${__AKRR_DIR}
    chmod -R o-rwx ${__AKRR_DIR}
}

function untar_akrr {
    info "Exploding AKRR..."
    tar -xvzf ${__TARBALL}
}

# Function that will be executed when the script exist.
function clean_up {
    if [ ${__SUCCESS} -eq 0 ]
    then
        warning "Something went horribly wrong...Please Check previous messages." >&2
        error "AKRR Not Initialized." >&2
    else
        info "AKRR Initialized Successfully!"
    fi
}

# Ensure that the cleanup function always executes
trap "clean_up" EXIT SIGQUIT SIGKILL SIGTERM

info "AKRR Initialization started..."

read_akrr_creds

read_modw_creds

generate_modified_sql

execute_sql_script ${__SQL_SCRIPT}

#untar_akrr

#echo `pwd`

#cd ${__AKRR_DIR}

#echo `pwd`

generate_self_signed_certificate

generate_settings_file

set_permission_on_files

info "AKRR Initialization ended."

# ENSURE: that if we've made it this far that we mark our install as a success.
__SUCCESS=1
