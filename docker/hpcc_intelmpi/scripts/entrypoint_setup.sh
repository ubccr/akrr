#!/bin/bash
echo $@
python $scriptsLoc/setup_hpcc_input.py "$@"

cd /home/hpccuser
/bin/bash
