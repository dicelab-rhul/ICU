import tkinter as tk
import math


from icu.eyetracking import eyetracker, filter
from icu.event import EventCallback, initialise_global_event_callback

initialise_global_event_callback()

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

canvas = tk.Canvas(root, bg="white")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()


px, py = (100, 100)
x, y = px, py
radius = 50
pointer = canvas.create_oval(
    x - radius, y - radius, x + radius, y + radius, fill="red", width=0
)


def update(x, y):
    if not (math.isnan(x) or math.isnan(y)):
        canvas.coords(pointer, x - radius, y - radius, x + radius, y + radius)
    print(x, y)


def repeat(ms, fun):
    fun()
    root.after(ms, lambda: repeat(ms, fun))


def track(self, *args, **kwargs):
    # print(args, kwargs)
    # update(-root.winfo_x() + kwargs['x'] + canvas.winfo_width()/2, -root.winfo_y() - kwargs['y'] + canvas.winfo_height()/2)
    # update(-root.winfo_x() + kwargs['x'] + screen_width/2, -root.winfo_y() - kwargs['y'] + screen_height/2)
    # print(kwargs)
    update(kwargs["x"], kwargs["y"])


EventCallback.source = track  # monkey patch for testing

# repeat(100, lambda : update(px + 1, py + 1))
calibrate = False
filter_n = 10
filter_threshold = 100

et = eyetracker(root, filter=filter.TobiiFilter(filter_n, filter_threshold))
et.start()

canvas.pack(fill="both", expand=True)
root.mainloop()
