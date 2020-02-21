#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tkinter as tk

from . import constants
from . import event
from . import panel
from . import system_monitor
from . import main_panel
from . import tracking
from . import fuel_monitor

__all__ = ('panel', 'system_monitor', 'constants', 'event', 'main_panel', 'tracking', 'fuel_monitor')



event.GLOBAL_EVENT_CALLBACK.add_event_callback(lambda *args: print("callback: ", *args))

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


def quit():
    global finish
    finish = True
    root.destroy()

root = tk.Tk()
root.title("MATB-II")
root.protocol("WM_DELETE_WINDOW", quit)
root.geometry('%dx%d+%d+%d' % (1000, 1000, 1000, 500))

event.tk_event_schedular(root) #initial global event schedular

main = main_panel.MainPanel(root)

system_monitor_widget = system_monitor.SystemMonitorWidget(main.top, width=constants.SYSTEM_MONITOR_WIDTH, 
                                                                     height=constants.SYSTEM_MONITOR_HEIGHT)

system_monitor_widget.pack(side='left')

tracking_widget = tracking.TrackingWidget(main.top, size=400)
tracking_widget.pack(side='left')

fuel_monitor_widget = fuel_monitor.FuelWidget(main.bottom, width=constants.FUEL_MONITOR_WIDTH, 
                                                           height=constants.FUEL_MONITOR_HEIGHT)
fuel_monitor_widget.pack(side='left')

main.pack()

event.event_scheduler.schedule(system_monitor.WarningLightEventGenerator(), sleep=1000, repeat=True)
event.event_scheduler.schedule(system_monitor.ScaleEventGenerator(), sleep=1000)
event.event_scheduler.schedule(tracking.TrackingEventGenerator(),sleep=1000, repeat=True)


if constants.JOYSTICK:
    print("TODO are we using a joystick!?")
else:
    #there is a delay, it needs an press/release handler to work smoothly and to handle simultanneous presses...
    root.bind("<Left>",     lambda *args: tracking_widget.left_callback(*args))
    root.bind("<Right>",    lambda *args: tracking_widget.right_callback(*args))
    root.bind("<Up>",       lambda *args: tracking_widget.up_callback(*args))
    root.bind("<Down>",     lambda *args: tracking_widget.down_callback(*args))

    #TODO record joystick data (send the event to somewhere else aswell!)
    #TODO record the target position at a given time interval, generate an event



root.mainloop()