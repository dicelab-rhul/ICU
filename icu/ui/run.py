from dataclasses import dataclass
import multiprocessing
import pygame

from .window import new_window, get_window_info
from ..event2 import EventSystem, SinkBase, SourceLocal, SinkLocal, DELIMITER
from .draw import draw_circle, draw_rectangle, draw_line, clear

from .commands import *


from .task import SystemTask


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
        }

    def update(self, pygame_event):
        if pygame_event.type in self._event_gen:
            self._event_gen[pygame_event.type](pygame_event)

class ExternalSource(SinkLocal):
    
    def __init__(self, external_source):
        super().__init__(external_source.put)

    def get_subscriptions(self):
        return ["UI::*"] # all UI events

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

    system_task = SystemTask(window, (0,0), (400,600))
    for widget in system_task.children.values(): # move this to Widget class?
        event_system.add_source(widget)
        event_system.add_sink(widget)

    
    running = True
    while running:
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
        clear(window, dict(color="black"))
        system_task.update()
        ui_canvas.update()


    pygame.quit()    
    event_system.close()
