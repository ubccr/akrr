# coding: utf-8
from sqlalchemy import CHAR, Column, DateTime, Float, String, Table, Text, text
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, LONGTEXT, TINYINT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


t_active_tasks = Table(
    'active_tasks', metadata,
    Column('task_id', INTEGER(11), unique=True),
    Column('next_check_time', DateTime, nullable=False),
    Column('status', Text),
    Column('status_info', Text),
    Column('status_update_time', DateTime),
    Column('datetime_stamp', Text),
    Column('time_activated', DateTime),
    Column('time_submitted_to_queue', DateTime),
    Column('task_lock', INTEGER(11)),
    Column('time_to_start', DateTime),
    Column('repeat_in', CHAR(20)),
    Column('resource', Text),
    Column('app', Text),
    Column('resource_param', Text),
    Column('app_param', Text),
    Column('task_param', Text),
    Column('group_id', Text),
    Column('fatal_errors_count', INTEGER(4), server_default=text("'0'")),
    Column('fails_to_submit_to_the_queue', INTEGER(4), server_default=text("'0'")),
    Column('taskexeclog', LONGTEXT),
    Column('master_task_id', INTEGER(4), nullable=False, server_default=text("'0'"), comment='0 - independent task, otherwise task_id of master task '),
    Column('parent_task_id', INTEGER(11))
)


t_ak_on_nodes = Table(
    'ak_on_nodes', metadata,
    Column('resource_id', INTEGER(11), nullable=False),
    Column('node_id', INTEGER(11), nullable=False),
    Column('task_id', INTEGER(11), nullable=False),
    Column('collected', DateTime, nullable=False),
    Column('status', INTEGER(11))
)


class AkrrDefaultWalltimeLimit(Base):
    __tablename__ = 'akrr_default_walltime_limit'

    id = Column(INTEGER(11), primary_key=True)
    resource = Column(Text)
    app = Column(Text)
    walltime_limit = Column(INTEGER(11), comment='wall time limit in minutes')
    resource_param = Column(Text)
    app_param = Column(Text)
    last_update = Column(DateTime, nullable=False)
    comments = Column(Text, nullable=False)


t_akrr_err_distribution_alltime = Table(
    'akrr_err_distribution_alltime', metadata,
    Column('Rows', BIGINT(21), server_default=text("'0'")),
    Column('err_regexp_id', INTEGER(11), server_default=text("'1'")),
    Column('err_msg', Text)
)


class AkrrErrRegexp(Base):
    __tablename__ = 'akrr_err_regexp'

    id = Column(INTEGER(8), primary_key=True)
    active = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    resource = Column(String(255), nullable=False, server_default=text("'*'"))
    app = Column(String(255), nullable=False, server_default=text("'*'"))
    reg_exp = Column(Text, nullable=False)
    reg_exp_opt = Column(String(255), nullable=False, server_default=text("''"))
    source = Column(String(255), nullable=False, server_default=text("'*'"), comment='where reg_exp will be applied')
    err_msg = Column(Text, nullable=False, comment='Brief error message which will reported upstream')
    description = Column(Text, nullable=False)


t_akrr_erran = Table(
    'akrr_erran', metadata,
    Column('task_id', INTEGER(11)),
    Column('time_finished', DateTime),
    Column('resource', Text),
    Column('app', Text),
    Column('resource_param', Text),
    Column('status', INTEGER(1)),
    Column('walltime', Float),
    Column('body', LONGTEXT),
    Column('appstdout', LONGTEXT),
    Column('stderr', LONGTEXT),
    Column('stdout', LONGTEXT)
)


t_akrr_erran2 = Table(
    'akrr_erran2', metadata,
    Column('task_id', INTEGER(11)),
    Column('time_finished', DateTime),
    Column('resource', Text),
    Column('app', Text),
    Column('resource_param', Text),
    Column('status', INTEGER(1)),
    Column('err_regexp_id', INTEGER(11), server_default=text("'1'")),
    Column('err_msg', Text),
    Column('walltime', Float),
    Column('akrr_status', Text),
    Column('akrr_status_info', Text),
    Column('appstdout', LONGTEXT),
    Column('stderr', LONGTEXT),
    Column('stdout', LONGTEXT),
    Column('ii_body', LONGTEXT),
    Column('ii_msg', LONGTEXT)
)


t_akrr_errmsg = Table(
    'akrr_errmsg', metadata,
    Column('task_id', INTEGER(11), unique=True),
    Column('err_regexp_id', INTEGER(11), nullable=False, server_default=text("'1'")),
    Column('appstdout', LONGTEXT),
    Column('stderr', LONGTEXT),
    Column('stdout', LONGTEXT),
    Column('taskexeclog', LONGTEXT)
)


