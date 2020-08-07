#!/usr/bin/env python3
""" setup script for Application Kernels Remote Runner (AKRR) """
from setuptools import setup

setup(
    name='akrr',
    version='2.1.1',
    description='Application Kernels Remote Runner',
    long_description='Periodical execution of application kernels'
                     '(applications with input parameters) on HPC resources for performance monitoring',
    classifiers=[
        'Environment :: Console',
        'Operating System :: POSIX',
        'Programming Language :: Python'
    ],
    license='LGPLv3',
    author='Nikolay A Simakov @ CCR UB SUNY',
    author_email='nikolays@buffalo.edu',
    url='https://github.com/ubccr/akrr',
    scripts=['bin/akrr'],
    packages=[
        'akrr',
        'akrr/parsers',
        'akrr/akrr_task',
        'akrr/cli',
        'akrr/pexpect',
        'akrr/pexpect/ptyprocess',
        'akrr/util'
    ],
    requires=['MySQLdb', 'requests', 'bottle'],
    package_data={
        'akrr': ['templates/*.conf', 'default_conf/*.conf', 'appker_repo/inputs.tar.gz', 'appker_repo/execs.tar.gz']}
)
