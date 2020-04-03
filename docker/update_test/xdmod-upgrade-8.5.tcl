#!/usr/bin/env expect
# xdmod-upgrade to xdmod 8.5

# Load helper functions from helper-functions.tcl
source [file join [file dirname [info script]] helper-functions.tcl]

set timeout 240
spawn "xdmod-upgrade"

provideInput {Are you sure you want to continue (yes, no)? \[no\]} yes
provideInput {Enable Dashboard Tab (on, off)? \[off\]} {}
provideInput {Export Directory: \[/var/spool/xdmod/export\]} {}
provideInput {Export File Retention Duration in Days: \[30\]} {}
provideInput {Do you want to run aggregation now (yes, no)? \[no\]} {}

lassign [wait] pid spawnid os_error_flag value
exit $value
