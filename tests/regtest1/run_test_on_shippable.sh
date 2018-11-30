#!/usr/bin/env bash
export REPO_FULL_NAME=${REPO_FULL_NAME:-ubccr/akrr}
export SETUP_WAY=${1:-dev}
set -e

# Start all daemons
cmd_start self_contained_slurm_wlm
squeue
sinfo
ps -Af

cd /root/src/github.com/${REPO_FULL_NAME}

#install source code
if [ "${SETUP_WAY}" == "rpm" ]; then
    # Build RPM
    ./setup.py bdist_rpm

    # Install RPM
    rpm -Uvh dist/akrr-*.noarch.rpm
elif [ "${SETUP_WAY}" == "dev" ]; then
    ./setup.py develop
else
    echo "Unknown setup.py call"
    exit 1
fi

# Run pylint tests
pylint --errors-only akrr.util

# Run unit tests
mkdir -p shippable/testresults
mkdir -p shippable/codecoverage
pytest --junitxml=shippable/testresults/testresults.xml \
       --cov=akrr --cov-report=xml:shippable/codecoverage/coverage.xml \
       -m "not openstack" \
       ./tests/unit_tests

# Run this regression test
export PATH=/root/src/github.com/${REPO_FULL_NAME}/tests/bin:$PATH
/root/src/github.com/${REPO_FULL_NAME}/tests/regtest1/run_test.sh

#remove akrr from crontab to avoid uncontrolled AKRR launch
cd tests/regtest1
/root/src/github.com/${REPO_FULL_NAME}/tests/bin/akrrregtest remove --crontab --crontab-remove-mailto
cd ../..
# Rerun unit tests and run system tests together
rm shippable/testresults/testresults.xml shippable/codecoverage/coverage.xml

# Change directory to test to avoid conflicts between local akrr and system akrr
cd tests
pytest -v --junitxml=../shippable/testresults/testresults.xml \
       --cov=akrr --cov-report=xml:../shippable/codecoverage/coverage.xml \
       -m "not openstack" \
       ./unit_tests ./sys_tests
cd ..
