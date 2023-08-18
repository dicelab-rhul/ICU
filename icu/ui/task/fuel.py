


from ...event2 import DELIMITER
from ..commands import INPUT_MOUSEDOWN, INPUT_MOUSEUP, INPUT_MOUSECLICK
from ..draw import draw_rectangle, draw_line, draw_arrow
from ..constants import *
from ..widget import Widget, property_event, cosmetic_options, gettable_properties, settable_properties
from ..utils import Point

from enum import Enum


# TODO inherit from parent decorator? 
class FuelWing(Widget):
    def __init__(self, wing):
        super().__init__(f"Wing{wing}")
        self._wing = wing - 1
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
    
    def draw(self, window):
        #draw_simple_rect(window, dict(position = self.position, size = self.size, width = self.parent.line_width, color=COLOR_BLACK))
        for widget in self.children.values():
            widget.draw(window)

@cosmetic_options(
    background_color = COLOR_GREY,
    goal_color = COLOR_GREEN,
    fail_color = COLOR_RED,
    line_color = LINE_COLOR,
)
class FuelTank(Widget):

    @settable_properties('fuel_level', 'capacity')
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

    def get_pump_position(self, tank2, pump):
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

    def get_pump_position(self, tank2, pump):
        p1, p2 = self.get_connecting_line(tank2)
        off = (p1[0] - p2[0]) / 12
        return Point(min(p1[0], p2[0]) + abs(p1[0] - p2[0])/2 + off, p1[1]) - pump.size / 2

class FuelTankLeft(FuelTank):
    @property
    def position(self):
        ps, s = self.parent.size, self.size
        return Point(self.parent.padding[0], ps[1] - s[1] - self.parent.padding[1])
    @property
    def size(self):
        return Point(self.parent.size[0] / 6, self.parent.size[1] / 3)

    def get_pump_position(self, tank2, pump):
        return Point(0,0)

class FuelTankRight(FuelTank):
    @property
    def position(self):
        ps, s = self.parent.size, self.size
        return Point(ps[0] - s[0] - self.parent.padding[0], ps[1] - s[1] - self.parent.padding[1])
    @property
    def size(self):
        return Point(self.parent.size[0] / 4, self.parent.size[1] / 3)

    def get_pump_position(self, tank2, pump):
        # if tank 2 is above
        if isinstance(tank2, FuelTankMain):
            return Point(0,0) 
        elif isinstance(tank2, FuelTankLeft):
            return Point(0,0) 
        else:
            raise ValueError(f"Invalid tank {type(self).__name__} for {type(self).__name__}, tanks do not share a {Pump.__name__}.") # unreachable...
        

# class syntax

class PumpState(Enum):
    IDLE = 1
    ON = 2
    OFF = 3

    def __getitem__(i):
        return [PumpState.IDLE, PumpState.ON, PumpState.OFF]

@cosmetic_options(
    background_color = COLOR_GREY,
    on_color = COLOR_GREEN,
    off_color = COLOR_RED,
    line_color = LINE_COLOR,
    arrow_color = LINE_COLOR,
    arrow_fill_head = True,
    scale = (0.8, 0.8)
)
class Pump(Widget):
    def __init__(self, tank1, tank2):
        super().__init__(f"Pump{tank1.name[-1] + tank2.name[-1]}", clickable=True)
        self.tank1 = tank1
        self.tank2 = tank2
        self._state = 0 # 0 clickable, 1 on, 2 failure

    @property_event
    def state(self):
        return self._state
    
    @state.setter
    def state(self, value):
        if isinstance(value, int):
            self._state = PumpState[value]
        elif isinstance(value, PumpState):
            self._state = value
        else:
            raise ValueError(f"Failed to set `state`, value {value} must of type {PumpState} or int.")

    @property
    def position(self):
        # yes its weird to off load this to the fuel tanks, but it avoids a large conditional statement for type checking...
        return self.tank1.get_pump_position(self.tank2, self)

    @property
    def _colors(self):
        return [self.background_color, self.on_color, self.off_color]

    @property
    def size(self):
        return Point(self.scale) * self.tank1.size[1] / 4
    
    def draw(self, window):
        draw_rectangle(window, position = self.canvas_position, size = self.size, color=self._colors[self.state], fill=True)
        draw_rectangle(window, position = self.canvas_position, size = self.size, color=self.line_color, line_width = self.parent.line_width)
        
        # draw arrow
        draw_arrow(window, start_position = self.canvas_position + self.size/2, length=self.size[0] / 4, 
                   color=self.arrow_color, head_only=True, fill_head=self.arrow_fill_head, head_length=self.size[0] / 2)




@cosmetic_options(
    position = Point(0, 0),
    size = Point(780, 480),
    padding = (1.5*PADDING, PADDING),
    background_color = COLOR_GREY,
    line_color = COLOR_BLACK,
    line_width = LINE_WIDTH,
)
class FuelTask(Widget): 
    # TODO this could be much more sophisticated... have options specified on each constructor of child widget? 
    # rather than ever passing these options directly, they should be updated via the event system!
   
    def __init__(self, 
                window):
        super().__init__(SYSTEMTASK, clickable=False)
        self.window = window

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

        self.add_child(Pump(main1, main2))
        # self.add_child(Pump(left1, main1))
        # self.add_child(Pump(right1, main1))
        # self.add_child(Pump(right1, left1))
        self.add_child(Pump(main2, main1))
        # self.add_child(Pump(left2, main2))
        # self.add_child(Pump(right2, main2))
        # self.add_child(Pump(right2, left2))

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
    def padding(self, value):
        self._padding = value 

    def _draw_wing_connecting_lines(self, wing):
        main, left, right = wing.fuel_tanks
        tl = Point(left.canvas_position[0] + left.size[0]/2, main.canvas_position[1] + main.size[1] * 3/4)
        br = right.canvas_position + right.size / 2
        size = br - tl
        draw_rectangle(self.window, position = tl, size = size, line_width = self.line_width, color = self.line_color)
        return main

    def update(self):
        # draw widget background
        draw_rectangle(self.window, position = self.position, size = self.size, color=self.background_color, fill=True)
        
        # TODO this should probably be done in Wing?
        # draw connecting lines
        main1 = self._draw_wing_connecting_lines(self._wings[0])
        main2 = self._draw_wing_connecting_lines(self._wings[1])
        s1, e1  = main1.get_connecting_line(main2)
        s2, e2  = main2.get_connecting_line(main1)
        draw_line(self.window, start_position = s1, end_position = e1, width = self.line_width, color=self.line_color)
        draw_line(self.window, start_position = s2, end_position = e2, width = self.line_width, color=self.line_color)

        for widget in self.children.values():
            widget.draw(self.window) # TODO what if position changes?