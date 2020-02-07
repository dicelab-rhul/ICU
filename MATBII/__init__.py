#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tkinter as tk
from threading import Thread 



from . import constants
from . import event
from . import panel
from . import system_monitor

__all__ = ('panel', 'system_monitor', 'constants', 'event')

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

    def gen_repeat(self, generator, sleep):
        e = next(generator)
        self.after(sleep, self.gen_repeat, generator, sleep)
        event.EVENT_SINKS[e.args[0]].sink(e)

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

main_panel = tk.Frame(root)

system_monitor_widget = system_monitor.SystemMonitor(main_panel, width=constants.SYSTEM_MONITOR_WIDTH, 
                                                     height=constants.SYSTEM_MONITOR_HEIGHT)
system_monitor_widget.pack()
main_panel.pack()

event_scheduler = TKSchedular()
event_scheduler.schedule(system_monitor.WarningLightEventGenerator(), sleep=1000, repeat=True)
event_scheduler.schedule(system_monitor.ScaleEventGenerator(), sleep=500)

root.mainloop()