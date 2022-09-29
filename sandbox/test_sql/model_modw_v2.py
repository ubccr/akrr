# coding: utf-8
from sqlalchemy import Column, DateTime, Index, String, text
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Resourcefact(Base):
    __tablename__ = 'resourcefact'
    __table_args__ = (
        Index('uniq', 'organization_id', 'name', 'start_date', unique=True),
        Index('aggregation_index', 'resourcetype_id', 'id'),
        {'comment': 'Information about resources.'}
    )

    id = Column(INTEGER(11), primary_key=True, comment='The id of the resource record')
    resourcetype_id = Column(INTEGER(11), index=True, comment='The resource type id.')
    organization_id = Column(INTEGER(11), nullable=False, index=True, server_default=text("1"), comment='The organization of the resource.')
    name = Column(String(200), nullable=False, server_default=text("''"), comment='The name of the resource.')
    code = Column(String(64), nullable=False, comment='The short name of the resource.')
    description = Column(String(1000), comment='The description of the resource.')
    start_date = Column(DateTime, nullable=False, server_default=text("'0000-00-00 00:00:00'"), comment='The date the resource was put into commission.')
    start_date_ts = Column(INTEGER(14), nullable=False, server_default=text("0"))
    end_date = Column(DateTime, comment='The end date of the resource.')
    end_date_ts = Column(INTEGER(14))
    shared_jobs = Column(INTEGER(1), nullable=False, server_default=text("0"))
    timezone = Column(String(30), nullable=False, server_default=text("'UTC'"))
    resource_origin_id = Column(INTEGER(11), nullable=False, server_default=text("0"))


class Resourcespec(Base):
    __tablename__ = 'resourcespecs'
    __table_args__ = (
        Index('unq', 'name', 'start_date_ts'),
    )

    resource_id = Column(INTEGER(11), primary_key=True, nullable=False)
    start_date_ts = Column(INTEGER(11), primary_key=True, nullable=False)
    end_date_ts = Column(INTEGER(11))
    processors = Column(INTEGER(11))
    q_nodes = Column(INTEGER(11))
    q_ppn = Column(INTEGER(11))
    comments = Column(String(500))
    name = Column(String(200))
