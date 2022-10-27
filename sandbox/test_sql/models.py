import sqlalchemy
from sqlalchemy import MetaData, Table, Column, String, Integer
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy import Column, Integer, String, Index, ForeignKey,Text, Boolean, JSON
from sqlalchemy.orm import registry
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from sqlalchemy.dialects.mysql import DOUBLE
from hashlib import md5
import json


def guid_calc(s):
    return md5(s.encode()).hexdigest()

import enum
from sqlalchemy import Enum
mapper_registry = registry()

@mapper_registry.mapped
class Resource:
    __tablename__ = "xd_resource"
    __table_args__ = {'comment': 'Resource definitions'}

    resource_id = Column(Integer, primary_key=True, autoincrement=True)
    resource_name = Column(String(64), nullable=False, unique=True, comment='short name used in AKRR, typically lowercase')
    resource_full_name = Column(String(128), nullable=False, unique=True, comment='full name for display')
    resource_description = Column(Text, nullable=False, default="")
    xdmod_resource_id = Column(Integer, default=None, nullable=True)
    xdmod_cluster_id = Column(Integer, default=None, nullable=True)

    # enabled = Column(Boolean, nullable=False, default=True)  # should it be here?
    # visible = Column(Boolean, nullable=False, default=True)  # should it be here?

    def __repr__(self):
        return "<Resource(%r, %r, %r, %r, %r))>" % (self.resource_id, self.name, self.short_name, self.enabled, self.visible)


@mapper_registry.mapped
class ResourceRequests:
    __tablename__ = 'xd_resource_request'
    __table_args__ = (
        {'comment': 'Compute resource request. For example 4 nodes, 128 cores,8 GPUS'}
    )

    resource_request_id = Column(Integer, primary_key=True)
    request = Column(JSON, nullable=False,
                     comment="JSON with specific request, number of nodes, cores, gpus and so on")
    guid = Column(String(64), nullable=False, unique=True, index=True, comment="JSON hash for uniqness constrain")
    nodes = Column(Integer, nullable=False)
    cores = Column(Integer, nullable=False)
    accelerators = Column(Integer, nullable=False, comment="Number of accelerators, like GPUs, TSUs, ASICs, FPGAs and so on")

    def __init__(self, request):
        self.request = request
        self.hash_request = guid_calc(json.dumps(request, sort_keys=True).encode("utf-8"))
        if 'nodes' in request:
            self.nodes = request['nodes']
        if 'cores' in request:
            self.cores = request['cores']
        if 'accelerators' in request:
            self.accelerators = request['accelerators']
        else:
            self.accelerators = 0

    def __repr__(self):
        s = "<Resource_Requests(%r, %r, %r)>" % (
            self.total_compute_resource_spec_id, self.description,
            ",".join((f"{v.compute_resource_spec.proc_units} {v.compute_resource_spec.compute_resource_type.name}s" for v in self.total_compute_resource_spec_list)))
        return s


@mapper_registry.mapped
class App:
    __tablename__ = 'xd_app'
    __table_args__ = {'comment': 'Application definition.'}

    app_id = Column(Integer, primary_key=True, autoincrement=True)
    app_name = Column(String(128), nullable=False, unique=True, comment='short name used in AKRR, typically lowercase')
    app_full_name = Column(String(128), nullable=False, unique=True, comment='full name for display')
    app_description = Column(Text, nullable=False, default="")

    app_input = relationship("AppInput", back_populates="app")
    # enabled = Column(Boolean, nullable=False, default=True)  # should it be here?
    # visible = Column(Boolean, nullable=False, index=True, default=True)  # should it be here?
    # processor_unit = Column(Enum('node', 'core'))
    # control_criteria = Column(Float(asdecimal=True))


@mapper_registry.mapped
class AppInput:
    __tablename__ = 'xd_app_input'
    __table_args__ = (
        sqlalchemy.UniqueConstraint('app_id', 'input_name', name='_app_input_uc'),
        {'comment': 'Application and input parameter definition.'}
    )

    app_input_id = Column(Integer, primary_key=True, autoincrement=True)
    app_id = Column(ForeignKey(f"{App.__tablename__}.app_id", ondelete="CASCADE"), nullable=False)
    input_name = Column(String(128), nullable=False, default="default", comment='input for application')
    app_input_description = Column(Text, nullable=False, default="")

    app = relationship("App", back_populates="app_input")


class DataType(enum.Enum):
    float = 1
    string = 2


@mapper_registry.mapped
class Metric:
    __tablename__ = "xd_metric"
    __table_args__ = (
        {'comment': 'Individual metric definitions'}
    )

    metric_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False, index=True, unique=True)
    unit = Column(String(32), nullable=True, default=None)
    guid = Column(String(64), nullable=False, index=True, unique=True)
    type = Column(sqlalchemy.Enum(DataType), default=DataType.string)
    better = Column(Integer, default=0,
                    comment="Direction of better performance " +
                            "+1 bigger better, -1 smaller better, 0 not a quantitative metric")

    def __repr__(self):
        return "<Metric(%r, %r, %r, %r, %r)>" % (self.metric_id, self.name, self.unit, self.guid, self.better)


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
    __table_args__ = (
        sqlalchemy.UniqueConstraint(
            'resource_id', 'app_input_id', 'metric_id', 'task_id', name='_resource_app_input_metric_task_uc'),
        sqlalchemy.Index("_resource_app_input_metric_task_index",
                         'resource_id', 'app_input_id', 'task_id', 'metric_id'),
        sqlalchemy.Index("_resource_app_input_metric_collected_index",
                         'resource_id', 'app_input_id', 'metric_id', 'collected'),
        {'comment': 'Collected application kernel data fact table'}
    )
    # COMMENT='Collected application kernel data fact table'
    metric_num_data_id = Column(Integer, primary_key=True, autoincrement=True)
    resource_id = Column(ForeignKey(f"{Resource.__tablename__}.resource_id", ondelete="CASCADE"), nullable=False)
    # app_id = Column(ForeignKey(f"{App.__tablename__}.app_id", ondelete="CASCADE"), nullable=False)
    app_input_id = Column(ForeignKey(f"{AppInput.__tablename__}.app_input_id", ondelete="CASCADE"), nullable=False)
    metric_id = Column(ForeignKey(f"{Metric.__tablename__}.metric_id", ondelete="CASCADE"), nullable=False)

    task_id = Column(Integer, nullable=False, index=True, unique=False)
    collected = Column(sqlalchemy.DateTime, nullable=False, index=True, unique=False)

    value = Column(DOUBLE, nullable=False)
    running_average = Column(DOUBLE, default=None)
    control = Column(DOUBLE, default=None)
    control_region_id = Column(Integer, default=None)
    control_status = Column(sqlalchemy.Enum(ControlStatus), nullable=False, default=ControlStatus.undefined)

    metric = relationship("Metric")
    resource = relationship("Resource")
    app_input = relationship("AppInput")
    def __repr__(self):
        return "<MetricFloatData(%r, %r, %r, %r, %r)>" % (
            self.metric.name, self.app_input_id, self.resource_id, self.collected, self.value)
