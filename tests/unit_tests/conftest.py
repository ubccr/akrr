from __future__ import unicode_literals
from distutils import dir_util
from pytest import fixture
import os


@fixture
def datadir(tmpdir, request):
    """
    Fixture responsible for searching a folder with the same name of test
    module and, if available, moving all contents to a temporary directory so
    tests can use them freely.
    """
    filename = request.module.__file__
    test_dir, _ = os.path.splitext(filename)

    if os.path.isdir(test_dir):
        dir_util.copy_tree(test_dir, str(tmpdir))

    return tmpdir


# test configuration internal storage dictionary
__testconfig = None


@fixture
def testconfig():
    """
    testconfig fixture. It returns test configuration specified in testconfig.conf.py
    """
    global __testconfig
    if __testconfig is None:
        import inspect
        import os
        from akrr.util import exec_files_to_dict
        curdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        testconfig_filename = os.path.join(curdir, "testconfig.conf.py")
        if os.path.exists(testconfig_filename):
            __testconfig = exec_files_to_dict(testconfig_filename)
        else:
            __testconfig = {}
        __testconfig["loads count"] = 0

    __testconfig["loads count"] += 1
    return __testconfig
