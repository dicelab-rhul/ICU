from dataclasses import dataclass
import multiprocessing
from typing import Tuple, Union
import pygame


import pygame

from .window import new_window, get_window_info
from ..event2 import EventSystem, SinkBase, DELIMITER

UI_CANVAS = "UI::CANVAS"
DRAW_CIRCLE = "DRAW_CIRCLE"
DRAW_RECT   = "DRAW_RECT"
DRAW_LINE   = "DRAW_LINE"
CLEAR       = "CLEAR"

@dataclass
class CommandDrawLine:
    start_position : Tuple
    end_position : Tuple
    color : Union[Tuple, str]
    width : float

@dataclass
class CommandDrawRect:
    position : Tuple
    size : Tuple
    color : Union[Tuple, str]
    width : float

@dataclass
class CommandDrawCircle:
    position : Tuple
    radius : float
    color : Union[Tuple, str]
    width : float

@dataclass
class CommandClear:
    pass 


class Canvas(SinkBase):

    def __init__(self, window):
        super().__init__()
        self._window = window

        self._commands = {
            DRAW_CIRCLE : draw_circle,
            DRAW_RECT   : draw_rect,
            DRAW_LINE   : draw_line,
            CLEAR       : clear,  
        }

    def get_subscriptions(self):
        return [UI_CANVAS + DELIMITER + "*"]

    def sink(self, event):
        command = event.type.split(DELIMITER)[-1] # LINE, RECT, CIRCLE ?     
        if not command in self._commands:
            pass # TODO warning?
        else:
            self._commands[command](self._window, event)
        
def draw_circle(window, event):
    pygame.draw.circle(window, event.data.get('color', 'black'), event.data['position'], event.data['radius'], width=event.data.get('width', 1)) 

def draw_rect(window, event):
    pygame.draw.rect(window, event.data.get('color', 'black'), (*event.data['position'], *event.data['size']), width=event.data.get('width', 1)) 

def draw_line(window, event):
    pygame.draw.line(window, event.data.get('color', 'black'), event.data['start_position'], event.data['end_position'], event.data.get('width', 1))

def clear(window, event):
    window.fill(event.data['color'])
        
def start(source, sink, config):
    pygame_process = multiprocessing.Process(target=run, args=[source, sink, config])
    pygame_process.start()
    return pygame_process

def run(source, sink, config):
    """ Runner for the ICU gui

    Args:
        source (SourceRemote): event buffer for all out going UI events. These will be pulled and processed by the main ICU process.
        sink (SinkRemote): event buffer for all in coming UI events. These events are commands for the UI (e.g. draw).
        config (dict): UI configuration.
    """
    event_system = EventSystem()
    event_system.add_source(sink) # remotely this is a sink but here it is a source (events will be pulled from the RemoteSink by get_events)

    window = new_window(config['window_position'], config['window_size'])
    ui_canvas = Canvas(window)
    event_system.add_sink(ui_canvas) # subscriptions are already handled

    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                source.source("UI::CONTROL::QUIT", {}) # events will be pulled remotely from this source
                running = False
        
        event_system.pull_events()
        event_system.publish()

        # Draw shapes
        pygame.display.flip()

    pygame.quit()    
    event_system.close()
