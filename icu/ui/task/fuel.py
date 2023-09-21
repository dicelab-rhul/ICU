


import math
from ...event2 import DELIMITER
from ..commands import INPUT_MOUSEDOWN, INPUT_MOUSEUP, INPUT_MOUSECLICK
from ..draw import draw_rectangle, draw_line, draw_arrow
from ..constants import *
from ..widget import Widget, castPoint, property_event, cosmetic_options, gettable_properties, settable_properties
from ..utils.math import Point

from enum import Enum
import time


# TODO inherit from parent decorator? 
class FuelWing(Widget):
    def __init__(self, wing):
        super().__init__(f"Wing{wing}")
        self._wing = wing - 1
    @property
    def event_frequency(self):
        return self.parent.event_frequency
    @property
    def size(self):
        s = self.parent.size
        return Point(s[0] / 2, s[1])
    @property
    def position(self):
        return Point(self._wing * self.size[0], 0)
    @property
    def padding(self):
        return self.parent.padding
    @property
    def line_width(self):
        return self.parent.line_width
    @property
    def background_color(self):
        return self.parent.background_color
    @property
    def line_color(self):
        return self.parent.line_color
    @property
    def fuel_tanks(self): # main, left, right
        return list(dict(sorted(self.children.items())).values())[:3]
    @property # this widget is not addressable
    def address(self):
        return self.parent.address

@cosmetic_options(
    background_color = COLOR_GREY,
    goal_color = COLOR_GREEN,
    fail_color = COLOR_RED,
    line_color = LINE_COLOR,
)
class FuelTank(Widget):

    @settable_properties('fuel_level', 'capacity')
    @gettable_properties('fuel_level', 'capacity')
    def __init__(self, name, fuel_level, capacity):
        super().__init__(name)
        self._fuel_level = fuel_level
        self._capacity = capacity
        self._fuel_color = self.goal_color

    @property_event
    def fuel_level(self):
        return self._fuel_level
    @fuel_level.setter
    def fuel_level(self, value):
        self._fuel_level = min(max(value, 0), self.capacity)
    @property_event
    def capacity(self):
        return self._capacity
    @capacity.setter
    def capacity(self, value):
        self._capacity = max(value, 0)

    def draw(self, window):
        fuel_prop = self.fuel_level / self.capacity
        size = Point(self.size[0], self.size[1] * fuel_prop)
        position = self.canvas_position + self.size - size

        if self.in_failure():
            self._fuel_color = self.fail_color
        else:
            self._fuel_color = self.goal_color
        
        draw_rectangle(window, position = self.canvas_position, size = self.size, color=self.background_color, fill=True)
        draw_rectangle(window, position = position, size = size, color=self._fuel_color, fill=True)
        draw_rectangle(window, position = self.canvas_position, size = self.size, line_width = self.parent.line_width, color=self.line_color)
    
    def in_failure(self):
        return False # only applies to the main tank

    def _get_pump_position(self, tank2, pump):
        raise NotImplementedError()
    
    def _get_pump_arrow_angle(self, tank2):
        raise NotImplementedError() 

