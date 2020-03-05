import tkinter as tk

from . import panel
from .constants import MAIN_BANNER_COLOUR, MAIN_BANNER_HEIGHT, BACKGROUND_COLOUR

class MainPanel(tk.Frame):

    def __init__(self, parent):
        super(MainPanel, self).__init__(parent, bg=BACKGROUND_COLOUR)
        #create banners
        self.top_frame = tk.Frame(self, bg=BACKGROUND_COLOUR)
        self.top_frame.grid(row=0,column=0,sticky='we')
        self.top_banner = tk.Canvas(self.top_frame, bg = MAIN_BANNER_COLOUR, height=MAIN_BANNER_HEIGHT)
        self.top_banner.pack(fill=tk.X)

        self.bottom_frame = tk.Frame(self, bg=BACKGROUND_COLOUR)
        self.bottom_frame.grid(row=1,column=0, sticky='we')
        self.bottom_banner = tk.Canvas(self.bottom_frame, bg = MAIN_BANNER_COLOUR, height=MAIN_BANNER_HEIGHT)
        self.bottom_banner.pack(fill=tk.X)

    @property
    def top(self):
        return self.top_frame

    @property
    def bottom(self):
        return self.bottom_frame

    def highlight(self):
        print("TODO highlight main panel?")