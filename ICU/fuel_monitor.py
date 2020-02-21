import tkinter as tk
import random

from .constants import BACKGROUND_COLOUR, FUEL_TANK_LINE_THICKNESS, FUEL_TANK_LINE_COLOUR, COLOUR_GREEN, COLOUR_RED
from .constants import PUMP_HEIGHT, PUMP_WIDTH, OUTLINE_COLOUR, OUTLINE_WIDTH, PUMP_EVENT_RATE, PUMP_FLOW_RATE, PUMP_FAIL_SCHEDULE

from . import event

from .event import Event, EventCallback, EVENT_SINKS

from pprint import pprint

class FuelTank:

    def __init__(self, canvas, rect, capacity, fuel, name):
        self.canvas = canvas
        self.name = name
        self.canvas.tanks[name] = self

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

    def move(self, dx, dy):
        self.canvas.move(self.canvas_background, dx, dy)
        self.canvas.move(self.canvas_fuel, dx, dy)
        self.canvas.move(self.canvas_rect, dx, dy)
        self.rect = (self.rect[0] + dx, self.rect[1] + dy, self.rect[2] + dx, self.rect[3] + dy)

    def update(self, dfuel):
        self.fuel = min(max(self.fuel + dfuel, 0), self.capacity)
        fuel_y1 = self.rect[3] - (self.fuel / self.capacity) * (self.rect[3] - self.rect[1]) 
        rect = (self.rect[0], fuel_y1, self.rect[2], self.rect[3])
        self.canvas.coords(self.canvas_fuel, *rect) #this should be synchronised
        
    @property
    def center(self):
        return ((self.rect[2] + self.rect[0])/2, (self.rect[3] + self.rect[1])/2)

    @property
    def width(self):
        return self.rect[2] - self.rect[0]

    @property
    def height(self):
        return self.rect[3] - self.rect[1]

    @property
    def size(self):
        return self.width, self.height

class FuelTankInfinite(FuelTank):

    def __init__(self, *args, **kwargs):
        super(FuelTankInfinite, self).__init__(*args, **kwargs)

    def update(self, dfuel):
        pass

class PumpEventGenerator:

    def __init__(self, pump, flow_rate=100, event_rate=1):
        '''
            Event Generator for pumps.
            Arguments:
                pump: that is transfering fuel between two tanks.
                flow: fuel transfer per second. 
                event_rate: number of events per second;
        '''
        super(PumpEventGenerator, self).__init__()
        self.pump = pump
        self.flow_rate = flow_rate
        self.event_rate = event_rate
        self.on = False
        self.pump_name = '{0}:{1}'.format(Pump.__name__, self.pump.name)
        event.event_scheduler.schedule(self.fail(), sleep=PUMP_FAIL_SCHEDULE, repeat=True)


    def start(self):
        self.on = True
        event.event_scheduler.schedule(self.transfer(), sleep=int(1000/self.event_rate), repeat=True)

    def stop(self):
        self.on = False

    def fail(self):
        while True:
            if self.pump._Pump__state == 2:
                yield Event(self.pump_name, 'repair')
            else:
                self.stop()
                yield Event(self.pump_name, 'fail')


    def transfer(self):
        while self.on:
            flow = self.flow_rate / self.event_rate
            if self.pump.tank1.fuel == 0 or self.pump.tank2.fuel == self.pump.tank2.capacity:
                flow = 0
            yield Event(self.pump_name, 'transfer', flow)

class Pump(EventCallback, tk.Frame):

    ON_COLOUR = COLOUR_GREEN
    OFF_COLOUR = BACKGROUND_COLOUR
    FAIL_COLOUR = COLOUR_RED
    COLOURS = [ON_COLOUR, OFF_COLOUR, FAIL_COLOUR]

    def __init__(self, parent, tank1, tank2, text, initial_state=1):
        super(EventCallback, self).__init__()
        super(Pump, self).__init__(parent, height=PUMP_HEIGHT, width=PUMP_WIDTH,
                                    highlightbackground=OUTLINE_COLOUR, highlightthickness=OUTLINE_WIDTH, borderwidth=0)
        
        self.name = "{0}{1}".format(tank1.name, tank2.name)
        self.register(self.name)

        parent.pumps[self.name] = self
        
        self.__state = initial_state
        self.tank1 = tank1
        self.tank2 = tank2

        self.pack_propagate(0) # don't shrink
        self.label = tk.Label(self, bg=Pump.COLOURS[initial_state], text=text)
        self.label.pack(fill=tk.BOTH, expand=1)

        self.label.bind("<Button-1>", self.click_callback)

        self.generator = PumpEventGenerator(self, flow_rate=PUMP_FLOW_RATE[self.name], event_rate=PUMP_EVENT_RATE) #transfer 10 fuel every 1 seconds

    def click_callback(self, *args):
        if self.__state == 2: #fail (nothing happens)
            #GLOBAL CALLBACK?
            pass
        else: #otherise flip the state on/off
            self.__state = abs(self.__state - 1)
            self.label.config(bg=Pump.COLOURS[self.__state])
            (self.generator.start, self.generator.stop)[self.__state]()
        
        self.source('click') #notify global

    def sink(self, event):
        if len(event.args) == 3:
            self.tank1.update(-event.args[2])
            self.tank2.update(event.args[2])
        elif len(event.args) == 2:    
            if event.args[1] == 'fail':
                self.__state = 2
            elif event.args[1] == 'repair':
                self.__state = 1
            self.label.config(bg=Pump.COLOURS[self.__state])

