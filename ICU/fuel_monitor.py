import tkinter as tk
import random

from .constants import BACKGROUND_COLOUR, FUEL_TANK_LINE_THICKNESS, FUEL_TANK_LINE_COLOUR, COLOUR_GREEN, COLOUR_RED
from .constants import PUMP_HEIGHT, PUMP_WIDTH, OUTLINE_COLOUR, OUTLINE_WIDTH, PUMP_EVENT_RATE, PUMP_FLOW_RATE, PUMP_FAIL_SCHEDULE
from .constants import WARNING_OUTLINE_COLOUR, WARNING_OUTLINE_WIDTH


from . import event

from .event import Event, EventCallback, EVENT_SINKS

from .component import Component, CanvasWidget, SimpleComponent, BoxComponent, LineComponent


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

class FuelTank(EventCallback, Component, CanvasWidget):

    def __init__(self, canvas, x, y, width, height, capacity, fuel, name):
        super(FuelTank, self).__init__(canvas, x=x, y=y, width=width, height=height, background_colour=BACKGROUND_COLOUR)

        EventCallback.register(self, name)
        Component.register(self, name)

        self.capacity = capacity
        self.fuel = fuel

        fh = (self.fuel / self.capacity) * height
        self.components['fuel'] = BoxComponent(canvas, x=x, y=y+height-fh, width=width, height=fh, colour=COLOUR_GREEN, outline_thickness=0)
        self.components['outline'] = BoxComponent(canvas, x=x, y=y, width=width, height=height, outline_thickness=FUEL_TANK_LINE_THICKNESS, outline_colour=FUEL_TANK_LINE_COLOUR)
       
    def sink(self, event):
        if event.args[1] == EVENT_NAME_HIGHLIGHT:
            self.highlight(event.args[2])
        else:
            raise ValueError("{0} received invalid event: {1}".format(self.name, event)) #???

    def update(self, dfuel):
        self.fuel = min(max(self.fuel + dfuel, 0), self.capacity)
        
        fh = (self.fuel / self.capacity) * self.height
        self.components['fuel'].y = self.y + self.height - fh
        self.components['fuel'].height = fh


        
    def highlight(self, state):
        self.canvas.itemconfigure(self.highlight_rect, state=('hidden', 'normal')[state])

class FuelTankInfinite(FuelTank):

    def __init__(self, *args, **kwargs):
        super(FuelTankInfinite, self).__init__(*args, **kwargs)

    def update(self, dfuel):
        pass

class Pump(EventCallback, Component, CanvasWidget):

    ON_COLOUR = COLOUR_GREEN
    OFF_COLOUR = BACKGROUND_COLOUR
    FAIL_COLOUR = COLOUR_RED
    COLOURS = [ON_COLOUR, OFF_COLOUR, FAIL_COLOUR]

    def __init__(self, canvas, x, y, width, height, tank1, tank2, text, initial_state=1):
        self.__state = initial_state
        
        super(Pump, self).__init__(canvas, x=x, y=y, width=width, height=height, background_colour=Pump.COLOURS[self.__state], outline_thickness=OUTLINE_WIDTH)

        name = "{0}{1}".format(tank1.name.split(':')[1], tank2.name.split(':')[1])
        EventCallback.register(self, name)
        Component.register(self, name)

        #parent.pumps[self.name] = self
        self.__state = initial_state
        self.tank1 = tank1
        self.tank2 = tank2

        self.bind("<Button-1>", self.click_callback) #bind mouse events
        self.front()

        self.generator = PumpEventGenerator(self, flow_rate=PUMP_FLOW_RATE[self.name.split(":")[1]], event_rate=PUMP_EVENT_RATE)
 
    @property
    def name(self):
        return self._Component__name

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, value):
        self.__state = value
        self.background_colour = Pump.COLOURS[value]

    def highlight(self, state):
        self.highlight_state = state
        self.canvas.itemconfigure(self.highlight_rect, state=('hidden', 'normal')[state])

    def click_callback(self, *args):
        print('click')
        if self.state == 2: #the pump has failed
            self.source('click') #notify global
            return

        self.state = abs(self.__state - 1)
        (self.generator.start, self.generator.stop)[self.state]()
        self.source('click') #notify global

    def sink(self, event):
        if event.args[1] == EVENT_NAME_TRANSFER:
            self.tank1.update(-event.args[2])
            self.tank2.update(event.args[2])
        elif event.args[1] == EVENT_NAME_FAIL:
            self.state = 2
        elif event.args[1] == EVENT_NAME_REPAIR:
            self.state = 1
        elif event.args[1] == EVENT_NAME_HIGHLIGHT:
            self.highlight(event.args[2])

