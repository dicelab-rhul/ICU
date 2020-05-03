import json
import os
import re
import random

from types import SimpleNamespace



class ConfigurationError(Exception):
    pass

# =================================== # =================================== # =================================== # 
# =================================== # ======== ALL CONFIG OPTIONS ======= # =================================== # 
# =================================== # =================================== # =================================== #

def default_config_screen():
    return dict(screen_width=800, 
                screen_height=800, 
                screen_x = 0,
                screen_y = 0,
                screen_full=False)

def default_event_schedule():
    return dict(schedule_warning_light='uniform(0, 1000)',
                schedule_scale=1000,
                schedule_tracking=[[500,200]])

def default_config():
    
    return dict(**default_config_screen(), **default_event_schedule())

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
        return random.gauss(self.mu, self.sigma) #not thread safe?

distributions = lambda: {k.__name__:k for k in Distribution.__subclasses__()}

# =================================== # =================================== # =================================== # 

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
            def list_repeat(v):
                while True:
                    for i in v:
                        yield i
            return list_repeat(v)
        else:
            v = Validator.validate_iter(k, v)
            return v

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
    
    def is_type(*types, **kwargs): #validate type
        k = next(iter(kwargs.keys()))
        v = kwargs[k]
        #print(k,v,types)
        if not isinstance(v, tuple(types)):
            raise ConfigurationError("Invalid value '{0}' for '{1}', must be one of type: {2}.".format(v, k, tuple([t.__name__ for t in types])))
        return v

    # ================================================================================== #

    screen_width    = lambda **kwargs: Validator.is_type(int, float, **kwargs)
    screen_height   = lambda **kwargs: Validator.is_type(int, float, **kwargs)
    screen_x        = lambda **kwargs: Validator.is_type(int, float, **kwargs)
    screen_y        = lambda **kwargs: Validator.is_type(int, float, **kwargs)
    screen_full     = lambda **kwargs: Validator.is_type(bool, **kwargs)

    schedule_warning_light  =  lambda **kwargs: Validator.is_schedule(**kwargs)
    schedule_scale          =  lambda **kwargs: Validator.is_schedule(**kwargs)
    schedule_tracking       =  lambda **kwargs: Validator.is_schedule(**kwargs)
    
    # ================================================================================== #

    def __call__(self, **kwargs):
        return {k:getattr(Validator, k)(**{k:v}) for k,v in kwargs.items()}
            
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
        return data

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