@cosmetic_options(
    fuel_level_protrusion = FUELTANKMAIN_FUEL_LEVEL_PROTRUSION
)
class FuelTankMain(FuelTank):
    @settable_properties('failure_interval')
    def __init__(self, name, fuel_level, capacity, failure_interval):
        super().__init__(name, fuel_level, capacity)
        self._failure_interval = failure_interval

    @property_event
    def failure_interval(self):
        return self._failure_interval

    @failure_interval.setter
    def failure_interval(self, value):
        assert isinstance(value, (tuple, list, Point))
        self._failure_interval = (min(value), max(value)) 

    def draw(self, window):
        failure_center = sum(self.failure_interval) / 2
        px = self.canvas_position[0]
        ix = self.fuel_level_protrusion # change this?
        cy = self.canvas_position[1] + self.size[1] * failure_center
        iy = (self.failure_interval[1] - self.failure_interval[0]) * self.size[1]
        draw_line(window, start_position = (px - ix, cy), end_position = (px + self.size[0] + ix -1, cy), width = int(iy), color=COLOR_LIGHT_BLUE)
        draw_line(window, start_position = (px - ix, cy), end_position = (px + self.size[0] + ix -1, cy), width = 4, color=COLOR_BLUE)
        super().draw(window)

    def in_failure(self):
        interval = Point(self.failure_interval) * self.capacity
        return self.fuel_level < interval[0] or self.fuel_level > interval[1]

    @property
    def position(self):
        ps, s = self.parent.size, self.size
        return Point(ps[0] / 2 - s[0] / 2, self.parent.padding[1])
    @property
    def size(self):
        return Point(self.parent.size[0] / 3, self.parent.size[1] / 3)
    
    def get_connecting_line(self, tank2):
        if isinstance(tank2, FuelTankMain):
            x1 = self.canvas_position[0] + self.size[0] / 2
            x2 = tank2.canvas_position[0] + tank2.size[0] / 2
            y = self.canvas_position[1] + self.size[1] * (self.parent._wing + 1) / 4 
            return Point(x1, y), Point(x2, y)
        else:
            raise ValueError(f"No fuel line connection between {self} and {tank2}.")

    def _get_pump_position(self, tank2, pump):
        w = self.parent._wing
        y = self.position[1] + self.size[1] * (w + 1) / 4 
        x = self.position[0] + (self.size[0] * (1-w)) # either side of the correct tank
        x -= ((w*2) - 1) * self.size[0]/2
        return Point(x,y) - pump.size / 2
        
    def _get_pump_arrow_angle(self, tank2):
        d = (self.canvas_position[0] - tank2.canvas_position[0])
        return ((d/abs(d)) + 1) * 90

class FuelTankLeft(FuelTank):
    @property
    def position(self):
        ps, s = self.parent.size, self.size
        return Point(self.parent.padding[0], ps[1] - s[1] - self.parent.padding[1])
    @property
    def size(self):
        return Point(self.parent.size[0] / 6, self.parent.size[1] / 3)

    def _get_pump_position(self, tank2, pump):
        if isinstance(tank2, FuelTankMain):
            x = self.position[0] + self.size[0] / 2
            y = self.position[1] - (self.position[1] - (tank2.position[1] + tank2.size[1])) / 2
            return Point(x, y) - pump.size/2
        else:
            raise ValueError(f"Invalid tank {type(self).__name__} for {type(self).__name__}, tanks do not share a {Pump.__name__}.") # unreachable...
        
    def _get_pump_arrow_angle(self, tank2):
        return 90

class FuelTankRight(FuelTank):
    @property
    def position(self):
        ps, s = self.parent.size, self.size
        return Point(ps[0] - s[0] - self.parent.padding[0], ps[1] - s[1] - self.parent.padding[1])
    @property
    def size(self):
        return Point(self.parent.size[0] / 4, self.parent.size[1] / 3)

    def _get_pump_position(self, tank2, pump):
        if isinstance(tank2, FuelTankMain):
            x = self.position[0] + self.size[0] / 2
            y = self.position[1] - (self.position[1] - (tank2.position[1] + tank2.size[1])) / 2
            return Point(x, y) - pump.size/2
        elif isinstance(tank2, FuelTankLeft):
            x = (tank2.position[0] + tank2.size[0] / 2) + (self.position[0] - tank2.position[0]) / 2
            y = self.position[1] + self.size[1] /2
            return Point(x,y) - pump.size/2
        else:
            raise ValueError(f"Invalid tank {type(self).__name__} for {type(self).__name__}, tanks do not share a {Pump.__name__}.") # unreachable...
        
    def _get_pump_arrow_angle(self, tank2):
        if isinstance(tank2, FuelTankMain):
            return 90
        elif isinstance(tank2, FuelTankLeft):
            return 180
        else:
            raise ValueError(f"Invalid tank {type(self).__name__} for {type(self).__name__}, tanks do not share a {Pump.__name__}.") # unreachable...
        
class PumpState(Enum):
    OFF = 0
    ON = 1
    FAIL = 2

    @classmethod
    def get(cls, index):
        return list(cls)[index]

