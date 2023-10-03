import pygame
import time

from icu.event2.event import SourceLocal

from icu.ui.utils.math import Point
from icu.ui.widget import Widget
from icu.ui.window import Window

from icu.ui.draw import fill


class Root(Widget):
    def __init__(self, event_system):
        super().__init__(name="UI")
        self.running = False
        self._event_system = event_system
        self._clock = pygame.time.Clock()
        self._window = Window()
        self._window.register(event_system)

    @property
    def position(self):
        return Point(0, 0)

    def size(self):
        return self._window.size

    @property
    def canvas(self):
        return self._window.window

    def start_pygame_event_loop(self):
        running = True
        while running:
            dt = self._clock.tick(60)
            events = pygame.event.get()
            for event in events:
                self._window.update(event)
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.WINDOWRESIZED:
                    self.draw(self.canvas)  # update/redraw everything
            self.draw(self.canvas)
            self.update_event_system()
            yield dt

        pygame.quit()
        self._event_system.close()

    def draw(self, canvas):
        pygame.display.flip()
        fill(canvas, self._window.background_color)
        for child in self.children.values():
            child.draw(canvas)

    def update_event_system(self):
        self._event_system.pull_events()
        self._event_system.publish()
