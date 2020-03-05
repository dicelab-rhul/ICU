import tkinter as tk
import random

from .constants import BACKGROUND_COLOUR, FUEL_TANK_LINE_THICKNESS, FUEL_TANK_LINE_COLOUR, COLOUR_GREEN, COLOUR_RED
from .constants import PUMP_HEIGHT, PUMP_WIDTH, OUTLINE_COLOUR, OUTLINE_WIDTH, PUMP_EVENT_RATE, PUMP_FLOW_RATE, PUMP_FAIL_SCHEDULE
from .constants import WARNING_OUTLINE_COLOUR, WARNING_OUTLINE_WIDTH


from . import event

from .event import Event, EventCallback, EVENT_SINKS
from .component import Component


from pprint import pprint

EVENT_NAME_FAIL = "fail"
EVENT_NAME_TRANSFER = "transfer"
EVENT_NAME_REPAIR = "repair"
EVENT_NAME_HIGHLIGHT = "highlight"

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
        self.pump_name = self.pump.name
        event.event_scheduler.schedule(self.fail(), sleep=PUMP_FAIL_SCHEDULE, repeat=True)

    def start(self):
        self.on = True
        event.event_scheduler.schedule(self.transfer(), sleep=int(1000/self.event_rate), repeat=True)

    def stop(self):
        self.on = False

    def fail(self):
        while True:
            if self.pump._Pump__state == 2:
                yield Event(self.pump_name, EVENT_NAME_REPAIR)
            else:
                self.stop()
                yield Event(self.pump_name, EVENT_NAME_FAIL)

    def transfer(self):
        while self.on:
            flow = self.flow_rate / self.event_rate
            if self.pump.tank1.fuel == 0 or self.pump.tank2.fuel == self.pump.tank2.capacity:
                flow = 0
            yield Event(self.pump_name, EVENT_NAME_TRANSFER, flow)

def highlight_rect(canvas, rect):
    r = (rect[0] - WARNING_OUTLINE_WIDTH, rect[1] - WARNING_OUTLINE_WIDTH, 
         rect[2] + WARNING_OUTLINE_WIDTH, rect[3] + WARNING_OUTLINE_WIDTH)
    return canvas.create_rectangle(*r, width=0, fill=WARNING_OUTLINE_COLOUR)



class FuelTank(EventCallback, Component):

    def __init__(self, canvas, rect, capacity, fuel, name):
        super(FuelTank, self).__init__()

        EventCallback.register(self, name)
        Component.register(self, name)

        self.canvas = canvas
        self.canvas.tanks[name] = self

        self.capacity = capacity
        self.fuel = fuel
        # (0,0)
        # (x1,y1)|
        #  |     |
        #  |     |
        #  |_____(x2,y2)
        self.rect = (min(rect[0], rect[2]), min(rect[1], rect[3]), max(rect[0], rect[2]), max(rect[1], rect[3]))
        
        self.highlight_rect = highlight_rect(self.canvas, self.rect)
        self.highlight(0) #hide highlight

        #TODO rename some of this stuff?
        fuel_y1 = rect[3] - (self.fuel / self.capacity) * (self.rect[3] - self.rect[1])
        self.canvas_background = self.canvas.create_rectangle(*self.rect, fill=BACKGROUND_COLOUR, width=0)
        self.canvas_fuel = self.canvas.create_rectangle(self.rect[0], fuel_y1, self.rect[2], self.rect[3], fill=COLOUR_GREEN, width=0)
        self.canvas_rect = self.canvas.create_rectangle(*self.rect, outline=FUEL_TANK_LINE_COLOUR, width=FUEL_TANK_LINE_THICKNESS)

    def sink(self, event):
        if event.args[1] == EVENT_NAME_HIGHLIGHT:
            self.highlight(event.args[2])
        else:
            raise ValueError("{0} received invalid event: {1}".format(self.name, event)) #???

    def move(self, dx, dy):
        self.canvas.move(self.canvas_background, dx, dy)
        self.canvas.move(self.canvas_fuel, dx, dy)
        self.canvas.move(self.canvas_rect, dx, dy)
        self.canvas.move(self.highlight_rect, dx, dy)
        self.rect = (self.rect[0] + dx, self.rect[1] + dy, self.rect[2] + dx, self.rect[3] + dy)

    def update(self, dfuel):
        self.fuel = min(max(self.fuel + dfuel, 0), self.capacity)
        fuel_y1 = self.rect[3] - (self.fuel / self.capacity) * (self.rect[3] - self.rect[1]) 
        rect = (self.rect[0], fuel_y1, self.rect[2], self.rect[3])
        self.canvas.coords(self.canvas_fuel, *rect) #this should be synchronised
        
    def highlight(self, state):
        self.canvas.itemconfigure(self.highlight_rect, state=('hidden', 'normal')[state])

    @property
    def name(self):
        return self._Component__name
    
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

