"""
Testing of configuration subsystem
"""


def test_akrr_default_conf():
    """
    Test default akrr configuration
    """
    import os
    import inspect
    import runpy

    cur_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    akrr_mod_dir = os.path.abspath(os.path.join(os.path.dirname(cur_dir), "..", "..", "akrr"))

    print(akrr_mod_dir)



def test_conf_strategy():
    """
    test_conf_strategy

    if this is not working then something need to be done with a way how AKRR validate akrr.conf
    """
    from . import cfg_test

    assert cfg_test.new_var == "New Variable"
    assert cfg_test.fruit == "Pineapple"
    assert cfg_test.color == "red"


    assert 0


def test_resource_conf():
    """
    Test resource configureation
    """

    pass
