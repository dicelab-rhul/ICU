#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""
__author__ = "Benedict Wilkins"
__email__ = "benrjw@gmail.com"
__status__ = "Development"

import json
import os

import logging
LOGGER = logging.getLogger("ICU")

from types import SimpleNamespace
import importlib


from .distribution import *
from .validate import validate_schedule
from .exception import ConfigurationError

from .default import default_config, default_external

def hook(config_hook):
    # update validation for external options using a config hook, the hook may be (serialisable) object, or a module path
    # the config hook must define "options" and "defaults", these will be added to ICU options and defaults and used to validate the config file.
    if isinstance(config_hook, str):
        try:
                config_hook = importlib.import_module(config_hook)
        except:
            raise ConfigurationError("Failed to get hook: {0}".format(config_hook))
    
    try:
        config_hook.options
        config_hook.defaults
    except:
        raise ConfigurationError("Config hook {0} doesnt define 'defaults' or 'options'...".format(config_hook))

    def find_conflict(a, b):
        return set(a.keys()).intersection(set(b.keys()))

    c = find_conflict(options, config_hook.options)
    if len(c) > 0:
        raise ConfigurationError("config hook {0} contains conflicting keys: {1}".format(config_hook, c))

    options.update(config_hook.options)
    default_external.update(config_hook.defaults)

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
    schedule           = Option('target', validate_schedule),           # event schedule. Target drift, each event moves the target by `step` amount.
    step               = Option('target', is_type(int, float)),         # distance (pixels) the Target moves on each event
    invert             = Option('target', is_type(bool))                # invert controls for tracking
)

warninglight_options = dict(
    schedule            = Option('warning_light', validate_schedule),   # event schedule. Each event switches the light to the undesired state (off for WarningLight:0 and on for WarningLight:1)
    grace               = Option('warning_light', is_type(int, float)), # grace period (the time after which the light may turn on/off after a user has clicked)
    key                 = Option('warning_light', is_type(str)),        # key-binding shortcut, may be used instead of clicking
    state               = Option('warning_light', is_type(int)),        # initial state (on or off)
    on_colour           = Option('warning_light', is_type(str)),        # cosmetic, colour of the on state
    off_colour          = Option('warning_light', is_type(str)),        # cosmetic, colour of the off state
    outline_colour      = Option('warning_light', is_type(str)),        # cosmetic, colour of the outline 
    outline_thickness   = Option('warning_light', is_type(int))         # cosmetic, thickness of the outline
)

scale_options = dict(
    schedule            = Option('scale', validate_schedule),           # event schedule. Each events moves the slider up/down 1 place. 
    key                 = Option('scale', is_type(str)),                # key-binding shortcut, may be used instead of clicking
    size                = Option('scale', is_type(int)),                # size of the scale (number of positions that the slider may be in)
    position            = Option('scale', is_type(int)),                # initial position of the slider
    background_colour   = Option('scale', is_type(str)),                # cosmetic, background colour of the scale
    outline_colour      = Option('scale', is_type(str)),                # cosmetic, outline colour of the scale (and slider)
    outline_thickness   = Option('scale', is_type(int)),                # cosmetic, outline thickness of the scale (and slider)
    slider_colour       = Option('scale', is_type(str))                 # cosmetic, colour of the slider
)

pump_options = dict(
    schedule            = Option('pump', validate_schedule),            # event schedule. Each event causes the pump to fail/repair (repeating every two events).
    flow_rate           = Option('pump', is_type(int)),                 # transfer rate of fuel from one tank to another (units/second)
    event_rate          = Option('pump', is_type(int)),                 # number of events to trigger /second
    scale               = Option('pump', is_type(float))                # cosmetic, the display scale of the pump
)

tank_options = dict(
    burn_rate           = Option('tank', is_type(int, float)),          # rate at which fuel is burnt units/second
    accept_position     = Option('tank', is_type(int, float)),          # position of the acceptable level of fuel (for a main tank)
    accept_proportion   = Option('tank', is_type(int, float)),          # proportion of acceptability of fuel (for a main tank), fuel levels within the range: position +- proportion are acceptable.
    capacity            = Option('tank', is_type(int, float)),          # capacity of the tank
    fuel                = Option('tank', is_type(int, float)),          # initial fuel level
    
    fuel_colour         = Option('tank', is_type(str)),                 # cosmetic, colour of the fuel
    background_colour   = Option('tank', is_type(str)),                 # cosmetic, background colour of the tank
    outline_colour      = Option('tank', is_type(str)),                 # cosmetic, outline colour of the tank
    outline_thickness   = Option('tank', is_type(int)),                 # cosmetic, outline thickness of the tank
)

