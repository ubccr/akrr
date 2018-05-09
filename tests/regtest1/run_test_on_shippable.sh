#!/usr/bin/env bash


set -e
# Start all daemons
cmd_start self_contained_slurm_wlm
squeue
sinfo
ps -Af
# Build RPM
cd /root/src/github.com/$REPO_FULL_NAME
./setup.py bdist_rpm
# Install RPM
rpm -Uvh dist/akrr-*.noarch.rpm
# Run tests
export PATH=/root/src/github.com/$REPO_FULL_NAME/tests/bin:$PATH
/root/src/github.com/$REPO_FULL_NAME/tests/regtest1/run_test.sh
