#! /usr/bin/python3
# -*- coding: utf-8 -*-

import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()
REQUIREMENTS = open(os.path.join(os.path.dirname(__file__), 'requirements.txt')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='ochDownloader',
    version='0.1',
    description='ochDownloader is a Python based download manager and accelerator.',
    author='Esteban Castro Borsani',
    author_email='ecastroborsani@gmail.com',
    long_description=README,
    url='http://ochdownloader.com/',
    packages=[
        'ochDownloader',
    ],
    test_suite="ochDownloader.tests.suite",
    include_package_data=True,
    install_requires=REQUIREMENTS,
    license='MIT License',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Other Environment',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet',
        'Topic :: Desktop Environment',
    ],
)