class AkrrInternalFailureCode(Base):
    __tablename__ = 'akrr_internal_failure_codes'

    id = Column(INTEGER(11), primary_key=True)
    description = Column(Text, nullable=False)


class AkrrResourceMaintenance(Base):
    __tablename__ = 'akrr_resource_maintenance'

    id = Column(INTEGER(11), primary_key=True)
    resource = Column(String(255), nullable=False)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
    comment = Column(Text, nullable=False)


class AkrrTaskError(Base):
    __tablename__ = 'akrr_task_errors'

    task_id = Column(INTEGER(11), primary_key=True)
    err_reg_exp_id = Column(INTEGER(11), comment='errors identified using reg_exp')


t_akrr_xdmod_instanceinfo = Table(
    'akrr_xdmod_instanceinfo', metadata,
    Column('instance_id', BIGINT(20), nullable=False, unique=True),
    Column('collected', DateTime, nullable=False),
    Column('committed', DateTime, nullable=False),
    Column('resource', String(255), nullable=False),
    Column('executionhost', String(255), nullable=False),
    Column('reporter', String(255), nullable=False),
    Column('reporternickname', String(255), nullable=False),
    Column('status', INTEGER(1)),
    Column('message', LONGTEXT),
    Column('stderr', LONGTEXT),
    Column('body', LONGTEXT),
    Column('memory', Float, nullable=False),
    Column('cputime', Float, nullable=False),
    Column('walltime', Float, nullable=False),
    Column('job_id', BIGINT(20)),
    Column('internal_failure', INTEGER(11), nullable=False, server_default=text("'0'")),
    Column('nodes', Text),
    Column('ncores', INTEGER(11)),
    Column('nnodes', INTEGER(11))
)


class AppKernel(Base):
    __tablename__ = 'app_kernels'

    id = Column(INTEGER(11), primary_key=True)
    name = Column(String(256), nullable=False, unique=True)
    enabled = Column(TINYINT(1), nullable=False, server_default=text("'1'"))
    nodes_list = Column(String(255), server_default=text("'1;2;4;8;16'"), comment='list of nodes numbers on which app kernel can run')


t_completed_tasks = Table(
    'completed_tasks', metadata,
    Column('task_id', INTEGER(11), unique=True),
    Column('time_finished', DateTime),
    Column('status', Text),
    Column('status_info', Text),
    Column('time_to_start', DateTime),
    Column('datetime_stamp', Text),
    Column('time_activated', DateTime),
    Column('time_submitted_to_queue', DateTime),
    Column('repeat_in', CHAR(20)),
    Column('resource', Text),
    Column('app', Text),
    Column('resource_param', Text),
    Column('app_param', Text),
    Column('task_param', Text),
    Column('group_id', Text),
    Column('fatal_errors_count', INTEGER(11), server_default=text("'0'")),
    Column('fails_to_submit_to_the_queue', INTEGER(11), server_default=text("'0'")),
    Column('parent_task_id', INTEGER(11))
)


class Node(Base):
    __tablename__ = 'nodes'

    node_id = Column(INTEGER(11), primary_key=True)
    resource_id = Column(INTEGER(11), nullable=False)
    name = Column(String(128), nullable=False)


class ResourceAppKernel(Base):
    __tablename__ = 'resource_app_kernels'

    id = Column(INTEGER(11), primary_key=True)
    resource_id = Column(INTEGER(11), nullable=False, index=True)
    app_kernel_id = Column(INTEGER(11), nullable=False, index=True)
    enabled = Column(TINYINT(1), nullable=False, server_default=text("'1'"))


class Resource(Base):
    __tablename__ = 'resources'

    id = Column(INTEGER(11), primary_key=True)
    xdmod_resource_id = Column(INTEGER(11))
    name = Column(String(256), nullable=False, unique=True)
    enabled = Column(TINYINT(1), nullable=False, server_default=text("'1'"))


class ScheduledTask(Base):
    __tablename__ = 'scheduled_tasks'

    task_id = Column(INTEGER(11), primary_key=True)
    time_to_start = Column(DateTime)
    repeat_in = Column(CHAR(20))
    resource = Column(Text)
    app = Column(Text)
    resource_param = Column(Text)
    app_param = Column(Text)
    task_param = Column(Text)
    group_id = Column(Text)
    parent_task_id = Column(INTEGER(16))


class XdResource(Base):
    __tablename__ = 'xd_resources'

    id = Column(INTEGER(11), primary_key=True)
    name = Column(String(128), nullable=False, unique=True)
    short_name = Column(String(32), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    enabled = Column(INTEGER(11), nullable=False)
    visible = Column(INTEGER(11), nullable=False)
    xdmod_resource_id = Column(INTEGER(11))
    xdmod_cluster_id = Column(INTEGER(11))
