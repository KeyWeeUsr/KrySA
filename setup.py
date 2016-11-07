#!/usr/bin/env python

import os
import sys
import os.path as op
from distutils import dir_util
from distutils import sysconfig
from setuptools import setup, find_packages

name = 'krysa'
files = [name, ]

root = op.dirname(op.abspath(__file__)) + op.sep

# remove all *.pyc files here before packaging
if 'sdist' in sys.argv:
    rem_files = []
    for path, folders, filenames in os.walk(root):
        for file in filenames:
            rem_files.append(op.join(path, file))
    for file in rem_files:
        if '.pyc' in file:
            print('Removing {}'.format(file))
            os.remove(file)

# get version from main
with open(op.join(root, 'krysa', 'main.py')) as f:
    for i, line in enumerate(f):
        if i == 2:
            version = line[len('# Version: '):-1]
        elif i > 2:
            break

# check version format
ver_split = version.split('.')
num_check = [int(n) for n in ver_split]
if len(ver_split) != 3:
    raise Exception('No correct version! ( {0} )'.format(version))

setup(
    name=name,
    packages=find_packages(),
    include_package_data=True,
    install_requires=['kivy', 'numpy', 'scipy', 'matplotlib'],
    version=version,
    description='KrySA - Statistical analysis for rats',
    author='Peter Badida',
    author_email='keyweeusr@gmail.com',
    url='https://github.com/KeyWeeUsr/KrySA',
    download_url='https://github.com/KeyWeeUsr/KrySA/tarball/' + version,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: Android',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
    keywords=['krysa', 'statistics', 'kivy'],
    license="GNU General Public License v3 (GPLv3)",
)
