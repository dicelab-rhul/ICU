import json
import os
import re
import random

from types import SimpleNamespace
from collections import defaultdict

from itertools import cycle, islice


class ConfigurationError(Exception):
    pass

# =================================== # =================================== # =================================== # 
# =================================== # ======== ALL CONFIG OPTIONS ======= # =================================== # 
# =================================== # =================================== # =================================== #

def tasks():
    return SimpleNamespace(**{k:k for k in ['system', 'fuel', 'track']})

def default_config_screen():
    return dict(screen_width=800, 
                screen_height=800, 
                screen_x = 0,
                screen_y = 0,
                screen_full=False)

def default_task_options():
    return   {"system" : True, "track" : True,"fuel" : True}

def default_event_schedule():
    return {"Scale:0" :         default_scale_schedule(),
            "Scale:1" :         default_scale_schedule(),
            "Scale:2" :         default_scale_schedule(),
            "Scale:3" :         default_scale_schedule(),
            "WarningLight:0" :  default_warning_light_schedule(),
            "WarningLight:1" :  default_warning_light_schedule(),
            "Target:0" :      default_target_schedule()}

def default_pump_config():
    return dict(flow_rate = 10, event_rate = 10)

def default_event_generator():
    return {"ScaleComponent" : "ScaleEventGenerator"}

def default_scale_schedule():
    return uniform(1000,10000) 

def default_warning_light_schedule():
    return uniform(1000,10000) 

def default_pump_schedule():
    return uniform(0,20000)

def default_target_schedule():
    return cycle([300])

def default_overlay():
    return dict(transparent=True, outline=True, arrow=True)

def default_config():
    return dict(**default_config_screen(), task=default_task_options(), schedule=default_event_schedule(), overlay=default_overlay())

ScreenOptions = SimpleNamespace(**{k:k for k in default_config_screen().keys()})
# TODO other options

# =================================== # =================================== # =================================== # 

# =================================== # =================================== # =================================== # 
# =================================== # ========= DISTRIBUTIONS =========== # =================================== # 
# =================================== # =================================== # =================================== #

class Distribution: #must be an iterable...
    
    def __iter__(self):
        return self

    def __next__(self):
        return self.sample()

class uniform(Distribution):

    def __init__(self, a, b):
        try:
            #assert a >= 0 and b >= 0
            a = float(a)
            b = float(b)
            self.a = min(a,b)
            self.b = max(a,b)
        except:
            raise ConfigurationError("Invalid arguments for uniform distribution: {0}, {1}, must be numbers > 0".format(a,b))

    def sample(self):
        return random.uniform(self.a, self.b)

class normal(Distribution):

    def __init__(self, mu, sigma, decay=1.):
        try:
            self.mu = float(mean)
            self.sigma = float(std)
            self.decay = float(decay) #multiplicative decay?
        except:
            raise ConfigurationError("Invalid arguments for uniform distribution: {0}, {1}, must be numbers".format(a,b))

    def sample(self):
        self.mu = self.mu * self.decay
        return max(0, random.gauss(self.mu, self.sigma)) #not thread safe?

distributions = lambda: {k.__name__:k for k in Distribution.__subclasses__()}

# =================================== # =================================== # =================================== # 

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

def condition(cond):
    def _condition(**kwargs):
        assert len(kwargs) == 1
        k = next(iter(kwargs.keys()))
        v = kwargs[k]

        cond(v)


        
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

pump_options = dict(
    flow_rate           = Option('pump', is_type(int)),
    event_rate          = Option('pump', is_type(int))

)

target_options = dict(
    step               = Option('target', is_type(int, float)),

)
warninglight_options = dict(
    on_colour           = Option('warning_light', is_type(str)),
    off_colour          = Option('warning_light', is_type(str)),
    outline_colour      = Option('warning_light', is_type(str)),
    outline_thickness   = Option('warning_light', is_type(int))
)

scale_options = dict(
    size                = Option('scale', is_type(int)),
    position            = Option('scale', is_type(int)),
    background_colour   = Option('scale', is_type(str)),
    outline_colour      = Option('scale', is_type(str)),
    outline_thickness   = Option('scale', is_type(int)),
    slider_colour       = Option('scale', is_type(str))
)

