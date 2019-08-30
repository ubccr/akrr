#!/usr/bin/env bash
echo PATH=$PATH
echo USER=$USER
# This script is executed in docker as local user
# either on shippable or in local docker run
# mimicing shippable directory layout
#
# Local user do sudo to start-up nessesary services
# most test done as local user

export REPO_FULL_NAME=${REPO_FULL_NAME:-ubccr/akrr}
export AKRR_SETUP_WAY=${AKRR_SETUP_WAY:-dev}
export AKRR_SETUP_WAY=${1:-$AKRR_SETUP_WAY}
export AKRR_SRC=${AKRR_SRC:-/home/akrruser/akrr_src}
export AKRR_SHORT_TESTS=${AKRR_SHORT_TESTS:-false}

# AKRR_SETUP_HOME enviroment variable would set AKRR_HOME installation path

# exit on first error
set -e

# before exit on first error print line number where error occured
trap 'catch $? $LINENO' ERR
catch() {
  echo "Error $1 occurred on line $2"
}

highlight='-e "\e[30;48;5;82m[AKRR_Reg_Test:0]\e[0m"'
red_highlight='-e "\e[30;48;5;1m[AKRR_Reg_Test:0]\e[0m"'
# Start all daemons
sudo /usr/local/sbin/cmd_start self_contained_slurm_wlm

# check slurm and log processes for debugging
squeue
sinfo
ps -Af

cd "${AKRR_SRC}"

export AKRR_TEST_PYTHONPATH=${PYTHONPATH}
#install source code
if [ "${AKRR_SETUP_WAY}" == "rpm" ]; then
    echo "Install with RPM"
    # Build RPM
    ./setup.py bdist_rpm
    # Install RPM
    sudo rpm -Uvh dist/akrr-*.noarch.rpm
elif [ "${AKRR_SETUP_WAY}" == "dev" ]; then
    echo "Develop install"
    sudo ./setup.py develop
elif [ "${AKRR_SETUP_WAY}" == "src" ]; then
    echo "Running in source"
    # export PATH=${AKRR_SRC}/bin:$PATH
    export AKRR_TEST_PYTHONPATH=${AKRR_SRC}:${PYTHONPATH}
else
    echo "Unknown setup.py call"
    exit 1
fi

if [ "${AKRR_SHORT_TESTS}" == "false" ]; then
    #Run pylint tests
    echo $highlight "Running pylint tests"
    pylint --errors-only akrr.util

    #Run unit tests
    echo $highlight "Running unit tests"
    mkdir -p shippable/testresults
    mkdir -p shippable/codecoverage
    PYTHONPATH=${AKRR_TEST_PYTHONPATH} pytest \
           --junitxml=shippable/testresults/testresults.xml \
           --cov=akrr --cov-report=xml:shippable/codecoverage/coverage.xml \
           -m "not openstack" \
           ./tests/unit_tests
    rm shippable/testresults/testresults.xml shippable/codecoverage/coverage.xml
fi

# Run this regression test
echo $highlight "Running regression test"
export PATH=${AKRR_SRC}/tests/bin:$PATH
"${AKRR_SRC}/tests/regtest1/_test_install_deploy.sh"
# source .bashrc to load AKRR environment variables (AKRR_HOME and PATH in case of non-standard location)
source ~/.bashrc

#remove akrr from crontab to avoid uncontrolled AKRR launch
echo $highlight "remove akrr from crontab to avoid uncontrolled AKRR launch"
cd tests/regtest1
# @todo add test with crontab
PYTHONPATH=${AKRR_TEST_PYTHONPATH}  "${AKRR_SRC}/tests/bin/akrrregtest" remove --crontab --crontab-remove-mailto
cd ../..

# Rerun unit tests and run system tests together
echo $highlight "Rerunning unit tests and run system tests together"

set +e
ps -Af|grep akrr
ls -l /home/akrruser/akrr/log/data
ls -l /home/akrruser/akrr/log/data/srv
akrr daemon start
if [ $? -ne 0 ]
then
  echo $red_highlight "AKRR is not up!"
  ps -Af|grep akrr
  akrr daemon status
  ls -l /home/akrruser/akrr/log/data
  ls -l /home/akrruser/akrr/log/data/srv
  for f in /home/akrruser/akrr/log/data/srv/*.log
  do
    echo $red_highlight $f
    cat $f
    exit 1
  done
fi
set -e
# Change directory to test to avoid conflicts between local akrr and system akrr
cd tests
PYTHONPATH=${AKRR_TEST_PYTHONPATH} pytest -v --junitxml=../shippable/testresults/testresults.xml \
       --cov=akrr --cov-report=xml:../shippable/codecoverage/coverage.xml \
       --cov-branch -m "not openstack" \
       ./unit_tests ./sys_tests
cd ..