class Pump(EventCallback, Component):

    ON_COLOUR = COLOUR_GREEN
    OFF_COLOUR = BACKGROUND_COLOUR
    FAIL_COLOUR = COLOUR_RED
    COLOURS = [ON_COLOUR, OFF_COLOUR, FAIL_COLOUR]

    def __init__(self, parent, rect, tank1, tank2, text, initial_state=1):
        name = "{0}{1}".format(tank1.name.split(':')[1], tank2.name.split(':')[1])

        super(Pump, self).__init__()

        EventCallback.register(self, name)
        Component.register(self, name)

        parent.pumps[self.name] = self
        
        self.__state = initial_state
        self.tank1 = tank1
        self.tank2 = tank2

        self.canvas = parent

        self.rect = (min(rect[0], rect[2]), min(rect[1], rect[3]), max(rect[0], rect[2]), max(rect[1], rect[3]))

        self.highlight_rect = highlight_rect(self.canvas, self.rect)
        self.highlight_state = 0
        self.highlight(0) #hide highlight

        self.box = self.canvas.create_rectangle(*self.rect, fill=Pump.COLOURS[initial_state], 
                                                outline=FUEL_TANK_LINE_COLOUR, width=FUEL_TANK_LINE_THICKNESS)

        self.canvas.tag_bind(self.box, "<Button-1>", self.click_callback) #bind mouse events
        self.generator = PumpEventGenerator(self, flow_rate=PUMP_FLOW_RATE[self.name.split(":")[1]], event_rate=PUMP_EVENT_RATE)
       
    @property
    def name(self):
        return self._Component__name

    def move(self, dx, dy):
        self.canvas.move(self.box, dx, dy)
        self.canvas.move(self.highlight_rect, dx, dy)
        self.rect = (self.rect[0] + dx, self.rect[1] + dy, self.rect[2] + dx, self.rect[3] + dy)

    def highlight(self, state):
        self.highlight_state = state
        self.canvas.itemconfigure(self.highlight_rect, state=('hidden', 'normal')[state])

    def click_callback(self, *args):
        if self.__state == 2: #fail (nothing happens)
            #GLOBAL CALLBACK?
            pass
        else: #otherise flip the state on/off
            self.__state = abs(self.__state - 1)
            self.canvas.itemconfig(self.box, fill=Pump.COLOURS[self.__state])
            (self.generator.start, self.generator.stop)[self.__state]()
        print(self.__state)
        self.source('click') #notify global

    def sink(self, event):
        if event.args[1] == EVENT_NAME_TRANSFER:
            self.tank1.update(-event.args[2])
            self.tank2.update(event.args[2])
        elif event.args[1] == EVENT_NAME_FAIL:
            self.__state = 2
            self.canvas.itemconfig(self.box, fill=Pump.COLOURS[self.__state])
        elif event.args[1] == EVENT_NAME_REPAIR:
            self.__state = 1
            self.canvas.itemconfig(self.box, fill=Pump.COLOURS[self.__state])
        elif event.args[1] == EVENT_NAME_HIGHLIGHT:
            self.highlight(event.args[2])

#TODO move this somewhere more appropriate?
def pump_rect(x,y):
    pw2 = PUMP_WIDTH/2
    ph2 = PUMP_HEIGHT/2
    return (x - pw2, y - ph2, x + pw2, y + ph2)

class Wing:
    
    def __init__(self, parent, width, height, small_tank_name, med_tank_name, big_tank_name):
        super(Wing, self).__init__()
        self.parent = parent

        #create full tanks
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

        self.pump21 = Pump(parent, pump_rect(ecx, ecy), self.tank2, self.tank1, "<")
        self.pump13 = Pump(parent, pump_rect(fts, height - margin - fth - PUMP_HEIGHT), self.tank1, self.tank3, '^')
        self.pump23 = Pump(parent, pump_rect(3 * fts, height - margin - fth - PUMP_HEIGHT), self.tank2, self.tank3, '^')

    def move(self, dx, dy):
        self.parent.move(self.line_rect, dx, dy)
        self.tank1.move(dx, dy)
        self.tank2.move(dx, dy)
        self.tank3.move(dx, dy)

        self.pump21.move(dx, dy)
        self.pump13.move(dx, dy)
        self.pump23.move(dx, dy)
   
class FuelWidget(tk.Canvas):

    def __init__(self, parent, width, height):
        super(FuelWidget, self).__init__(parent, width=width, height=height, bg=BACKGROUND_COLOUR)

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

        self.pumpAB = Pump(self, pump_rect((ax+bx)/2, ay-ah/6), self.tanks['A'], self.tanks['B'], ">")
        self.pumpBA = Pump(self, pump_rect((ax+bx)/2, ay+ah/6), self.tanks['B'], self.tanks['A'], "<")
 
    def highlight(self, child=None):
        if child is None:
            print("highlight self")
        elif child in self.pumps:
            print("highlight pump")
            pump = self.pumps[child]

        elif child in self.tanks:
            print("highlight tank")
        else:
            raise ValueError("Invalid child widget: {0}".format(child))