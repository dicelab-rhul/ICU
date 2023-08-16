import sys
import os
sys.stdout = open(os.devnull, "w")
import pygame # first time import to prevent welcome message display...
sys.stdout = sys.__stdout__


from . import ui
from . import event2
from . import exception