#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""
__author__ = "Benedict Wilkins"
__email__ = "benrjw@gmail.com"
__status__ = "Development"

import json
import os

from pprint import pprint # TODO remove

import copy

from types import SimpleNamespace
from collections import defaultdict

from itertools import cycle, islice, repeat

from .distribution import *
from .validate import validate_schedule
from .exception import ConfigurationError

from .default import default_config

# =================================== # =================================== # =================================== # 
# =================================== # ======== ALL CONFIG OPTIONS ======= # =================================== # 
# =================================== # =================================== # =================================== #

def tasks():
    return SimpleNamespace(**{k:k for k in ['system', 'fuel', 'track']})

def is_type(*types): #validate type(s) 
    def _is_type(**kwargs): #expects a singleton dictionary
        assert len(kwargs) == 1
        k = next(iter(kwargs.keys()))
        v = kwargs[k]
        #print(k,v,types)
        if not isinstance(v, tuple(types)):
            raise ConfigurationError("Invalid value '{0}' for '{1}', must be one of type: {2}.".format(v, k, tuple([t.__name__ for t in types])))
        return v
    return _is_type

def is_coord():
    def _is_coord(**kwargs):
        k = next(iter(kwargs.keys()))
        v = kwargs[k]
        if isinstance(v, list) and len(v) == 2 and isinstance(v[0], (int, float)) and isinstance(v[1], (int,float)):
            return tuple(v)
        else:
            raise ConfigurationError("Invalid value '{0}' for '{1}', must be a list of length 2 and contain only numbers.".format(v, k))
    return _is_coord

def condition(cond):
    def _condition(**kwargs):
        assert len(kwargs) == 1
        k = next(iter(kwargs.keys()))
        v = kwargs[k]
        if not cond(v):
            raise ConfigurationError("Invalid value '{0}' for '{1}'.".format(v, k))
        return v
    return _condition
        
def get_option(k, group, _options=None):
    if _options is None:
        _options = options

    k = k.split(":")[0]
    if k in _options:
        option = _options[k]
        assert isinstance(option, Option)
        if option.group == group:
            return option

    raise ConfigurationError("Invalid config option: \"{0}\" for config group: \"{1}\"".format(k, group))

def validate_options(group, _options=None):
    return (lambda **kwargs : {k:get_option(k, group, _options=_options)(**{k:v}) for k,v in next(iter(kwargs.values())).items()})

class Option:
    
    def __init__(self, group, fun):
        self.group =  group
        self.__fun = fun

    def __call__(self, **kwargs):
        return self.__fun(**kwargs)

# CONFIG OPTIONS ARE ALL DEFINED IN THE DICTIONARY BELOW - EACH SHOULD BE VALIDATED



target_options = dict(
    step               = Option('target', is_type(int, float)),
    invert             = Option('target', is_type(bool))
)

warninglight_options = dict(
    schedule            = Option('warning_light', validate_schedule),
    grace               = Option('warning_light', is_type(int, float)),
    key                 = Option('warning_light', is_type(str)),
    state               = Option('warning_light', is_type(int)),
    on_colour           = Option('warning_light', is_type(str)),
    off_colour          = Option('warning_light', is_type(str)),
    outline_colour      = Option('warning_light', is_type(str)),
    outline_thickness   = Option('warning_light', is_type(int))
)

scale_options = dict(
    schedule            = Option('scale', validate_schedule),
    key                 = Option('scale', is_type(str)),
    size                = Option('scale', is_type(int)),
    position            = Option('scale', is_type(int)),
    background_colour   = Option('scale', is_type(str)),
    outline_colour      = Option('scale', is_type(str)),
    outline_thickness   = Option('scale', is_type(int)),
    slider_colour       = Option('scale', is_type(str))
)

pump_options = dict(
    schedule            = Option('pump', validate_schedule),
    flow_rate           = Option('pump', is_type(int)),
    event_rate          = Option('pump', is_type(int)),
    #cosmetic
    scale               = Option('pump', is_type(float))
)

tank_options = dict(
    burn_rate           = Option('tank', is_type(int, float)),
    accept_position     = Option('tank', is_type(int, float)),
    accept_proportion   = Option('tank', is_type(int, float)),
    capacity            = Option('tank', is_type(int, float)),
    fuel                = Option('tank', is_type(int, float)),
    
    fuel_colour         = Option('tank', is_type(str)), # cosmetic
    background_colour   = Option('tank', is_type(str)), # cosmetic
    outline_colour      = Option('tank', is_type(str)), # cosmetic
    outline_thickness   = Option('tank', is_type(int)), # cosmetic
)

eyetracker_options = dict(
    enabled             = Option('eyetracker', is_type(bool)),
    stub                = Option('eyetracker', is_type(bool)),
    calibrate           = Option('eyetracker', is_type(bool)),
    sample_rate         = Option('eyetracker', is_type(int)),
)

