import sqlalchemy
from sqlalchemy import MetaData, Table, Column, String, Integer
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy import Column, Integer, String, Index, ForeignKey,Text, Boolean
from sqlalchemy.orm import registry
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from sqlalchemy.dialects.mysql import DOUBLE
from hashlib import md5
def guid_calc(s):
    return md5(s.encode()).hexdigest()

import enum
from sqlalchemy import Enum
mapper_registry = registry()

@mapper_registry.mapped
class Resource:
    __tablename__ = "resource"
    __table_args__ = {'comment': 'Resource definitions'}

    resource_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False, index=True, unique=True)
    short_name = Column(String(32), nullable=False, index=True, unique=True)
    description = Column(Text, nullable=False, default="")
    enabled = Column(Boolean, nullable=False, default=True)  # should it be here?
    visible = Column(Boolean, nullable=False, default=True)  # should it be here?
    xdmod_resource_id = Column(Integer, default=None, nullable=True)
    xdmod_cluster_id = Column(Integer, default=None, nullable=True)

    def __repr__(self):
        return "<Resource(%r, %r, %r, %r, %r))>" % (self.resource_id, self.name, self.short_name, self.enabled, self.visible)


@mapper_registry.mapped
class App:
    __tablename__ = 'app'
    __table_args__ = {'comment': 'Application definition.'}

    app_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False, unique=True, comment='short name used in AKRR, typically lowercase')
    full_name = Column(String(128), nullable=False, unique=True, comment='full name for display')
    description = Column(Text, nullable=False, default="")
    enabled = Column(Boolean, nullable=False, default=True)  # should it be here?
    visible = Column(Boolean, nullable=False, index=True, default=True)  # should it be here?
    #processor_unit = Column(Enum('node', 'core'))
    #control_criteria = Column(Float(asdecimal=True))
    app_kernels = relationship("AppKernel", back_populates="app")


@mapper_registry.mapped
class AppKernel:
    __tablename__ = 'app_kernel'
    __table_args__ = (
        sqlalchemy.UniqueConstraint('app_id', 'input', name='_app_input_uc'),
        {'comment': 'Application and input parameter definition.'}
    )

    app_kernel_id = Column(Integer, primary_key=True, autoincrement=True)
    app_id = Column(ForeignKey(f"{App.__tablename__}.app_id", ondelete="CASCADE"), nullable=False)
    input = Column(String(128), nullable=False, default="default", comment='input for application')
    description = Column(Text, nullable=False, default="")

    app = relationship("App", back_populates="app_kernels")


@mapper_registry.mapped
class ComputeResourceType:
    __tablename__ = 'compute_resource_type'
    __table_args__ = {'comment': 'Compute resource type, for example core,node,GPU.'}

    compute_resource_type_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False, unique=True)

    compute_resource_specs = relationship("ComputeResourceSpec", back_populates="compute_resource_type")

    def __repr__(self):
        return "<ComputeResourceType(%r, %r)>" % (self.compute_resource_type_id, self.name)


@mapper_registry.mapped
class ComputeResourceSpec:
    __tablename__ = 'compute_resource_spec'
    __table_args__ = (
        sqlalchemy.UniqueConstraint('compute_resource_type_id', 'proc_units', name='_compute_resource__proc_units_uc'),
        {'comment': 'Compute resource specification.'}
    )

    compute_resource_spec_id = Column(Integer, primary_key=True, autoincrement=True)
    compute_resource_type_id = Column(ForeignKey(f"{ComputeResourceType.__tablename__}.compute_resource_type_id", ondelete="CASCADE"), nullable=False)
    proc_units = Column(Integer, nullable=False, comment="number of processing units")

    compute_resource_type = relationship("ComputeResourceType", back_populates="compute_resource_specs")
#    total_compute_resources = relationship("TotalComputeResourceSpec", back_populates="compute_resource_spec")

    def __repr__(self):
        return "<ComputeResourceSpec(%r, %r, %r)>" % (self.compute_resource_spec_id, self.compute_resource_type.name, self.proc_units)