eyetracker_options = dict(
    enabled             = Option('eyetracker', is_type(bool)),          # enable eye tracking (requires a device to be connected)
    calibrate           = Option('eyetracker', is_type(bool)),          # calibrate the eye-tracker
    sample_rate         = Option('eyetracker', is_type(int)),           # sample rate for the eye-tracker (if configurable on the device)
    stub                = Option('eyetracker', is_type(bool)),          # use the mouse as a stub for an eye tracking device, functions exactly as an eyetracker (useful for testing) 
)

options = dict(

            main            = Option('-', validate_options('main')),

            Pump            = Option('main', validate_options('pump', _options=pump_options)),                  
            Target          = Option('main', validate_options('target', _options=target_options)),              
            WarningLight    = Option('main', validate_options('warning_light', _options=warninglight_options)), 
            Scale           = Option('main', validate_options('scale', _options=scale_options)),                
            FuelTank        = Option('main', validate_options('tank', _options=tank_options)),                  

            screen_width    = Option('main', is_type(int, float)),      # window width
            screen_height   = Option('main', is_type(int, float)),      # window height
            screen_size     = Option('main', is_coord()),               # window size
            screen_x        = Option('main', is_type(int, float)),      # window x position
            screen_y        = Option('main', is_type(int, float)),      # window y position
            screen_position = Option('main', is_coord()),               # window position

            screen_full            = Option('main', is_type(bool)),     # window full screen ?
            screen_resizable       = Option('main', is_type(bool)),     # window resizable ?
            screen_aspect          = Option('main', is_coord()),        # window aspect ratio
            screen_min_size        = Option('main', is_coord()),        # minimum window size
            screen_max_size        = Option('main', is_coord()),        # maximum window size
            background_colour      = Option('main', is_type(str)),      #cosmetic, window background colour
            
            task            = Option('main', validate_options('task')), 
            system          = Option('task', is_type(bool)),            # enable/disable tracking task
            track           = Option('task', is_type(bool)),            # enable/disable system task
            fuel            = Option('task', is_type(bool)),            # enable/disable fuel task

            input           = Option('main',  validate_options('input')), 
            mouse           = Option('input', is_type(bool)),               # enable/disable mouse input
            keyboard        = Option('input', is_type(bool)),               # enable/disable keyboard input
            joystick        = Option('input', is_type(bool)),               # enable/disable joystick input

            eyetracker      = Option('input', validate_options('eyetracker', _options=eyetracker_options)),

            shutdown          = Option('main', is_type(int, float)),        # time after which to stop the system (-1 to never stop)

            overlay             = Option('main',    validate_options('overlay')),
            enable              = Option('overlay', is_type(bool)),         # enable/disable overlay (highlighting, arrows etc)
            arrow               = Option('overlay', is_type(bool)),         # enable/disable arrows
            transparent         = Option('overlay', is_type(bool)),         # transparent highlights ? 
            outline             = Option('overlay', is_type(bool)),         # outlined highlights ?
            highlight_thickness = Option('overlay', is_type(int)),          # cosmetic, highlight outline thickness
            highlight_colour    = Option('overlay', is_type(str)),          # cosmetic, highlight colour
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

        config =  validate_options('main')(**{'main':kwargs})

        # ====== POST PROCESSING ====== # 
        #TOOD move this somewhere more suitable
        result = default_config()

        result = update(result, config)

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

    LOGGER.debug("USING CONFIG FILE: {0}".format(path))

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
        raise NotImplementedError() # TODO? 
        #json.dump(kwargs, f, indent=4, sort_keys=True)

if __name__ == "__main__":

    def run():
        path = 'icu/'
        save(path, **default_config())
        config = load(path)

        for k,v in config.items():
            print(k, v, type(v))
    run()
   