@cosmetic_options(
    off_color = COLOR_GREY,
    on_color = COLOR_GREEN,
    fail_color = COLOR_RED,
    line_color = LINE_COLOR,
    arrow_color = LINE_COLOR,
    arrow_fill_head = True,
    scale = (0.8, 0.8)
)
class Pump(Widget):
    
    @settable_properties('state', 'fail', 'flow_speed')
    @gettable_properties('state', 'fail', 'flow_speed')
    def __init__(self, tank1, tank2, flow_speed):
        super().__init__(f"PUMP{tank1.name[-1] + tank2.name[-1]}", clickable=True)
        self.tank1 = tank1
        self.tank2 = tank2
        self._state =  PumpState.OFF # 0 clickable, 1 on, 2 failure
        self._flow_speed = flow_speed
        self._last_event_time = time.time()

    @property_event
    def flow_speed(self):
        return self._flow_speed
    
    @flow_speed.setter
    def flow_speed(self, value):
        self._flow_speed = max(value, 0)

    @property_event
    def state(self):
        return self._state
    
    @property
    def fail(self):
        return int(self.state == PumpState.FAIL)
    
    @fail.setter
    def fail(self, value):
        self.state = PumpState.get((value % 2)*2)

    @state.setter
    def state(self, value):
        if isinstance(value, int):
            self._state = PumpState.get(value)
        elif isinstance(value, PumpState):
            self._state = value
        else:
            raise ValueError(f"Failed to set `state`, value {value} must of type {PumpState} or int.")

    @property
    def position(self):
        # yes its weird to off load this to the fuel tanks, but it avoids a large conditional statement for type checking...
        return self.tank1._get_pump_position(self.tank2, self)

    @property
    def _colors(self):
        return [self.off_color, self.on_color, self.fail_color]

    @property
    def size(self):
        return Point(self.scale) * self.tank1.size[1] / 4
    
    def draw(self, window):
        should, dif = self._should_transfer_fuel()
        if should:
            self.transfer(dif * self.flow_speed)

        draw_rectangle(window, position = self.canvas_position, size = self.size, color=self._colors[self.state.value], fill=True)
        draw_rectangle(window, position = self.canvas_position, size = self.size, color=self.line_color, line_width = self.parent.line_width)
        # draw arrow
        angle = self.tank1._get_pump_arrow_angle(self.tank2)
        draw_arrow(window, start_position = self.canvas_position + self.size/2, length=self.size[0] / 4, 
                   color=self.arrow_color, angle=angle, head_only=True, fill_head=self.arrow_fill_head, head_length=self.size[0] / 2)
        super().draw(window)

    def on_mouse_click(self, event):
        if self.state == PumpState.OFF:
            self.state = PumpState.ON
            self._last_event_time = time.time()
        elif self.state == PumpState.ON:
            self.state = PumpState.OFF
 
    def transfer(self, amount):
        f1 = self.tank1.fuel_level
        f2 = self.tank2.fuel_level
        # move `amount` from f1 to f2
        d1 = abs(max(f1 - amount, 0) - f1)
        d2 = amount - max(((f2 + amount) - self.tank2.capacity), 0) 
        d = min(d1, d2)
        if d > 0:
            self.tank1.fuel_level -= d
            self.tank2.fuel_level += d
        else:
            self.state = PumpState.OFF
        
    def _should_transfer_fuel(self):
        if self.state == PumpState.ON:
            current_time = time.time()
            dif = current_time - self._last_event_time
            if dif >= (1 / self.parent.event_frequency):
                self._last_event_time = current_time
                return (True, dif)
            return (False, dif)
        else:
            return (False, None)
    
