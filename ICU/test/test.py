import tkinter as tk

from collections import OrderedDict



def quit():
    global finish
    finish = True
    root.destroy()


root = tk.Tk()

root.title("Test")
root.protocol("WM_DELETE_WINDOW", quit)
root.geometry('%dx%d+%d+%d' % (1000, 1000, 1000, 500))

canvas = tk.Canvas(root, width=500, height=500, bg='white')
canvas.pack()

class CanvasBox:

    def __init__(self, canvas, width, height, components={}, background_colour=None, outline_colour=None, outline_thickness=None):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.__x = 0
        self.__y = 0

        self.__layers = []

        self.components = dict(**components)
        self.__component_order = [c for c in self.components]

        self.components['background'] = self.canvas.create_rectangle(0, 0, width, height,width=2) # background...?
        self.__component_order.insert(0, 'background')
        

        self.__debug = None
        #self.components['__debug'] = None

    @property
    def background(self):
        return self.components['background']

    @property
    def background_colour(self):
        return self.canvas.itemcget(self.background, "fill")

    @background_colour.setter
    def background_colour(self, value):
        self.canvas.itemconfigure(self.background, fill=value)

    @property
    def outline_thickness(self):
        return self.canvas.itemcget(self.background, "width") 

    @outline_thickness.setter
    def outline_thickness(self, value):
        self.canvas.itemconfigure(self.background, width=value)

    @property
    def outline_colour(self):
        return self.canvas.itemcget(self.background, "outline") 

    @outline_colour.setter
    def outline_colour(self, value):
        self.canvas.itemconfigure(self.background, outline=value)

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, value):
        dy = value - self.__y
        self.move(0, dy)

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, value):
        dx = value - self.__x
        self.move(dx, 0)

    def move(self, dx, dy):
        self.__x += dx
        self.__y += dy
        for component in self.__component_order:
            self.canvas.move(self.components[component], dx, dy)
        if self.__debug is not None:
            self.canvas.move(self.__debug, dx, dx)

    def scale(self, x, y):
        raise NotImplementedError("TODO...")

    def debug_outline(self):
        print(self.x, self.y, self.x+self.width, self.y+self.height)
        self.__debug = self.canvas.create_rectangle(self.x, self.y, self.x+self.width, self.y+self.height, width=1, outline='pink')

box1 = CanvasBox(canvas, 50, 100)

box1.move(20,20)
box1.x += 10
box1.y -= 60
box1.debug_outline()

def c_background_colour(*args):
    box1.background_colour = 'red'

def c_outline_thickness(*args):
    box1.outline_thickness = 10

def c_outline_colour(*args):
    box1.outline_colour = 'blue'

root.bind("<a>", c_background_colour)
root.bind("<b>", c_outline_thickness)
root.bind("<c>", c_outline_colour)

root.mainloop()