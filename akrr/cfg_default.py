"""
Initial and default configuration parameters for AKRR
"""


import datetime

###############################################################################
# XDMoD DB
###############################################################################
# Hostname of the database currently sering the 'modw' database ( the main XDMoD database ).
xd_db_host = "localhost"

# The port that the 'modw' database is currently being served from.
xd_db_port = 3306

# The user that has read only access to the 'modw.resourcefact' table.
xd_db_user = "{xd_user_name}"

# The password for the 'xd_db_user'
xd_db_passwd = "{xd_user_password}"

# The name that has been chosen for the 'modw' database. Note: CHANGE THIS AT YOUR OWN RISK.
xd_db_name = "modw"

# ==============================================================================
# MOD_AKRR DATABASE
# ==============================================================================

# The host name of the database server that the 'mod_akrr' database is served from.
akrr_db_host = xd_db_host

# Port that the 'mod_akrr' database is being served from.
akrr_db_port = xd_db_port

# Database user that will have full access to the 'mod_akrr' database.
akrr_db_user = "{akrr_user_name}"

# Password for the 'akrr_db_user'
akrr_db_passwd = "{akrr_user_password}"

# The name that has been chosen for the 'mod_akrr' database. Note: CHANGE THIS AT YOUR OWN RISK.
akrr_db_name = "mod_akrr"

# ==============================================================================
# External DB (In most cases same as Internal DB)
# NOTE: this database ( and the credentials required ) are usually the same as
#       the 'mod_akrr' database.
# ==============================================================================
export_db_host = akrr_db_host
export_db_port = akrr_db_port
export_db_user = akrr_db_user
export_db_passwd = akrr_db_passwd
export_db_name = akrr_db_name

###############################################################################
# App Kernel DB
# NOTE: this database ( and the credentials required ) are usually the same as
#       the 'mod_akrr' database.
###############################################################################

# Hostname of the database serving the 'mod_appkernel' database.
ak_db_host = akrr_db_host

# Port that the 'mod_appkernel' database is being served from.
ak_db_port = akrr_db_port

# User with full access to the 'mod_appkernel' database.
ak_db_user = akrr_db_user

# Password for the 'ak_db_user'
ak_db_passwd = akrr_db_passwd

# The name that has been chosen to represent the 'mod_appkernel' database. Note: CHANGE THIS AT YOUR OWN RISK.
ak_db_name = "mod_appkernel"

###############################################################################
# REST API
###############################################################################

# The hostname of the server that will be serving the RESTAPI. If you are testing and want to bind it to the loop-back
# address please note that 'localhost' produced more positive results than '127.0.0.1' did. Your mileage may vary.
restapi_host = "localhost"

# The port that the REST API will attempt to bind to on startup. Please change if you have a conflict.
# Please also ensure that this port is available for connection ( aka. please create a firewall rule if necessary. ).
restapi_port = 8091

# the root url fragment that will be pre-pended to all REST API routes [ ex. GET https://restapi/api/v1/scheduled_tasks
# hits the 'scheduled_tasks' route of the REST API ]. This fragment allows for versioning of the API.
restapi_apiroot = '/api/v1'

# The name of the SSL cert file ( required for HTTPS connections )
restapi_certfile = 'server.pem'

# Token expiration time in seconds
restapi_token_expiration_time = 3600

# User defined as having 'read / write' permission to the REST API
restapi_rw_username = 'rw'

# The password for the 'rw' user.
restapi_rw_password = "{restapi_rw_password}"

# User defined as having 'read-only' premissions to the REST API
restapi_ro_username = 'ro'

# The password for the 'ro' user.
restapi_ro_password = "{restapi_ro_password}"

###############################################################################
# Directories layout (relative paths are relative to location of this file)
###############################################################################

# This location is used to store various bits of information about the AKRR
# process such as the .pid file ( to track when AKRR is running ) as well as
# logs.
data_dir = "../data"

# This location is used to
completed_tasks_dir = "../comptasks"

###############################################################################
#
#  PARAMETERS BELLOW THIS POINT DO NOT OFTEN NEED TO BE CHANGED.
#  PROCEED AT YOUR OWN RISK!
#
###############################################################################

###############################################################################
# AKRR parameters
###############################################################################
# Number of sub-processes (workers) to handle tasks
max_task_handlers = 4

# redirect task processing to log file
redirect_task_processing_to_log_file = True

# The 'id' of the pickling protocol to use.
task_pickling_protocol = 0

# The amount of time that the tasks loop should sleep in between loops.
scheduled_tasks_loop_sleep_time = 1.0

# maximum number of active tasks for akrr TOTAL (-1 for unlimited)
max_number_of_active_tasks_total = -1


###############################################################################
# Error handling and repeat time
###############################################################################
# class datetime.timedelta format
# class datetime.timedelta([days[, seconds[, microseconds[, milliseconds[, minutes[, hours[, weeks]]]]]]])

############################
# Default error handling
############################

# Maximal number of regular fatal errors (regular in sense no special treatment)
max_fatal_errors_for_task = 10
# Default repeat time
active_task_default_attempt_repeat = datetime.timedelta(minutes=30)

# ***************************
# handler hangs
# ##########################

# maximal time for task handler single execution
max_wall_time_for_task_handlers = datetime.timedelta(minutes=30)
# time to repeat after termination
repeat_after_forcible_termination = active_task_default_attempt_repeat

# Failure to submit to the queue on remote machine hangs, usually an issue on machine with queue limits
max_fails_to_submit_to_the_queue = 48  # i.e.2 days

# amount of time to wait to submit the task back to the queue if it fails.
repeat_after_fails_to_submit_to_the_queue = datetime.timedelta(hours=1)

# Maximum amount of time a task is allowed to stay in the queue.
max_time_in_queue = datetime.timedelta(days=10)  # i.e. 10 days

# The amount of time that should elapse between attempts to connect to the 'export' db.
export_db_repeat_attempt_in = datetime.timedelta(hours=1)

# The maximum number of attempts that should be made to connect to the 'export' db.
export_db_max_repeat_attempts = 48

# The default parameters that should be made available to each task.
default_task_params = {'test_run': False}

# Encoding for conversion of bytes to sting. Default encoding is 'utf-8'
encoding = "utf-8"
