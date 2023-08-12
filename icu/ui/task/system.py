
import pygame_widgets

from collections import deque
from ...event2 import SinkBase, SourceBase, Event, DELIMITER

from ..commands import PYGAME_INPUT_MOUSEDOWN, PYGAME_INPUT_MOUSEUP, UI_INPUT_MOUSEDOWN, UI_INPUT_MOUSEUP, UI_INPUT_MOUSECLICK
from ..draw import draw_rectangle, draw_simple_rect, draw_line

from ..constants import * # colours

# TODO commands for the system task


PADDING = 0.05
WARNING_LIGHT_SIZE = (1/3, 1/5)
NUM_SLIDERS = 4
NUM_SLIDER_SCALES = 11


def in_bounds(position, rect_pos, rect_size):
    return rect_pos[0] <= position[0] <= rect_pos[0] + rect_size[0] and rect_pos[1] <= position[1] <= rect_pos[1] + rect_size[1]

class Widget(SourceBase, SinkBase):
    
    def __init__(self, name, clickable=False):
        super().__init__()
        self._parent = None # set by adding this as a child
        self.name = name
        self.children = dict() 
        self.clickable = clickable
        self.subscriptions = []
        if clickable:
            self.subscriptions.append(PYGAME_INPUT_MOUSEDOWN)
            self.subscriptions.append(PYGAME_INPUT_MOUSEUP)
        self._prepare_click = False
        self._source_buffer = deque()
    
    @property
    def parent(self):
        return self._parent
    
    def get_subscriptions(self):
        return self.subscriptions.copy()
    
    def add_child(self, child):
        self.children[child.name] = child
        child._parent = self # this must be upheld... 
    
    def remove_child(self, child):
        del self.children[child.name]    
        child._parent = None # orphaned... warning? 
    
    def get_events(self):
        while len(self._source_buffer) > 0:
            yield self._source_buffer.popleft()

    def sink(self, event):
        if self.clickable:
            if event.type == PYGAME_INPUT_MOUSEDOWN and self.in_bounds((event.data['x'], event.data['y'])):
                self._prepare_click = True
                self.on_mouse_down(event)
            elif event.type == PYGAME_INPUT_MOUSEUP and self.in_bounds((event.data['x'], event.data['y'])):
                if self._prepare_click:  # there was a click on this widget
                    self._prepare_click = False
                    self.on_mouse_click(event)
                self.on_mouse_up(event)

    def on_mouse_down(self, event):
        raise NotImplementedError() 

    def on_mouse_up(self, event):
        raise NotImplementedError()

    def on_mouse_click(self, event):
        raise NotImplementedError()

    def source(self, event_type, data):
        self._source_buffer.append(Event(event_type, data))

    def close(self):
        pass # nothing to close

    @property
    def canvas_position(self):
        return self.parent.canvas_position[0] + self.position[0], self.parent.canvas_position[0] + self.position[1]

    @property
    def bounds(self):
        raise NotImplementedError()

    def in_bounds(self, position):
        canvas_position = self.canvas_position
        return canvas_position[0] <= position[0] <= canvas_position[0] + self.size[0] and canvas_position[1] <= position[1] <= canvas_position[1] + self.size[1]

    def draw(self):
        raise NotImplementedError() 

    @property 
    def position(self):
        return self.bounds[0]
     
    @property
    def size(self):
        return self.bounds[1]
    
class WarningLight(Widget):

    def __init__(self, name, color, **kwargs):
        super().__init__(name, **kwargs)
        self.color = color 

    @property
    def bounds(self):
        raise NotImplementedError() 

    def draw(self, window):
        draw_simple_rect(window, dict(position = self.canvas_position, size = self.size, color = self.color))
        draw_simple_rect(window, dict(position = self.canvas_position, size = self.size, color = COLOR_BLACK, width=OUTLINE_THICKESS))

    def on_mouse_click(self, event):
        self.source(UI_INPUT_MOUSECLICK + DELIMITER + self.name, data=dict(widget = self.name, x = event.data['x'], y = event.data['y']))
        # TODO change color
    
    def on_mouse_up(self, event):
        self.source(UI_INPUT_MOUSEUP + DELIMITER + self.name, data=dict(widget = self.name, x = event.data['x'], y = event.data['y']))
    
    def on_mouse_down(self, event):
        self.source(UI_INPUT_MOUSEDOWN + DELIMITER + self.name, data=dict(widget = self.name, x = event.data['x'], y = event.data['y']))

class WarningLight1(WarningLight):

    def __init__(self, color):
        super().__init__("WARNINGLIGHT::1", color, clickable=True)
        self.color = color
    
    @property
    def bounds(self):
        size = (WARNING_LIGHT_SIZE[0] * self.parent.size[0], WARNING_LIGHT_SIZE[1]  * self.parent.size[0])
        position = (self.parent._padding, self.parent._padding) 
        return (position, size)
    

class WarningLight2(WarningLight):

    def __init__(self, color):
        super().__init__("WARNINGLIGHT::2", color, clickable=True)
 
    @property
    def bounds(self):
        size = (WARNING_LIGHT_SIZE[0] * self.parent.size[0], WARNING_LIGHT_SIZE[1]  * self.parent.size[0])
        position = (self.parent.size[0] - size[0] - self.parent._padding, self.parent._padding)
        return (position, size)

class SystemTask(Widget): 

    def __init__(self, window, position, size=(480,640)):
        super().__init__("SYSTEMTASK", clickable=False)
        self.window = window
        self._position = position
        self._size = size
        self.add_child(WarningLight1(COLOR_RED))
        self.add_child(WarningLight2(COLOR_GREEN))

    @property
    def bounds(self):
        return self._position, self._size

    @property
    def canvas_position(self): # top level widget...
        return self.position[0], self.position[1]

    @property
    def _padding(self):
        return min(self.size[0], self.size[1]) * PADDING

    def update(self):
        # draw widget background
        draw_simple_rect(self.window, dict(position = self.position, size = self.size, color=COLOR_GREY))

        for widget in self.children.values():
            widget.draw(self.window) # TODO what if position changes?

        # draw sliders
        # for i in range(NUM_SLIDERS):
        #     p, s = self.get_slider_bounds(i)
        #     draw_simple_rect(self.window, dict(position = p, size = s, width=OUTLINE_THICKESS, color=COLOR_BLACK))
        #     inc = s[1] / NUM_SLIDER_SCALES
        #     for i in range(NUM_SLIDER_SCALES):
        #         y = p[1] + i * inc
        #         draw_line(self.window, dict(start_position = (p[0], y), end_position = (p[0] + s[0] -1, y), width=OUTLINE_THICKESS, color=COLOR_BLACK))

    # def get_slider_bounds(self, i):
    #     p, s = self.widgets["WARNINGLIGHT::1"].canvas_position, self.widgets["WARNINGLIGHT::1"].size
    #     slider_y = p[1] + s[1]
    #     slider_w = (self.size[0] - (self._padding * (NUM_SLIDERS + 1))) / NUM_SLIDERS
    #     slider_h = (self.size[1] - slider_y - 2 * self._padding)
    #     p = (self.position[0] + self._padding + i * (slider_w + self._padding), slider_y + self._padding)
    #     return p, (slider_w, slider_h)
    
    def get_subscriptions(self):
        return []

    def get_events(self): # this widget doesnt produce any events
        pass 


    
