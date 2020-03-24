#!/usr/bin/env expect
# xdmod-upgrade to xdmod 8.1

set timeout 240
spawn "xdmod-upgrade"

provideInput {Are you sure you want to continue (yes, no)? \[no\]} yes

lassign [wait] pid spawnid os_error_flag value
exit $value
