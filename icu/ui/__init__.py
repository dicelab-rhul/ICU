"""
    ui module contains code for creating and manipulating a flexible UI. This module wraps the `pygame` module.
""" 




from .window import *
from .run import start
from . import config




from ..config.utils import read_configpy_file
DEFAULT_WINDOW_CONFIGURATION = read_configpy_file(config.__file__)
