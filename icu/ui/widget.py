
from collections import deque
from ..event2 import SinkBase, SourceBase, Event, DELIMITER
from .commands import PYGAME_INPUT_MOUSEDOWN, PYGAME_INPUT_MOUSEUP, COSMETIC, PROPERTY, SET_RESPONSE, GET_RESPONSE
from .constants import * # colours

# TODO these decorators dont work with inheritance!

def cosmetic_options(**options):
    # TODO have these options as part of the platform config
    def decorator(func):
        def fun(self, *args, **kwargs):
            if hasattr(self, '__cosmetic_options__'):
                self.__cosmetic_options__.update(options)
            else:
                self.__cosmetic_options__ = options
            func(self, *args, **kwargs)
        return fun
    return decorator

def settable_properties(*options):
    def decorator(func):
        def fun(self, *args, **kwargs):
            if hasattr(self, '__settable_options__'):
                self.__settable_options__.update(options)
            else:
                self.__settable_options__ = options
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

def in_bounds(position, rect_pos, rect_size):
    return rect_pos[0] <= position[0] <= rect_pos[0] + rect_size[0] and rect_pos[1] <= position[1] <= rect_pos[1] + rect_size[1]

class Widget(SourceBase, SinkBase):
    
    @gettable_properties('cosmetic_options')
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
    def cosmetic_options(self):
        return self.__cosmetic_options__
           
    @property
    def address(self): # event system address for this widget
        parent = self.parent.address if self.parent is not None else "UI"
        return f"{parent}::{self.name}"

    @property
    def parent(self):
        return self._parent
    
    def get_subscriptions(self):
        return self.subscriptions + [ f"{self.address}::*"]
    
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
        #event_suffix#event_type = event.type.split(DELIMITER)
        #event_suffix = event_type[-1]
        if f"{self.address}::{COSMETIC}" == event.type:
            self.on_cosmetic(event)
        elif f"{self.address}::{PROPERTY}" == event.type:
            self.on_property(event) 
        
        elif self.clickable:
            if event.type == PYGAME_INPUT_MOUSEDOWN and self.in_bounds((event.data['x'], event.data['y'])):
                self._prepare_click = True
                return self.on_mouse_down(event) 
            elif event.type == PYGAME_INPUT_MOUSEUP and self.in_bounds((event.data['x'], event.data['y'])):
                if self._prepare_click:  # there was a click on this widget
                    self._prepare_click = False
                    self.on_mouse_click(event)
                return self.on_mouse_up(event)
        
    def on_property(self, event):
        # set these options, and produce an event that shows the change
        _toset = event.data.get('set', None) # properties to set
        if _toset is not None:
            toset = {k:v for k,v in _toset.items() if k in self.__settable_options__}
            if len(_toset) != len(toset):
                pass # TODO log warning? return errors for these?


            old = {k:getattr(self, k) for k in toset}
            for k,v in toset.items():
                setattr(self, k, v)
            self.source(self.address + PROPERTY + SET_RESPONSE, dict(old=old, new=toset))

        # get these options and produce an event that shows them
        _toget = event.data.get('get', None)
        if _toget is not None:
            toget = {k:getattr(self, k) for k in _toget if k in self.__gettable_options__}
            if len(_toget) != len(toget):
                pass # TODO log warning? return errors for these?
            
            self.source(self.address + PROPERTY + GET_RESPONSE, toget)

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
    def canvas_position(self):
        return self.parent.canvas_position[0] + self.position[0], self.parent.canvas_position[1] + self.position[1]

    @property
    def canvas_bounds(self):
        p, s = self.bounds
        pp, _ = self.parent.canvas_bounds if self.parent is not None else ((0,0), (1,1))
        return (p[0] + pp[0], p[1] + pp[1]), s

    @property
    def bounds(self):
        raise NotImplementedError()

    def in_bounds(self, position):
        p, s = self.canvas_bounds
        return p[0] <= position[0] <= p[0] + s[0] and p[1] <= position[1] <= p[1] + s[1]

    def draw(self):
        raise NotImplementedError() 

    @property 
    def position(self):
        return self.bounds[0]
     
    @property
    def size(self):
        return self.bounds[1]
    
    # register widget and children with the end system
    def register(self, event_system):
        event_system.add_sink(self)
        event_system.add_source(self)
        for child in self.children.values():
            child.register(event_system)
