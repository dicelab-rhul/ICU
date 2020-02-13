import tkinter as tk
import random

from .constants import TRACKING_LINE_COLOUR, TRACKING_TARGET_SPEED, BACKGROUND_COLOUR

from .event import Event, EventCallback, EVENT_SINKS

# TODO keys are mutually exclusive, they should be able to be pressed them simultaneously.

def TrackingEventGenerator():
    scales = [s for s in EVENT_SINKS.keys() if TrackingWidget.__name__ in s]
    step = 10

    while True:
        dy = random.randint(-step, step)
        dx = random.randint(-step, step)
        yield Event(scales[0], dx, dy)

class Target:

    def __init__(self, canvas, radius, inner_radius, line_thickness=3):
        self.canvas = canvas
        size = canvas.winfo_width()
        
        self.circle = canvas.create_oval(size/2-radius,size/2-radius,size/2+radius,size/2+radius, outline=TRACKING_LINE_COLOUR, width=line_thickness*2)
        self.dot = canvas.create_oval(size/2-inner_radius,size/2-inner_radius,size/2+inner_radius,size/2+inner_radius, fill=TRACKING_LINE_COLOUR, width=0)
        self.px = size/2
        self.py = size/2

    def move_to(self, x, y):
        dx = x - self.px
        dy = y - self.py
        self.canvas.move(self.circle, dx, dy)
        self.canvas.move(self.dot, dx, dy)
        self.px = x
        self.py = y

    def move(self, dx, dy):
        #if 0 <= self.px + dx <= self.canvas.winfo_width() and 0 <= self.py + dy <= self.canvas.winfo_height():
        self.canvas.move(self.circle, dx, dy)
        self.canvas.move(self.dot, dx, dy)
        self.px += dx
        self.py += dy

class TrackingWidget(EventCallback, tk.Canvas):

    def __init__(self, parent, size, **kwargs):
        super(EventCallback, self).__init__()
        super(TrackingWidget, self).__init__(parent, width=size, height=size, bg=BACKGROUND_COLOUR, **kwargs)

        self.register(str(0)) #there is only one!

        #draw the tracking pattern
        line_size = size/16
        line_thickness = 3
        edge = line_thickness // 2 + 1

        self.target = Target(self, size/12, 6)
        self.target.move_to(size/2, size/2)

        #four corners
        #NW
        self.create_line(0, edge, line_size, edge, fill=TRACKING_LINE_COLOUR, width=line_thickness)
        self.create_line(edge, 0, edge, line_size, fill=TRACKING_LINE_COLOUR, width=line_thickness)
        #SW
        self.create_line(0, size-edge, line_size, size-edge, fill=TRACKING_LINE_COLOUR, width=line_thickness)
        self.create_line(edge, size, edge, size-line_size, fill=TRACKING_LINE_COLOUR, width=line_thickness)
        #SE
        self.create_line(size, size-edge, size-line_size, size-edge, fill=TRACKING_LINE_COLOUR, width=line_thickness)
        self.create_line(size-edge, size, size-edge, size-line_size, fill=TRACKING_LINE_COLOUR, width=line_thickness)
        #NE
        self.create_line(size, edge, size-line_size, edge, fill=TRACKING_LINE_COLOUR, width=line_thickness)
        self.create_line(size-edge, 0, size-edge, line_size, fill=TRACKING_LINE_COLOUR, width=line_thickness)

        #main middle lines
        self.create_line(size/2, 0, size/2, size, fill=TRACKING_LINE_COLOUR, width=line_thickness)
        self.create_line(0, size/2, size, size/2, fill=TRACKING_LINE_COLOUR, width=line_thickness)

        #middle lines
        self.create_line(size/2 - line_size, edge, size/2 + line_size, edge, fill=TRACKING_LINE_COLOUR, width=line_thickness)
        self.create_line(size/2 - line_size, size-edge, size/2 + line_size, size-edge, fill=TRACKING_LINE_COLOUR, width=line_thickness)

        self.create_line(edge, size/2-line_size, edge, size/2+line_size, fill=TRACKING_LINE_COLOUR, width=line_thickness)
        self.create_line(size-edge, size/2-line_size, size-edge, size/2+line_size, fill=TRACKING_LINE_COLOUR, width=line_thickness)

        #middle lines.... middle ;)
        self.create_line(size/2 - line_size/2, edge + size/8, size/2 + line_size/2, edge + size/8, fill=TRACKING_LINE_COLOUR, width=line_thickness)
        self.create_line(size/2 - line_size, edge + 2*size/8, size/2 + line_size, edge + 2*size/8, fill=TRACKING_LINE_COLOUR, width=line_thickness)

        self.create_line(size/2 - line_size, -edge + 6*size/8, size/2 + line_size, -edge + 6*size/8, fill=TRACKING_LINE_COLOUR, width=line_thickness)
        self.create_line(size/2 - line_size/2, -edge + 7*size/8, size/2 + line_size/2, -edge + 7*size/8, fill=TRACKING_LINE_COLOUR, width=line_thickness)

        self.create_line(edge + size/8, size/2 + line_size/2, edge + size/8, size/2 - line_size/2, fill=TRACKING_LINE_COLOUR, width=line_thickness)
        self.create_line(edge + 2*size/8, size/2 + line_size, edge + 2*size/8, size/2 - line_size, fill=TRACKING_LINE_COLOUR, width=line_thickness)
        
        self.create_line(-edge + 6*size/8, size/2 + line_size, -edge + 6*size/8, size/2 - line_size, fill=TRACKING_LINE_COLOUR, width=line_thickness)
        self.create_line(-edge + 7*size/8, size/2 + line_size/2, -edge + 7*size/8, size/2 - line_size/2, fill=TRACKING_LINE_COLOUR, width=line_thickness)

        #middle rectangle
        self.create_rectangle(edge + 3*size/8, edge + 3*size/8, -edge + 5*size/8, -edge + 5*size/8, outline=TRACKING_LINE_COLOUR, width=line_thickness)

    def sink(self, event):
        self.target.move(event.args[1], event.args[2])

    def left_callback(self, *args):
        self.target.move(-TRACKING_TARGET_SPEED, 0)
        self.source("left", -TRACKING_TARGET_SPEED, 0)

    def right_callback(self, *args):
        self.target.move(TRACKING_TARGET_SPEED, 0)
        self.source("right", TRACKING_TARGET_SPEED, 0)

    def up_callback(self, *args):
        self.target.move(0, -TRACKING_TARGET_SPEED)
        self.source("up", 0, -TRACKING_TARGET_SPEED)

    def down_callback(self, *args):
        self.target.move(0, TRACKING_TARGET_SPEED)
        self.source("down", 0, TRACKING_TARGET_SPEED)
