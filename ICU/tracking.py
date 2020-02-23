import tkinter as tk
import random

from .constants import TRACKING_LINE_COLOUR, TRACKING_TARGET_SPEED, BACKGROUND_COLOUR

from .event import Event, EventCallback, EVENT_SINKS

# TODO keys are mutually exclusive, they should be able to be pressed them simultaneously.

def get_tracking_widget_handle(): #get the name of the tracking widget for use in event callback
    return [s for s in EVENT_SINKS.keys() if TrackingWidget.__name__ in s][0]

def TrackingEventGenerator():
    trackingwidget = get_tracking_widget_handle()
    step = 10

    while True:
        dy = random.randint(-step, step)
        dx = random.randint(-step, step)
        yield Event(trackingwidget, dx, dy)


def KeyEventGenerator(keyhandler):
    trackingwidget = get_tracking_widget_handle()
    dx = 0
    dy = 0

    while True:
        if keyhandler.isPressed('Left'):
            dx -= TRACKING_TARGET_SPEED
        if keyhandler.isPressed('Right'):
            dx += TRACKING_TARGET_SPEED
        if keyhandler.isPressed('Up'):
            dy -= TRACKING_TARGET_SPEED
        if keyhandler.isPressed('Down'):
            dy += TRACKING_TARGET_SPEED
        
        if dx != 0 or dy != 0:
            yield Event(trackingwidget, dx, dy)
            dx = 0
            dy = 0
        else:
            yield None
    

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
        print(event)
        self.target.move(event.args[1], event.args[2])

    def move_callback(self, dx, dy):
        self.target.move(dx,dy)
        self.source("move", dx, dy)


