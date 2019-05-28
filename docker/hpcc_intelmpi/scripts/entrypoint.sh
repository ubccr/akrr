#!/bin/bash
# script that runs at entrypoint - mainly to be able to use ENV variables properly
echo "Arguments: " $@
$scriptsLoc/setup_hpcc.sh "$@"

cd /home/hpccuser
/bin/bash
