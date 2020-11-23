#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""
__author__ = "Benedict Wilkins"
__email__ = "benrjw@gmail.com"
__status__ = "Development"

import re
from itertools import cycle, repeat

from .distribution import distributions
from .exception import ConfigurationError

class Schedule:
    """ Class representing a schedule. """

    def __init__(self, schedule):
        super(Schedule, self).__init__()
        self._rep = str(schedule)

        if isinstance(schedule, (int, float)):         # schedule a single event
            self.schedule = iter([lambda : schedule])
        elif isinstance(schedule, str):                # schedule a random event
            self.schedule = iter([Schedule.validate_distribution(schedule)])
        elif isinstance(schedule, list):               # schedule a number of events (may be repeated)
            self.schedule = Schedule.validate_list(schedule)
        else:
            raise ConfigurationError("Invalid value '{0}', must be a number, tuple, list or distribution.".format(schedule))

    def __str__(self):
        return "schedule: " + self._rep

    def __repr__(self):
        return str(self)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.schedule)()
 
    def validate_distribution(v):
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
                    raise ConfigurationError("Invalid value '{0}', failed to build distribution, perhaps the arguments were invalid.".format(v)) from e
            else:
                raise ConfigurationError("Invalid value '{0}', distribution not found, valid distributions include: {2}".format(v,tuple(distributions().keys())))

    def validate_iter(v):
        def _validate_element(i):
            if isinstance(i, (int, float)):
                return lambda: i
            elif isinstance(i, (str)):
                return Schedule.validate_distribution(i)
            else: 
                raise ConfigurationError("Invalid value '{0}' in repeating schedule {1}, must be a number.".format(i, v))  
        
        return [_validate_element(i) for i in v]

    def validate_list(v):
        if len(v) > 0 and isinstance(v[0], list):
            if len(v) > 1:
                raise ConfigurationError("Invalid value '{0}' a repeating schedule is specified through the use of double square brackets: [[...]].".format(v))
            v = Schedule.validate_iter(v[0])
            return cycle(v)
        else:
            v = Schedule.validate_iter(v)
            return iter(v)

def validate_schedule(schedule, **kwargs): # validate schedule (number, list, tuple, str)
    """ Validate a schedule specified in the configuration.

    Args:
        schedule (int, float, list, tuple, str): the raw schedule

    Returns:
        Schedule: A schedule object derived from the supplied raw schedule that can be used directly with the ICU scheduling system.
    """
    assert len(kwargs) == 0 # UNEXPECTED ERROR ... VALIDATION HAS GONE WRONG SOMEWHERE
    return Schedule(schedule)