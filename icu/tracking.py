import tkinter as tk
import random

from .constants import TRACKING_LINE_COLOUR, TRACKING_TARGET_SPEED, BACKGROUND_COLOUR
from .constants import WARNING_OUTLINE_COLOUR, WARNING_OUTLINE_WIDTH

from .event import Event, EventCallback
from .component import Component

from .component import Component, CanvasWidget, SimpleComponent, BoxComponent, LineComponent
from .highlight import Highlight


EVENT_NAME_MOVE = 'move'
EVENT_NAME_HIGHLIGHT = "highlight"

def TrackingEventGenerator():
    trackingwidget = TrackingWidget.all_components()[0]
    step = 10

    while True:
        dy = random.randint(-step, step)
        dx = random.randint(-step, step)
        yield Event('tracking_event_generator', trackingwidget, label=EVENT_NAME_MOVE, dx=dx, dy=dy)

def KeyEventGenerator(keyhandler):
    trackingwidget = TrackingWidget.all_components()[0]
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
            yield Event('key_event_generator', trackingwidget, label=EVENT_NAME_MOVE, dx=dx, dy=dy)
            dx = 0
            dy = 0
        else:
            yield None
    
class Target(CanvasWidget):

    def __init__(self, canvas, radius, inner_radius, line_thickness=5):
        if line_thickness > 5:
            raise ValueError("line_thickness above 5 may lead to visual artefacts... fix incoming")
        circle = SimpleComponent(canvas, canvas.create_oval(0,0,radius*2,radius*2, outline=TRACKING_LINE_COLOUR, width=line_thickness))
        dot = SimpleComponent(canvas, canvas.create_oval(radius-inner_radius*2, radius-inner_radius*2, radius+inner_radius*2, radius+inner_radius*2, fill=TRACKING_LINE_COLOUR, width=0))
        super(Target, self).__init__(canvas, components={'circle':circle, 'dot':dot})

class TrackingWidget(EventCallback, Component, CanvasWidget):

    __instance__ = None

    def all_components():
        return (TrackingWidget.__instance__,)

    def __init__(self, canvas, size, **kwargs):
        super(TrackingWidget, self).__init__(canvas, width=size, height=size, background_colour=BACKGROUND_COLOUR, **kwargs)

        name = str(0)
        EventCallback.register(self, name)
        Component.register(self, name)    
    
        #draw the tracking pattern
        line_size = size/16
        line_thickness = 3
        edge = line_thickness // 2 + 1

        ts = size/12

        def add(**kwargs): #add components
            for k,v in kwargs.items():
                self.components[k] = v

        target = Target(canvas, ts, ts/10)
        target.position = (size/2 - ts, size/2 - ts)

        add(target=target)
        #four corners
        #NW
        add(NW1=LineComponent(canvas, 0, edge, line_size, edge, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))
        add(NW2=LineComponent(canvas, edge, 0, edge, line_size, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))
        #SW
        add(SW1=LineComponent(canvas, 0, size-edge, line_size, size-edge, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))
        add(SW2=LineComponent(canvas, edge, size, edge, size-line_size, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))
        #SE
        add(SE1=LineComponent(canvas, size, size-edge, size-line_size, size-edge, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))
        add(SE2=LineComponent(canvas, size-edge, size, size-edge, size-line_size, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))
        #NE
        add(NE1=LineComponent(canvas, size, edge, size-line_size, edge, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))   
        add(NE2=LineComponent(canvas, size-edge, 0, size-edge, line_size, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))

        #main middle lines
        add(M1=LineComponent(canvas, size/2, 0, size/2, size, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))
        add(M2=LineComponent(canvas, 0, size/2, size, size/2, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))

        #middle lines
        add(M3=LineComponent(canvas, size/2 - line_size, edge, size/2 + line_size, edge, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))
        add(M4=LineComponent(canvas, size/2 - line_size, size-edge, size/2 + line_size, size-edge, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))

        add(M5=LineComponent(canvas, edge, size/2-line_size, edge, size/2+line_size, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))
        add(M6=LineComponent(canvas, size-edge, size/2-line_size, size-edge, size/2+line_size, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))

        #middle lines.... middle ;)
        add(M7=LineComponent(canvas, size/2 - line_size/2, edge + size/8, size/2 + line_size/2, edge + size/8, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))
        add(M8=LineComponent(canvas, size/2 - line_size, edge + 2*size/8, size/2 + line_size, edge + 2*size/8, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))

        add(M9=LineComponent(canvas, size/2 - line_size, -edge + 6*size/8, size/2 + line_size, -edge + 6*size/8, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))
        add(M10=LineComponent(canvas, size/2 - line_size/2, -edge + 7*size/8, size/2 + line_size/2, -edge + 7*size/8, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))

        add(M11=LineComponent(canvas, edge + size/8, size/2 + line_size/2, edge + size/8, size/2 - line_size/2, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))
        add(M12=LineComponent(canvas, edge + 2*size/8, size/2 + line_size, edge + 2*size/8, size/2 - line_size, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))
        
        add(M13=LineComponent(canvas, -edge + 6*size/8, size/2 + line_size, -edge + 6*size/8, size/2 - line_size, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))
        add(M14=LineComponent(canvas, -edge + 7*size/8, size/2 + line_size/2, -edge + 7*size/8, size/2 - line_size/2, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))

        #middle rectangle
        #TODO
        #add(B=BoxComponent(canvas, edge + 3*size/8, edge + 3*size/8, -edge + 5*size/8, -edge + 5*size/8, outline_colour=TRACKING_LINE_COLOUR, outline_thickness=line_thickness))

        #self.c.size = (size-200, size-50) #test resize

        self.highlight = Highlight(canvas, self)
        assert TrackingWidget.__instance__ is None #there can only be one tracking widget
        TrackingWidget.__instance__ = self.name


    def sink(self, event):
        self.components['target'].move(event.data.dx, event.data.dy)

       


