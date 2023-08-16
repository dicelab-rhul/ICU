
from collections import deque
from typing import Any
from ..event2 import SinkBase, SourceBase, Event, DELIMITER
from .commands import PYGAME_INPUT_MOUSEDOWN, PYGAME_INPUT_MOUSEUP, COSMETIC, SET_PROPERTY, GET_PROPERTY, SET_RESPONSE, GET_RESPONSE, CHANGED
from .constants import * # colours

from .utils import Point

# used to ensure events trigger when cosmetic options are changed in a widget
class CosmeticOptionsDict:

    def __init__(self, initial, source):
        super().__init__()
        self._dict = {**initial}
        self._source = source

    def __getitem__(self, key):
        return self._dict[key]

    def __setitem__(self, key, value):
        old_value = self._dict[key]
        self._dict[key] = value
        self._source.source(self._source.address + DELIMITER + CHANGED, dict(old = {key.__name__ : old_value}, new = {key  : value}) ) # this decorator can only be used on an event source... TODO check this? 

    def __delitem__(self, key):
        del self._dict[key]

    def update(self, data):
        return self._dict.update(data)

    def __contains__(self, key):
        return key in self._dict

    def keys(self):
        return self._dict.keys()

    def values(self):
        return self._dict.values()

    def items(self):
        return self._dict.items()
  
def cosmetic_options(**options):
    def decorator(cls):
        original_init = cls.__init__
        def _cosmetic_init_(self, *args, **kwargs):
            # useful for determining what is settable..
            if hasattr(self, '__cosmetic_options__'): 
                self.__cosmetic_options__ += list(options)
            else:
                self.__cosmetic_options__ = list(options)
            # set backing variables
            for option, value in options.items():
                backing = "_" + option
                setattr(self, backing, value)
            return original_init(self, *args, **kwargs)
        # set properties for the class
        for option, _ in options.items():
            backing = "_" + option
            if not hasattr(cls, option): # its already been set, leave this up to the class :)
                setattr(cls, option, property_event(lambda self, backing=backing: getattr(self, backing), lambda self, v, backing=backing: setattr(self, backing, v)))
        cls.__init__ = _cosmetic_init_
        return cls
    return decorator

def settable_properties(*options):
    def decorator(func):
        def fun(self, *args, **kwargs):
            if hasattr(self, '__settable_options__'):
                self.__settable_options__ += list(options)
            else:
                self.__settable_options__ = list(options)
            func(self, *args, **kwargs)
        return fun
    return decorator

def gettable_properties(*options):
    def decorator(func):
        def fun(self, *args, **kwargs):
            if hasattr(self, '__gettable_options__'):
                self.__gettable_options__ += list(options)
            else:
                self.__gettable_options__ = list(options)
            func(self, *args, **kwargs)
        return fun
    return decorator


class property_event(property):
    def __set__(self, obj, value):
        old_value = super().__get__(obj)
        result = super().__set__(obj, value)
        new_value = super().__get__(obj)
        obj.source(obj.address + DELIMITER + CHANGED, dict(old = {self.fset.__name__ : old_value}, new = {self.fset.__name__  : new_value}) ) # this decorator can only be used on an event source... TODO check this? 
        return result 

def in_bounds(position, rect_pos, rect_size):
    return rect_pos[0] <= position[0] <= rect_pos[0] + rect_size[0] and rect_pos[1] <= position[1] <= rect_pos[1] + rect_size[1]

