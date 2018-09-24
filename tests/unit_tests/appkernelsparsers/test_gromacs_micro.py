import os
import pytest


def test_parser(datadir):
    from akrr.appkernelsparsers.app_md_gromacs_micro import processAppKerOutput
    r = processAppKerOutput(
        appstdout=str(datadir.join('appstdout')),
        stdout=str(datadir.join('stdout')),
        stderr=str(datadir.join('stderr')),
        geninfo=str(datadir.join('geninfo')),
    )
    print(r)