@mapper_registry.mapped
class TotalComputeResourceSpec:
    __tablename__ = 'total_compute_resource_spec'
    __table_args__ = (
        {'comment': 'Total compute resource specification. For example 4 nodes, 128 cores,8 GPUS'}
    )

    total_compute_resource_spec_id = Column(Integer, primary_key=True)
    description = Column(String(128), nullable=False, default="", comment='should be auto-set')

    total_compute_resource_spec_list = relationship("TotalComputeResourceSpecList")

    def __repr__(self):
        s = "<TotalComputeResourceSpec(%r, %r, %r)>" % (
            self.total_compute_resource_spec_id, self.description,
            ",".join((f"{v.compute_resource_spec.proc_units} {v.compute_resource_spec.compute_resource_type.name}s" for v in self.total_compute_resource_spec_list)))
        return s


@mapper_registry.mapped
class TotalComputeResourceSpecList:
    __tablename__ = 'total_compute_resource_spec_list'
    __table_args__ = (
        sqlalchemy.UniqueConstraint('total_compute_resource_spec_id', 'compute_resource_spec_id', name='_total_compute_resource_uc'),
        {'comment': 'Total compute resource specification. For example 4 nodes, 128 cores,8 GPUS'}
    )

    total_compute_resource_spec_id = Column(ForeignKey(f"{TotalComputeResourceSpec.__tablename__}.total_compute_resource_spec_id"), primary_key=True)
    compute_resource_spec_id = Column(ForeignKey(f"{ComputeResourceSpec.__tablename__}.compute_resource_spec_id"), primary_key=True)

    total_compute_resource_spec = relationship("TotalComputeResourceSpec")
    compute_resource_spec = relationship("ComputeResourceSpec")

    def __repr__(self):
        return "<TotalComputeResourceSpecList(%r, %r, %r)>" % (self.total_compute_resource_spec_id, self.compute_resource_spec.compute_resource_type.name, self.compute_resource_spec.proc_units)

class DataType(enum.Enum):
    float = 1
    string = 2


@mapper_registry.mapped
class Metric:
    __tablename__ = "xd_metric"
    # COMMENT='Individual metric definitions'

    metric_id = Column(Integer, primary_key=True, autoincrement=True)
    short_name = Column(String(32), default=None)
    name = Column(String(128), nullable=False, index=True, unique=True)
    unit = Column(String(32), default=None)
    guid = Column(String(64), nullable=False, index=True, unique=True)
    type = Column(sqlalchemy.Enum(DataType), default=DataType.string)

    def __repr__(self):
        return "<Metric(%r, %r, %r, %r)>" % (self.metric_id, self.name, self.unit, self.guid)


class ControlStatus(enum.Enum):
    undefined = 1
    control_calculation_region = 2
    in_control = 3
    under_performing = 4
    over_performing = 5
    failed = 6


@mapper_registry.mapped
class MetricNumData:
    __tablename__ = "xd_metric_num_data"
    # COMMENT='Collected application kernel data fact table'
    metric_num_data_id = Column(Integer, primary_key=True, autoincrement=True)

    ak_id = Column(Integer, nullable=False)
    resource_id = Column(ForeignKey(f"{Resource.__tablename__}.resource_id", ondelete="CASCADE"), nullable=False)
    task_id = Column(Integer, nullable=False, index=True, unique=False)
    metric_id = Column(ForeignKey(f"{Metric.__tablename__}.metric_id", ondelete="CASCADE"), nullable=False)
    collected = Column(sqlalchemy.DateTime, nullable=False, index=True, unique=False)

    value = Column(DOUBLE, nullable=False)
    running_average = Column(DOUBLE, default=None)
    control = Column(DOUBLE, default=None)
    control_region_id = Column(Integer, default=None)
    control_status = Column(sqlalchemy.Enum(ControlStatus), nullable=False, default=ControlStatus.undefined)

    metric = relationship("Metric")
    resource = relationship("Resource")


    __table_args__ = (
        sqlalchemy.UniqueConstraint(
            'resource_id', 'ak_id', 'metric_id','task_id', name='_resource_ak_metric_task_uc'),
        sqlalchemy.Index("_resource_ak_metric_task_index",
                         'resource_id', 'ak_id', 'task_id', 'metric_id'),
        sqlalchemy.Index("_resource_ak_metric_collected_index",
                         'resource_id', 'ak_id', 'metric_id', 'collected'),
                     )

    def __repr__(self):
        return "<MetricFloatData(%r, %r, %r, %r, %r)>" % (
            self.metric.name, self.ak_id, self.resource_id, self.collected, self.value)
