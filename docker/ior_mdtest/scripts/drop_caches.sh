#!/bin/bash


# helper script that just clears out the caches
sync; echo 3 > /proc/sys/vm/drop_caches
# Script should be called with sudo


