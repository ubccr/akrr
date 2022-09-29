# coding: utf-8
from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, ForeignKeyConstraint, Index, LargeBinary, String, Table, Text, text
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, LONGBLOB, LONGTEXT, TINYINT
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


t_a_data = Table(
    'a_data', metadata,
    Column('ak_name', String(64), nullable=False, comment='\t\t'),
    Column('resource', String(128), nullable=False),
    Column('metric', String(128), nullable=False),
    Column('num_units', INTEGER(10), nullable=False, index=True, server_default=text("'1'")),
    Column('processor_unit', Enum('node', 'core')),
    Column('collected', INTEGER(10), nullable=False, index=True, server_default=text("'0'")),
    Column('env_version', String(64), index=True),
    Column('unit', String(32)),
    Column('metric_value', String(255)),
    Column('ak_def_id', INTEGER(10), nullable=False, server_default=text("'0'")),
    Column('resource_id', INTEGER(10), nullable=False, index=True, server_default=text("'0'")),
    Column('metric_id', INTEGER(10), nullable=False, index=True, server_default=text("'0'")),
    Column('status', Enum('success', 'failure', 'error', 'queued'), index=True),
    Index('ak_name', 'ak_name', 'resource', 'metric', 'num_units'),
    Index('ak_def_id', 'ak_def_id', 'resource_id', 'metric_id', 'num_units')
)


t_a_data2 = Table(
    'a_data2', metadata,
    Column('ak_name', String(64), nullable=False, comment='\t\t'),
    Column('resource', String(128), nullable=False),
    Column('metric', String(128), nullable=False),
    Column('num_units', INTEGER(10), nullable=False, index=True, server_default=text("'1'")),
    Column('processor_unit', Enum('node', 'core')),
    Column('collected', INTEGER(10), nullable=False, index=True, server_default=text("'0'")),
    Column('env_version', String(64), index=True),
    Column('unit', String(32)),
    Column('metric_value', String(255)),
    Column('running_average', Float(asdecimal=True)),
    Column('control', Float(asdecimal=True)),
    Column('controlStart', Float(asdecimal=True)),
    Column('controlEnd', Float(asdecimal=True)),
    Column('controlMin', Float(asdecimal=True)),
    Column('controlMax', Float(asdecimal=True)),
    Column('ak_def_id', INTEGER(10), nullable=False, server_default=text("'0'")),
    Column('resource_id', INTEGER(10), nullable=False, index=True, server_default=text("'0'")),
    Column('metric_id', INTEGER(10), nullable=False, index=True, server_default=text("'0'")),
    Column('status', Enum('success', 'failure', 'error', 'queued'), index=True),
    Column('controlStatus', Enum('undefined', 'control_region_time_interval', 'in_contol', 'under_performing', 'over_performing', 'failed'), nullable=False, server_default=text("'undefined'")),
    Index('ak_def_id', 'ak_def_id', 'resource_id', 'metric_id', 'num_units'),
    Index('ak_name', 'ak_name', 'resource', 'metric', 'num_units'),
    Index('ak_collected', 'ak_def_id', 'collected', 'status')
)


t_a_tree = Table(
    'a_tree', metadata,
    Column('ak_name', String(64), nullable=False, comment='\t\t'),
    Column('resource', String(128), nullable=False),
    Column('metric', String(128), nullable=False),
    Column('unit', String(32)),
    Column('processor_unit', Enum('node', 'core')),
    Column('num_units', INTEGER(10), nullable=False, server_default=text("'1'")),
    Column('ak_def_id', INTEGER(10), nullable=False, server_default=text("'0'")),
    Column('resource_id', INTEGER(10), nullable=False, index=True),
    Column('metric_id', INTEGER(10), nullable=False, server_default=text("'0'")),
    Column('start_time', DateTime, index=True),
    Column('end_time', DateTime, index=True),
    Column('status', Enum('success', 'failure', 'error', 'queued'), index=True),
    Index('ak_def_id', 'ak_def_id', 'resource_id', 'metric_id', 'num_units')
)


t_a_tree2 = Table(
    'a_tree2', metadata,
    Column('ak_name', String(64), nullable=False, comment='\t\t'),
    Column('resource', String(128), nullable=False),
    Column('metric', String(128), nullable=False),
    Column('unit', String(32)),
    Column('processor_unit', Enum('node', 'core')),
    Column('num_units', INTEGER(10), nullable=False, server_default=text("'1'")),
    Column('ak_def_id', INTEGER(10), nullable=False, server_default=text("'0'")),
    Column('resource_id', INTEGER(10), nullable=False, index=True),
    Column('metric_id', INTEGER(10), nullable=False, server_default=text("'0'")),
    Column('start_time', DateTime, index=True),
    Column('end_time', DateTime, index=True),
    Column('status', Enum('success', 'failure', 'error', 'queued'), index=True),
    Index('ak_def_id', 'ak_def_id', 'resource_id', 'metric_id', 'num_units')
)


