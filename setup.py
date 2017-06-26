#!/usr/bin/env python
""" setup script for Application Kernels Remote Runner (AKRR) """
from setuptools import setup
import sys
import os

# For rpm-based builds want the configuration files to
# go in the standard location. Also need to rewrite the file list so that
# the config filesa are listed as %config(noreplace)
IS_RPM_BUILD = False
if 'bdist_rpm' in sys.argv or 'RPM_BUILD_ROOT' in os.environ:
    IS_RPM_BUILD = True
    confpath = '/etc/akrr'
#     with open('.rpm_install_script.txt', 'w') as fp:
#         fp.write('%s %s install -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES\n' % (sys.executable, os.path.basename(sys.argv[0])))
#         fp.write('sed -i \'s#^\\(%s\\)#%%config(noreplace) \\1#\' INSTALLED_FILES\n' % (confpath, ))
else:
    confpath = 'etc/akrr'


setup(name='akrr',
    version='1.0.1',
    description='Application Kernels Remote Runner',
    long_description='Periodical execution of application kernels (applications with input parameters) on HPC resources for performance monitoring',
    license='LGPLv3',
    author='Nikolay A Simakov',
    author_email='nikolays@buffalo.edu',
    url='https://github.com/ubccr/akrr',
    scripts=['bin/akrrd'],
    packages = ['akrr'],
    package_dir={'akrr': 'src/akrr'},
    requires=['MySQLdb'],
)
#    packages=['akrr'],
#       data_files=[(confpath,                         ['config/config.json']),
#                   ('share/supremm/templates/slurm',       ['config/templates/slurm/slurm-epilog',  'config/templates/slurm/slurm-prolog']),
#                   ('share/supremm/templates/pmlogger',    ['config/templates/pmlogger/control',    'config/templates/pmlogger/pmlogger-supremm.config']),
#                   ('share/supremm/templates/pmie',        ['config/templates/pmie/control',        'config/templates/pmie/pmie-supremm.config',
#                                                            'config/templates/pmie/pcp-restart.sh', 'config/templates/pmie/procpmda_check.sh']),
#                   ('share/supremm/templates/pmda-logger', ['config/templates/pmda-logger/logger.conf']),
#                   ('share/supremm/setup/', ['assets/modw_supremm.sql', 'assets/mongo_setup.js'])
#       ],
#     scripts=[
#         "src/__init__.py",
#         "src/akrr.py",
#         "src/akrrappkeroutputparser.py",
#         "src/akrrctl.py",
#         "src/akrrlogging.py",
#         "src/akrrrestapi.py",
#         "src/akrrrestclient.py",
#         "src/akrrscheduler.py",
#         "src/akrrtask.py",
#         "src/akrrtaskappker.py",
#         "src/akrrtaskbase.py",
#         "src/akrrtaskbundle.py",
#         "src/akrrversion.py",
#         "src/rest_cli.py",
#         
#         "src/models/__init__.py",
#         "src/models/task.py",
#         
#         "src/util/__init__.py",
#         "src/util/colorize.py",
#         "src/util/functional.py",
#         "src/util/generators.py",
#         "src/util/logging.py",
# 
#         
#         "src/appkernelsparsers/mpipi_parser.py",
#         "src/appkernelsparsers/test_parser.py",
#         "src/appkernelsparsers/xdmod.app.astro.enzo.py",
#         "src/appkernelsparsers/xdmod.app.chem.gamess.py",
#         "src/appkernelsparsers/xdmod.app.chem.nwchem.py",
#         "src/appkernelsparsers/xdmod.app.climate.wrf.py",
#         "src/appkernelsparsers/xdmod.app.md.amber.py",
#         "src/appkernelsparsers/xdmod.app.md.charmm.py",
#         "src/appkernelsparsers/xdmod.app.md.lammps.py",
#         "src/appkernelsparsers/xdmod.app.md.namd.py",
#         "src/appkernelsparsers/xdmod.app.phys.quantum_espresso.py",
#         "src/appkernelsparsers/xdmod.benchmark.graph.graph500.py",
#         "src/appkernelsparsers/xdmod.benchmark.hpcc.py",
#         "src/appkernelsparsers/xdmod.benchmark.io.ior.py",
#         "src/appkernelsparsers/xdmod.benchmark.io.mdtest.py",
#         "src/appkernelsparsers/xdmod.benchmark.io.mpi-tile-io.py",
#         "src/appkernelsparsers/xdmod.benchmark.mpi.imb.py",
#         "src/appkernelsparsers/xdmod.bundle.py",
#         "src/appkernelsparsers/xdmod.generic.py",
#         
#         "src/default.app.inp.py",
#         "src/default.resource.inp.py",
#         
#         "src/appkernels/mpipi.app.inp.py",
#         "src/appkernels/test.app.inp.py",
#         "src/appkernels/xdmod.app.astro.enzo.app.inp.py",
#         "src/appkernels/xdmod.app.chem.gamess.app.inp.py",
#         "src/appkernels/xdmod.app.chem.nwchem.app.inp.py",
#         "src/appkernels/xdmod.app.md.namd.app.inp.py",
#         "src/appkernels/xdmod.benchmark.graph.graph500.app.inp.py",
#         "src/appkernels/xdmod.benchmark.hpcc.app.inp.py",
#         "src/appkernels/xdmod.benchmark.io.ior.app.inp.py",
#         "src/appkernels/xdmod.benchmark.io.mdtest.app.inp.py",
#         "src/appkernels/xdmod.benchmark.mpi.imb.app.inp.py",
#         "src/appkernels/xdmod.bundle.app.inp.py",
#         
# 
#         "src/templates/resource.app.inp.py",
#         "src/templates/template.app.inp.py",
#         "src/templates/template.pbs.inp.py",
#         "src/templates/template.slurm.inp.py",
#         "src/templates/xdmod.app.astro.enzo.app.inp.py",
#         "src/templates/xdmod.app.chem.gamess.app.inp.py",
#         "src/templates/xdmod.app.chem.nwchem.app.inp.py",
#         "src/templates/xdmod.app.md.namd.app.inp.py",
#         "src/templates/xdmod.benchmark.graph.graph500.app.inp.py",
#         "src/templates/xdmod.benchmark.hpcc.app.inp.py",
#         "src/templates/xdmod.benchmark.io.ior.app.inp.py",
#         "src/templates/xdmod.benchmark.mpi.imb.app.inp.py",
# 
#     ],


# if IS_RPM_BUILD:
#     os.unlink('.rpm_install_script.txt')