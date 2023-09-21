import sys
import os
sys.stdout = open(os.devnull, "w")
import pygame # first time import to prevent welcome message display...
sys.stdout = sys.__stdout__