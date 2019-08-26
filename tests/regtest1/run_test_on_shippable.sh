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

# exit on first error
set -e

# before exit on first error print line number where error occured
trap 'catch $? $LINENO' ERR
catch() {
  echo "Error $1 occurred on line $2"
}

highlight='-e "\e[32,1m[AKRR_Reg_Test:0]\e[0m"'

# Start all daemons
sudo /usr/local/sbin/cmd_start self_contained_slurm_wlm

# check slurm and log processes for debugging
squeue
sinfo
ps -Af

cd "/home/$USER/akrr_src"

#install source code
if [ "${AKRR_SETUP_WAY}" == "rpm" ]; then
    # Build RPM
    ./setup.py bdist_rpm
    # Install RPM
    sudo rpm -Uvh dist/akrr-*.noarch.rpm
elif [ "${AKRR_SETUP_WAY}" == "dev" ]; then
    sudo ./setup.py develop
elif [ "${AKRR_SETUP_WAY}" == "src" ]; then
    echo "Running in source"
else
    echo "Unknown setup.py call"
    exit 1
fi

#Run pylint tests
echo $highlight "Running pylint tests"
pylint --errors-only akrr.util

#Run unit tests
echo $highlight "Running unit tests"
mkdir -p shippable/testresults
mkdir -p shippable/codecoverage
pytest --junitxml=shippable/testresults/testresults.xml \
       --cov=akrr --cov-report=xml:shippable/codecoverage/coverage.xml \
       -m "not openstack" \
       ./tests/unit_tests

# Run this regression test
echo $highlight "Running regression test"
export PATH=${AKRR_SRC}/tests/bin:$PATH
"${AKRR_SRC}/tests/regtest1/run_test.sh"

#remove akrr from crontab to avoid uncontrolled AKRR launch
echo $highlight "remove akrr from crontab to avoid uncontrolled AKRR launch"
cd tests/regtest1
# @todo add test with crontab
"${AKRR_SRC}/tests/bin/akrrregtest" remove --crontab --crontab-remove-mailto
cd ../..

# Rerun unit tests and run system tests together
echo $highlight "Rerunning unit tests and run system tests together"
rm shippable/testresults/testresults.xml shippable/codecoverage/coverage.xml

# Change directory to test to avoid conflicts between local akrr and system akrr
cd tests
pytest -v --junitxml=../shippable/testresults/testresults.xml \
       --cov=akrr --cov-report=xml:../shippable/codecoverage/coverage.xml \
       --cov-branch -m "not openstack" \
       ./unit_tests ./sys_tests
cd ..
