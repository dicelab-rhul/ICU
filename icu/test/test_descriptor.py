#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Created on 12-10-2020 13:58:58

    [Description]
"""
__author__ = "Benedict Wilkins"
__email__ = "benrjw@gmail.com"
__status__ = "Development"


class etuple(tuple):
    
    def __new__(self, *args):
        return super(etuple, self).__new__(etuple, args)

class event_property(property):

    def __set__(self, obj, value):
        cause = None
        if isinstance(value, etuple):
            assert len(value) == 2
            value, cause = value

        super(event_property, self).__set__(obj, value)
        nvalue = self.__get__(obj)
        print()
        print("CAUSE", cause)


class test:

    def __init__(self):
        self.__x = None

    @event_property
    def x(self):
        return self.__x

    @x.setter
    def x(self, value):
        print("SET", value)

    
t = test()
t.x = etuple(1, 2)
t.x = 3