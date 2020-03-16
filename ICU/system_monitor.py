import tkinter as tk
import random
from types import SimpleNamespace

from . import panel
from .constants import BACKGROUND_COLOUR, OUTLINE_WIDTH, OUTLINE_COLOUR, SYSTEM_MONITOR_SCALE_BACKGROUND_COLOUR, SYSTEM_MONITOR_SCALE_BACKGROUND_COLOUR_FILL
from .constants import SYSTEM_MONITOR_SCALE_POSITIONS, COLOUR_GREEN, COLOUR_RED
from .constants import WARNING_OUTLINE_COLOUR, WARNING_OUTLINE_WIDTH

#from .constants import WARNING_LIGHT_MIN_HEIGHT, WARNING_LIGHT_MIN_WIDTH

from .event import Event, EventCallback, EVENT_SINKS

from .component import Component, CanvasWidget, SimpleComponent, BoxComponent, LineComponent

EVENT_NAME_CLICK = 'click'
EVENT_NAME_SLIDE = 'slide'
EVENT_NAME_SWITCH = 'switch'

EVENT_NAME_HIGHTLIGHT = 'highlight'

Y_SCALE = 1/8
X_SCALE = 1/2
PADDING = 20


NUM_SCALE_SPLIT = 11

def highlight_rect(canvas, rect):
    r = (rect[0] - WARNING_OUTLINE_WIDTH, rect[1] - WARNING_OUTLINE_WIDTH, 
         rect[2] + WARNING_OUTLINE_WIDTH, rect[3] + WARNING_OUTLINE_WIDTH)
    return canvas.create_rectangle(*r, width=0, fill=WARNING_OUTLINE_COLOUR)

def ScaleEventGenerator():
    scales = [s for s in EVENT_SINKS.keys() if Scale.__name__ in s]
    while True:
        r = random.randint(0, len(scales)-1)
        y = random.randint(0, 1) * 2 - 1
        yield Event(scales[r], EVENT_NAME_SLIDE, y)

def WarningLightEventGenerator():
    warning_lights = [s for s in EVENT_SINKS.keys() if WarningLight.__name__ in s]
    while True:
        r = random.randint(0, len(warning_lights)-1)
        yield Event(warning_lights[r], EVENT_NAME_SWITCH)
        
