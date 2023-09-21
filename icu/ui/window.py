
from types import SimpleNamespace
import pygame
import os
import time
import pywinctl as pwc
from icu.event2.event import SourceLocal

from icu.ui.utils.math import Point

from icu.ui.widget import castPoint, gettable_properties, settable_properties, cosmetic_options, Widget
from icu.ui.commands import *

DEFAULT_WINDOW_CONFIG = dict(
    size = Point(1200,640),
    position = Point(0,0),
    min_size = Point(100,100),
    max_size = Point(2000,2000),
    full = False,
    resizable = False,
    aspect = 'none', # valid options are 'none', 'equal'
    background_color = '#808080', # grey
    in_focus = False,
)

WINDOW_TITLE = "icu"
WINDOW = "WINDOW"
ICU_WINDOW_SETPROPERTY = f"ICU::{WINDOW}::SET_PROPERTY"
ICU_WINDOW_GETPROPERTY = f"ICU::{WINDOW}::GET_PROPERTY"


@cosmetic_options(**DEFAULT_WINDOW_CONFIG)
class Window(Widget):
    
    @gettable_properties(DEFAULT_WINDOW_CONFIG.keys())
    @settable_properties(DEFAULT_WINDOW_CONFIG.keys())
    def __init__(self): 
        super().__init__(name = "WINDOW")
        self._window_title = WINDOW_TITLE
        self._window, self._flags = new_pygame_window(self.position.get(), self.size.get(), title=self._window_title)
        # pygame doesnt trigger a resize event when the window is created so
        # trigger one manually to inform other widgets of the initial window size
        self.size = self._size     
        self.subscriptions.append(ICU_WINDOW_SETPROPERTY)
        self.subscriptions.append(ICU_WINDOW_GETPROPERTY)

        self._event_gen = {
            pygame.QUIT:                    lambda event: self.source(UI_WINDOW_QUIT, {}),
            pygame.WINDOWFOCUSGAINED:       self._source_window_focus,
            pygame.WINDOWFOCUSLOST:         self._source_window_focus,
            pygame.WINDOWRESIZED:           self._source_window_resize,
            pygame.WINDOWMOVED:             self._source_window_reposition,
            pygame.MOUSEMOTION:             lambda event: self.source(UI_INPUT_MOUSEMOTION, dict(x=event.pos[0], y=event.pos[1])),
            pygame.MOUSEBUTTONDOWN:         lambda event: self.source(UI_INPUT_MOUSEDOWN, dict(x=event.pos[0], y=event.pos[1], button=event.button)),
            pygame.MOUSEBUTTONUP:           lambda event: self.source(UI_INPUT_MOUSEUP, dict(x=event.pos[0], y=event.pos[1], button=event.button)),
            pygame.KEYDOWN :                lambda event: self.source(UI_INPUT_KEYDOWN, dict(keycode = event.key, mod = event.mod, unicode = event.unicode)),
            pygame.KEYUP :                  lambda event: self.source(UI_INPUT_KEYUP, dict(keycode = event.key, mod = event.mod, unicode = event.unicode)),
        }

    def get_subscriptions(self):
        return self.subscriptions
    
    def sink(self, event):
        if event.type == ICU_WINDOW_SETPROPERTY:
            self.on_set_property(event) 
        elif event.type == ICU_WINDOW_GETPROPERTY:
            self.on_get_property(event) 
        else:
            raise ValueError(f"Invalid event type {event.type} received by {self.address}")

    @property
    def in_focus(self):
        return self._in_focus
    
    @in_focus.setter 
    def in_focus(self, value):
        self._in_focus = value
        if value:
            self.source(UI_WINDOW_WINDOWFOCUSGAINED, dict())
        else:
            self.source(UI_WINDOW_WINDOWFOCUSLOST, dict())

    @property
    def size(self):
        return self._size.clone()
    
    @size.setter
    @castPoint
    def size(self, value):
        self._size = Point(int(value[0]), int(value[1]))  
        npw = pwc.getActiveWindow()
        success = npw.title == WINDOW_TITLE
        success &= npw.resizeTo(int(self._size.x), int(self._size.y), wait = False)
        self.source(UI_WINDOW_WINDOWRESIZED, dict(width = self._size.x, height = self._size.y))

    @property
    def position(self):
        return self._position.clone()

    @position.setter
    @castPoint
    def position(self, value):
        self._position = value
        npw = pwc.getActiveWindow()
        success = npw.title == WINDOW_TITLE
        success &= npw.moveTo(int(self._position.x), int(self._position.y), wait = False)
        self.source(UI_WINDOW_WINDOWMOVED, dict(x = self._position.x, y = self._position.y))

    @property
    def window(self):
        return self._window
    
    def update(self, pygame_event):
        if pygame_event.type in self._event_gen:
            self._event_gen[pygame_event.type](pygame_event)

    # used to convert pygame events to ui events. This should not be called otherwise!
    def _source_window_reposition(self, event):
        if int(self.position[0]) != int(event.x) or int(self.position[1]) != int(event.y):
            self._position = Point(int(event.x), int(event.y)) # this will trigger an event
            self.source(UI_WINDOW_WINDOWMOVED, dict(x = self._position.x, y = self._position.y))

    # used to convert pygame events to ui events. This should not be called otherwise!
    def _source_window_resize(self, event):
        #print(event, self.size)
        if int(self.size[0]) != int(event.x) or int(self.size[1]) != int(event.y):
            self._size = Point(int(event.x), int(event.y))
            self.source(UI_WINDOW_WINDOWRESIZED, dict(width = self._size.x, height = self._size.y))

    # used to convert pygame events to ui events. This should not be called otherwise!
    def _source_window_focus(self, event):
        if event.type == pygame.WINDOWFOCUSGAINED:
            self.in_focus = True # this will trigger an event
        elif event.type == pygame.WINDOWFOCUSLOST:
            self.in_focus = False # this will trigger an event
        else:
            raise ValueError(f"Invalid event {event} encountered when setting window focus.")


def new_pygame_window(window_position, window_size, title=WINDOW_TITLE, resizeable=True):
    assert len(window_position) == 2
    assert len(window_size) == 2 
    
    #if SDL_VIDEO_WINDOW_POS in os.environ:
    #    old_window_position = os.environ[SDL_VIDEO_WINDOW_POS]
    #else:
    #    old_window_position = window_position
    #os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (window_position[0], window_position[1])
    pygame.init()
    flags = 0 
    if resizeable:
        flags |= pygame.RESIZABLE
    screen = pygame.display.set_mode(window_size, flags)
    if title is not None:
        pygame.display.set_caption(title)
    return screen, flags


def get_pygame_window_info():
    npw = pwc.getActiveWindow()
    return SimpleNamespace(window_size = (npw.width, npw.height), window_position=(npw.left, npw.top), window_title=npw.title)


