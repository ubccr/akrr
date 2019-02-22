#!/usr/bin/env bash
# Make RPMs for AKRR in docker container
script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
akrr_src_dir="$( dirname ${script_dir} )"
echo ${akrr_src_dir}
cd ${akrr_src_dir}
docker run -v ${akrr_src_dir}:/root/src/github.com/ubccr/akrr -it --rm \
    akrr_test "/root/src/github.com/ubccr/akrr/make_rpm.sh"
