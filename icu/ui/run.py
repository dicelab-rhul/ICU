from dataclasses import dataclass
import multiprocessing
import pygame
from icu.ui.root import Root

from icu.ui.widget import Widget

from .window import Window
from ..event2 import EventSystem, SinkBase, SourceLocal, SinkLocal, DELIMITER
from .draw import draw_circle, draw_rectangle, draw_line, rgb_to_hex

from .constants import * 
from .commands import *

from .task import SystemTask, TrackingTask, FuelTask

# TODO update this class.. perhaps just move the functionality into widget, then anything can be drawn on any widget.
class Canvas(Widget):

    def __init__(self):
        super().__init__(name = "Canvas")
        self._commands = {
            DRAW_CIRCLE : draw_circle,
            DRAW_RECT   : draw_rectangle,
            DRAW_LINE   : draw_line,
            CLEAR       : clear,  
        }
        self._command_buffer = []

    def get_subscriptions(self):
        return [UI_CANVAS + DELIMITER + "*"]

    def sink(self, event):
        command = event.type.split(DELIMITER)[-1] # LINE, RECT, CIRCLE ?   
        if command in self._commands:
            self._command_buffer.append((command, event))
        
    def update(self):
        for (command, event) in self._command_buffer:
            self._commands[command](self._window, event.data)
        
def start(source, sink):
    pygame_process = multiprocessing.Process(target=run, args=[source, sink])
    pygame_process.start()
    return pygame_process

class ExternalSource(SinkLocal):
    
    def __init__(self, external_source):
        super().__init__(external_source.put)

    def get_subscriptions(self):
        return ["UI::*", "PYGAME::*"] # all UI events

def run(source, sink):
    """ Runner for the ICU gui

    Args:
        source (SourceRemote): event buffer for all out going UI events. These will be pulled and processed by the main ICU process.
        sink (SinkRemote): event buffer for all in coming UI events. These events are commands for the UI (e.g. draw).
    """
    event_system = EventSystem()
    event_system.add_source(sink) # remotely this is a sink but here it is a source (events will be pulled from the RemoteSink by get_events)
    event_system.add_sink(ExternalSource(source))

    root = Root(event_system)
    
    #ui_canvas = Canvas()
    #event_system.add_sink(ui_canvas) # subscriptions are already handled
    #window.add_child(ui_canvas)

    print_sink = SinkLocal(print)
    print_sink.subscribe("UI::WINDOW::*")
    event_system.add_sink(print_sink)

    # TODO deal with the external source...
    system_task = SystemTask()
    system_task.register(event_system)
    root.add_child(system_task)

    tracking_task = TrackingTask()
    tracking_task.register(event_system)
    root.add_child(tracking_task)

    fuel_task = FuelTask()
    fuel_task.register(event_system)
    root.add_child(fuel_task)

    # start running the UI!
    for dt in root.start_pygame_event_loop():
        pass # do some intermediate thing? 

# TODO remove? 
import time

class ConditionalTimer:
    def __init__(self, interval):
        self.interval = interval
        self.last_execution = time.time()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def should_execute(self):
        current_time = time.time()
        if current_time - self.last_execution >= self.interval:
            self.last_execution = current_time
            return True
        return False
    