class Widget(SourceBase, SinkBase):
    
    @gettable_properties('cosmetic_options', 'gettable_properties', 'settable_properties')
    def __init__(self, name, clickable=False):
        super().__init__()
        assert not name in ["INPUT", "WINDOW"] # these are reserved names in the event system!
        self._parent = None # set by adding this as a child
        self.name = name
        self.children = dict() 
        self.clickable = clickable
        self.subscriptions = []
        if clickable:
            self.subscriptions.append(PYGAME_INPUT_MOUSEDOWN)
            self.subscriptions.append(PYGAME_INPUT_MOUSEUP)
        
        self._prepare_click = False
        self._source_buffer = deque() 

    @property   
    def gettable_properties(self):
        return list(self.__settable_options__) + list(self.__cosmetic_options__) # TODO check there are no collisions
    
    @property
    def settable_properties(self):
        return list(self.__gettable_options__) + list(self.__cosmetic_options__) # TODO check there are no collisions
    
    @property
    def cosmetic_options(self): # TODO when any cosmetic option is set, an event should be triggered?
        return self.__cosmetic_options__
           
    @property
    def address(self): # event system address for this widget
        parent = self.parent.address if self.parent is not None else "UI" # TODO perhaps instead have a single main parent called "UI" and None -> ""
        return f"{parent}::{self.name}"

    @property
    def parent(self):
        return self._parent
    
    def get_subscriptions(self):
        return self.subscriptions + [ f"{self.address}::*".replace("UI::", "ICU::")] # TODO do this somewhere else, its not reusable
    
    def add_child(self, child):
        self.children[child.name] = child
        child._parent = self # this must be upheld... 

    def remove_child(self, child):
        del self.children[child.name]    
        child._parent = None # orphaned... warning? 
    
    def get_events(self):
        while len(self._source_buffer) > 0:
            yield self._source_buffer.popleft()

    def sink(self, event):
        event_type = event.type.split(DELIMITER)
        event_suffix = event_type[-1]
        event_name = event_type[-2] # when setting properties, this will be the name of self (not a child)
        # TODO document this
        if event_name == self.name: # widget specific events...
            #if event_suffix == COSMETIC:
            #    self.on_cosmetic(event)
            if event_suffix == SET_PROPERTY:
                self.on_set_property(event) 
            elif event_suffix == GET_PROPERTY:
                self.on_get_property(event) 

        elif self.clickable:
            if event.type == PYGAME_INPUT_MOUSEDOWN and self.in_bounds((event.data['x'], event.data['y'])):
                self._prepare_click = True
                return self.on_mouse_down(event) 
            elif event.type == PYGAME_INPUT_MOUSEUP and self.in_bounds((event.data['x'], event.data['y'])):
                if self._prepare_click:  # there was a click on this widget
                    self._prepare_click = False
                    self.on_mouse_click(event)
                return self.on_mouse_up(event)
        
    
    def on_set_property(self, event):
        # set these options, and produce an event that shows the change
        _toset = event.data
        # TODO document this
        setflags = {
            '=' : lambda obj,k,v : setattr(obj, k, v),
            '-' : lambda obj,k,v : setattr(obj, k, getattr(obj, k) - v),
            '*' : lambda obj,k,v : setattr(obj, k, getattr(obj, k) * v),
            '/' : lambda obj,k,v : setattr(obj, k, getattr(obj, k) / v),
            '+' : lambda obj,k,v : setattr(obj, k, getattr(obj, k) + v),
        }

        # TODO move this and add more options e.g. starting with ? for "eval"
        def _getkv(k,v):
            #obj = self.cosmetic_options if k in self.cosmetic_options else self # might be setting cosmetic options?
            if k[0] in setflags.keys():
                return k[1:], (v, k[0])
            else:
                return k, (v, '=')

        # preprocess data to extract flags +/-* these are inplace modifiers
        _toset = dict(_getkv(k,v) for k,v in _toset.items())
        if _toset is not None:
            toset = {k:v for k,v in _toset.items() if k in self.settable_properties}
            if len(_toset) != len(toset):
                print(f"WARNING: trying to set missing properties on widget {self.name}: {list(set(_toset.keys()) - set(toset.keys()))} avaliable properties: {list(self.__settable_options__)}")
            
            old = {k:getattr(self, k) for k,v in toset.items()}

            def _set_property(k, v):
                x, f = v
                setflags[f](self, k, x)
                return getattr(self, k)
            new = {k:_set_property(k,v) for k,v in toset.items()}
            self.source(self.address + DELIMITER + SET_RESPONSE, dict(old=old, new=new))

    def on_get_property(self, event):
        # get these options and produce an event that shows them
        _toget = event.data
        if _toget is not None:
            toget = {k:getattr(self, k) for k in _toget if k in self.gettable_properties}
            
            if len(_toget) != len(toget):
                print(f"WARNING: trying to set missing properties on widget {self.name}: {list(set(_toget.keys()) - set(toget.keys()))} avaliable properties: {list(self.__gettable_options__)}")
            self.source(self.address + DELIMITER + GET_RESPONSE, toget)

    def on_cosmetic(self, event):
        for k,v in event.data.items(): # ignore any that are not valid TODO warning?
            if k in self.cosmetic_options:
                self.cosmetic_options[k] = v

    def on_mouse_down(self, event):
        pass # raise NotImplementedError() 

    def on_mouse_up(self, event):
        pass # raise NotImplementedError()

    def on_mouse_click(self, event):
        pass # raise NotImplementedError()

    def source(self, event_type, data):
        self._source_buffer.append(Event(event_type, data))

    def close(self):
        pass # nothing to close

    @property
    def bounds(self):
        return self.position, self.size
    
    @property
    def canvas_position(self):
        return Point(self.parent.canvas_position[0] + self.position[0], self.parent.canvas_position[1] + self.position[1])

    @property
    def canvas_bounds(self):
        p, s = self.bounds
        pp, _ = self.parent.canvas_bounds if self.parent is not None else ((0,0), (1,1))
        return (p[0] + pp[0], p[1] + pp[1]), s

    def in_bounds(self, position):
        p, s = self.canvas_bounds
        return p[0] <= position[0] <= p[0] + s[0] and p[1] <= position[1] <= p[1] + s[1]

    def draw(self):
        raise NotImplementedError() 
    
    # register widget and children with the end system
    def register(self, event_system):
        event_system.add_sink(self)
        event_system.add_source(self)
        for child in self.children.values():
            child.register(event_system)
