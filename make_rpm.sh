#!/usr/bin/env bash
# Make RPMs for AKRR
script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd ${script_dir}
./setup.py bdist_rpm
