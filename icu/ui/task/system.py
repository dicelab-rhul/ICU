

from ...event2 import DELIMITER
from ..commands import INPUT_MOUSEDOWN, INPUT_MOUSEUP, INPUT_MOUSECLICK
from ..draw import draw_simple_rect
from ..constants import *
from ..widget import Widget, cosmetic_options, gettable_properties, settable_properties
from ..utils import Point

class WarningLight(Widget):

    @gettable_properties('state')
    @settable_properties('state')
    def __init__(self, name, start_state = 0, **kwargs):
        super().__init__(name, **kwargs)
        assert start_state in (0,1) # goal state = 0, fail state = 1
        self._state = start_state 
        
    @property
    def state(self):
        return self._state % 2
    
    @state.setter
    def state(self, value):
        self._state = value 

    @property
    def _colors(self):
        return (self.color_goal, self.color_fail)

    def draw(self, window):
        p, s = self.canvas_bounds
        draw_simple_rect(window, dict(position = p, size = s, color = self._colors[self.state]))
        draw_simple_rect(window, dict(position = p, size = s, color = COLOR_BLACK, width=LINE_WIDTH))

    def on_mouse_click(self, event):
        rel = self.state - (1-self.state)
        self.state = 1-self.state
        self.source(self.address + DELIMITER + INPUT_MOUSECLICK, data=dict(widget = self.name, widget_state = self.state, widget_state_rel = rel, x = event.data['x'], y = event.data['y']))
        
    def on_mouse_up(self, event):
        self.source(self.address + DELIMITER + INPUT_MOUSEUP, data=dict(widget = self.name, x = event.data['x'], y = event.data['y']))
    
    def on_mouse_down(self, event):
        self.source(self.address + DELIMITER + INPUT_MOUSEDOWN, data=dict(widget = self.name, x = event.data['x'], y = event.data['y']))

@cosmetic_options(
    line_width = LINE_WIDTH, 
    line_color = LINE_COLOR, 
    color_goal = COLOR_GREEN,
    color_fail = COLOR_GREY)
class WarningLight1(WarningLight):

    def __init__(self, start_state=0):
        super().__init__(WARNINGLIGHT1, start_state=start_state, clickable=True)

    @property
    def bounds(self):
        return (self.position, self.size)
    
    @property
    def size(self):
        return (WARNING_LIGHT_SIZE[0] * self.parent.size[0], WARNING_LIGHT_SIZE[1]  * self.parent.size[0])
       
    @property
    def position(self):
        return (self.parent.padding, self.parent.padding)  
    
@cosmetic_options(
    line_width  = LINE_WIDTH, 
    line_color  = LINE_COLOR,
    color_goal      = COLOR_GREY,
    color_fail     = COLOR_RED)
class WarningLight2(WarningLight):

    def __init__(self, start_state=0):
        super().__init__(WARNINGLIGHT2, start_state=start_state, clickable=True)
 
    @property
    def size(self):
        return (WARNING_LIGHT_SIZE[0] * self.parent.size[0], WARNING_LIGHT_SIZE[1]  * self.parent.size[0])
        
    @property
    def position(self):
        return (self.parent.size[0] - self.size[0] - self.parent.padding, self.parent.padding)
    
