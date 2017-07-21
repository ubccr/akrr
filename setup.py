#!/usr/bin/env python
""" setup script for Application Kernels Remote Runner (AKRR) """
from setuptools import setup,find_packages
import sys
import os


setup(name='akrr',
    version='1.0.1',
    description='Application Kernels Remote Runner',
    long_description='Periodical execution of application kernels (applications with input parameters) on HPC resources for performance monitoring',
    classifiers=[
        'Environment :: Console',
        'Operating System :: POSIX',
        'Programming Language :: Python'
    ],
    license='LGPLv3',
    author='Nikolay A Simakov',
    author_email='nikolays@buffalo.edu',
    url='https://github.com/ubccr/akrrcfg',
    scripts=['bin/akrr'],
    packages = ['akrr','akrr/util','akrr/models','akrr/appkernelsparsers','akrr/akrrpexpect'],
    requires=['MySQLdb','requests','bottle'],
    package_data={'akrr':['templates/*.conf','default_conf/*.conf','appker_repo/inputs.tar.gz','appker_repo/execs.tar.gz']}
)