class AkSupremmMetric(Base):
    __tablename__ = 'ak_supremm_metrics'

    id = Column(INTEGER(11), primary_key=True)
    ak_def_id = Column(INTEGER(11), nullable=False)
    supremm_metric_id = Column(INTEGER(11), nullable=False)


class AppKernelDef(Base):
    __tablename__ = 'app_kernel_def'
    __table_args__ = {'comment': 'App kernel definition.'}

    ak_def_id = Column(INTEGER(10), primary_key=True)
    name = Column(String(64), nullable=False, unique=True, comment='\t\t')
    ak_base_name = Column(String(128), nullable=False, unique=True)
    processor_unit = Column(Enum('node', 'core'))
    enabled = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    description = Column(Text)
    visible = Column(TINYINT(1), nullable=False, index=True, server_default=text("'0'"))
    control_criteria = Column(Float(asdecimal=True))


class ControlRegionDef(Base):
    __tablename__ = 'control_region_def'
    __table_args__ = (
        Index('resource_id__ak_def_id__control_region_starts', 'resource_id', 'ak_def_id', 'control_region_starts', unique=True),
    )

    control_region_def_id = Column(INTEGER(11), primary_key=True)
    resource_id = Column(INTEGER(10), nullable=False)
    ak_def_id = Column(INTEGER(10), nullable=False, index=True)
    control_region_type = Column(Enum('date_range', 'data_points'), server_default=text("'date_range'"))
    control_region_starts = Column(DateTime, nullable=False, comment='Beginning of control region')
    control_region_ends = Column(DateTime, comment='End of control region')
    control_region_points = Column(INTEGER(10), comment='Number of points for control region')
    comment = Column(String(255))


class ControlRegion(Base):
    __tablename__ = 'control_regions'
    __table_args__ = (
        Index('control_region_def_id__metric_id', 'control_region_def_id', 'ak_id', 'metric_id', unique=True),
    )

    control_region_id = Column(INTEGER(11), primary_key=True)
    control_region_def_id = Column(INTEGER(10), nullable=False)
    ak_id = Column(INTEGER(10), nullable=False, index=True)
    metric_id = Column(INTEGER(10), nullable=False, index=True)
    completed = Column(TINYINT(1), nullable=False, server_default=text("'0'"), comment='Is the control region already completed')
    controlStart = Column(Float(asdecimal=True))
    controlEnd = Column(Float(asdecimal=True))
    controlMin = Column(Float(asdecimal=True))
    controlMax = Column(Float(asdecimal=True))


t_ingester_log = Table(
    'ingester_log', metadata,
    Column('source', String(64), nullable=False),
    Column('url', String(255)),
    Column('num', INTEGER(11)),
    Column('last_update', DateTime, nullable=False),
    Column('start_time', DateTime),
    Column('end_time', DateTime),
    Column('success', TINYINT(1)),
    Column('message', String(2048)),
    Column('reportobj', LargeBinary, comment='Compressed serialized php object with counters'),
    Index('source', 'source', 'last_update')
)


class LogIdSeq(Base):
    __tablename__ = 'log_id_seq'

    sequence = Column(INTEGER(11), primary_key=True)


t_log_table = Table(
    'log_table', metadata,
    Column('id', INTEGER(11), index=True),
    Column('logtime', DateTime),
    Column('ident', Text),
    Column('priority', Text),
    Column('message', LONGTEXT)
)


class Metric(Base):
    __tablename__ = 'metric'
    __table_args__ = {'comment': 'Individual metric definitions'}

    metric_id = Column(INTEGER(10), primary_key=True)
    short_name = Column(String(32), nullable=False)
    name = Column(String(128), nullable=False)
    unit = Column(String(32))
    guid = Column(String(64), nullable=False, unique=True)


class MetricAttribute(Base):
    __tablename__ = 'metric_attribute'

    metric_id = Column(INTEGER(10), primary_key=True)
    larger = Column(TINYINT(1), nullable=False)


class Parameter(Base):
    __tablename__ = 'parameter'
    __table_args__ = {'comment': 'Individual parameter definitions'}

    parameter_id = Column(INTEGER(10), primary_key=True)
    tag = Column(String(64))
    name = Column(String(128), nullable=False)
    unit = Column(String(64))
    guid = Column(String(64), nullable=False, unique=True)


