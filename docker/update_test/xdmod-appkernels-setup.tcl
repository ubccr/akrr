#!/usr/bin/env expect
# Expect script that runs xdmod-setup to configure a
# xdmod-appkernels module.
# This script should be run after xdmod and akrr installation
# It will fail if other xdmod modules are already installed
# due to change in menu option numiration

#-------------------------------------------------------------------------------
# Load helper functions from helper-functions.tcl
source [file join [file dirname [info script]] helper-functions.tcl]

#-------------------------------------------------------------------------------
# main body - note there are some hardcoded addresses, usernames and passwords here
# they should typically not be changed as they need to match up with the
# settings in the docker container

set timeout 240
spawn "xdmod-setup"

selectMenuOption 9

# MySQL DB
answerQuestion {DB Hostname or IP} {}
answerQuestion {DB Port} {}
answerQuestion {DB Username} {}

expect {
	timeout { send_user "\nFailed to get prompt\n"; exit 1 }
	"Try again (yes, skip, abort)? \\\[yes\\\] " { send "skip\n"; exp_continue; }
	"Please provide the information necessary"
}


# AKRR REST API
answerQuestion {AKRR REST API username} {}
providePassword {AKRR REST API password:} rwuserpass
answerQuestion {AKRR REST API host} {}
answerQuestion {AKRR REST API port} {}
answerQuestion {AKRR REST API end point} {}

confirmFileWrite yes
enterToContinue

expect {
	timeout { send_user "\nFailed to get prompt\n"; exit 1 }
	"Do you want to see the output (yes, no)? \\\[no\\\] "
}
send "\n"

selectMenuOption q

lassign [wait] pid spawnid os_error_flag value
exit $value
