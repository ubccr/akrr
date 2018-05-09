#!/usr/bin/env bash
export REPO_FULL_NAME=${REPO_FULL_NAME:-ubccr/akrr}

set -e

# Start all daemons
cmd_start self_contained_slurm_wlm
squeue
sinfo
ps -Af

# Build RPM
cd /root/src/github.com/${REPO_FULL_NAME}
./setup.py bdist_rpm

# Install RPM
rpm -Uvh dist/akrr-*.noarch.rpm

# Run unit tests
mkdir -p shippable/testresults
mkdir -p shippable/codecoverage
pytest --junitxml=shippable/testresults/testresults.xml
pytest --cov=akrr --cov-report=xml:shippable/codecoverage/coverage.xml

# Run this regression test
export PATH=/root/src/github.com/${REPO_FULL_NAME}/tests/bin:$PATH
/root/src/github.com/${REPO_FULL_NAME}/tests/regtest1/run_test.sh
