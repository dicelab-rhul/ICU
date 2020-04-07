"""
    An overlay may be displayed at a given positon on the GUI, make use of the Overlay class to do this.

    @Author: Benedict Wilkins
    @Date: 2020-04-02 21:57:11
"""

from .event import Event, EventCallback
from .component import Component
from .component import SimpleComponent


class Overlay(EventCallback, Component, SimpleComponent):
    """
        A GUI widget that is placed above other widgets. Accepts 'move' and 'place' events to move the widget.
    """

    def __init__(self, canvas, component):
        super(Overlay, self).__init__(canvas, component)
        name = self.__class__.__name__
        EventCallback.register(self, name)
        Component.register(self, name) 

    def sink(self, event):
        if event.data.label == 'place':
            self.x = event.data.x
            self.y = event.data.y
        elif event.data.label == 'move':
            self.x += event.data.dx
            self.y += event.data.dy