class Report(Base):
    __tablename__ = 'report'

    user_id = Column(INTEGER(11), primary_key=True)
    send_report_daily = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    send_report_weekly = Column(INTEGER(11), nullable=False, server_default=text("'0'"), comment='Negative-None, otherwise days of the week, i.e. 2 - Monday')
    send_report_monthly = Column(INTEGER(11), nullable=False, server_default=text("'0'"), comment='negative is none, otherwise day of the month')
    settings = Column(Text, nullable=False)


class Resource(Base):
    __tablename__ = 'resource'
    __table_args__ = {'comment': 'Resource definitions'}

    resource_id = Column(INTEGER(10), primary_key=True)
    resource = Column(String(128), nullable=False)
    nickname = Column(String(64), nullable=False)
    description = Column(Text)
    enabled = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    visible = Column(TINYINT(1), nullable=False, index=True, server_default=text("'0'"))
    xdmod_resource_id = Column(INTEGER(11))
    xdmod_cluster_id = Column(INTEGER(11))


class SupremmMetric(Base):
    __tablename__ = 'supremm_metrics'

    id = Column(INTEGER(11), primary_key=True, unique=True)
    name = Column(String(128), nullable=False, unique=True)
    formula = Column(Text, nullable=False)
    label = Column(Text, nullable=False)
    units = Column(Text)
    info = Column(Text, nullable=False)


t_v_ak_metrics = Table(
    'v_ak_metrics', metadata,
    Column('name', String(128)),
    Column('enabled', TINYINT(1), server_default=text("'0'")),
    Column('num_units', INTEGER(10), server_default=text("'1'")),
    Column('ak_id', INTEGER(10), server_default=text("'0'")),
    Column('metric_id', INTEGER(10)),
    Column('guid', String(64))
)


t_v_ak_parameters = Table(
    'v_ak_parameters', metadata,
    Column('name', String(128)),
    Column('enabled', TINYINT(1), server_default=text("'0'")),
    Column('num_units', INTEGER(10), server_default=text("'1'")),
    Column('ak_id', INTEGER(10), server_default=text("'0'")),
    Column('parameter_id', INTEGER(10)),
    Column('guid', String(64))
)


t_v_tree_debug = Table(
    'v_tree_debug', metadata,
    Column('ak_name', String(64)),
    Column('resource', String(128)),
    Column('processor_unit', Enum('node', 'core')),
    Column('num_units', INTEGER(10), server_default=text("'1'")),
    Column('ak_def_id', INTEGER(10), server_default=text("'0'")),
    Column('resource_id', INTEGER(10)),
    Column('collected', BIGINT(17)),
    Column('status', Enum('success', 'failure', 'error', 'queued')),
    Column('instance_id', INTEGER(11))
)


class AppKernel(Base):
    __tablename__ = 'app_kernel'
    __table_args__ = (
        Index('index_unique', 'num_units', 'ak_def_id', unique=True),
        {'comment': 'Application kernel info including num processing units'}
    )

    ak_id = Column(INTEGER(10), primary_key=True, nullable=False)
    num_units = Column(INTEGER(10), primary_key=True, nullable=False, server_default=text("'1'"))
    ak_def_id = Column(ForeignKey('app_kernel_def.ak_def_id', ondelete='CASCADE'), index=True)
    name = Column(String(128), nullable=False)
    type = Column(String(64))
    parser = Column(String(64))

    ak_def = relationship('AppKernelDef')
    parameters = relationship('Parameter', secondary='ak_has_parameter')