tank_options = dict(
    burn_rate           = Option('tank', is_type(int, float)),
    accept_position     = Option('tank', is_type(int, float)),
    accept_proportion   = Option('tank', is_type(int, float)),
    capacity            = Option('tank', is_type(int, float)),
    fuel                = Option('tank', is_type(int, float)),

    fuel_colour         = Option('tank', is_type(str)),
    background_colour   = Option('tank', is_type(str)),
    outline_colour      = Option('tank', is_type(str)),
    outline_thickness   = Option('tank', is_type(int)),
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
            screen_x        = Option('main', is_type(int, float)),
            screen_y        = Option('main', is_type(int, float)),
            screen_full     = Option('main', is_type(bool)),

            schedule        = Option('main', lambda **kwargs: {k:Validator.is_schedule(**{k:v}) for k,v in next(iter(kwargs.values())).items()}),
            
            task            = Option('main', validate_options('task')),
            system          = Option('task', is_type(bool)),
            track           = Option('task', is_type(bool)),
            fuel            = Option('task', is_type(bool)),

            input           = Option('main',  validate_options('input')),
            mouse           = Option('input', is_type(bool)),
            keyboard        = Option('input', is_type(bool)),
            joystick        = Option('input', is_type(bool)),
            eye_tracker     = Option('input', is_type(bool)),

            generators      = Option('main', lambda **kwargs: None), #TODO

            overlay             = Option('main',    validate_options('overlay')),
            arrow               = Option('overlay', is_type(bool)),
            transparent         = Option('overlay', is_type(bool)),
            outline             = Option('overlay', is_type(bool)),
            highlight_thickness = Option('overlay', is_type(int)),
            highlight_colour    = Option('overlay', is_type(str))
    )

class Validator:

    def validate_iter(k, v):
        for i in v:
            if not isinstance(i, (int, float)):
                raise ConfigurationError("Invalid value '{0}' for '{1}' in repeating schedule {2}, must be a number.".format(i, k, v))
        return v

    def validate_list(k, v):
        if len(v) > 0 and isinstance(v[0], list):
            if len(v) > 1:
                raise ConfigurationError("Invalid value '{0}' for '{1}', a repeating schedule is specified through the use of double square brackets: [[...]].".format(k, v))
            v = Validator.validate_iter(k, v[0])
            return cycle(v)
        else:
            v = Validator.validate_iter(k, v)
            return iter(v)

    def validate_str(k, v):
        pattern = '\w+\(((\w|\d)+,)*((\w|\d)+)?\)'
        r = re.match(pattern, re.sub(r"\s+", "", v))
        if r is not None:
            name, args = v.split('(')
            dists = distributions()
            if name in dists:
                args = args[:-1].split(",")
                try:
                    return dists[name](*args)
                except Exception as e:
                    raise ConfigurationError("Invalid value '{0}' for '{1}', failed to build distribution, perhaps the arguments were invalid.".format(v,k)) from e
            else:
                raise ConfigurationError("Invalid value '{0}' for '{1}', distribution not found, valid distributions include: {2}".format(v,k,tuple(distributions().keys())))


    def is_schedule(**kwargs): #validate schedule (number, list, tuple, str)
        k = next(iter(kwargs.keys()))
        v = kwargs[k]
        if isinstance(v, (int, float)): #schedule a single event
            return v
        elif isinstance(v, list):
            return Validator.validate_list(k, v)
        elif isinstance(v, str): #build schedule object
            return Validator.validate_str(k, v)
        raise ConfigurationError("Invalid value '{0}' for '{1}', must be a number, tuple, list or distribution.".format(v,k))


    def __call__(self, **kwargs):
        return validate_options('main')(**{'main':kwargs}) #{k:get_option(k, 'main')(**{k:v}) for k,v in kwargs.items()}
    
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
    if not path.endswith('config.json'):
        path = os.path.join(path, 'config.json')
    if not os.path.exists(path):
        raise FileNotFoundError("Could not find config file at location: {0}".format(path))
    with open(path, 'r') as f: 
        data = json.load(f)
        data = validate(**data)
        result = default_config()
        result.update(data)
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
    
    """
    def match(v):
        pattern = '\w+\(((\w|\d),)*((\w|\d)+)?\)'
        r = re.match(pattern, v)
        return r

    print(match('uniform(0,1000)'))
    print(match('uniform(10)'))
    print(match('uniform()'))
    """