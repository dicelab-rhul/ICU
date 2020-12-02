#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Created on 23-11-2020 13:33:07
"""
__author__ = "Benedict Wilkins"
__email__ = "benrjw@gmail.com"
__status__ = "Development"


# Extract config documentation for website from config/__init__.py

import re
import os 
from pprint import pprint

result = []

type_P = "is_type(.*)\)"
group_P = "Option\(\'(.*)\'"

from icu.config.default import default_input, default_overlay, default_config, default_pump, default_scale, default_tracking, default_warning_light, default_target

DEFAULT_KEYS = {"scale": default_scale("<K>"), 
                "warning_light": default_warning_light("<K>", "0/1"),
                "target": default_target(),
                "pump": default_pump(),
                "main": default_config(),
                "overlay":default_overlay(),
                "input":default_input()}



config = default_config()

with open(os.path.abspath("icu/config/__init__.py"), "r") as f:
    for line in f.readlines():
        if "options" in line and "dict" in line:
            line = line.split("=")[0].strip().replace("_", " ").title()
            result.append("")
            result.append(line)
            
        elif "Option" in line and "#" in line:
   
            option, doc = line.split("#")
            # option info
            option, _type = option.split("=")
            option = option.strip()
            _type = _type.strip()
            group = _type.split(",")[0]
            group = re.search(group_P, group).group(1)

            _type = re.search(type_P,_type)
            if _type is not None:
                _type = _type.group(1)
            else:
                _type = ""
     
            doc = doc.strip() 
            if DEFAULT_KEYS.get(group) is not None:
                if DEFAULT_KEYS[group].get(option, None) is not None:
                    default = str(DEFAULT_KEYS[group][option])
                    doc = "{0}. Default: {1}".format(doc, default) # get defaults from config/default.py

            option = "`{0} {1}`".format(option, _type)
            
            result.append("* {0} : {1}.".format(option.strip(), doc))

for l in result:
    print(l)