options = dict(

            main            = Option('-', validate_options('main')),

            #TODO validate these arguments?
            Pump            = Option('main', validate_options('pump', _options=pump_options)),
            Target          = Option('main', validate_options('target', _options=target_options)),
            WarningLight    = Option('main', validate_options('warning_light', _options=warninglight_options)),
            Scale           = Option('main', validate_options('scale', _options=scale_options)),
            FuelTank        = Option('main', validate_options('tank', _options=tank_options)),

            screen_width    = Option('main', is_type(int, float)),
            screen_height   = Option('main', is_type(int, float)),
            screen_size     = Option('main', is_coord()),
            screen_x        = Option('main', is_type(int, float)),
            screen_y        = Option('main', is_type(int, float)),
            screen_position        = Option('main', is_coord()),

            screen_full            = Option('main', is_type(bool)),
            screen_resizable       = Option('main', is_type(bool)),
            screen_aspect          = Option('main', is_coord()),
            screen_min_size        = Option('main', is_coord()),
            screen_max_size        = Option('main', is_coord()),
            background_colour       = Option('main', is_type(str)),
            
            #schedule        = Option('main', lambda **kwargs: {k:Validator.is_schedule(**{k:v}) for k,v in next(iter(kwargs.values())).items()}),
            
            task            = Option('main', validate_options('task')),
            system          = Option('task', is_type(bool)),
            track           = Option('task', is_type(bool)),
            fuel            = Option('task', is_type(bool)),

            input           = Option('main',  validate_options('input')),
            mouse           = Option('input', is_type(bool)),
            keyboard        = Option('input', is_type(bool)),
            joystick        = Option('input', is_type(bool)),

            eyetracker      = Option('input', validate_options('eyetracker', _options=eyetracker_options)),

            generators      = Option('main', lambda **kwargs: None), #TODO
            shutdown          = Option('main', is_type(int, float)), # stop the system

            overlay             = Option('main',    validate_options('overlay')),
            enable              = Option('overlay', is_type(bool)),
            arrow               = Option('overlay', is_type(bool)),
            transparent         = Option('overlay', is_type(bool)),
            outline             = Option('overlay', is_type(bool)),
            highlight_thickness = Option('overlay', is_type(int)),
            highlight_colour    = Option('overlay', is_type(str)),
        
    )


import collections.abc

def update(d, u): #recursive dictionary update
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d

class Validator:

    def __call__(self, **kwargs):
        config =  validate_options('main')(**{'main':kwargs}) #{k:get_option(k, 'main')(**{k:v}) for k,v in kwargs.items()}

        # ====== POST PROCESSING ====== # 
        #TOOD move this somewhere more suitable
        result = default_config()

        result = update(result, config)
        pprint(result)

        result['screen_size'] = (result.get('screen_width', result['screen_size'][0]), result.get('screen_height', result['screen_size'][1]))
        result['screen_position'] = (result.get('screen_x', result['screen_position'][0]), result.get('screen_y', result['screen_position'][1]))
        result['screen_width'], result['screen_height'] = result['screen_size']
        result['screen_x'], result['screen_y'] = result['screen_position']
        return result

validate = Validator()

def save(path, **kwargs):
    """ Save config to a file.

    Args:
        path (str): path to config file (config file is always called 'config.json')
    """
    if not path.endswith('config.json'):
        path = os.path.join(path, 'config.json')
    if not os.path.exists(path):
        raise FileNotFoundError("Could not find config file at location: {0}".format(path))
    with open(path, 'w') as f:
        # maybe validate here?
        json.dump(kwargs, f, indent=4, sort_keys=True)
    
def load(path):
    """ Load a config file.

    Args:
        path (str): path to config file

    Returns:
        dict: a dictionary containing loaded config
    """
    path = os.path.abspath(path)
    if not path.endswith('config.json'):
        path = os.path.join(path, 'config.json')
    if not os.path.exists(path):
        raise FileNotFoundError("Could not find config file at location: {0}".format(path))

    print("USING CONFIG FILE: {0}".format(path))

    with open(path, 'r') as f: 
        data = json.load(f)
        result = validate(**data)
        return result

def reset(path):
    """ Reset config file to default values.

    Args:
        path (str): path to config file
    """
    if not path.endswith('config.json'):
        path = os.path.join(path, 'config.json')
    if not os.path.exists(path):
        raise FileNotFoundError("Could not find config file at location: {0}".format(path))
    with open(path, 'w') as f:
        json.dump(kwargs, f, indent=4, sort_keys=True)

if __name__ == "__main__":

    def run():
        path = 'icu/'
        save(path, **default_config())
        config = load(path)

        for k,v in config.items():
            print(k, v, type(v))
    run()

    #regex tests...
    from pprint import pprint
    for i in default_config_screen():
        print(i, ":")
    print()
    for i in default_event_schedule():
        print(i, ":")
    
   