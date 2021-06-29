"""
Unit tests for open stack. Currently works on computers with openstack_env_set.sh script which set all environment
variables.

Run at root of akrr git repo:
PYTHONPATH=`pwd` pytest -m "openstack"  ./tests/unit_tests
"""
import pytest


@pytest.mark.openstack
def test_openstack():
    return


@pytest.mark.openstack
def test_openstack_expired_token():
    from akrr.util import log
    from akrr.util.openstack import OpenStack
    log.set_verbose()
    ostack = OpenStack()
    out = ostack.run_cloud_cmd("image list")
    assert out.count("ID") > 0 and out.count("Name") > 0 and out.count("Status") > 0
    ostack.token_revoke()
    out = ostack.run_cloud_cmd("image list")
    assert out.count("ID") > 0 and out.count("Name") > 0 and out.count("Status") > 0
