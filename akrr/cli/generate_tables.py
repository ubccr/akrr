"""
Python script for installing AKRR ( Application Remote Runner )
This script will perform the following steps:
  - Create the default tables required by AKRR to function properly.
  - Other things tbd later ;-)
"""

###############################################################################
# IMPORTS
###############################################################################

import sys
import MySQLdb

import akrr.db
from akrr.util import log


###############################################################################
# UTILITY FUNCTIONS
###############################################################################
def create_and_populate_tables(
        default_tables, 
        population_statements, 
        starting_comment, ending_comment,
        connection_function,
        host=None, user=None, password=None, db=None,
        dry_run=False
        ):
    """
    :param default_tables:
    :param population_statements:
    :param starting_comment:
    :param ending_comment:
    :param connection_function:
    :type connection_function: function
    """
    log.info(starting_comment)

    try:
        if not dry_run:
            if host and user and password and db:
                connection = MySQLdb.connect(host, user, password, db)
                cursor = connection.cursor()
            else:
                connection, cursor = connection_function(True)

            with connection:
                for (table_name, table_script) in default_tables:
                    log.info("CREATING: %s" % table_name)
                    try:
                        result = cursor.execute(table_script)
                        log.debug("Result of: %s -> %d" % (table_name, result))
                        log.info("CREATED: %s SUCCESSFULLY!" % table_name)
                    except MySQLdb.Warning:
                        pass

                for (description, statement) in population_statements:
                    log.info("EXECUTING: %s" % description)

                    result = cursor.execute(statement)
                    log.debug("Result of: %s -> %d" % (table_name, result))
                    log.info("EXECUTED: %s SUCCESSFULLY!" % description)
        else:
            for (table_name, table_script) in default_tables:
                log.dry_run("CREATING: %s" % table_name)
                #log.info("CREATED: %s SUCCESSFULLY!" % table_name)

            for (description, statement) in population_statements:
                log.dry_run("EXECUTING: %s" % description)
                #log.info("EXECUTED: %s SUCCESSFULLY!" % description)
        log.info(ending_comment)
    except MySQLdb.Error as e:
        log.critical("Error %d: %s" % (e.args[0], e.args[1]))
        sys.exit(1)

