#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""
__author__ = "Benedict Wilkins"
__email__ = "benrjw@gmail.com"
__status__ = "Development"

import random
from .exception  import ConfigurationError

class Distribution: 
    """ Base class for distributions, used in scheduling. """
    def __call__(self):
        return self.sample()

class uniform(Distribution):
    """ Uniform distribution, used for scheduling. """

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

    def __str__(self):
        return "uniform({0},{1})".format(self.a, self.b)

    def __repr__(self):
        return str(self)

class normal(Distribution):
    """ Normal distribution, used for scheduling. """

    def __init__(self, mu, sigma, decay=1.):
        try:
            self.mu = float(mu)
            self.sigma = float(sigma)
            self.decay = float(decay) #multiplicative decay?
        except:
            raise ConfigurationError("Invalid arguments for uniform distribution: {0}, {1}, must be numbers".format(mu, sigma))

    def sample(self):
        self.mu = self.mu * self.decay
        return max(0, random.gauss(self.mu, self.sigma)) #not thread safe?
    
    def __str__(self):
        return "normal({0},{1})".format(self.mu, self.sigma)

    def __repr__(self):
        return str(self)

distributions = lambda: {k.__name__:k for k in Distribution.__subclasses__()} # get all of the distribution sub-classes that have been defined
