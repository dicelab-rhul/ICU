
from ..widget import Widget, cosmetic_options, property_event, gettable_properties, settable_properties, in_bounds
from ..constants import *
from ..draw import draw_rectangle, draw_line, draw_dashed_line, draw_circle
from ..commands import *
from ..utils import Point

import pygame
import math
import time

@cosmetic_options(
        line_color = TRACKING_LINE_COLOUR,
        line_width = TRACKING_LINE_WIDTH,
        scale = 1)
class Target(Widget):
    
    @gettable_properties('position')
    @settable_properties('position')
    def __init__(self, position=(0,0)):
        super().__init__(TARGET1, clickable=False)
        # trigger events for initial values settings
        self._position = Point(position)
 
    @property
    def size(self):
        return Point(0.2, 0.2) * self.scale * self.parent.size[0]

    @property
    def radius(self):
        return self.size[0] / 2 # TODO maybe this should be drawing an ellipse?
    
    def draw(self, window):
        pos, _ = self.canvas_bounds
        draw_circle(window, position=pos, radius=self.radius, color=self._line_color, width=self._line_width)
        draw_circle(window, position=pos, radius=self.radius/10, color=self._line_color, width=0)

    @property_event
    def position(self):
        return self._position 
    
    @position.setter
    def position(self, value):
        if isinstance(value, (list, tuple)):
            value = Point(value)
        r = self.radius
        ps = Point(self.parent.size)
        # check within bounds
        if value.x - r < 0:
            value.x = r
        if value.y - r < 0:
            value.y = r
        if value.x + r > ps.x:
            value.x = ps.x - r
        if value.y + r > ps.y:
            value.y = ps.y - r
        self._position = value

    @property_event
    def scale(self):
        return self._scale
    
    @scale.setter
    def scale(self, value):
        self._scale = value
        # update position to stop the target from being out of bounds?
        self.position = self._position 

@cosmetic_options(
    position = Point(500, 10),
    size = Point(480,480),
    padding = PADDING,
    background_color = COLOR_GREY,
    line_width = TRACKING_LINE_WIDTH,
    line_color = TRACKING_LINE_COLOUR,
    goal_color = TRACKING_LINE_COLOUR,
    fail_color = COLOR_RED,
    dash_length = 10) # TODO
