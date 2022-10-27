import sqlalchemy
from sqlalchemy import MetaData, Table, Column, String, Integer
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy import Column, Integer, String, Index, ForeignKey,Text
from sqlalchemy.orm import registry
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from sqlalchemy.dialects.mysql import DOUBLE

from xml.etree import ElementTree

from akrr.util import log
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)
log.set_verbose()


import akrr
import akrr.akrrerror
from akrr.cfg import find_resource_by_name
# from models_mod_akrr_v2 import Resource as ResourceModAKRROld
from models_mod_appkernel_v2 import Resource as ResourceAppkernelV2
from models_modw_v2 import Resourcespec

# set db access
engine_root = None
SessionRoot = None
engine_akrr = None
SessionAKRR = None
engine_appkernel = None
SessionAppKernel = None
engine_appkernel_v2 = None
SessionAppKernelV2 = None
engine_xdmod = None
SessionXDMoD = None


def set_db_access():
    global engine_root
    global SessionRoot
    global engine_akrr
    global SessionAKRR
    global engine_appkernel
    global SessionAppKernel
    global engine_appkernel_v2
    global SessionAppKernelV2
    global engine_xdmod
    global SessionXDMoD
    # just for testing purposes to drop db
    engine_root = create_engine(
        'mysql+mysqldb://akrruser:akrruser@127.0.0.1:3371/mysql?charset=utf8mb4', pool_recycle=3600, future=True)
    SessionRoot = sessionmaker(bind=engine_root, future=True)

    engine_appkernel = create_engine(
        'mysql+mysqldb://akrruser:akrruser@127.0.0.1:3371/mod_appkernel_new?charset=utf8mb4', pool_recycle=3600,
        future=True)
    SessionAppKernel = sessionmaker(bind=engine_appkernel, future=True)

    engine_akrr = create_engine(
        'mysql+mysqldb://akrruser:akrruser@127.0.0.1:3371/mod_akrr?charset=utf8mb4', pool_recycle=3600, future=True)
    SessionAKRR = sessionmaker(bind=engine_akrr, future=True, expire_on_commit=False)

    engine_appkernel_v2 = create_engine(
        'mysql+mysqldb://akrruser:akrruser@127.0.0.1:3371/mod_appkernel?charset=utf8mb4', pool_recycle=3600,
        future=True)
    SessionAppKernelV2 = sessionmaker(bind=engine_appkernel, future=True, expire_on_commit=False)

    engine_xdmod = create_engine(
        'mysql+mysqldb://akrruser:akrruser@127.0.0.1:3371/modw?charset=utf8mb4', pool_recycle=3600, future=True)
    SessionXDMoD = sessionmaker(bind=engine_xdmod, future=True, expire_on_commit=False)

if engine_akrr is None:
    set_db_access()


def reset_new_db():
    with SessionRoot() as session:
        session.execute(text("drop database if exists mod_appkernel_new"))
        session.execute(text("create database if not exists mod_appkernel_new"))
        session.commit()


def get_ppn(resource_name, ppn_lookup={}, return_all_ppn=False):
    """
    Get PPN from various sources
    """
    ppn = {
        'lookup':None, # from look up dict the most reliable provided by user
        'akrr_cfg':None,  # stright from akrr etc config. Most reliable
        'modw_by_xdmod_resource_id':None,  # from modw.resourcespec by matching xdmod_resource_id, somewhat reliable
        'modw_by_name':None,  # from modw.resourcespec by matching name
        'modw_by_partial_name':None,  # from modw.resourcespec by partial matching name
    }
    resource = None
    # get from akrr
    try:
        resource = find_resource_by_name(resource_name)
        log.debug(f"{resource_name} found in AKRR config directory.")
        ppn['akrr_cfg'] = resource['ppn']
    except akrr.akrrerror.AkrrError:
        log.debug(f"{resource_name} is not in AKRR config directory!")

    # get_xdmod_resource_id
    xdmod_resource_id = None
    with SessionAppKernelV2() as session:
        try:
            resource = session.query(ResourceAppkernelV2).filter_by(resource=resource_name).one()
            xdmod_resource_id = resource.xdmod_resource_id
        except sqlalchemy.orm.exc.NoResultFound:
            log.debug2(f"{resource_name} is not in mod_appkernel.resource table!")
        except sqlalchemy.orm.exc.MultipleResultsFound:
            log.error(f"{resource_name} has multiple matches in mod_appkernel.resource table!")
    if xdmod_resource_id is not None:
        with SessionXDMoD() as session:
            try:
                resource = session.query(Resourcespec).filter_by(resource_id=xdmod_resource_id).one()
                ppn['modw_by_xdmod_resource_id'] = resource.q_ppn
            except sqlalchemy.orm.exc.NoResultFound:
                log.debug2(f"Resource with resource_id {xdmod_resource_id} is not in modw.resourcespecs table!")
            except sqlalchemy.orm.exc.MultipleResultsFound:
                log.error(f"Resource with resource_id {xdmod_resource_id} has multiple matches in modw.resourcespecs table!")
    # by name
    with SessionXDMoD() as session:
        try:
            resource = session.query(Resourcespec).filter_by(name=resource_name).one()
            ppn['modw_by_name'] = resource.q_ppn
        except sqlalchemy.orm.exc.NoResultFound:
            log.debug2(f"Resource with name {resource_name} is not in modw.resourcespecs table!")
        except sqlalchemy.orm.exc.MultipleResultsFound:
            log.error(f"Resource with name {resource_name} has multiple matches in modw.resourcespecs table!")
    # by parial name
    with SessionXDMoD() as session:
        try:
            resource = session.query(Resourcespec).filter(Resourcespec.name.like(f"{resource_name}.%")).one()
            ppn['modw_by_partial_name'] = resource.q_ppn
        except sqlalchemy.orm.exc.NoResultFound:
            log.debug2(f"Resource with name {resource_name}.% is not in modw.resourcespecs table!")
        except sqlalchemy.orm.exc.MultipleResultsFound:
            log.debug2(f"Resource with name {resource_name}.% has multiple matches in modw.resourcespecs table!")
    # from lookup
    if resource_name in ppn_lookup:
        ppn['lookup'] = ppn_lookup[resource_name]
    the_ppn = None
    ppn_sel_method = None
    for k,v in ppn.items():
        if v is not None:
            the_ppn = v
            ppn_sel_method=k
            break
    for k,v in ppn.items():
        if v is not None and v !=the_ppn:
            log.warning(f"PPN for resource {resource_name} does not match {v}({k}) != {the_ppn}({ppn_sel_method})")
    if return_all_ppn:
        return ppn
    else:
        return the_ppn
