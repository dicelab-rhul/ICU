import tkinter as tk

from . import panel
from .constants import MAIN_BANNER_COLOUR, MAIN_BANNER_HEIGHT, BACKGROUND_COLOUR

from .component import CanvasWidget

from .overlay import Overlay

class MainPanel(tk.Canvas):

    def __init__(self, parent, width, height):
        super(MainPanel, self).__init__(parent, width=width, height=height, bg='blue')
        #create banners
        self.__main = CanvasWidget(self, x=10, y=10, width=width-20, height=width-20)

        self.top_frame = CanvasWidget(self)
        self.bottom_frame = CanvasWidget(self)
        self.__main.components['top'] = self.top_frame
        self.__main.components['bottom'] = self.bottom_frame
        
        self.__main.layout_manager.split('top', 'Y')
        self.__main.layout_manager.split('bottom', 'Y')

        self.__main.layout_manager.fill('top', 'X')
        self.__main.layout_manager.fill('bottom', 'X')

        self.__overlay = None

    def resize(self, event):
        #print(event.width, event.height)
        if self.winfo_width() != event.width or self.winfo_height() != event.height:
            self.config(width=event.width, height=event.height)
            self.__main.size = (event.width-20, event.height-20)
            self.pack()

    def overlay(self, component):
        self.__overlay = Overlay(self, component)
        self.__overlay.front()
        self.__main.components['overlay'] = self.__overlay

    @property
    def top(self):
        return self.top_frame

    @property
    def bottom(self):
        return self.bottom_frame