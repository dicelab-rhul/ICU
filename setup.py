#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  2 21:22:31 2019

@author: ben
"""

import setuptools

setuptools.setup(
    name="icu",
    version="0.0.2",
    description="Integrated Cognitive User Assistance",
    url="https://github.com/dicelab-rhul/ICU",
    author="Benedict Wilkins",
    author_email="benrjw@googlemail.co.uk",
    license="GNU3",
    packages=setuptools.find_packages(),
    package_data={"icu": ["*.json"]},
    include_package_data=True,
    install_requires=[
        "shortuuid",  # for generating consise UUIDs for the event system
        "pygame",  # for ui
        "pywinctl",  # for cross-platform window control
        "screeninfo",  # for getting monitor size/resolution
    ],
    python_requires=">=3.9",
    extras_require={"tobii": ["tobii-research==1.11.0"]},  # requires python 3.6!
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)
