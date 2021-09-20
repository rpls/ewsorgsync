#!/usr/bin/env python3
from __future__ import print_function

import sys

from setuptools import find_packages, setup

if sys.version_info[0] < 3 or sys.version_info[1] < 6:
    print('This package requires at least Python 3.6!', file=sys.stderr)
    sys.exit(-1)

setup(name='ewsorgsync',
      version="0.2",
      description='EWS Calendar to org-mode syncronization tool',
      packages=find_packages(),
      install_requires=['exchangelib >= 4.5', 'keyring >= 13.2'],
      python_requires='>=3.6',
      author='Richard Petri',
      author_email='git@rpls.de',
      url='https://github.com/rpls/ewsorgsync',
      entry_points={
          'console_scripts': 'ewsorgsync = ewsorgsync.__main__:main'
      }
      )
