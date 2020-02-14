import tkinter as tk
import random
from types import SimpleNamespace

from . import panel
from .constants import BACKGROUND_COLOUR, OUTLINE_WIDTH, OUTLINE_COLOUR, SYSTEM_MONITOR_SCALE_BACKGROUND_COLOUR, SYSTEM_MONITOR_SCALE_BACKGROUND_COLOUR_FILL
from .constants import SYSTEM_MONITOR_SCALE_POSITIONS, COLOUR_GREEN, COLOUR_RED

from .event import Event, EventCallback, EVENT_SINKS

Y_SCALE = 1/8
X_SCALE = 1/2

NUM_SCALE_SPLIT = 11

def ScaleEventGenerator():
    scales = [s for s in EVENT_SINKS.keys() if Scale.__name__ in s]
    while True:
        r = random.randint(0, len(scales)-1)
        y = random.randint(0, 1) * 2 - 1
        yield Event(scales[r], y)

def WarningLightEventGenerator():
    warning_lights = [s for s in EVENT_SINKS.keys() if WarningLight.__name__ in s]
    while True:
        r = random.randint(0, len(warning_lights)-1)
        yield Event(warning_lights[r])
        

class Scale(EventCallback, tk.Canvas):

    def __init__(self, parent, name, height, width, **kwargs):
        super(EventCallback, self).__init__()
        super(Scale, self).__init__(parent, width=width, height=height, **kwargs, 
                                    highlightbackground=OUTLINE_COLOUR, highlightthickness=OUTLINE_WIDTH, borderwidth=0)
        self.register(name)

        self.inc = height / NUM_SCALE_SPLIT
        self.block = self.create_rectangle(0,0,width+2, self.inc*3, fill=SYSTEM_MONITOR_SCALE_BACKGROUND_COLOUR_FILL)
        for i in range(1, NUM_SCALE_SPLIT):
            self.create_line(0,self.inc*i,width+2,self.inc*i, width=OUTLINE_WIDTH)
        self.__state = 0
        self.bind("<Button-1>", self.click_callback)

    def slide(self, y):
        if 0 <= self.__state - y <= NUM_SCALE_SPLIT-3: 
            self.__state -= y
            self.move(self.block, 0, self.inc * -y)

    def sink(self, event):
        #event(name, y)
        self.slide(event.args[1])

    def click_callback(self, *args):
        #move the state towards the middle...?
        self.slide(self.__state - NUM_SCALE_SPLIT // 2 + 1)
        self.source('click')

class WarningLight(EventCallback, tk.Canvas):

    def __init__(self, parent, name, width, height, state=0, on_colour=COLOUR_GREEN, off_colour=COLOUR_RED):
        self.__state_colours = [off_colour, on_colour]
        super(EventCallback, self).__init__()
        super(WarningLight, self).__init__(parent, bg=self.__state_colours[state], width=width, height=height,
                                            highlightbackground=OUTLINE_COLOUR, highlightthickness=OUTLINE_WIDTH, borderwidth=0)
        
        self.register(name)
        
        self.__state = state
        self.name = name
        #self.create_rectangle(OUTLINE_WIDTH//2 + 1, OUTLINE_WIDTH//2 + 1, width-OUTLINE_WIDTH//2, height-OUTLINE_WIDTH//2, outline='black', width=OUTLINE_WIDTH)
        self.bind("<Button-1>", self.click_callback)

    def click_callback(self, *args):
        self.sink(None)
        self.source('click') #notify global

    def sink(self, _):
        self.__state = int(not bool(self.__state))
        self.configure(bg=self.__state_colours[self.__state])

class SystemMonitorWidget(tk.Frame):

    def __init__(self, parent, width=480, height=640):
        super(SystemMonitorWidget, self).__init__(parent, width=width, height=height, bg=BACKGROUND_COLOUR) 
        self.top_frame = tk.Frame(self, bg=BACKGROUND_COLOUR)
        self.top_frame.pack(side=tk.TOP, anchor=tk.N, fill='x', pady=20, padx=X_SCALE*10)

        self.warning_light_left = WarningLight(self.top_frame, name=str(0), width=X_SCALE * width/2, height=height * Y_SCALE,
                                                on_colour=COLOUR_GREEN, off_colour=BACKGROUND_COLOUR, state=1)
        self.warning_light_left.pack(side=tk.LEFT, padx=X_SCALE*20)

        self.warning_light_right = WarningLight(self.top_frame, name=str(1), width=X_SCALE * width/2,  height=height * Y_SCALE,
                                                on_colour=COLOUR_RED, off_colour=BACKGROUND_COLOUR, state=0)
        self.warning_light_right.pack(side=tk.RIGHT, padx=X_SCALE*20)

        self.bottom_frame = tk.Frame(self, bg=BACKGROUND_COLOUR)
        self.bottom_frame.pack(side=tk.BOTTOM, anchor=tk.S, pady=20)
        
        self.scales = []
        scale_height = height - (height * Y_SCALE)
        scale_width =  (width * (1 - X_SCALE)) / len(SYSTEM_MONITOR_SCALE_POSITIONS)

        for i in range(len(SYSTEM_MONITOR_SCALE_POSITIONS)):
            #scale_frame = tk.Frame(self.bottom_frame, bg='gray', width=scale_width, height=scale_height)
            scale = Scale(self.bottom_frame, name=str(i), bg=SYSTEM_MONITOR_SCALE_BACKGROUND_COLOUR, width=scale_width, height=scale_height)
            scale.grid(row=0, column=i, padx=X_SCALE*30)
            scale.slide(-SYSTEM_MONITOR_SCALE_POSITIONS[i])
            self.scales.append(scale)
