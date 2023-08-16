
import ast
from dataclasses import dataclass
import pathlib
from typing import Union
import yaml
import re

from ..event2 import Event
from ..exception import ConfigurationError

from .distribution import get_distribution_cls

def read_configpy_file(file_path):
    config_dict = {}
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read(), filename=file_path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        key = target.id.lower()
                        value = ast.literal_eval(node.value)
                        config_dict[key] = value
    return config_dict

def load_config_file(file):
    file = pathlib.Path(file).expanduser().resolve().absolute()

    with open(str(file, 'r')) as yfile:
        data = yaml.safe_load(yfile)
    
        