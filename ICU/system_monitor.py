import tkinter as tk
import random
from types import SimpleNamespace

from . import panel
from .constants import BACKGROUND_COLOUR, OUTLINE_WIDTH, OUTLINE_COLOUR, SYSTEM_MONITOR_SCALE_BACKGROUND_COLOUR, SYSTEM_MONITOR_SCALE_BACKGROUND_COLOUR_FILL
from .constants import SYSTEM_MONITOR_SCALE_POSITIONS, COLOUR_GREEN, COLOUR_RED
from .constants import WARNING_OUTLINE_COLOUR, WARNING_OUTLINE_WIDTH

#from .constants import WARNING_LIGHT_MIN_HEIGHT, WARNING_LIGHT_MIN_WIDTH

from .event import Event, EventCallback, EVENT_SINKS
from .component import Component, CanvasWidget, SimpleComponent, BoxComponent

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
        
class Scale(EventCallback, Component):

    def __init__(self, parent, name, height, width, **kwargs):
        super(Scale, self).__init__()

        self.canvas = parent   
        self.width = width
        self.height = height     
        
        EventCallback.register(self, name)
        Component.register(self, name)

        self.inc = height / NUM_SCALE_SPLIT

        self.background = self.canvas.create_rectangle(0,0,width,height,fill=SYSTEM_MONITOR_SCALE_BACKGROUND_COLOUR, width=OUTLINE_WIDTH)
        
        self.block = self.canvas.create_rectangle(0,0,width, self.inc*3, fill=SYSTEM_MONITOR_SCALE_BACKGROUND_COLOUR_FILL, width=OUTLINE_WIDTH)

        self.lines = []

        for i in range(1, NUM_SCALE_SPLIT):
            self.lines.append(self.canvas.create_line(0, self.inc*i,width,self.inc*i, width=OUTLINE_WIDTH))

        self.__state = 0

        self.canvas.tag_bind(self.block, "<Button-1>", self.click_callback)

    def move(self, dx, dy):
        self.canvas.move(self.background, dx, dy)
        self.canvas.move(self.block, dx, dy)
        for line in self.lines:
            self.canvas.move(line, dx, dy)
    
    def slide(self, y):
        if 0 <= self.__state - y <= NUM_SCALE_SPLIT-3: 
            self.__state -= y
            self.canvas.move(self.block, 0, self.inc * -y)

    def highlight(self, state):
        print("TODO highlight scale")

    def sink(self, event):
        if event.args[1] == EVENT_NAME_SLIDE:
            self.slide(event.args[2])
        elif event.args[1] == EVENT_NAME_HIGHTLIGHT:
            self.highlight(event.args[2])

    def click_callback(self, *args):
        #move the state towards the middle...?
        self.slide(self.__state - NUM_SCALE_SPLIT // 2 + 1)
        self.source(EVENT_NAME_CLICK)


class WarningLight(EventCallback, Component, BoxComponent):

    def __init__(self, canvas, name, width, height, state=0, on_colour=COLOUR_GREEN, off_colour=COLOUR_RED):
        self.__state_colours = [off_colour, on_colour]
        self.__state = state
        colour = self.__state_colours[self.__state]

        super(WarningLight, self).__init__(canvas, width, height, colour=colour, outline_thickness=OUTLINE_WIDTH, outline_colour=OUTLINE_COLOUR)
        
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
        return self.width - 2 * PADDING
    
    @property
    def content_height(self):
        return self.height - 2 * PADDING

    def __init__(self, parent, width=480, height=640):
        super(SystemMonitorWidget, self).__init__(parent, width=width, height=height, bg=BACKGROUND_COLOUR) 

        self.width = width
        self.height = height

        wl_content_height = self.content_height / 6
        sc_content_height = self.content_height - wl_content_height - PADDING

        wl_width = self.content_width / 3
        wl_height = wl_content_height

        #warning_lights = {'left':, 'right'}

        #warning lights
        wlr = WarningLight(self, name=str(0), width=wl_width, height=wl_height,
                            on_colour=COLOUR_GREEN, off_colour=BACKGROUND_COLOUR, state=1)
        wll = WarningLight(self, name=str(1), width=wl_width,  height=wl_height,
                            on_colour=COLOUR_RED,   off_colour=BACKGROUND_COLOUR, state=0)
        warning_components = {'warning_left':wll, 'warning_right':wlr}

        self.warning_light_widget = CanvasWidget(self, self.content_width, self.content_height / 6, components=warning_components)
        self.warning_light_widget.move(PADDING, PADDING)

        self.warning_light_widget.anchor('warning_left', 'E')
        self.warning_light_widget.anchor('warning_right', 'W')

        self.scale_widget = CanvasWidget(self, self.content_width, self.content_width - self.warning_light_widget.height - PADDING)
        self.scale_widget.move(PADDING, self.warning_light_widget.height + 2 * PADDING)
        
        


       


                                        


    '''
        self.scales = []

        scale_width =  (self.content_width / 1.8) / len(SYSTEM_MONITOR_SCALE_POSITIONS)
        scale_height = height

        inc = self.content_width / len(SYSTEM_MONITOR_SCALE_POSITIONS)

        for i in range(len(SYSTEM_MONITOR_SCALE_POSITIONS)):
            #scale_frame = tk.Frame(self.bottom_frame, bg='gray', width=scale_width, height=scale_height)
            scale = Scale(self, name=str(i), bg=SYSTEM_MONITOR_SCALE_BACKGROUND_COLOUR, width=scale_width, height=scale_height)
            
            #scale.move(PADDING + scale.width/2 + i * inc, )


            scale.slide(-SYSTEM_MONITOR_SCALE_POSITIONS[i])
            self.scales.append(scale)
    '''