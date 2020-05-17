import tkinter as tk
import random
import copy
from types import SimpleNamespace

from . import panel
from .constants import BACKGROUND_COLOUR, OUTLINE_WIDTH, OUTLINE_COLOUR, COLOUR_LIGHT_BLUE, COLOUR_BLUE
from .constants import SYSTEM_MONITOR_SCALE_POSITIONS, COLOUR_GREEN, COLOUR_RED
from .constants import WARNING_OUTLINE_COLOUR, WARNING_OUTLINE_WIDTH

#from .constants import WARNING_LIGHT_MIN_HEIGHT, WARNING_LIGHT_MIN_WIDTH

from .event import Event, EventCallback, get_event_sinks

from .component import Component, CanvasWidget, SimpleComponent, BoxComponent, LineComponent
from .highlight import Highlight


EVENT_NAME_CLICK = 'click'
EVENT_NAME_SLIDE = 'slide'
EVENT_NAME_SWITCH = 'switch'

EVENT_NAME_HIGHTLIGHT = 'highlight'

Y_SCALE = 1/8
X_SCALE = 1/2
PADDING = 20

NUM_SCALE_SPLIT = 11

def ScaleEventGenerator():
    scales = Scale.all_components()
    while True:
        r = random.randint(0, len(scales)-1) #choose a random slider
        y = random.randint(0, 1) * 2 - 1 #+-1
        yield Event('scale_event_generator', scales[r], label=EVENT_NAME_SLIDE, slide=y)

def WarningLightEventGenerator():
    import time
    
    warning_lights = WarningLight.all_components()
    while True:
        r = random.randint(0, len(warning_lights)-1)
        yield Event('warning_light_event_generator', warning_lights[r], label=EVENT_NAME_SWITCH)
        
class Scale(EventCallback, Component, CanvasWidget):

    __scale_components__ = [] #just names

    def all_components():
        return copy.deepcopy(Scale.__scale_components__)

    def __init__(self, canvas, name, width=1., height=1., **kwargs):
        super(Scale, self).__init__(canvas, width=width, height=height, background_colour=COLOUR_LIGHT_BLUE, 
                                             outline_thickness=OUTLINE_WIDTH, outline_colour=OUTLINE_COLOUR) 
        self.__state = 0 #the position (int) of the block slider
        name = "{0}:{1}".format(Scale.__name__, name)
        EventCallback.register(self, name)
        Component.register(self, name)
    
        block =  BoxComponent(canvas, height=1/NUM_SCALE_SPLIT, outline_colour=OUTLINE_COLOUR, 
                                outline_thickness=OUTLINE_WIDTH, colour=COLOUR_BLUE)
        block.bind("<Button-1>", self.click_callback)
        self.components['block'] = block

        for i in range(1, NUM_SCALE_SPLIT):
            line = LineComponent(self.canvas, 0, i * 1/NUM_SCALE_SPLIT, 1, i * 1/NUM_SCALE_SPLIT, thickness=OUTLINE_WIDTH)
            self.components['line-' + str(i)] = line

        #self.highlight = Highlight(canvas, self)

        Scale.__scale_components__.append(self.name)
    
    def slide(self, y):
        inc = self.content_height / NUM_SCALE_SPLIT
        self.__state += y
        self.__state = max(0, min(NUM_SCALE_SPLIT-1, self.__state))
        self.components['block'].y = self.y + inc * self.__state

    def sink(self, event):
        #TODO validate event?
        self.slide(event.data.slide)

    def click_callback(self, *args):
        print("click_callback scale")
        self.slide(NUM_SCALE_SPLIT // 2 - self.__state)
        self.source('Global', label='click', value=self.__state) #notify global


class WarningLight(EventCallback, Component, BoxComponent):

    __all_components__ = []
    
    def all_components():
        return WarningLight.__all_components__

    def __init__(self, canvas, name, width=1., height=1., state=0, on_colour=COLOUR_GREEN, off_colour=COLOUR_RED):
        self.__state_colours = [off_colour, on_colour]
        self.__state = state
        colour = self.__state_colours[self.__state]
        super(WarningLight, self).__init__(canvas, width=width, height=height, colour=colour, outline_thickness=OUTLINE_WIDTH, outline_colour=OUTLINE_COLOUR)
        
        name = "{0}:{1}".format(WarningLight.__name__, name)
        EventCallback.register(self, name)
        Component.register(self, name)

        self.bind("<Button-1>", self.click_callback)

        self.highlight = Highlight(canvas, self)
        WarningLight.__all_components__.append(self.name)

    def update(self):
        self.__state = int(not bool(self.__state))
        self.colour = self.__state_colours[self.__state]

    def click_callback(self, *args):
        self.update()
        self.source('Global', label='click', value=self.__state) #notify global

    def sink(self, event):
        self.update()
        
class SystemMonitorWidget(CanvasWidget):

    def __init__(self, canvas, width=480, height=640):
        super(SystemMonitorWidget, self).__init__(canvas, width=width, height=height, background_colour=BACKGROUND_COLOUR, padding=PADDING) 

        #warning lights
        scale_prop = 0.2

        #warning light widget
        self.warning_light_widget = CanvasWidget(canvas)
        self.components['warning_light_widget'] = self.warning_light_widget
      

        self.warning_light_widget.components['warning_right'] = WarningLight(canvas, name=str(0), width=1/3,
                            on_colour=COLOUR_GREEN, off_colour=BACKGROUND_COLOUR, state=1)
        self.warning_light_widget.components['warning_left'] = WarningLight(canvas, name=str(1), width=1/3,
                            on_colour=COLOUR_RED,   off_colour=BACKGROUND_COLOUR, state=0)

        self.layout_manager.fill('warning_light_widget', 'X')
        self.layout_manager.split('warning_light_widget', 'Y', scale_prop)

        #scale widget
        self.scale_widget = CanvasWidget(canvas, padding=PADDING, inner_sep=self.content_width/(len(SYSTEM_MONITOR_SCALE_POSITIONS)*3))
        self.components['scale_widget'] = self.scale_widget
        self.layout_manager.fill('scale_widget', 'X')
        self.layout_manager.split('scale_widget', 'Y', 1-scale_prop)

        #place warning lights
        self.warning_light_widget.layout_manager.anchor('warning_left', 'E')
        self.warning_light_widget.layout_manager.fill('warning_left', 'Y')
        self.warning_light_widget.layout_manager.anchor('warning_right', 'W')
        self.warning_light_widget.layout_manager.fill('warning_right', 'Y')
        
        for i in range(len(SYSTEM_MONITOR_SCALE_POSITIONS)):
            scale = Scale(canvas, name=str(i))
            scale.slide(SYSTEM_MONITOR_SCALE_POSITIONS[i])
            self.scale_widget.components[str(i)] = scale

            self.scale_widget.layout_manager.fill(str(i), 'Y')
            self.scale_widget.layout_manager.split(str(i), 'X')

        
        self.highlight = Highlight(canvas, self)
        
        #self.scale_widget.debug()
        #self.warning_light_widget.debug()

    @property
    def name(self):
        return self.__class__.__name__
