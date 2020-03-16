import tkinter as tk

from collections import OrderedDict

def quit():
    global finish
    finish = True
    root.destroy()

from ICU.component import SimpleComponent, CanvasWidget, BoxComponent


root = tk.Tk()

root.title("Test")
root.protocol("WM_DELETE_WINDOW", quit)
root.geometry('%dx%d+%d+%d' % ( 600, 600, 1200, 100))

canvas = tk.Canvas(root, width=500, height=500, bg='white')
canvas.pack()

cw = CanvasWidget(canvas)
c1 = BoxComponent(canvas)
c1.size = 0.5,0.5
c1.x = 0.5
c1.y = 0.5


cw.components['c1'] = c1

cw.size = (100,100)


cw.debug()

def resize(*args):
    cw.size=(200,200)
    cw.debug()

root.after(1000, resize)
root.mainloop()