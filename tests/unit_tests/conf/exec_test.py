"""
AKRR read configuration files as python scripts,
it executes them withing the AKRR python code.
This module tests that execution of python scripts goes as
intended.

python file loaded to module
"""


import os
import inspect
# import runpy
# from akrr.util import clear_from_build_in_var

cur_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

specific_conf_filename = os.path.join(cur_dir, "exec_test", "sample_conf")

# Exec vs runpy.run_path
#
# exec example:
# with open(default_conf_filename, "r") as file_in:
#     exec(file_in.read())
#
# runpy.run_path example and still not working :
# globals().update(runpy.run_path(default_conf_filename, clear_from_build_in_var(globals())))
#
# so we stick with exec

# load default
# pylint: disable=wildcard-import,unused-wildcard-import,relative-beyond-top-level,wrong-import-position
from .default_conf import *

assert fruit == "apple"
assert color == "red"

# load specific parameters
with open(specific_conf_filename, "r") as file_in:
    exec(file_in.read())  # pylint: disable=exec-used


def test_exec():
    """
    Test results of reading exec_test/default_conf into global space of this module
    """
    global fruit  # pylint: disable=global-variable-not-assigned,global-statement
    global color  # pylint: disable=global-variable-not-assigned,global-statement
    global amount  # pylint: disable=global-variable-not-assigned,global-statement

    assert fruit == "banana"  # pylint: disable=undefined-variable
    assert color == "yellow"  # pylint: disable=undefined-variable
    assert amount == 2  # pylint: disable=undefined-variable
