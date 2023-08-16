from dataclasses import dataclass
import multiprocessing
import pygame
import random

from datetime import datetime
import math

from .window import new_window, get_window_info
from ..event2 import EventSystem, SinkBase, SourceLocal, SinkLocal, DELIMITER, utils
from .draw import draw_circle, draw_rectangle, draw_line, clear, rgb_to_hex

from .constants import * 
from .commands import *


from .task import SystemTask, TrackingTask

class Canvas(SinkBase):

    def __init__(self, window):
        super().__init__()
        self._window = window
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
        
def start(source, sink, config):
    pygame_process = multiprocessing.Process(target=run, args=[source, sink, config])
    pygame_process.start()
    return pygame_process

class PygameEventSource(SourceLocal):

    def __init__(self):
        super().__init__()
      
        self._event_gen = {
            pygame.QUIT: lambda event: self.source(UI_WINDOW_QUIT, {}),
            pygame.WINDOWFOCUSGAINED: lambda event: self.source(UI_WINDOW_WINDOWFOCUSGAINED, {}),
            pygame.WINDOWFOCUSLOST: lambda event: self.source(UI_WINDOW_WINDOWFOCUSLOST, {}),
            pygame.WINDOWRESIZED: lambda event: self.source(UI_WINDOW_WINDOWRESIZED, dict(width=event.x, height=event.y)),
            pygame.WINDOWMOVED: lambda event: self.source(UI_WINDOW_WINDOWMOVED, dict(x=event.x, y=event.y)),
            pygame.MOUSEMOTION: lambda event: self.source(PYGAME_INPUT_MOUSEMOTION, dict(x=event.pos[0], y=event.pos[1])),
            pygame.MOUSEBUTTONDOWN: lambda event: self.source(PYGAME_INPUT_MOUSEDOWN, dict(x=event.pos[0], y=event.pos[1], button=event.button)),
            pygame.MOUSEBUTTONUP: lambda event: self.source(PYGAME_INPUT_MOUSEUP, dict(x=event.pos[0], y=event.pos[1], button=event.button)),
            pygame.KEYDOWN : lambda event : self.source(PYGAME_INPUT_KEYDOWN, dict(keycode = event.key, mod = event.mod, unicode = event.unicode)),
            pygame.KEYUP : lambda event : self.source(PYGAME_INPUT_KEYUP, dict(keycode = event.key, mod = event.mod, unicode = event.unicode)),
        }

    def update(self, pygame_event):
        if pygame_event.type in self._event_gen:
            self._event_gen[pygame_event.type](pygame_event)

class ExternalSource(SinkLocal):
    
    def __init__(self, external_source):
        super().__init__(external_source.put)

    def get_subscriptions(self):
        return ["UI::*", "PYGAME::*"] # all UI events

def run(source, sink, config):
    """ Runner for the ICU gui

    Args:
        source (SourceRemote): event buffer for all out going UI events. These will be pulled and processed by the main ICU process.
        sink (SinkRemote): event buffer for all in coming UI events. These events are commands for the UI (e.g. draw).
        config (dict): UI configuration.
    """
    event_system = EventSystem()
    event_system.add_source(sink) # remotely this is a sink but here it is a source (events will be pulled from the RemoteSink by get_events)

    event_system.add_sink(ExternalSource(source))

    window = new_window(config['window_position'], config['window_size'])
    ui_canvas = Canvas(window)
    event_system.add_sink(ui_canvas) # subscriptions are already handled

    pygame_event_source = PygameEventSource()
    event_system.add_source(pygame_event_source)

    # TODO deal with the external source...
    system_task = SystemTask(window)
    system_task.register(event_system)

    tracking_task = TrackingTask(window)
    tracking_task.register(event_system)
    
    running = True
    while running:
        time.sleep(0.01)

        # Handle events
        events = pygame.event.get()
        for event in events:
            pygame_event_source.update(event)
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.WINDOWRESIZED:
                # redraw everything...
                ui_canvas.update()

        pygame.display.flip()

        event_system.pull_events()
        event_system.publish()
        clear(window, dict(color=config['window_background_color']))

        system_task.update()
        tracking_task.update()

        ui_canvas.update()


    pygame.quit()    
    event_system.close()


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
    