@cosmetic_options(
    position = Point(50,50),
    size = Point(780, 480),
    padding = Point(1.5*PADDING, PADDING),
    background_color = COLOR_GREY,
    line_color = COLOR_BLACK,
    line_width = LINE_WIDTH,
)
class FuelTask(Widget): 

    def __init__(self, event_frequency=30):
        super().__init__(FUELTASK, clickable=False)
        self._wings = [FuelWing(1), FuelWing(2)]

        self.add_child(self._wings[0])
        self.add_child(self._wings[1])

        # add tanks
        self._wings[0].add_child(FuelTankMain("FUELTANKA", FUELTANKMAIN_CAPACITY/2, FUELTANKMAIN_CAPACITY, FUELTANKMAIN_FAILURE_INTERVAL))
        self._wings[0].add_child(FuelTankLeft("FUELTANKB", FUELTANKLEFT_CAPACITY/2, FUELTANKLEFT_CAPACITY))
        self._wings[0].add_child(FuelTankRight("FUELTANKC", FUELTANKRIGHT_CAPACITY/2, FUELTANKRIGHT_CAPACITY))
        self._wings[1].add_child(FuelTankMain("FUELTANKD", FUELTANKMAIN_CAPACITY/2, FUELTANKMAIN_CAPACITY, FUELTANKMAIN_FAILURE_INTERVAL))
        self._wings[1].add_child(FuelTankLeft("FUELTANKE", FUELTANKLEFT_CAPACITY/2, FUELTANKLEFT_CAPACITY))
        self._wings[1].add_child(FuelTankRight("FUELTANKF", FUELTANKRIGHT_CAPACITY/2, FUELTANKRIGHT_CAPACITY))
        
        # add pumps
        main1, left1, right1 = self._wings[0].fuel_tanks
        main2, left2, right2 = self._wings[1].fuel_tanks

        self._wings[0].add_child(Pump(main1,  main2, PUMP_FLOW_SPEED))
        self._wings[0].add_child(Pump(left1,  main1, PUMP_FLOW_SPEED))
        self._wings[0].add_child(Pump(right1, main1, PUMP_FLOW_SPEED))
        self._wings[0].add_child(Pump(right1, left1, PUMP_FLOW_SPEED))
        self._wings[1].add_child(Pump(main2,  main1, PUMP_FLOW_SPEED))
        self._wings[1].add_child(Pump(left2,  main2, PUMP_FLOW_SPEED))
        self._wings[1].add_child(Pump(right2, main2, PUMP_FLOW_SPEED))
        self._wings[1].add_child(Pump(right2, left2, PUMP_FLOW_SPEED))

        # used to control the speed of fuel flow
        self._event_frequency = event_frequency
    
    @property_event
    def event_frequency(self):
        return self._event_frequency

    @event_frequency.setter
    def event_frequency(self, value):
        if value <= 0:
            raise ValueError(f"event_frequency must be greater than 0. got {self.event_frequency}")
        self._event_frequency = value

    @property
    def bounds(self):
        return self._position, self._size

    @property
    def canvas_position(self): # top level widget...
        return self.position[0], self.position[1]

    @property
    def padding(self):
        return self.size * self._padding

    
    @padding.setter
    @castPoint
    def padding(self, value):
        assert isinstance(value, Point)
        self._padding = value

    def _draw_wing_connecting_lines(self, window, wing):
        main, left, right = wing.fuel_tanks
        tl = Point(left.canvas_position[0] + left.size[0]/2, main.canvas_position[1] + main.size[1] * 3/4)
        br = right.canvas_position + right.size / 2
        size = br - tl
        draw_rectangle(window, position = tl, size = size, line_width = self.line_width, color = self.line_color)
        return main

    def draw(self, window):
        # draw widget background
        draw_rectangle(window, position = self.position, size = self.size, color=self.background_color, fill=True)
        
        # TODO this should probably be done in Wing?
        # draw connecting lines
        main1 = self._draw_wing_connecting_lines(window, self._wings[0])
        main2 = self._draw_wing_connecting_lines(window, self._wings[1])
        s1, e1  = main1.get_connecting_line(main2)
        s2, e2  = main2.get_connecting_line(main1)
        draw_line(window, start_position = s1, end_position = e1, width = self.line_width, color=self.line_color)
        draw_line(window, start_position = s2, end_position = e2, width = self.line_width, color=self.line_color)

        for widget in self.children.values():
            widget.draw(window)
            









        