class Wing:
    
    def __init__(self, parent, width, height, small_tank_name, med_tank_name, big_tank_name):
        super(Wing, self).__init__()
        #create full tanks
        self.parent = parent

        fts = width / 4
        ftw_small = width / 6
        ftw_med = ftw_small * 1.4
        ftw_large = ftw_small * 2
        fth = height / 3
        margin = 20

        self.tank1 = FuelTank(parent, (fts - ftw_small/2, height - margin - fth, fts + ftw_small/2, height - margin), 1000, 500, small_tank_name)
        self.tank2 = FuelTankInfinite(parent, (3 * fts - ftw_med/2, height - margin - fth, 3 * fts + ftw_med/2, height - margin), 2000, 1000, med_tank_name)
        self.tank3 = FuelTank(parent, (2 * fts - ftw_large/2, margin, 2*fts + ftw_large/2, margin + fth), 3000, 1000, big_tank_name)
        
        #create pumps
        cx = (fts + ftw_small/2)
        ex = (3 * fts - ftw_med/2)
        ecx = (cx + ex) / 2
        ecy = height - margin - fth / 2

        self.line_rect = parent.create_rectangle(fts, fth, 3 * fts , ecy, width=OUTLINE_WIDTH) #connects pumps to tanks
        parent.tag_lower(self.line_rect)

        self.pump21 = Pump(parent, self.tank2, self.tank1, "<")
        self.pump21.pack()
        self.pump21_w = parent.create_window(ecx, ecy, window=self.pump21)

        self.pump13 = Pump(parent, self.tank1, self.tank3, '^')
        self.pump13.pack()
        self.pump13_w = parent.create_window(fts, height - margin - fth - PUMP_HEIGHT, window=self.pump13)
        
        self.pump23 = Pump(parent, self.tank2, self.tank3, '^')
        self.pump23.pack()
        self.pump23_w = parent.create_window(3 * fts, height - margin - fth - PUMP_HEIGHT, window=self.pump23)

    def move(self, dx, dy):
        self.parent.move(self.line_rect, dx, dy)
        self.tank1.move(dx, dy)
        self.tank2.move(dx, dy)
        self.tank3.move(dx, dy)

        self.parent.move(self.pump21_w, dx, dy)
        self.parent.move(self.pump13_w, dx, dy)
        self.parent.move(self.pump23_w, dx, dy)
   
class FuelWidget(tk.Canvas):

    def __init__(self, parent, width, height):
        super(FuelWidget, self).__init__(parent, width=width, height=height, bg='white')

        self.tanks = {}
        self.pumps = {}

        self.wing_left = Wing(self, width / 2, height, small_tank_name="C",
                                med_tank_name="E", big_tank_name="A")

        self.wing_right = Wing(self, width / 2, height, small_tank_name="D",
                                med_tank_name="F", big_tank_name="B")
        
        self.wing_right.move(width/2, 0)

        (ax, ay) = self.tanks['A'].center
        (aw, ah) = self.tanks['A'].size

        (bx, by) = self.tanks['B'].center
        (bw, bh) = self.tanks['B'].size

        self.line_AB = self.create_line(ax+aw/2,ay-ah/6,bx-bw/2,by-bh/6, width=OUTLINE_WIDTH)
        self.line_BA = self.create_line(ax+aw/2,ay+ah/6,bx-bw/2,by+bh/6, width=OUTLINE_WIDTH)

        self.pumpAB = Pump(self, self.tanks['A'], self.tanks['B'], ">")
        self.pumpAB.pack()
        self.pumpAB_w = self.create_window((ax+bx)/2, ay-ah/6, window=self.pumpAB)
        
        self.pumpBA = Pump(self, self.tanks['B'], self.tanks['A'], "<")
        self.pumpBA.pack()
        self.pumpBA_w = self.create_window((ax+bx)/2, ay+ah/6, window=self.pumpBA)