""" Utility module that defines different kinds of distributions that may be used in schedule files. 

For example:
```
    "!uniform(-5,5)"
```
The `!` is required to let the schedule parse know that this is not a `str` type. 
See scheduling documentation for further details. 
"""

import random
from .exception  import ConfigurationError

def get_distribution_cls(name):
    names = {k.__name__.lower():k for k in Distribution.__subclasses__()} # get all of the distribution sub-classes that have been defined
    return names.get(name, None)

class Distribution: 
    """ Base class for distributions. """
    def __call__(self):
        return self.sample()
    
class Choice(Distribution):

    def __init__(self, *choices):
        self.choices = tuple(choices)

    def sample(self):
        return random.choice([c() for c in self.choices])
    
    def __str__(self):
        return "choice" + str(self.choices)

    def __repr__(self):
        return str(self)

class Uniform(Distribution):
    """ Uniform distribution. """

    def __init__(self, a, b):
       super().__init__()
       self.a = a
       self.b = b

    def sample_float(self, a, b):
        return random.uniform(a, b)

    def sample_int(self, a, b):
        return random.randint(a, b)
    
    def sample(self):
        a, b = self.a(), self.b()
        if isinstance(a, int) and isinstance(b, int):
            return self.sample_int(a,b)
        elif isinstance(a, float) or isinstance(b, float):
            return self.sample_float(a,b)
        else:
            raise ConfigurationError("Invalid arguments for uniform distribution sampling: {0}, {1}, must be numbers.".format(a,b))

    def __str__(self):
        return "uniform({0},{1})".format(self.a, self.b)

    def __repr__(self):
        return str(self)

class Normal(Distribution):
    """ Normal distribution."""

    def __init__(self, mu, sigma):
        super().__init__()
        self.mu = mu
        self.sigma = sigma
       
    def sample(self):
        mu, sigma = self.mu(), self.sigma()
        if isinstance(mu, (int, float)) and isinstance(sigma, (int, float)):
            return random.gauss(self.mu, self.sigma)
        else:
            raise ConfigurationError("Invalid arguments for normal distribution sampling: {0}, {1}, must be numbers".format(mu, sigma))

    
    def __str__(self):
        return "normal({0},{1})".format(self.mu, self.sigma)
    

    def __repr__(self):
        return str(self)


# except:
            