def create_and_populate_mod_akrr_tables(dry_run=False):
    """
    Create / Populate the tables required in the mod_akrr database.
    """

    # DEFINE: the default tables to be created.
    default_tables = (
        ('ACTIVETASKS', '''
        CREATE TABLE IF NOT EXISTS `ACTIVETASKS` (
        `task_id` INT(11) DEFAULT NULL,
        `next_check_time` DATETIME NOT NULL,
        `status` TEXT,
        `status_info` TEXT,
        `statusupdatetime` DATETIME DEFAULT NULL,
        `datetimestamp` TEXT,
        `time_activated` DATETIME DEFAULT NULL,
        `time_submitted_to_queue` DATETIME DEFAULT NULL,
        `task_lock` INT(11) DEFAULT NULL,
        `time_to_start` DATETIME DEFAULT NULL,
        `repeat_in` CHAR(20) DEFAULT NULL,
        `resource` TEXT,
        `app` TEXT,
        `resource_param` TEXT,
        `app_param` TEXT,
        `task_param` TEXT,
        `group_id` TEXT,
        `fatal_errors_count` INT(4) DEFAULT '0',
        `fails_to_submit_to_the_queue` INT(4) DEFAULT '0',
        `taskexeclog` LONGTEXT,
        `master_task_id` INT(4) NOT NULL DEFAULT '0' COMMENT '0 - independent task, otherwise task_id of master task ',
        `parent_task_id` INT(11) DEFAULT NULL,
        UNIQUE KEY `task_id` (`task_id`)
        ) ENGINE=MyISAM DEFAULT CHARSET=latin1;
        '''),
        ('ak_on_nodes', '''
        CREATE TABLE IF NOT EXISTS `ak_on_nodes` (
        `resource_id` INT(11) NOT NULL,
        `node_id` INT(11) NOT NULL,
        `task_id` INT(11) NOT NULL,
        `collected` DATETIME NOT NULL,
        `status` INT(11) DEFAULT NULL
        ) ENGINE=MyISAM DEFAULT CHARSET=latin1;
        '''),
        ('akrr_default_walllimit', '''
        CREATE TABLE IF NOT EXISTS `akrr_default_walllimit` (
        `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        `resource` TEXT,
        `app` TEXT,
        `walllimit` INT(11) DEFAULT NULL COMMENT 'wall time limit in minutes',
        `resource_param` TEXT,
        `app_param` TEXT,
        `last_update` DATETIME NOT NULL,
        `comments` TEXT NOT NULL,
        UNIQUE `resource_app_resource_param_app_param` ( `resource`(100), `app`(100), `resource_param`(100), `app_param`(100))
        ) ENGINE=MyISAM DEFAULT CHARSET=latin1;
        '''),
        ('akrr_errmsg', '''
        CREATE TABLE IF NOT EXISTS `akrr_errmsg` (
        `task_id` INT(11) DEFAULT NULL,
        `err_regexp_id` INT(11) NOT NULL DEFAULT '1',
        `appstdout` LONGTEXT,
        `stderr` LONGTEXT,
        `stdout` LONGTEXT,
        `taskexeclog` LONGTEXT,
        UNIQUE KEY `task_id` (`task_id`)
        ) ENGINE=MyISAM DEFAULT CHARSET=latin1;
        '''),
        ('DROP akrr_err_regexp',
         """
         DROP TABLE IF EXISTS `akrr_err_regexp`;
         """),
        ('akrr_err_regexp', '''
        CREATE TABLE IF NOT EXISTS `akrr_err_regexp` (
        `id` INT(8) NOT NULL AUTO_INCREMENT,
        `active` TINYINT(1) NOT NULL DEFAULT '0',
        `resource` VARCHAR(255) NOT NULL DEFAULT '*',
        `app` VARCHAR(255) NOT NULL DEFAULT '*',
        `reg_exp` TEXT NOT NULL,
        `reg_exp_opt` VARCHAR(255) NOT NULL DEFAULT '',
        `source` VARCHAR(255) NOT NULL DEFAULT '*' COMMENT 'where reg_exp will be applied',
        `err_msg` TEXT NOT NULL COMMENT 'Brief error message which will reported upstream',
        `description` TEXT NOT NULL,
        PRIMARY KEY (`id`)
        ) ENGINE=MyISAM AUTO_INCREMENT=1000002 DEFAULT CHARSET=latin1;
        '''),
        ('DROP akrr_internal_failure_code',
         """
         DROP TABLE IF EXISTS `akrr_internal_failure_codes`;
         """),
        ('akrr_internal_failure_code', '''
        CREATE TABLE IF NOT EXISTS `akrr_internal_failure_codes` (
        `id` INT(11) NOT NULL,
        `description` TEXT NOT NULL,
        PRIMARY KEY (`id`)
        ) ENGINE=MyISAM DEFAULT CHARSET=latin1;
        '''),
        ('akrr_resource_maintenance', '''
        CREATE TABLE IF NOT EXISTS `akrr_resource_maintenance` (
        `id` INT(11) NOT NULL AUTO_INCREMENT,
        `resource` VARCHAR(255) NOT NULL,
        `start` DATETIME NOT NULL,
        `end` DATETIME NOT NULL,
        `comment` TEXT NOT NULL,
        PRIMARY KEY (`id`)
        ) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;
        '''),
        ('akrr_taks_errors', '''
        CREATE TABLE IF NOT EXISTS `akrr_taks_errors` (
        `task_id` INT(11) NOT NULL,
        `err_reg_exp_id` INT(11) DEFAULT NULL COMMENT 'errors identified using reg_exp',
        PRIMARY KEY (`task_id`)
        ) ENGINE=MyISAM DEFAULT CHARSET=latin1;
        '''),
        ('akrr_xdmod_instanceinfo', '''
        CREATE TABLE IF NOT EXISTS `akrr_xdmod_instanceinfo` (
        `instance_id` BIGINT(20) NOT NULL,
        `collected` DATETIME NOT NULL,
        `committed` DATETIME NOT NULL,
        `resource` VARCHAR(255) NOT NULL,
        `executionhost` VARCHAR(255) NOT NULL,
        `reporter` VARCHAR(255) NOT NULL,
        `reporternickname` VARCHAR(255) NOT NULL,
        `status` INT(1) UNSIGNED DEFAULT NULL,
        `message` LONGTEXT,
        `stderr` LONGTEXT,
        `body` LONGTEXT,
        `memory` FLOAT NOT NULL,
        `cputime` FLOAT NOT NULL,
        `walltime` FLOAT NOT NULL,
        `job_id` BIGINT(20) DEFAULT NULL,
        `internal_failure` INT(11) NOT NULL DEFAULT '0',
        `nodes` TEXT,
        `ncores` INT(11) DEFAULT NULL,
        `nnodes` INT(11) DEFAULT NULL,
        UNIQUE KEY `instance_id` (`instance_id`)
        ) ENGINE=MyISAM DEFAULT CHARSET=latin1;
        '''),
        ('COMPLETEDTASKS', '''
        CREATE TABLE IF NOT EXISTS `COMPLETEDTASKS` (
        `task_id` INT(11) DEFAULT NULL,
        `time_finished` DATETIME DEFAULT NULL,
        `status` TEXT,
        `status_info` TEXT,
        `time_to_start` DATETIME DEFAULT NULL,
        `datetimestamp` TEXT,
        `time_activated` DATETIME DEFAULT NULL,
        `time_submitted_to_queue` DATETIME DEFAULT NULL,
        `repeat_in` CHAR(20) DEFAULT NULL,
        `resource` TEXT,
        `app` TEXT,
        `resource_param` TEXT,
        `app_param` TEXT,
        `task_param` TEXT,
        `group_id` TEXT,
        `fatal_errors_count` INT(11) DEFAULT '0',
        `fails_to_submit_to_the_queue` INT(11) DEFAULT '0',
        `parent_task_id` INT(11) DEFAULT NULL,
        UNIQUE KEY `task_id` (`task_id`)
        ) ENGINE=MyISAM DEFAULT CHARSET=latin1;
        '''),
        ('nodes', '''
        CREATE TABLE IF NOT EXISTS `nodes` (
        `node_id` INT(11) NOT NULL AUTO_INCREMENT,
        `resource_id` INT(11) NOT NULL,
        `name` VARCHAR(128) NOT NULL,
        PRIMARY KEY (`node_id`)
        ) ENGINE=MyISAM AUTO_INCREMENT=1704 DEFAULT CHARSET=latin1;
        '''),
        ('SCHEDULEDTASKS', '''
        CREATE TABLE IF NOT EXISTS `SCHEDULEDTASKS` (
        `task_id` INT(11) NOT NULL AUTO_INCREMENT,
        `time_to_start` DATETIME DEFAULT NULL,
        `repeat_in` CHAR(20) DEFAULT NULL,
        `resource` TEXT,
        `app` TEXT,
        `resource_param` TEXT,
        `app_param` TEXT,
        `task_param` TEXT,
        `group_id` TEXT,
        `parent_task_id` INT(16) DEFAULT NULL,
        PRIMARY KEY (`task_id`)
        ) ENGINE=MyISAM AUTO_INCREMENT=3144529 DEFAULT CHARSET=latin1;
        '''),
        ('resources', '''
        CREATE TABLE IF NOT EXISTS resources (
        id                INT PRIMARY KEY AUTO_INCREMENT,
        xdmod_resource_id INT               NULL,
        name              VARCHAR(256)      NOT NULL,
        enabled           BOOL DEFAULT TRUE NOT NULL,
        CONSTRAINT UNIQUE INDEX resource_name_unique (name)
        ) ENGINE=MyISAM DEFAULT CHARSET=latin1;
        '''),
        ('app_kernels', '''
        CREATE TABLE IF NOT EXISTS app_kernels (
        id      INT PRIMARY KEY AUTO_INCREMENT,
        name    VARCHAR(256)      NOT NULL,
        enabled BOOL DEFAULT TRUE NOT NULL,
        nodes_list VARCHAR(255) DEFAULT '1;2;4;8;16' COMMENT 'list of nodes numbers on which app kernel can run',
        CONSTRAINT UNIQUE INDEX app_kernels_name_unique (name)
        ) ENGINE=MyISAM DEFAULT CHARSET=latin1;
        '''),
        ('resource_app_kernels', '''
        CREATE TABLE IF NOT EXISTS resource_app_kernels (
        id            INT PRIMARY KEY AUTO_INCREMENT,
        resource_id   INT               NOT NULL,
        app_kernel_id INT               NOT NULL,
        enabled       BOOL DEFAULT TRUE NOT NULL,
        CONSTRAINT FOREIGN KEY resource_app_kernels_resource_id (resource_id)
        REFERENCES mod_akrr.resources (id)
          ON DELETE CASCADE,
        CONSTRAINT FOREIGN KEY resource_app_kernels_app_kernel_id (app_kernel_id)
        REFERENCES mod_akrr.app_kernels (id)
          ON DELETE CASCADE
        ) ENGINE=MyISAM DEFAULT CHARSET=latin1;
        '''),
        ('akrr_erran', '''
        CREATE OR REPLACE VIEW `akrr_erran` AS select `c`.`task_id` AS `task_id`,`c`.`time_finished` AS `time_finished`,`c`.`resource` AS `resource`,`c`.`app` AS `app`,`c`.`resource_param` AS `resource_param`,`ii`.`status` AS `status`,`ii`.`walltime` AS `walltime`,`ii`.`body` AS `body`,`em`.`appstdout` AS `appstdout`,`em`.`stderr` AS `stderr`,`em`.`stdout` AS `stdout` from ((`COMPLETEDTASKS` `c` join `akrr_xdmod_instanceinfo` `ii`) join `akrr_errmsg` `em`) where ((`c`.`task_id` = `ii`.`instance_id`) and (`c`.`task_id` = `em`.`task_id`));
        '''),
        ('akrr_erran2', '''
        CREATE OR REPLACE VIEW `akrr_erran2` AS select `ct`.`task_id` AS `task_id`,`ct`.`time_finished` AS `time_finished`,`ct`.`resource` AS `resource`,`ct`.`app` AS `app`,`ct`.`resource_param` AS `resource_param`,`ii`.`status` AS `status`,`em`.`err_regexp_id` AS `err_regexp_id`,`re`.`err_msg` AS `err_msg`,`ii`.`walltime` AS `walltime`,`ct`.`status` AS `akrr_status`,`ct`.`status` AS `akrr_status_info`,`em`.`appstdout` AS `appstdout`,`em`.`stderr` AS `stderr`,`em`.`stdout` AS `stdout`,`ii`.`body` AS `ii_body`,`ii`.`message` AS `ii_msg` from (((`COMPLETEDTASKS` `ct` join `akrr_xdmod_instanceinfo` `ii`) join `akrr_errmsg` `em`) join `akrr_err_regexp` `re`) where ((`ct`.`task_id` = `ii`.`instance_id`) and (`ct`.`task_id` = `em`.`task_id`) and (`re`.`id` = `em`.`err_regexp_id`));
        '''),
        ('akrr_err_distribution_alltime', '''
        CREATE OR REPLACE VIEW `akrr_err_distribution_alltime` AS select count(0) AS `Rows`,`akrr_erran2`.`err_regexp_id` AS `err_regexp_id`,`akrr_erran2`.`err_msg` AS `err_msg` from `akrr_erran2` group by `akrr_erran2`.`err_regexp_id` order by `akrr_erran2`.`err_regexp_id`;
        ''')

    )

    population_statements = (
        ('POPULATE akrr_internal_failure_codes', '''
INSERT INTO `akrr_internal_failure_codes` VALUES (0,'No Error/Internal Error is not detected'),(10000,'Unspecified internal error'),(10001,'Resource on Maintenance\r\n'),(10002,'Insufficient wall-time'),(10003,'Testing/Demployment'),(10004,'The subtask was probably never run. Possibly previous subtask in master task stuck and/or use up all walltime');
        '''),
        ('POPULATE akrr_err_regexp', """
INSERT INTO `akrr_err_regexp` VALUES
(1,    0, '',  '',  '',                                                                       '','*','Completed Successfully','Holder for no errors, i.e. successful runs'),
(1004, 1, '*', '*', 'ERROR: Job was killed on remote resource due to walltime exceeded limit','0','akrr_status','Job was killed on remote resource due to walltime exceeded limit','walltime exceeded limit,\r\nprocessing from akrr_status'),
(1000, 0, '',  '',  '',                                                                       '','*','Unknown Error','Holder for unknown errors'),
(1003, 0, '*', '*', '',                                                                       '','*','','On Ranger sometimes can not read from $WORK even if the quota is ok\r\n\r\nTraceback (most recent call last):\r\n  File \"/home/xdtas/akrrpack/akrr/akrrtaskinca.py\", line 173, in CreateBatchJobScriptAndSubmitIt\r\n    raise akrr.AkrrError(akrr.ERROR_REMOTE_JOB,\"Can''t get job id. \"+msg)\r\nAkrrError: Can''t run job.Can''t get job id. -------------------------------------------------------------------\r\n------- Welcome to TACC''s Ranger System, an NSF XD Resource -------\r\n-------------------------------------------------------------------\r\n--> Checking that you specified -V...\r\n--> Checking that you specified a time limit...\r\n--> Checking that you specified a queue...\r\n--> Setting project...\r\n--> Checking that you specified a parallel environment...\r\n--> Checking that you specified a valid parallel environment name...\r\n--> Checking that the minimum and maximum PE counts are the same...\r\n--> Checking that the number of PEs requested is valid...\r\n--> Ensuring absence of dubious h_vmem,h_data,s_vmem,s_data limits...\r\n--> Requesting valid memory configuration (31.3G)...\r\n--> Verifying WORK file-system availability...\r\n-------------------> Rejecting job <-------------------\r\nUnable to read from your WORK file system.\r\nPlease verify that you are not over disk quota before\r\nsubmitting subsequent jobs.\r\n\r\n\r\nPlease contact TACC Consulting if you believe you have\r\nreceived this message in error.\r\n-------------------------------------------------------\r\nUnable to run job: JSV rejected job.\r\nExiting.\r\n'),
(1001, 1, '*', '*', 'WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED.*IT IS POSSIBLE THAT SOMEONE IS DOING SOMETHING NASTY','re.DOTALL|re.I','akrr_status_info,akrr_task_log','ssh connection refused because remote host identification has changed','Error message is :\r\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\r\n\r\n@    WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!     @\r\n\r\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\r\n\r\nIT IS POSSIBLE THAT SOMEONE IS DOING SOMETHING NASTY!\r\n\r\nSomeone could be eavesdropping on you right now (man-in-the-middle attack)!\r\n\r\nIt is also possible that the RSA host key has just been changed.'),
(1002, 1, '*', '*', 'cannot connect to local mpd \\(.*\\); possible causes:.*no mpd is running on this host.*an mpd is running but was started without a \"console\" \\(-n option\\)','re.DOTALL|re.I','appstdout,stderr,stdout','Can not start MPI job (can not locate MPI daemon)','Probably problems with starting MPI job\r\n\r\noriginal error message:\r\n\r\non edge:\r\nmpiexec_d07n29b.ccr.buffalo.edu: cannot connect to local mpd (/tmp/mpd2.console_xdtas_$$); possible causes:\r\n  1. no mpd is running on this host\r\n  2. an mpd is running but was started without a \"console\" (-n option)\r\n\r\non tresles?:\r\n\r\nmpdallexit: cannot connect to local mpd (*?); possible causes:\r\n  1. no mpd is running on this host\r\n  2. an mpd is running but was started without a \"console\" (-n option)\r\nIn case 1, you can start an mpd on this host with:\r\n    mpd &\r\nand you will be able to run jobs just on this host.\r\nFor more details on starting mpds on a set of hosts, see\r\nthe MVAPICH2 User Guide.'),
(1005, 1, '*', '*', 'forrtl: severe \\(174\\): SIGSEGV, segmentation fault occurred',         're.I','appstdout,stderr,stdout','SIGSEGV in Fortran code, try to increase stacksize ','Error Message:\r\nforrtl: severe (174): SIGSEGV, segmentation fault occurred\r\n\r\nCaught on edge xdmod.benchmark.npb'),(1000001,0,'*','*','SIGSEGV','re.I','appstdout,stderr,stdout','segmentation fault occurred during remote execution',''),
(1006, 1, '*', '*', 'rank.*in job.*caused collective abort of all ranks.*exit status of rank.*killed by signal 9','re.DOTALL|re.I','appstdout,stderr,stdout','Terminated by SIGKILL. Probably \"out of memory\"','caught on edge (xdmod.benchmark.io.ior):\r\npossible related message is:\r\nrank 0 in job 4  d09n39a_37781   caused collective abort of all ranks\r\n  exit status of rank 0: killed by signal 9 \r\n\r\nhttp://www.quantumwise.com/support/faq/104-killed-by-signal-9?catid=24%3Aerror-messages\r\nsuggests:\r\n\r\nWhen running in parallel, sometimes you may see an error like\r\n\r\nrank 1 in job 34  n7_3767\r\n caused collective abort of all ranks  \r\nexit status of rank 1: killed by signal 9\r\n\r\nIn most situations this is a case of \"out of memory\". Be careful not to run many MPI processes on the same node!');
        """),
        ('POPULATE app_kernels',"""
        INSERT INTO `app_kernels` (id,name,nodes_list) VALUES
            (7,'xdmod.benchmark.mpi.imb','2;4;8;16'),
            (22,'xdmod.app.chem.gamess','1;2;4;8'),
            (23,'xdmod.app.md.namd','1;2;4;8'),
            (24,'xdmod.app.chem.nwchem','1;2;4;8'),
            (25,'xdmod.benchmark.hpcc','1;2;4;8;16'),
            (27,'xdmod.benchmark.io.ior','1;2;4;8'),
            (28,'xdmod.benchmark.graph.graph500','1;2;4;8'),
            (29,'xdmod.app.astro.enzo','1;2;4;8'),
            (30,'xdmod.app.md.gromacs.micro','1')
        ON DUPLICATE KEY UPDATE id=VALUES(id);
        """)
    )

    connection_function=None
    if not dry_run:
        from akrr import cfg
        connection_function= akrr.db.get_akrr_db
        
    create_and_populate_tables(
        default_tables,
        population_statements,
        "Creating mod_akrr Tables / Views...",
        "mod_akrr Tables / Views Created!",
        connection_function,
        dry_run=dry_run
    )


