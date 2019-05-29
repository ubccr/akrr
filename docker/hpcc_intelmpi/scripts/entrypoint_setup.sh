#!/bin/bash
echo $@
# old arg parser, we want to use bash
#python $scriptsLoc/setup_hpcc_input.py "$@"
./setup_hpcc_input.sh "$@"

echo $@

cd /home/hpccuser
/bin/bash
