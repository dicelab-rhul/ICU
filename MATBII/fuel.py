import tkinter as tk
import random

from .constants import BACKGROUND_COLOUR
from .event import Event, EventCallback, EVENT_SINKS




class FuelTank:

    def __init__(self, parent, capacity):
        pass

class Pump(EventCallback, tk.Label):

    ON_COLOUR = 'green'
    OFF_COLOUR = BACKGROUND_COLOUR
    FAIL_COLOUR = 'red'
    COLOURS = [ON_COLOUR, OFF_COLOUR, FAIL_COLOUR]

    def __init__(self, parent, name, text):
        super(EventCallback, self).__init__()
        super(Pump, self).__init__(parent, text=text, bg='red')
        self.__state = 0

        self.bind("<Button-1>", self.click_callback)

    def click_callback(self, *args):
        print('click')

class FuelWidget(tk.Canvas):

    def __init__(self, parent, width, height):
        super(FuelWidget, self).__init__(parent, width=width, height=height, bg=BACKGROUND_COLOUR)
        self.pumpAB = Pump(self, str(0), "pump!")
        self.pumpAB.pack()
        self.create_window(100, 100, window=self.pumpAB)