class TrackingTask(Widget): 
    
    @gettable_properties("target_speed", 
                         "event_frequency", 
                         "failure_boundary",
                         "failure_boundary_proportion")
    @settable_properties("target_speed", 
                        "event_frequency",
                        "failure_boundary_proportion")
    def __init__(self, 
                window,
                failure_boundary_proportion = 1/4, 
                target_speed = 10,       # pixels per second
                event_frequency = 30     # events per second
            ):
        """ Tracking task widget.

        Args:
            window (Window): pygame window to render to.
            failure_boundary_proportion (float, optional): proportion of the task that consisitues the correct region for the target. This is always a box around the center of the task. Defaults to 1/4.
            target_speed (int, optional): _description_. Defaults to 10.
        """
        super().__init__(TRACKINGTASK, clickable=False)
        self.window = window
        self.add_child(Target((self.size[0] / 2, self.size[1] / 2)))

        # subscribe to keyboard input
        self.subscriptions.append(PYGAME_INPUT_KEYUP)
        self.subscriptions.append(PYGAME_INPUT_KEYDOWN)

        # how far from the center can the target go?
        self._failure_boundary_proportion = failure_boundary_proportion

        # used to produce events that move the target
        self._target_speed = target_speed
        self._event_frequency = event_frequency

        self._last_event_time = time.time()
        self._target_direction = Point(0,0)
    
    @property_event
    def event_frequency(self):
        return self._event_frequency

    @event_frequency.setter
    def event_frequency(self, value):
        if value <= 0:
            raise ValueError(f"event_frequency must be greater than 0. got {self.event_frequency}")
        self._event_frequency = value

    @property_event
    def target_speed(self):
        return self._target_speed

    @target_speed.setter
    def target_speed(self, value):
        if value <= 0:
            raise ValueError(f"target_speed must be greater than 0, got {self.target_speed}")
        self._target_speed = value

    @property_event
    def failure_boundary_proportion(self):
        return self._failure_boundary_proportion

    @failure_boundary_proportion.setter
    def failure_boundary_proportion(self, value):
        if value <= 0 or value >= 1: 
            raise ValueError(f"failure_boundary_proportion {self.failure_boundary_proportion} not in the interval (0,1) (exclusive).")
        self._failure_boundary_proportion = value

    @property
    def failure_boundary(self):
        p = self.size / 2 - self.size * (self.failure_boundary_proportion / 2)
        s = self.size * self.failure_boundary_proportion
        return p, s

    def in_failure(self):
        sp = self.size
        inc = sp * (self.failure_boundary_proportion/2) # either side of the center
        fbp, fbs = (sp/2 - inc), inc * 2
        return not in_bounds(self.target.position, fbp, fbs)
        
    def on_key_down(self, event):
        keycode = event.data['keycode']
        if keycode in (pygame.K_w, pygame.K_UP):
            self._target_direction[1] -= 1
        elif keycode in (pygame.K_s, pygame.K_DOWN):
            self._target_direction[1] += 1  
        elif keycode in (pygame.K_a, pygame.K_LEFT):
            self._target_direction[0] -= 1 
        elif keycode in (pygame.K_d, pygame.K_RIGHT):
            self._target_direction[0] += 1

    def on_key_up(self, event):
        # TODO does this have the potential to go bad?
        keycode = event.data['keycode']
        if keycode in (pygame.K_w, pygame.K_UP):
            self._target_direction[1] += 1
        elif keycode in (pygame.K_s, pygame.K_DOWN):
            self._target_direction[1] -= 1
        elif keycode in (pygame.K_a, pygame.K_LEFT):
            self._target_direction[0] += 1
        elif keycode in (pygame.K_d, pygame.K_RIGHT):
            self._target_direction[0] -= 1

    def sink(self, event):
        if event.type == PYGAME_INPUT_KEYUP:
            self.on_key_up(event) 
        elif event.type == PYGAME_INPUT_KEYDOWN:
            self.on_key_down(event) 
        super().sink(event)

    @property
    def target(self):
        return next(iter(self.children.values()))

    def _should_move_target(self):
        current_time = time.time()
        dif = current_time - self._last_event_time
        if dif >= (1 / self.event_frequency):
            self._last_event_time = current_time
            return (True, dif)
        return (False, dif)
    
    def user_control_target(self):
        (smt, tdif) = self._should_move_target()
        if smt and self._target_direction.abs().sum():
            dif = self.target_speed * tdif
            p = self.target.position
            d = self._target_direction.normalised()
            self.target.position = (p[0] + self.target_speed * dif * d[0], p[1] +  self.target_speed * dif * d[1])

    def update(self):
        # update target position if keys are pressed.
        self.user_control_target() 

        # draw widget background
        pos, size = self.canvas_bounds
        draw_rectangle(self.window, position = pos, size = size, color=self.background_color, fill=True)
        # draw lines
        size = size[0]
        line_color = self.line_color     
        line_width =  self.line_width
        dash_length = self.dash_length
        line_size = size/16
        edge = line_width // 2 - 1
        edge2 = line_width // 2
        tgp = lambda x, y : (x + pos[0], y + pos[1]) # convert to canvas coordinate system

        # # draw border lines
        draw_line(self.window, start_position= tgp(0, edge),               end_position=tgp(line_size, edge),                  color=line_color, width=line_width)
        draw_line(self.window, start_position= tgp(edge, 0),               end_position=tgp(edge, line_size),                  color=line_color, width=line_width)
        draw_line(self.window, start_position= tgp(0, size-edge2),         end_position=tgp(line_size, size-edge2),            color=line_color, width=line_width)
        draw_line(self.window, start_position= tgp(edge, size-1),          end_position=tgp(edge, size-line_size-1),           color=line_color, width=line_width)
        draw_line(self.window, start_position= tgp(size-edge2, size-edge2),end_position=tgp(size-line_size-edge2, size-edge2), color=line_color, width=line_width)
        draw_line(self.window, start_position= tgp(size-edge2, size-1),    end_position=tgp(size-edge2, size-line_size-1),     color=line_color, width=line_width)
        draw_line(self.window, start_position= tgp(size-edge2, edge),      end_position=tgp(size-line_size-edge2, edge),       color=line_color, width=line_width)  
        draw_line(self.window, start_position= tgp(size-edge2, 0),         end_position=tgp(size-edge2, line_size),            color=line_color, width=line_width)

        # # #main middle lines
        draw_line(self.window, start_position= tgp( size/2,                  0,                  ), end_position=tgp(  size/2,                 size-1,             ), color=line_color, width=line_width )
        draw_line(self.window, start_position= tgp( 0,                       size/2,             ), end_position=tgp(  size-1,                 size/2,             ), color=line_color, width=line_width )
        draw_line(self.window, start_position= tgp( size/2 - line_size,      edge,               ), end_position=tgp(  size/2 + line_size,     edge,               ), color=line_color, width=line_width )
        draw_line(self.window, start_position= tgp( size/2 - line_size,      size-edge2,         ), end_position=tgp(  size/2 + line_size,     size-edge2,         ), color=line_color, width=line_width )
        draw_line(self.window, start_position= tgp( edge,                    size/2-line_size,   ), end_position=tgp(  edge,                   size/2+line_size,   ), color=line_color, width=line_width )
        draw_line(self.window, start_position= tgp( size-edge2,               size/2-line_size,  ), end_position=tgp(  size-edge2,             size/2+line_size,   ), color=line_color, width=line_width )
        draw_line(self.window, start_position= tgp( size/2 - line_size/2,    edge + size/8,      ), end_position=tgp(  size/2 + line_size/2,   edge + size/8,      ), color=line_color, width=line_width )
        draw_line(self.window, start_position= tgp( size/2 - line_size,      edge + 2*size/8,    ), end_position=tgp(  size/2 + line_size,     edge + 2*size/8,    ), color=line_color, width=line_width )
        draw_line(self.window, start_position= tgp( size/2 - line_size,      -edge + 6*size/8,   ), end_position=tgp(  size/2 + line_size,     -edge + 6*size/8,   ), color=line_color, width=line_width )
        draw_line(self.window, start_position= tgp( size/2 - line_size/2,    -edge + 7*size/8,    ), end_position=tgp( size/2 + line_size/2,   -edge + 7*size/8,    ), color=line_color, width=line_width )
        draw_line(self.window, start_position= tgp( edge + size/8,           size/2 + line_size/2,), end_position=tgp( edge + size/8,          size/2 - line_size/2,), color=line_color, width=line_width )
        draw_line(self.window, start_position= tgp( edge + 2*size/8,         size/2 + line_size,  ), end_position=tgp( edge + 2*size/8,        size/2 - line_size,  ), color=line_color, width=line_width )
        draw_line(self.window, start_position= tgp( -edge + 6*size/8,        size/2 + line_size,  ), end_position=tgp( -edge + 6*size/8,       size/2 - line_size,  ), color=line_color, width=line_width )
        draw_line(self.window, start_position= tgp( -edge + 7*size/8,        size/2 + line_size/2,), end_position=tgp( -edge + 7*size/8,       size/2 - line_size/2,), color=line_color, width=line_width )

        # # draw the central box that defines the failure boundary
        fb, fs = self.failure_boundary
        p1 = fb
        p2 = fb + Point(fs[0], 0)
        p3 = fb + fs
        p4 = fb + Point(0, fs[1])
        draw_dashed_line(self.window, start_position= tgp(*p1), end_position=tgp(*p2), color=line_color, width=line_width, dash_length=dash_length)
        draw_dashed_line(self.window, start_position= tgp(*p2), end_position=tgp(*p3), color=line_color, width=line_width, dash_length=dash_length)
        draw_dashed_line(self.window, start_position= tgp(*p3), end_position=tgp(*p4), color=line_color, width=line_width, dash_length=dash_length)
        draw_dashed_line(self.window, start_position= tgp(*p4), end_position=tgp(*p1), color=line_color, width=line_width, dash_length=dash_length)
        
        
        # dont emit an event so use _line_color
        if self.in_failure():
            self.target._line_color = self.fail_color
        else:
            self.target._line_color = self.goal_color

        for widget in self.children.values():
            widget.draw(self.window)

    @property
    def canvas_position(self): # top level widget...
        return self.position[0], self.position[1]

    @property_event
    def padding(self):
        return min(self.size[0], self.size[1]) * self._padding
    
    @padding.setter
    def padding(self, value):
        self._padding = value 