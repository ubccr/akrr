#!/bin/bash
cd
echo "Running Update Test 1.0 -> 2.0"

echo "USER: $USER"
echo "CWD: " `pwd`

mv ~/akrr ~/akrr_old

~/xdmod_wsp/akrr/bin/akrr -vv update --old-akrr-home=~/akrr_old --dry-run