class AkHasMetric(Base):
    __tablename__ = 'ak_has_metric'
    __table_args__ = (
        ForeignKeyConstraint(['ak_id', 'num_units'], ['app_kernel.ak_id', 'app_kernel.num_units'], ondelete='CASCADE'),
        Index('fk_reporter_has_metric_reporter', 'ak_id', 'num_units'),
        {'comment': 'Association between app kernels and metrics'}
    )

    ak_id = Column(ForeignKey('app_kernel.ak_id'), primary_key=True, nullable=False)
    metric_id = Column(ForeignKey('metric.metric_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
    num_units = Column(INTEGER(10), primary_key=True, nullable=False)

    ak = relationship('AppKernel', primaryjoin='AkHasMetric.ak_id == AppKernel.ak_id')
    ak1 = relationship('AppKernel', primaryjoin='AkHasMetric.ak_id == AppKernel.ak_id')
    metric = relationship('Metric')


t_ak_has_parameter = Table(
    'ak_has_parameter', metadata,
    Column('ak_id', ForeignKey('app_kernel.ak_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True),
    Column('parameter_id', ForeignKey('parameter.parameter_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True),
    comment='Association between app kernels and parameters'
)


class AkInstance(Base):
    __tablename__ = 'ak_instance'
    __table_args__ = (
        Index('ak_def_id', 'ak_def_id', 'collected', 'resource_id', 'env_version'),
        {'comment': 'Execution instance'}
    )

    ak_id = Column(ForeignKey('app_kernel.ak_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True, comment='\t')
    collected = Column(DateTime, primary_key=True, nullable=False)
    resource_id = Column(ForeignKey('resource.resource_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
    instance_id = Column(INTEGER(11), index=True)
    job_id = Column(String(32), comment='resource mgr job id')
    status = Column(Enum('success', 'failure', 'error', 'queued'))
    ak_def_id = Column(INTEGER(10), nullable=False)
    env_version = Column(String(64))
    controlStatus = Column(Enum('undefined', 'control_region_time_interval', 'in_contol', 'under_performing', 'over_performing', 'failed'), nullable=False, server_default=text("'undefined'"))

    ak = relationship('AppKernel')
    resource = relationship('Resource')


class AkInstanceDebug(AkInstance):
    __tablename__ = 'ak_instance_debug'
    __table_args__ = (
        ForeignKeyConstraint(['ak_id', 'collected', 'resource_id'], ['ak_instance.ak_id', 'ak_instance.collected', 'ak_instance.resource_id']),
        {'comment': 'Debugging information for application kernels.'}
    )

    ak_id = Column(INTEGER(10), primary_key=True, nullable=False)
    collected = Column(DateTime, primary_key=True, nullable=False)
    resource_id = Column(INTEGER(10), primary_key=True, nullable=False)
    instance_id = Column(INTEGER(11), index=True)
    message = Column(LargeBinary)
    stderr = Column(LargeBinary)
    walltime = Column(Float)
    cputime = Column(Float)
    memory = Column(Float)
    ak_error_cause = Column(LargeBinary)
    ak_error_message = Column(LargeBinary)
    ak_queue_time = Column(INTEGER(11))


class MetricDatum(Base):
    __tablename__ = 'metric_data'
    __table_args__ = (
        ForeignKeyConstraint(['ak_id', 'collected', 'resource_id'], ['ak_instance.ak_id', 'ak_instance.collected', 'ak_instance.resource_id'], ondelete='CASCADE'),
        Index('fk_metric_data_reporter_instance', 'ak_id', 'collected', 'resource_id'),
        {'comment': 'Collected application kernel data fact table'}
    )

    metric_id = Column(ForeignKey('metric.metric_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
    ak_id = Column(INTEGER(10), primary_key=True, nullable=False)
    collected = Column(DateTime, primary_key=True, nullable=False, comment='\t')
    resource_id = Column(INTEGER(10), primary_key=True, nullable=False)
    value_string = Column(String(255))
    running_average = Column(Float(asdecimal=True))
    control = Column(Float(asdecimal=True))
    controlStart = Column(Float(asdecimal=True))
    controlEnd = Column(Float(asdecimal=True))
    controlMin = Column(Float(asdecimal=True))
    controlMax = Column(Float(asdecimal=True))
    controlStatus = Column(Enum('undefined', 'control_region_time_interval', 'in_contol', 'under_performing', 'over_performing', 'failed'), nullable=False, server_default=text("'undefined'"))

    ak = relationship('AkInstance')
    metric = relationship('Metric')


class ParameterDatum(Base):
    __tablename__ = 'parameter_data'
    __table_args__ = (
        ForeignKeyConstraint(['ak_id', 'collected', 'resource_id'], ['ak_instance.ak_id', 'ak_instance.collected', 'ak_instance.resource_id'], ondelete='CASCADE'),
        Index('fk_parameter_data_reporter_instance', 'ak_id', 'collected', 'resource_id'),
        {'comment': 'Collected application kernel parameters fact table'}
    )

    ak_id = Column(INTEGER(10), primary_key=True, nullable=False)
    collected = Column(DateTime, primary_key=True, nullable=False)
    resource_id = Column(INTEGER(10), primary_key=True, nullable=False)
    parameter_id = Column(ForeignKey('parameter.parameter_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
    value_string = Column(LONGBLOB)
    value_md5 = Column(String(32), nullable=False, index=True)

    ak = relationship('AkInstance')
    parameter = relationship('Parameter')
