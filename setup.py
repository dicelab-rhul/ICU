#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  2 21:22:31 2019

@author: ben
"""

import setuptools

setuptools.setup(name='icu',
      version='0.0.1',
      description='',
      url='https://github.com/dicelab-rhul/ICU',
      author='Benedict Wilkins',
      author_email='benrjw@googlemail.co.uk',
      license='',
      packages=setuptools.find_packages(),
      package_data={'': ['*.json']},
      include_package_data=True,
      classifiers=[
        "Programming Language :: Python :: 3.7",
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
      ])