def create_and_populate_mod_appkernel_tables(dry_run=False):
    """
    Create / Populate the required tables / views in the mod_appkernel database.
    """

    # DEFINE: the tables / views that mod_appkernel needs.
    default_tables = (
        ('a_data', '''
        CREATE TABLE IF NOT EXISTS `a_data` (
  `ak_name` VARCHAR(64) NOT NULL COMMENT '		',
  `resource` VARCHAR(128) NOT NULL,
  `metric` VARCHAR(128) NOT NULL,
  `num_units` INT(10) UNSIGNED NOT NULL DEFAULT '1',
  `processor_unit` ENUM('node','core') DEFAULT NULL,
  `collected` INT(10) NOT NULL DEFAULT '0',
  `env_version` VARCHAR(64) DEFAULT NULL,
  `unit` VARCHAR(32) DEFAULT NULL,
  `metric_value` VARCHAR(255) DEFAULT NULL,
  `ak_def_id` INT(10) UNSIGNED NOT NULL DEFAULT '0',
  `resource_id` INT(10) UNSIGNED NOT NULL DEFAULT '0',
  `metric_id` INT(10) UNSIGNED NOT NULL DEFAULT '0',
  `status` ENUM('success','failure','error','queued') DEFAULT NULL,
  KEY `ak_def_id` (`ak_def_id`,`resource_id`,`metric_id`,`num_units`),
  KEY `ak_name` (`ak_name`,`resource`,`metric`,`num_units`),
  KEY `resource_id` (`resource_id`),
  KEY `metric_id` (`metric_id`),
  KEY `num_units` (`num_units`),
  KEY `env_version` (`env_version`),
  KEY `collected` (`collected`),
  KEY `status` (`status`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
    '''),
        ('a_data2', '''
    CREATE TABLE IF NOT EXISTS `a_data2` (
  `ak_name` VARCHAR(64) NOT NULL COMMENT '		',
  `resource` VARCHAR(128) NOT NULL,
  `metric` VARCHAR(128) NOT NULL,
  `num_units` INT(10) UNSIGNED NOT NULL DEFAULT '1',
  `processor_unit` ENUM('node','core') DEFAULT NULL,
  `collected` INT(10) NOT NULL DEFAULT '0',
  `env_version` VARCHAR(64) DEFAULT NULL,
  `unit` VARCHAR(32) DEFAULT NULL,
  `metric_value` VARCHAR(255) DEFAULT NULL,
  `running_average` DOUBLE DEFAULT NULL,
  `control` DOUBLE DEFAULT NULL,
  `controlStart` DOUBLE DEFAULT NULL,
  `controlEnd` DOUBLE DEFAULT NULL,
  `controlMin` DOUBLE DEFAULT NULL,
  `controlMax` DOUBLE DEFAULT NULL,
  `ak_def_id` INT(10) UNSIGNED NOT NULL DEFAULT '0',
  `resource_id` INT(10) UNSIGNED NOT NULL DEFAULT '0',
  `metric_id` INT(10) UNSIGNED NOT NULL DEFAULT '0',
  `status` ENUM('success','failure','error','queued') DEFAULT NULL,
  `controlStatus` enum('undefined','control_region_time_interval','in_contol','under_performing','over_performing','failed') NOT NULL DEFAULT 'undefined',
  KEY `ak_def_id` (`ak_def_id`,`resource_id`,`metric_id`,`num_units`),
  KEY `ak_name` (`ak_name`,`resource`,`metric`,`num_units`),
  KEY `ak_collected` (`ak_def_id`,`collected`,`status`),
  KEY `resource_id` (`resource_id`),
  KEY `metric_id` (`metric_id`),
  KEY `num_units` (`num_units`),
  KEY `env_version` (`env_version`),
  KEY `collected` (`collected`),
  KEY `status` (`status`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
    '''),
        ('app_kernel_def', '''
    CREATE TABLE IF NOT EXISTS `app_kernel_def` (
  `ak_def_id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(64) NOT NULL COMMENT '		',
  `ak_base_name` VARCHAR(128) NOT NULL,
  `processor_unit` ENUM('node','core') DEFAULT NULL,
  `enabled` TINYINT(1) NOT NULL DEFAULT '0',
  `description` TEXT,
  `visible` TINYINT(1) NOT NULL DEFAULT '0',
  `control_criteria` DOUBLE NULL DEFAULT NULL,
  PRIMARY KEY (`ak_def_id`),
  UNIQUE KEY `name_UNIQUE` (`name`),
  UNIQUE KEY `reporter_base` (`ak_base_name`),
  KEY `visible` (`visible`)
) ENGINE=InnoDB AUTO_INCREMENT=1000 DEFAULT CHARSET=latin1 COMMENT='App kernel definition.';
    '''),
        ('app_kernel', '''
    CREATE TABLE IF NOT EXISTS `app_kernel` (
  `ak_id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `num_units` INT(10) UNSIGNED NOT NULL DEFAULT '1',
  `ak_def_id` INT(10) UNSIGNED DEFAULT NULL,
  `name` VARCHAR(128) NOT NULL,
  `type` VARCHAR(64) DEFAULT NULL,
  `parser` VARCHAR(64) DEFAULT NULL,
  PRIMARY KEY (`ak_id`,`num_units`),
  UNIQUE KEY `index_unique` (`num_units`,`ak_def_id`),
  KEY `fk_reporter_app_kernel` (`ak_def_id`),
  CONSTRAINT `fk_reporter_app_kernel` FOREIGN KEY (`ak_def_id`) REFERENCES `app_kernel_def` (`ak_def_id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=107 DEFAULT CHARSET=latin1 COMMENT='Application kernel info including num processing units';
    '''),
        ('metric', '''
    CREATE TABLE IF NOT EXISTS `metric` (
  `metric_id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `short_name` VARCHAR(32) NOT NULL,
  `name` VARCHAR(128) NOT NULL,
  `unit` VARCHAR(32) DEFAULT NULL,
  `guid` VARCHAR(64) NOT NULL,
  PRIMARY KEY (`metric_id`),
  UNIQUE KEY `unique_guid` (`guid`)
) ENGINE=InnoDB AUTO_INCREMENT=270 DEFAULT CHARSET=latin1 COMMENT='Individual metric definitions';
    '''),
        ('parameter', '''
    CREATE TABLE IF NOT EXISTS `parameter` (
  `parameter_id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `tag` VARCHAR(64) DEFAULT NULL,
  `name` VARCHAR(128) NOT NULL,
  `unit` VARCHAR(64) DEFAULT NULL,
  `guid` VARCHAR(64) NOT NULL,
  PRIMARY KEY (`parameter_id`),
  UNIQUE KEY `unique_guid` (`guid`)
) ENGINE=InnoDB AUTO_INCREMENT=162 DEFAULT CHARSET=latin1 COMMENT='Individual parameter definitions';
    '''),
        ('resource', '''
    CREATE TABLE IF NOT EXISTS `resource` (
  `resource_id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `resource` VARCHAR(128) NOT NULL,
  `nickname` VARCHAR(64) NOT NULL,
  `description` TEXT,
  `enabled` TINYINT(1) NOT NULL DEFAULT '0',
  `visible` TINYINT(1) NOT NULL DEFAULT '0',
  `xdmod_resource_id` INT(11) DEFAULT NULL,
  `xdmod_cluster_id` INT(11) DEFAULT NULL,
  PRIMARY KEY (`resource_id`),
  KEY `visible` (`visible`)
) ENGINE=InnoDB AUTO_INCREMENT=1000 DEFAULT CHARSET=latin1 COMMENT='Resource definitions';
    '''),
        ('ak_has_metric', '''
    CREATE TABLE IF NOT EXISTS `ak_has_metric` (
  `ak_id` INT(10) UNSIGNED NOT NULL,
  `metric_id` INT(10) UNSIGNED NOT NULL,
  `num_units` INT(10) UNSIGNED NOT NULL,
  PRIMARY KEY (`ak_id`,`metric_id`,`num_units`),
  KEY `fk_reporter_has_metric_metric` (`metric_id`),
  KEY `fk_reporter_has_metric_reporter` (`ak_id`,`num_units`),
  CONSTRAINT `ak_has_metric_ibfk_1` FOREIGN KEY (`ak_id`) REFERENCES `app_kernel` (`ak_id`),
  CONSTRAINT `fk_reporter_has_metric_metric` FOREIGN KEY (`metric_id`) REFERENCES `metric` (`metric_id`) ON DELETE CASCADE ON UPDATE NO ACTION,
  CONSTRAINT `fk_reporter_has_metric_reporter` FOREIGN KEY (`ak_id`, `num_units`) REFERENCES `app_kernel` (`ak_id`, `num_units`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Association between app kernels and metrics';
    '''),
        ('ak_has_parameter', '''
    CREATE TABLE IF NOT EXISTS `ak_has_parameter` (
  `ak_id` INT(10) UNSIGNED NOT NULL,
  `parameter_id` INT(10) UNSIGNED NOT NULL,
  PRIMARY KEY (`ak_id`,`parameter_id`),
  KEY `fk_reporter_has_parameter_parameter` (`parameter_id`),
  KEY `fk_reporter_has_parameter_reporter` (`ak_id`),
  CONSTRAINT `fk_reporter_has_parameter_parameter` FOREIGN KEY (`parameter_id`) REFERENCES `parameter` (`parameter_id`) ON DELETE CASCADE ON UPDATE NO ACTION,
  CONSTRAINT `fk_reporter_has_parameter_reporter` FOREIGN KEY (`ak_id`) REFERENCES `app_kernel` (`ak_id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Association between app kernels and parameters';
    '''),
        ('ak_instance', '''
    CREATE TABLE IF NOT EXISTS `ak_instance` (
  `ak_id` INT(10) UNSIGNED NOT NULL COMMENT '	',
  `collected` DATETIME NOT NULL,
  `resource_id` INT(10) UNSIGNED NOT NULL,
  `instance_id` INT(11) DEFAULT NULL,
  `job_id` VARCHAR(32) DEFAULT NULL COMMENT 'resource mgr job id',
  `status` ENUM('success','failure','error','queued') DEFAULT NULL,
  `ak_def_id` INT(10) UNSIGNED NOT NULL,
  `env_version` VARCHAR(64) DEFAULT NULL,
  `controlStatus` enum('undefined','control_region_time_interval','in_contol','under_performing','over_performing','failed') NOT NULL DEFAULT 'undefined',
  PRIMARY KEY (`ak_id`,`collected`,`resource_id`),
  KEY `fk_reporter_instance_reporter` (`ak_id`),
  KEY `fk_reporter_instance_resource` (`resource_id`),
  KEY `ak_def_id` (`ak_def_id`,`collected`,`resource_id`,`env_version`),
  KEY `instance_id` (`instance_id`),
  CONSTRAINT `fk_reporter_instance_reporter` FOREIGN KEY (`ak_id`) REFERENCES `app_kernel` (`ak_id`) ON DELETE CASCADE ON UPDATE NO ACTION,
  CONSTRAINT `fk_reporter_instance_resource` FOREIGN KEY (`resource_id`) REFERENCES `resource` (`resource_id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Execution instance';
    '''),
        ('ak_instance_debug', '''
    CREATE TABLE IF NOT EXISTS `ak_instance_debug` (
  `ak_id` INT(10) UNSIGNED NOT NULL,
  `collected` DATETIME NOT NULL,
  `resource_id` INT(10) UNSIGNED NOT NULL,
  `instance_id` INT(11) DEFAULT NULL,
  `message` BLOB,
  `stderr` BLOB,
  `walltime` FLOAT DEFAULT NULL,
  `cputime` FLOAT DEFAULT NULL,
  `memory` FLOAT DEFAULT NULL,
  `ak_error_cause` BLOB,
  `ak_error_message` BLOB,
  `ak_queue_time` INT(11) DEFAULT NULL,
  PRIMARY KEY (`ak_id`,`collected`,`resource_id`),
  KEY `instance_id` (`instance_id`),
  CONSTRAINT `fk_ak_debug_ak_instance1` FOREIGN KEY (`ak_id`, `collected`, `resource_id`) REFERENCES `ak_instance` (`ak_id`, `collected`, `resource_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Debugging information for application kernels.';
    '''),
        ('ak_supremme_metrics', '''
    CREATE TABLE IF NOT EXISTS `ak_supremm_metrics` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `ak_def_id` INT(11) NOT NULL,
  `supremm_metric_id` INT(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=latin1;
    '''),
        ('a_tree', '''
    CREATE TABLE IF NOT EXISTS `a_tree` (
  `ak_name` VARCHAR(64) NOT NULL COMMENT '		',
  `resource` VARCHAR(128) NOT NULL,
  `metric` VARCHAR(128) NOT NULL,
  `unit` VARCHAR(32) DEFAULT NULL,
  `processor_unit` ENUM('node','core') DEFAULT NULL,
  `num_units` INT(10) UNSIGNED NOT NULL DEFAULT '1',
  `ak_def_id` INT(10) UNSIGNED NOT NULL DEFAULT '0',
  `resource_id` INT(10) UNSIGNED NOT NULL,
  `metric_id` INT(10) UNSIGNED NOT NULL DEFAULT '0',
  `start_time` DATETIME DEFAULT NULL,
  `end_time` DATETIME DEFAULT NULL,
  `status` ENUM('success','failure','error','queued') DEFAULT NULL,
  KEY `ak_def_id` (`ak_def_id`,`resource_id`,`metric_id`,`num_units`),
  KEY `resource_id` (`resource_id`),
  KEY `start_time` (`start_time`),
  KEY `end_time` (`end_time`),
  KEY `status` (`status`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
    '''),
        ('a_tree2', '''
    CREATE TABLE IF NOT EXISTS `a_tree2` (
  `ak_name` VARCHAR(64) NOT NULL COMMENT '		',
  `resource` VARCHAR(128) NOT NULL,
  `metric` VARCHAR(128) NOT NULL,
  `unit` VARCHAR(32) DEFAULT NULL,
  `processor_unit` ENUM('node','core') DEFAULT NULL,
  `num_units` INT(10) UNSIGNED NOT NULL DEFAULT '1',
  `ak_def_id` INT(10) UNSIGNED NOT NULL DEFAULT '0',
  `resource_id` INT(10) UNSIGNED NOT NULL,
  `metric_id` INT(10) UNSIGNED NOT NULL DEFAULT '0',
  `start_time` DATETIME DEFAULT NULL,
  `end_time` DATETIME DEFAULT NULL,
  `status` ENUM('success','failure','error','queued') DEFAULT NULL,
  KEY `ak_def_id` (`ak_def_id`,`resource_id`,`metric_id`,`num_units`),
  KEY `resource_id` (`resource_id`),
  KEY `start_time` (`start_time`),
  KEY `end_time` (`end_time`),
  KEY `status` (`status`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
    '''),
        ('control_set', '''
    CREATE TABLE IF NOT EXISTS `control_set` (
  `metric_id` INT(10) NOT NULL,
  `ak_id` INT(10) NOT NULL,
  `resource_id` INT(10) NOT NULL,
  `min_collected` DATETIME NOT NULL,
  `max_collected` DATETIME NOT NULL COMMENT 'This remembers the control region used for each dataset.',
  PRIMARY KEY (`metric_id`,`ak_id`,`resource_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
    '''),
        ('ingester_log', '''
    CREATE TABLE IF NOT EXISTS `ingester_log` (
  `source` VARCHAR(64) NOT NULL,
  `url` VARCHAR(255) DEFAULT NULL,
  `num` INT(11) DEFAULT NULL,
  `last_update` DATETIME NOT NULL,
  `start_time` DATETIME DEFAULT NULL,
  `end_time` DATETIME DEFAULT NULL,
  `success` TINYINT(1) DEFAULT NULL,
  `message` VARCHAR(2048) DEFAULT NULL,
  `reportobj` BLOB COMMENT 'Compressed serialized php object with counters',
  KEY `source` (`source`,`last_update`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
    '''),
        ('log_id_seq', '''
    CREATE TABLE IF NOT EXISTS `log_id_seq` (
  `sequence` INT(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`sequence`)
) ENGINE=MyISAM AUTO_INCREMENT=415424 DEFAULT CHARSET=latin1;
    '''),
        ('log_table', '''
    CREATE TABLE IF NOT EXISTS `log_table` (
  `id` INT(11) DEFAULT NULL,
  `logtime` DATETIME DEFAULT NULL,
  `ident` TEXT,
  `priority` TEXT,
  `message` LONGTEXT,
  KEY `unique_id_idx` (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
    '''),

        ('metric_attribute', '''
    CREATE TABLE IF NOT EXISTS `metric_attribute` (
  `metric_id` INT(10) NOT NULL,
  `larger` TINYINT(1) NOT NULL,
  PRIMARY KEY (`metric_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
    '''
        ),
        ('metric_data', '''
    CREATE TABLE IF NOT EXISTS `metric_data` (
  `metric_id` INT(10) UNSIGNED NOT NULL,
  `ak_id` INT(10) UNSIGNED NOT NULL,
  `collected` DATETIME NOT NULL COMMENT '	',
  `resource_id` INT(10) UNSIGNED NOT NULL,
  `value_string` VARCHAR(255) DEFAULT NULL,
  `running_average` DOUBLE DEFAULT NULL,
  `control` DOUBLE DEFAULT NULL,
  `controlStart` DOUBLE DEFAULT NULL,
  `controlEnd` DOUBLE DEFAULT NULL,
  `controlMin` DOUBLE DEFAULT NULL,
  `controlMax` DOUBLE DEFAULT NULL,
  `controlStatus` enum('undefined','control_region_time_interval','in_contol','under_performing','over_performing','failed') NOT NULL DEFAULT 'undefined',
  PRIMARY KEY (`metric_id`,`ak_id`,`collected`,`resource_id`),
  KEY `fk_metric_data_metric` (`metric_id`),
  KEY `fk_metric_data_reporter_instance` (`ak_id`,`collected`,`resource_id`),
  CONSTRAINT `fk_metric_data_metric` FOREIGN KEY (`metric_id`) REFERENCES `metric` (`metric_id`) ON DELETE CASCADE ON UPDATE NO ACTION,
  CONSTRAINT `fk_metric_data_reporter_instance` FOREIGN KEY (`ak_id`, `collected`, `resource_id`) REFERENCES `ak_instance` (`ak_id`, `collected`, `resource_id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Collected application kernel data fact table';
    '''),

        ('parameter_data', '''
    CREATE TABLE IF NOT EXISTS `parameter_data` (
  `ak_id` INT(10) UNSIGNED NOT NULL,
  `collected` DATETIME NOT NULL,
  `resource_id` INT(10) UNSIGNED NOT NULL,
  `parameter_id` INT(10) UNSIGNED NOT NULL,
  `value_string` LONGBLOB,
  `value_md5` VARCHAR(32) NOT NULL,
  PRIMARY KEY (`ak_id`,`collected`,`resource_id`,`parameter_id`),
  KEY `fk_parameter_data_reporter_instance` (`ak_id`,`collected`,`resource_id`),
  KEY `fk_parameter_data_parameter` (`parameter_id`),
  KEY `md5sum` (`value_md5`),
  CONSTRAINT `fk_parameter_data_parameter` FOREIGN KEY (`parameter_id`) REFERENCES `parameter` (`parameter_id`) ON DELETE CASCADE ON UPDATE NO ACTION,
  CONSTRAINT `fk_parameter_data_reporter_instance` FOREIGN KEY (`ak_id`, `collected`, `resource_id`) REFERENCES `ak_instance` (`ak_id`, `collected`, `resource_id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Collected application kernel parameters fact table';
    '''),
        ('report', '''
    CREATE TABLE IF NOT EXISTS `report` (
  `user_id` INT(11) NOT NULL,
  `send_report_daily` INT(11) NOT NULL DEFAULT '0',
  `send_report_weekly` INT(11) NOT NULL DEFAULT '0' COMMENT 'Negative-None, otherwise days of the week, i.e. 2 - Monday',
  `send_report_monthly` INT(11) NOT NULL DEFAULT '0' COMMENT 'negative is none, otherwise day of the month',
  `settings` TEXT NOT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
    '''),

        ('sumpremm_metrics', '''
    CREATE TABLE IF NOT EXISTS `supremm_metrics` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(256) NOT NULL,
  `formula` TEXT NOT NULL,
  `label` TEXT NOT NULL,
  `units` TEXT,
  `info` TEXT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `id` (`id`),
  UNIQUE KEY `id_2` (`id`),
  UNIQUE KEY `name_2` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
    '''),
        ('v_ak_metrics', '''
    CREATE OR REPLACE VIEW `mod_appkernel`.`v_ak_metrics` AS select `mod_appkernel`.`app_kernel_def`.`ak_base_name` AS `name`,`mod_appkernel`.`app_kernel_def`.`enabled` AS `enabled`,`mod_appkernel`.`app_kernel`.`num_units` AS `num_units`,`mod_appkernel`.`app_kernel`.`ak_id` AS `ak_id`,`mod_appkernel`.`ak_has_metric`.`metric_id` AS `metric_id`,`mod_appkernel`.`metric`.`guid` AS `guid` from (((`mod_appkernel`.`app_kernel_def` join `mod_appkernel`.`app_kernel` on((`mod_appkernel`.`app_kernel_def`.`ak_def_id` = `mod_appkernel`.`app_kernel`.`ak_def_id`))) join `mod_appkernel`.`ak_has_metric` on(((`mod_appkernel`.`app_kernel`.`ak_id` = `mod_appkernel`.`ak_has_metric`.`ak_id`) and (`mod_appkernel`.`app_kernel`.`num_units` = `mod_appkernel`.`ak_has_metric`.`num_units`)))) join `mod_appkernel`.`metric` on((`mod_appkernel`.`ak_has_metric`.`metric_id` = `mod_appkernel`.`metric`.`metric_id`)));
    '''),
        ('v_ak_parameters', '''
    CREATE OR REPLACE VIEW `mod_appkernel`.`v_ak_parameters` AS select `mod_appkernel`.`app_kernel_def`.`ak_base_name` AS `name`,`mod_appkernel`.`app_kernel_def`.`enabled` AS `enabled`,`mod_appkernel`.`app_kernel`.`num_units` AS `num_units`,`mod_appkernel`.`app_kernel`.`ak_id` AS `ak_id`,`mod_appkernel`.`ak_has_parameter`.`parameter_id` AS `parameter_id`,`mod_appkernel`.`parameter`.`guid` AS `guid` from (((`mod_appkernel`.`app_kernel_def` join `mod_appkernel`.`app_kernel` on((`mod_appkernel`.`app_kernel_def`.`ak_def_id` = `mod_appkernel`.`app_kernel`.`ak_def_id`))) join `mod_appkernel`.`ak_has_parameter` on((`mod_appkernel`.`app_kernel`.`ak_id` = `mod_appkernel`.`ak_has_parameter`.`ak_id`))) join `mod_appkernel`.`parameter` on((`mod_appkernel`.`ak_has_parameter`.`parameter_id` = `mod_appkernel`.`parameter`.`parameter_id`)));
    '''),
        ('v_tree_debug', '''
    CREATE OR REPLACE VIEW `mod_appkernel`.`v_tree_debug` AS select `def`.`name` AS `ak_name`,`r`.`resource` AS `resource`,`def`.`processor_unit` AS `processor_unit`,`ak`.`num_units` AS `num_units`,`def`.`ak_def_id` AS `ak_def_id`,`ai`.`resource_id` AS `resource_id`,unix_timestamp(`ai`.`collected`) AS `collected`,`ai`.`status` AS `status`,`ai`.`instance_id` AS `instance_id` from (((`mod_appkernel`.`app_kernel_def` `def` join `mod_appkernel`.`app_kernel` `ak` on((`def`.`ak_def_id` = `ak`.`ak_def_id`))) join `mod_appkernel`.`ak_instance` `ai` on((`ak`.`ak_id` = `ai`.`ak_id`))) join `mod_appkernel`.`resource` `r` on((`ai`.`resource_id` = `r`.`resource_id`))) where ((`def`.`visible` = 1) and (`r`.`visible` = 1)) order by `def`.`name`,`r`.`resource`,`ak`.`num_units`,`ai`.`collected`;
    '''),
        # not sure how to set CONSTRAINT here
        # CONSTRAINT `fk_resource_id_ak_def_id` FOREIGN KEY (`resource_id`,`ak_def_id`) REFERENCES `ak_instance` (`ak_id`, `collected`, `resource_id`) ON DELETE CASCADE ON UPDATE NO ACTION
       ('control_region_def',"""
CREATE TABLE IF NOT EXISTS `control_region_def` (
  `control_region_def_id` int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
  `resource_id` int(10) unsigned NOT NULL,
  `ak_def_id` int(10) unsigned NOT NULL,
  `control_region_type` ENUM('date_range', 'data_points') DEFAULT 'date_range',
  `control_region_starts` datetime NOT NULL COMMENT 'Beginning of control region',
  `control_region_ends` datetime DEFAULT NULL COMMENT 'End of control region',
  `control_region_points` int(10) unsigned DEFAULT NULL COMMENT 'Number of points for control region',
  `comment`  varchar(255) DEFAULT NULL,
  CONSTRAINT `fk_ak_def_id` FOREIGN KEY (`ak_def_id`) REFERENCES `app_kernel_def` (`ak_def_id`) ON DELETE CASCADE ON UPDATE NO ACTION,
  CONSTRAINT `fk_resource_id` FOREIGN KEY (`resource_id`) REFERENCES `resource` (`resource_id`) ON DELETE CASCADE ON UPDATE NO ACTION,
  UNIQUE KEY `resource_id__ak_def_id__control_region_starts` (`resource_id`,`ak_def_id`,`control_region_starts`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;"""),
        ('control_regions',"""
CREATE TABLE IF NOT EXISTS `control_regions` (
  `control_region_id` int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
  `control_region_def_id` int(10) unsigned NOT NULL,
  `ak_id` int(10) unsigned NOT NULL,
  `metric_id` int(10) unsigned NOT NULL,
  `completed` TINYINT(1) NOT NULL DEFAULT '0' COMMENT 'Is the control region already completed',
  `controlStart` DOUBLE DEFAULT NULL,
  `controlEnd` DOUBLE DEFAULT NULL,
  `controlMin` DOUBLE DEFAULT NULL,
  `controlMax` DOUBLE DEFAULT NULL,
  UNIQUE KEY `control_region_def_id__metric_id` (`control_region_def_id`,`ak_id`,`metric_id`),
  CONSTRAINT `fk_control_region_def_id` FOREIGN KEY (`control_region_def_id`) REFERENCES `control_region_def` (`control_region_def_id`) ON DELETE CASCADE ON UPDATE NO ACTION,
  CONSTRAINT `fk_metric_id` FOREIGN KEY (`metric_id`) REFERENCES `metric` (`metric_id`) ON DELETE CASCADE ON UPDATE NO ACTION,
  CONSTRAINT `fk_ak_id` FOREIGN KEY (`ak_id`) REFERENCES `app_kernel` (`ak_id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;""") 
    )

    # DEFINE: The insert statements that will be needed to populate the tables.
    population_statements = (
        ('POPULATE app_kernel_def', """
INSERT INTO `app_kernel_def` VALUES
(7, 'IMB', 'xdmod.benchmark.mpi.imb', 'node', 0, '<a href="http://www.intel.com/software/imb/" target="_blank" alt="imb">Intel MPI Benchmark</a> (formally Pallas MPI Benchmark) suite. The suite measures the interconnect''s latency, bandwidth, bidirectional bandwidth, and various MPI collective operations'' latencies (Broadcast, AllToAll, AllGather, AllReduce, etc). It also measures the MPI-2 Remote Direct Memory Access (RDMA) performance.\r\n<p>\r\nThe benchmarks are run with one process (single-threaded mode) per node.', 0,NULL),
(22, 'GAMESS', 'xdmod.app.chem.gamess', 'node', 0, '<a href="http://www.msg.chem.iastate.edu/gamess/" target="_blank" alt="gamess">GAMESS</a> is an ab initio computational chemistry software package developed by Professor Mark Gordon''s research group at Iowa State University.\r\n<p>\r\nThe input to the benchmark runs is restricted Hartree-Fock energy calculation of C8H10 with MP2 correction.\r\n<p>\r\nThe version of GAMESS being benchmarked is 1 MAY 2012 (R1).\r\n', 0,NULL),
(23, 'NAMD', 'xdmod.app.md.namd', 'node', 0, '<a href="http://www.ks.uiuc.edu/Research/namd/" target="_blank" alt="namd">NAMD</a> is a molecular dynamics simulation package developed by the Theoretical and Computational Biophysics Group in the Beckman Institute for Advanced Science and Technology at the University of Illinois at Urbana-Champaign.\r\n<p>\r\nThe input to the benchmark runs is the Apolipoprotein A1 benchmark input, which consists of 92,224 atoms, uses 2 fs step size, 0,200 steps, and uses the NVE ensemble.\r\n<p>\r\nThe version of NAMD being benchmarked is 2.7b2', 0,NULL),
(24, 'NWChem', 'xdmod.app.chem.nwchem', 'node', 0, '<a href="http://www.nwchem-sw.org" target="_blank" alt="nwchem">NWChem</a> is an ab initio computational chemistry software package developed by Pacific Northwest National Laboratory.\r\n<p>\r\nThe input to the benchmark runs is the Hartree-Fock energy calculation of Au+ with MP2 and Coupled Cluster corrections.\r\n<p>\r\nThe version of NWChem being benchmarked is 5.1.1.\r\n<p>\r\nThe metrics we show here contain NWChem''s self-collected Global Arrays statistics. The Global Arrays toolkit is the communication library used by NWChem to manipulate large akrrays distributed across compute nodes. The Global Arrays toolkit has three basic operations: Get (fetch values from remote memory), Put (store values to remote memory), and Accumulate (update values in remote memory). NWChem measures the numbers of these operations and the amount of data affected by them.', 0,NULL),
(25, 'HPCC', 'xdmod.benchmark.hpcc', 'node', 0, '<a href="http://icl.cs.utk.edu/hpcc/" target="_blank" alt="hpcc">HPC Challenge Benchmark</a> suite. It consists of a) High Performance LINPACK, which solves a linear system of equations and measures the floating-point performance, b) Parallel Matrix Transpose (PTRANS), which measures total communications capacity of the interconnect, c) MPI Random Access, which measures the rate of random updates of remote memory, d) Fast Fourier Transform, which measures the floating-point performance of double-precision complex one-dimensional Discrete Fourier Transform. ', 0,NULL),
(27, 'IOR', 'xdmod.benchmark.io.ior', 'node', 0, 'IOR (Interleaved-Or-Random) measures the performance of a storage system under simple access patterns. It uses four different I/O interfaces: POSIX, MPI IO, HDF (Hierarchical Data Format), and Parallel NetCDF (Network Common Data Form) to read and write contiguous chunks of data against either a single file (N-to-1 mode) or N files (N-to-N mode), and it reports the aggregate I/O throughput.', 0,NULL),
(28, 'Graph500', 'xdmod.benchmark.graph.graph500', 'node', 0, '<a href="http://www.graph500.org" target="_blank" alt="graph500">Graph 500</a> is a benchmark designed to measure the performance of graph algorithms, an increasingly important workload in the data-intensive analytics applications.\r\n<p>\r\nCurrently Graph 500 benchmark contains one computational kernel: the breadth-first search. The input is a pre-generated graph created with the following parameters:  SCALE=16 and edgefactor=16. These translate to, on a per MPI process basis,  2^SCALE=65536 vertices and 65536*edgefactor=1.04 million edges.', 0,NULL),
(29, 'Enzo', 'xdmod.app.astro.enzo', 'node', 0, '<a href="http://enzo-project.org/" target="_blank" alt="Enzo">Enzo:</a> an Adaptive Mesh Refinement Code for Astrophysics\r\n<p>', 0,NULL),
(30, 'GROMACS-micro', 'xdmod.app.md.gromacs.micro', 'node', 0, '<a href="http://www.gromacs.org/" target="_blank" alt="GROMACS">GROMACS:</a> based micro-benchmark for testing purposes\r\n<p>', 0,NULL)
ON DUPLICATE KEY UPDATE ak_def_id=VALUES(ak_def_id);
        """),
    )

    # EXECUTE: the statements defined previously
    connection_function=None
    if not dry_run:
        from akrr import cfg
        connection_function= akrr.db.get_ak_db
    
    create_and_populate_tables(
        default_tables,
        population_statements,
        "Creating mod_appkernel Tables / Views...",
        "mod_appkernel Tables / Views Created!",
        connection_function,
        dry_run=dry_run
    )