class SliderBox(Widget):
    
    def __init__(self, i, 
                steps=NUM_SLIDER_STEPS, 
                start_state = NUM_SLIDER_STEPS//2, 
                goal_state=NUM_SLIDER_STEPS//2):
        
        super().__init__(SLIDERBOX.format(i), clickable=True)
        self.steps = steps
        self.state = start_state if start_state < steps else steps // 2
        self.goal_state = goal_state if goal_state < steps else steps // 2
        
    @property
    def size(self):
        s = self.parent.size
        inc = s[1] / self.parent.steps
        size = (s[0], inc)
        return size

    @property
    def position(self):
        s = self.parent.size
        inc = s[1] / self.parent.steps
        state = self.state
        position = (0, inc * state)
        return position
    
    def draw(self, window):
        p, s = self.canvas_bounds 
        color = self.parent.box_color_goal if self.state == self.goal_state else self.parent.box_color_fail
        p = (p[0], p[1] - 1) # avoids glitches
        draw_simple_rect(window, dict(position = p, size = s, color = color, width=0))

    def on_mouse_click(self, event):
        self.parent.on_mouse_click(event) # delegate the event trigger to the parent...

    @property
    def cosmetic_options(self):
        return self.parent.cosmetic_options
    
@cosmetic_options(
    line_width              = LINE_WIDTH, 
    line_color              = LINE_COLOR, 
    background_color        = COLOR_LIGHT_BLUE, 
    box_color_goal          = COLOR_BLUE,
    box_color_fail          = COLOR_RED)
class Slider(Widget):

    @gettable_properties('state', 'steps', 'goal_state')
    @settable_properties('state', 'steps', 'goal_state')
    def __init__(self, i, 
                start_state = NUM_SLIDER_STEPS // 2, 
                goal_state = NUM_SLIDER_STEPS // 2,
                steps = NUM_SLIDER_STEPS):
        super().__init__(SLIDER.format(i), clickable=False)
        self.i = i
        self.add_child(SliderBox(i, steps = steps, goal_state=goal_state, start_state=start_state))

    @property
    def state(self):
        return self.box.state
    
    @state.setter
    def state(self, value):
        self.box.state = value

    @property
    def goal_state(self):
        return self.box.goal_state
    
    @goal_state.setter
    def goal_state(self, value):
        self.box.goal_state = value

    @property
    def steps(self):
        return self.box.steps
    
    @steps.setter
    def steps(self, value):
        self.box.steps = value

    @property 
    def box(self):
        return next(iter(self.children.values()))
    
    @property
    def position(self):
        p, s = self.parent.children[WARNINGLIGHT1].bounds
        y = p[1] + s[1] # sliders appear below warning lights
        w, _ = self.size
        pad = self.parent.padding
        p = (pad + (self.i-1) * (w + pad), y + pad)
        return p 

    @property
    def size(self):
        p, s = self.parent.children[WARNINGLIGHT1].bounds
        y = p[1] + s[1] # sliders appear below warning lights
        pad = self.parent.padding
        w = (self.parent.size[0] - (pad * (NUM_SLIDERS + 1))) / NUM_SLIDERS
        h = (self.parent.size[1] - y - 2 * pad)
        return (w,h)

    def draw(self, window):
        # draw each rect
        p, s = self.canvas_bounds
        draw_simple_rect(window, dict(position = p, size = s, color=self.background_color))
        
        # draw clickable rect
        for child in self.children.values():
            child.draw(window)

        inc = s[1] / (self.steps)
        for i in range(1, self.steps + 1):
            draw_simple_rect(window, dict(position = (p[0], p[1]), size = (s[0], i * inc), color=self.line_color, width=self.line_width)) 

    def on_mouse_click(self, event):
        rel = self.box.state - self.box.goal_state 
        self.box.state = self.box.goal_state
        self.source(self.address + DELIMITER + INPUT_MOUSECLICK, data=dict(widget = self.name, widget_state = self.box.state, widget_state_rel = rel, x = event.data['x'], y = event.data['y']))
    
@cosmetic_options(
    position = Point(0, 0),
    size = Point(480,640),
    padding = PADDING,
    background_color = COLOR_GREY)
class SystemTask(Widget): 

    # TODO this could be much more sophisticated... have options specified on each constructor of child widget? 
    # rather than ever passing these options directly, they should be updated via the event system!
   
    def __init__(self, 
                window):
        super().__init__(SYSTEMTASK, clickable=False)
        self.window = window
        self.add_child(WarningLight1())
        self.add_child(WarningLight2())
        for i in range(NUM_SLIDERS):
            self.add_child(Slider(i + 1))

    @property
    def bounds(self):
        return self._position, self._size

    @property
    def canvas_position(self): # top level widget...
        return self.position[0], self.position[1]

    @property
    def padding(self):
        return min(self._size[0], self._size[1]) * self._padding

    def update(self):
        # draw widget background
        draw_simple_rect(self.window, dict(position = self.position, size = self.size, color=self.background_color))
        for widget in self.children.values():
            widget.draw(self.window) # TODO what if position changes?