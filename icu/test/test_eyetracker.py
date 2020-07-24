import tkinter as tk

from icu.eyetracking import eyetracker, filter
from icu.event import EventCallback

root = tk.Tk()
fullscreen = False
def toggle_fullscreen(*args, **kwargs):
    global fullscreen
    fullscreen = not fullscreen
    root.attributes("-fullscreen", fullscreen)
root.attributes("-fullscreen", fullscreen)
root.bind("<Escape>", toggle_fullscreen)
root.bind("<F11>", toggle_fullscreen)
root.title("TestEyeTracker")
root.protocol("WM_DELETE_WINDOW", root.destroy)

canvas = tk.Canvas(root)

px, py = (100,100)
x, y = px, py
radius = 10
pointer = canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill="red", width=0)

def update(x,y):
    global px, py
    dx, dy = x - px, y - py
    px, py = x, y
    canvas.move(pointer, dx, dy)

def repeat(ms, fun):
    fun()
    root.after(ms, lambda: repeat(ms, fun))

def track(self, *args, **kwargs):
    print(args, kwargs)
    update(kwargs['x'], -kwargs['y'])

EventCallback.source = track #monkey patch for testing


#repeat(100, lambda : update(px + 1, py + 1))
calibrate = True
filter_n = 5
filter_threshold = 70

et = eyetracker(root, filter=filter.TobiiFilter(filter_n, filter_threshold), calibrate=calibrate)
et.start()

#canvas.pack(fill="both", expand=True)
#root.mainloop()