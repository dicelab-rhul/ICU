
import ast
from dataclasses import dataclass
import pathlib
from typing import Union
import yaml
import re

from ast import parse, Expression, Constant, Tuple, List, Set, Call, Name, Dict, BinOp, UnaryOp, UAdd, USub, Add, Sub

from ..event2 import Event
from .exception import ConfigurationError

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

# def load_config_file(file):
#     file = pathlib.Path(file).expanduser().resolve().absolute()
#     with open(str(file), 'r') as yfile:
#         data = yaml.safe_load(yfile)

def literal_eval_with_ops(node_or_string):
    """
    Safely evaluate an expression node or a string containing a Python
    expression. The string or node provided may only consist of the 
    following Python literal structures: strings, bytes, numbers, 
    tuples, lists, dicts, sets, booleans, None, and basic binary operations.
    
    Caution: A complex expression can overflow the C stack and cause a crash.
    """

    def _raise_malformed_node(node):
        msg = "malformed node or string"
        if lno := getattr(node, 'lineno', None):
            msg += f' on line {lno}'
        raise ValueError(msg + f': {node!r}')
        
    def _convert(node):
        if isinstance(node, Constant):
            return node.value
        elif isinstance(node, Tuple):
            return tuple(map(_convert, node.elts))
        elif isinstance(node, List):
            # Handle list with unpacking
            result = []
            for elt in node.elts:
                if isinstance(elt, ast.Starred):  # Unpacking operator
                    result.extend(_convert(elt.value))
                else:
                    result.append(_convert(elt))
            return result
        elif isinstance(node, Set):
            return set(map(_convert, node.elts))
        elif (isinstance(node, Call) and isinstance(node.func, Name) and
              node.func.id == 'set' and node.args == node.keywords == []):
            return set()
        elif isinstance(node, Dict):
            if len(node.keys) != len(node.values):
                _raise_malformed_node(node)
            return dict(zip(map(_convert, node.keys),
                            map(_convert, node.values)))
        elif isinstance(node, BinOp):  # Handle binary operations
            left = _convert(node.left)
            right = _convert(node.right)
            if isinstance(node.op, Add):
                return left + right
            elif isinstance(node.op, Sub):
                return left - right
            elif isinstance(node.op, ast.Mult):
                return left * right
            elif isinstance(node.op, ast.Div):
                return left / right
            else:
                _raise_malformed_node(node)
        else:
            _raise_malformed_node(node)

    try:
        if isinstance(node_or_string, str):
            node_or_string = parse(node_or_string.lstrip(" \t"), mode='eval')
        if isinstance(node_or_string, Expression):
            node_or_string = node_or_string.body
    except SyntaxError:
        _raise_malformed_node(node_or_string)
    
    return _convert(node_or_string)
