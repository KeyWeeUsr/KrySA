#!/usr/bin/env python

import os
import os.path as op
from distutils import dir_util
from distutils import sysconfig
from distutils.core import setup

name = 'krysa'
files = [name, ]

# get folders relative to root
root = op.dirname(op.abspath(__file__)) + op.sep
for walk in os.walk(op.join(root, name)):
    for dirname in walk[1]:
        path = op.join(walk[0], dirname).replace(root, '')
        files.append(op.join(path, '.'))

# get version from main
with open(op.join(root, "krysa/main.py")) as f:
    for i, line in enumerate(f):
        if i == 2:
            version = line[len('# Version: '):-1]
        elif i > 2:
            break

# check version format
ver_split = version.split('.')
num_check = [int(n) for n in ver_split]
if len(ver_split) != 3:
    raise Exception('No correct version! ( %s )' % version)

setup(
    name=name,
    packages=files,
    package_data={'': ['*.*', ]},
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
        'Programming Language :: Python :: 2 :: Only',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
    keywords=['krysa', 'statistics', 'kivy'],
    license="GNU General Public License v3 (GPLv3)",
)
