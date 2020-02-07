#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tkinter as tk
from threading import Thread 



from . import constants
from . import event
from . import panel
from . import system_monitor
from . import main_panel
from . import tracking
from . import fuel

__all__ = ('panel', 'system_monitor', 'constants', 'event', 'main_panel', 'tracking', 'fuel')

global finish

finish = False

class Sleep:

    def __init__(self, wait):
        self.wait = wait
       
    def __enter__(self):
        self.start = self.__t()
        self.finish = self.start + self.wait
    
    def __exit__(self, type, value, traceback):
        while self.__t() < self.finish:
            time.sleep(1./1000.)

    def __t(self):
        return int(round(time.time() * 1000))

class TKSchedular:

    def __init__(self):
        pass

    def schedule(self, generator, sleep=1000, repeat=True):
        if repeat:
            self.after(sleep, self.gen_repeat, generator, sleep)
        else:
            self.after(sleep, self.gen, generator)

    def gen(self, e):
        e = next(generator)
        event.EVENT_SINKS[e.args[0]].sink(e)
        event.GLOBAL_EVENT_CALLBACK(e)

    def gen_repeat(self, generator, sleep):
        e = next(generator)
        self.after(sleep, self.gen_repeat, generator, sleep)
        event.EVENT_SINKS[e.args[0]].sink(e)
        event.GLOBAL_EVENT_CALLBACK(e)

    def after(self, sleep, fun, *args):
        global finish
        if not finish:
            root.after(sleep, fun, *args)

def quit():
    global finish
    finish = True
    root.destroy()

root = tk.Tk()
root.title("MATB-II")
root.protocol("WM_DELETE_WINDOW", quit)

main = main_panel.MainPanel(root)

system_monitor_widget = system_monitor.SystemMonitorWidget(main.top, width=constants.SYSTEM_MONITOR_WIDTH, 
                                                     height=constants.SYSTEM_MONITOR_HEIGHT)

system_monitor_widget.pack(side='left')

tracking_widget = tracking.TrackingWidget(main.top, size=400)
tracking_widget.pack(side='left')

resource_management_widget = fuel.FuelWidget(main.bottom, width=500, height=200)
resource_management_widget.pack(side='left')

main.pack()

event_scheduler = TKSchedular()
#event_scheduler.schedule(system_monitor.WarningLightEventGenerator(), sleep=1000, repeat=True)
#event_scheduler.schedule(system_monitor.ScaleEventGenerator(), sleep=500)
#event_scheduler.schedule(tracking.TrackingEventGenerator(),sleep=100, repeat=True)

if constants.JOYSTICK:
    print("TODO are we using a joystick!?")
else:
    #there is a delay, it needs an press/release handler to work smoothly...
    root.bind("<Left>",     lambda *args: tracking_widget.left_callback(*args))
    root.bind("<Right>",    lambda *args: tracking_widget.right_callback(*args))
    root.bind("<Up>",       lambda *args: tracking_widget.up_callback(*args))
    root.bind("<Down>",     lambda *args: tracking_widget.down_callback(*args))

    #TODO record joystick data (send the event to somewhere else aswell!)
    #TODO record the target position at a given time interval, generate an event



root.mainloop()