#TODO move this somewhere more appropriate?
def pump_rect(x,y):
    pw2 = PUMP_WIDTH/2
    ph2 = PUMP_HEIGHT/2
    return (x - pw2, y - ph2, pw2*2, ph2*2)

class Wing(CanvasWidget):
    
    def __init__(self, canvas, small_tank_name, med_tank_name, big_tank_name):
        super(Wing, self).__init__(canvas)

        width = height = 1 #everything will scale relative to the super widget

        #create full tanks
        fts = width / 4

        ftw_small = width / 6
        ftw_med = ftw_small * 1.4
        ftw_large = ftw_small * 2

        fth = height / 3
        margin = 0.05 #using padding here is a bit too tricky, maybe update TODO

        self.components['tank1'] = FuelTank(canvas, fts - ftw_small/2, height - margin - fth, ftw_small, fth, 1000, 100, small_tank_name)
        self.components['tank2'] = FuelTankInfinite(canvas, 3 * fts - ftw_med/2, height - margin - fth, ftw_med, fth, 2000, 1000, med_tank_name)
        self.components['tank3'] = FuelTank(canvas, 2 * fts - ftw_large/2, margin, ftw_large, fth, 3000, 1000, big_tank_name)

        self.components['link'] = BoxComponent(canvas, fts, margin + fth/2, 2 * fts, height-2*margin - fth, outline_thickness=OUTLINE_WIDTH)
        
        #create pumps
        cx = (fts + ftw_small/2)
        ex = (3 * fts - ftw_med/2)
        ecx = (cx + ex) / 2
        ecy = height - margin - fth / 2

        pw = width / 16
        ph = height / 20

        self.components['pump21'] = Pump(canvas, ecx - pw/2, ecy - ph/2, pw, ph, self.components['tank2'], self.components['tank1'], "<")
        self.components['pump13'] = Pump(canvas, fts - pw/2, height/2 - ph/2, pw, ph, self.components['tank1'], self.components['tank3'], '^')
        self.components['pump23'] = Pump(canvas, 3 * fts - pw/2, height /2 - ph/2, pw, ph, self.components['tank2'], self.components['tank3'], '^')
        self.components['link'].back()
   
class FuelWidget(tk.Canvas):

    def __init__(self, canvas, width, height):
        super(FuelWidget, self).__init__(canvas, width=width, height=height, bg=BACKGROUND_COLOUR)

        self.tanks = {}
        self.pumps = {}

        canvas = self #TODO

        c = CanvasWidget(canvas,width=width, height=height, outline_thickness=0)

        self.wing_left = Wing(self, small_tank_name="C",
                                med_tank_name="E", big_tank_name="A")
        self.wing_right = Wing(self, small_tank_name="D",
                               med_tank_name="F", big_tank_name="B")
        

        c.components['wl'] = self.wing_left
        c.components['wr'] = self.wing_right

        c.layout_manager.fill('wl', 'Y')
        c.layout_manager.fill('wr', 'Y')
        c.layout_manager.split('wl', 'X', .5)
        c.layout_manager.split('wr', 'X', .5)

        #c.debug()
        #self.wing_left.debug()

        #self.wing_left.components['tank1'].debug()

        
        '''
        self.wing_right.move(width/2, 0)

        (ax, ay) = self.tanks['A'].center
        (aw, ah) = self.tanks['A'].size

        (bx, by) = self.tanks['B'].center
        (bw, bh) = self.tanks['B'].size

        self.line_AB = self.create_line(ax+aw/2,ay-ah/6,bx-bw/2,by-bh/6, width=OUTLINE_WIDTH)
        self.line_BA = self.create_line(ax+aw/2,ay+ah/6,bx-bw/2,by+bh/6, width=OUTLINE_WIDTH)

        self.pumpAB = Pump(self, pump_rect((ax+bx)/2, ay-ah/6), self.tanks['A'], self.tanks['B'], ">")
        self.pumpBA = Pump(self, pump_rect((ax+bx)/2, ay+ah/6), self.tanks['B'], self.tanks['A'], "<")
        '''


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