class ScaleComponent(EventCallback, Component, CanvasWidget):

    def __init__(self, canvas, name, width=1., height=1., **kwargs):
        super(ScaleComponent, self).__init__(canvas, width=width, height=height, background_colour=SYSTEM_MONITOR_SCALE_BACKGROUND_COLOUR, 
                                             outline_thickness=OUTLINE_WIDTH, outline_colour=OUTLINE_COLOUR) 
        self.__state = 0 #the position (int) of the block slider

        EventCallback.register(self, name)
        Component.register(self, name)
    
        block =  BoxComponent(canvas, height=1/NUM_SCALE_SPLIT, outline_colour=OUTLINE_COLOUR, 
                                outline_thickness=OUTLINE_WIDTH, colour=SYSTEM_MONITOR_SCALE_BACKGROUND_COLOUR_FILL)
        block.bind("<Button-1>", self.click_callback)
        self.components['block'] = block

        for i in range(1, NUM_SCALE_SPLIT):
            line = LineComponent(self.canvas, 0, i * 1/NUM_SCALE_SPLIT, 1, i * 1/NUM_SCALE_SPLIT, thickness=OUTLINE_WIDTH)
            self.components['line-' + str(i)] = line
    
    def slide(self, y):
        inc = self.content_height / NUM_SCALE_SPLIT
        self.__state += y
        self.components['block'].y = self.y + inc * self.__state

    def highlight(self, state):
        print("TODO highlight scale")

    def sink(self, event):
        if event.args[1] == EVENT_NAME_SLIDE:
            self.slide(event.args[2])
        elif event.args[1] == EVENT_NAME_HIGHTLIGHT:
            self.highlight(event.args[2])

    def click_callback(self, *args):
        self.slide(NUM_SCALE_SPLIT // 2 - self.__state)
        self.source(EVENT_NAME_CLICK)


class WarningLightComponent(EventCallback, Component, BoxComponent):

    def __init__(self, canvas, name, width=1., height=1., state=0, on_colour=COLOUR_GREEN, off_colour=COLOUR_RED):
        self.__state_colours = [off_colour, on_colour]
        self.__state = state
        colour = self.__state_colours[self.__state]
        super(WarningLightComponent, self).__init__(canvas, width=width, height=height, colour=colour, outline_thickness=OUTLINE_WIDTH, outline_colour=OUTLINE_COLOUR)
        
        EventCallback.register(self, name)
        Component.register(self, name)

        self.bind("<Button-1>", self.click_callback)

        #self.highlight_rect = highlight_rect(self.canvas, (0,0,self.width,self.height))
        #self.highlight(1)

    def update(self):
        self.__state = int(not bool(self.__state))
        self.colour = self.__state_colours[self.__state]

    def click_callback(self, *args):
        self.update()
        self.source(EVENT_NAME_CLICK) #notify global

    def sink(self, event):
        if event.args[1] == EVENT_NAME_SWITCH:
            self.update()
        elif event.args[1] == EVENT_NAME_HIGHTLIGHT:
            self.highlight(event.args[2])

    def highlight(self, state):
        self.canvas.itemconfigure(self.highlight_rect, state=('hidden', 'normal')[state])

class SystemMonitorWidget(tk.Canvas):

    @property
    def content_width(self):
        return self.width
    
    @property
    def content_height(self):
        return self.height

    def __init__(self, parent, width=480, height=640):
        super(SystemMonitorWidget, self).__init__(parent, width=width, height=height, bg=BACKGROUND_COLOUR) 
       
        self.width = width 
        self.height = height
   
        self.c = CanvasWidget(self, width=self.content_width, height=self.content_height, padding=PADDING)

        self.c.debug()

        #warning lights
        wlr = WarningLightComponent(self, name=str(0), width=1/3,
                            on_colour=COLOUR_GREEN, off_colour=BACKGROUND_COLOUR, state=1)
        wll = WarningLightComponent(self, name=str(1), width=1/3,
                            on_colour=COLOUR_RED,   off_colour=BACKGROUND_COLOUR, state=0)
        warning_components = {'warning_left':wll, 'warning_right':wlr}
        
        scale_prop = 0.2

        #warning light widget
        self.warning_light_widget = CanvasWidget(self, components=warning_components)
        self.c.components['warning_light_widget'] = self.warning_light_widget
        self.c.layout_manager.fill('warning_light_widget', 'X')
        self.c.layout_manager.split('warning_light_widget', 'Y', scale_prop)

        #scale widget
        self.scale_widget = CanvasWidget(self, padding=PADDING, inner_sep=self.content_width/(len(SYSTEM_MONITOR_SCALE_POSITIONS)*3))
        self.c.components['scale_widget'] = self.scale_widget
        self.c.layout_manager.fill('scale_widget', 'X')
        self.c.layout_manager.split('scale_widget', 'Y', 1-scale_prop)

        #place warning lights
        self.warning_light_widget.layout_manager.anchor('warning_left', 'E')
        self.warning_light_widget.layout_manager.fill('warning_left', 'Y')
        self.warning_light_widget.layout_manager.anchor('warning_right', 'W')
        self.warning_light_widget.layout_manager.fill('warning_right', 'Y')
        
        for i in range(len(SYSTEM_MONITOR_SCALE_POSITIONS)):
            scale = ScaleComponent(self, name=str(i))
            scale.slide(SYSTEM_MONITOR_SCALE_POSITIONS[i])
            self.scale_widget.components[str(i)] = scale

            self.scale_widget.layout_manager.fill(str(i), 'Y')
            self.scale_widget.layout_manager.split(str(i), 'X')

        
        self.scale_widget.debug()
        self.warning_light_widget.debug()
