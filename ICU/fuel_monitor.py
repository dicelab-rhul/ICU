import tkinter as tk
import random

from .constants import BACKGROUND_COLOUR, FUEL_TANK_LINE_THICKNESS, FUEL_TANK_LINE_COLOUR, COLOUR_GREEN, COLOUR_RED
from .constants import PUMP_HEIGHT, PUMP_WIDTH, OUTLINE_COLOUR, OUTLINE_WIDTH

from .event import Event, EventCallback, EVENT_SINKS




class FuelTank:

    def __init__(self, canvas, rect, capacity, fuel):
        self.canvas = canvas
        self.capacity = capacity
        self.fuel = fuel
        #(0,0)
        # (x1,y1)|
        #  |     |
        #  |     |
        #  |_____(x2,y2)
        self.rect = (min(rect[0], rect[2]), min(rect[1], rect[3]), max(rect[0], rect[2]), max(rect[1], rect[3]))

        fuel_y1 = rect[3] - (self.fuel / self.capacity) * (self.rect[3] - self.rect[1])
        self.canvas_background = self.canvas.create_rectangle(*self.rect, fill=BACKGROUND_COLOUR, width=0)
        self.canvas_fuel = self.canvas.create_rectangle(self.rect[0], fuel_y1, self.rect[2], self.rect[3], fill=COLOUR_GREEN, width=0)
        self.canvas_rect = self.canvas.create_rectangle(*self.rect, outline=FUEL_TANK_LINE_COLOUR, width=FUEL_TANK_LINE_THICKNESS)

    def update(self, dfuel):
        self.fuel += dfuel
        fuel_y1 = self.rect[3] - (self.fuel / self.capacity) * (self.rect[3] - self.rect[1]) 
        rect = (self.rect[0], fuel_y1, self.rect[2], self.rect[3])
        self.canvas.coords(self.canvas_fuel, *rect)

class Pump(EventCallback, tk.Frame):

    ON_COLOUR = COLOUR_GREEN
    OFF_COLOUR = BACKGROUND_COLOUR
    FAIL_COLOUR = COLOUR_RED
    COLOURS = [ON_COLOUR, OFF_COLOUR, FAIL_COLOUR]

    def __init__(self, parent, name, text, initial_state=1):
        super(EventCallback, self).__init__()
        super(Pump, self).__init__(parent, height=PUMP_HEIGHT, width=PUMP_WIDTH,
                                    highlightbackground=OUTLINE_COLOUR, highlightthickness=OUTLINE_WIDTH, borderwidth=0)
        self.register(name)
        
        self.__state = initial_state

        self.pack_propagate(0) # don't shrink
        self.label = tk.Label(self, bg=Pump.COLOURS[initial_state], text=text)
        self.label.pack(fill=tk.BOTH, expand=1)

        self.label.bind("<Button-1>", self.click_callback)

    def click_callback(self, *args):
        if self.__state == 2: #fail (nothing happens)
            #GLOBAL CALLBACK?
            pass
        else: #otherise flip the state on/off
            self.__state = abs(self.__state - 1)
            print(self.__state)
            self.label.config(bg=Pump.COLOURS[self.__state])
        
        self.source('click') #notify global

class Wing(tk.Canvas):
    
    def __init__(self, parent, width, height, small_tank_name, med_tank_name, big_tank_name):
        super(Wing, self).__init__(parent, width=width, height=height, bg='red')
        #create full tanks
        fts = width / 4
        ftw_small = width / 6
        ftw_med = ftw_small * 1.4
        ftw_large = ftw_small * 2
        fth = height / 3
        margin = 20

        self.tank1 = FuelTank(self, (fts - ftw_small/2, height - margin - fth, fts + ftw_small/2, height - margin), 2000, 1000)
        self.tank2 = FuelTank(self, (3 * fts - ftw_med/2, height - margin - fth, 3 * fts + ftw_med/2, height - margin), 2000, 1000)
        self.tank3 = FuelTank(self, (2 * fts - ftw_large/2, margin, 2*fts + ftw_large/2, margin + fth), 2000, 1000)
        
        #create pumps
        cx = (fts + ftw_small/2)
        ex = (3 * fts - ftw_med/2)
        ecx = (cx + ex) / 2
        ecy = height - margin - fth / 2

        self.rectEAC = self.create_rectangle(fts, fth, 3 * fts , ecy, width=OUTLINE_WIDTH) #connects pumps to tanks
        self.tag_lower(self.rectEAC)

        self.pump21 = Pump(self, '{0}{1}'.format(med_tank_name, small_tank_name), "<")
        self.pump21.pack()
        self.create_window(ecx, ecy, window=self.pump21)

        self.pump13 = Pump(self, '{0}{1}'.format(small_tank_name, big_tank_name), '^')
        self.pump13.pack()
        self.create_window(fts, height - margin - fth - PUMP_HEIGHT, window=self.pump13)
        
        self.pump23 = Pump(self, '{0}{1}'.format(med_tank_name, big_tank_name), '^')
        self.pump23.pack()
        self.create_window(3 * fts, height - margin - fth - PUMP_HEIGHT, window=self.pump23)


class FuelWidget(tk.Canvas):

    def __init__(self, parent, width, height):
        super(FuelWidget, self).__init__(parent, width=width, height=height, bg='white')

        self.wing_left = Wing(self, width / 2, height, small_tank_name="C",
                                med_tank_name="E", big_tank_name="A")
        self.wing_left_window = self.create_window(width/4, height/2, window=self.wing_left)

        self.wing_right = Wing(self, width / 2, height, small_tank_name="D",
                                med_tank_name="F", big_tank_name="B")
        self.wing_right_window = self.create_window(3*width/4, height/2, window=self.wing_right)