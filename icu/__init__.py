""" 
ICU is part of the Integerated Cognitive User Assistance project, see https://dicelab-rhul.github.io/ICU/. ICU is a clone of 
the MATBII system with some major usability improvements. It offers improved configuration/UI flexibility, 
eyetracking support, and is the basis for an agent-based approach to user assistance in the ICUa system, see https://github.com/dicelab-rhul/ICUa.
"""

import sys
import os
sys.stdout = open(os.devnull, "w")
import pygame # first time import to prevent welcome message display...
sys.stdout = sys.__stdout__