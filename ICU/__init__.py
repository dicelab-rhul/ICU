#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tkinter as tk
import os
import atexit

from pprint import pprint
import random

from . import constants
from . import event
from . import panel
from . import system_monitor
from . import main_panel
from . import tracking
from . import fuel_monitor
from . import keyhandler
from . import eyetracking
from . import component
from . import highlight



__all__ = ('panel', 'system_monitor', 'constants', 'event', 'main_panel', 'tracking', 'fuel_monitor')

def run():
    print("RUN!")
    os.system('xset r off') #problem with key press/release otherwise

    event.GLOBAL_EVENT_CALLBACK.add_event_callback(lambda *args: print("callback: ", *args))

    def quit():
        global finish
        finish = True
        root.destroy()

    class Fullscreen:

        def __init__(self, root, fullscreen=False):
            self.root = root
            self.fullscreen = fullscreen
            root.attributes("-fullscreen", self.fullscreen)
            print("full screen")
            self.root.bind("<Escape>", self.toggle)
            self.root.bind("<F11>", self.toggle)

        def toggle(self, event):
            self.fullscreen = not self.fullscreen
            root.attributes("-fullscreen", self.fullscreen)


    root = tk.Tk()
    full_screen = Fullscreen(root, False)

    root.title("MATB-II")
    root.protocol("WM_DELETE_WINDOW", quit)
    root.geometry('%dx%d+%d+%d' % (1000, 1000, 500, 0))

    event.tk_event_schedular(root) #initial global event schedular
    
    main = main_panel.MainPanel(root, width=500, height=500)
    root.bind("<Configure>", main.resize) #for resizing the window
    
    system_monitor_widget = system_monitor.SystemMonitorWidget(main, width=constants.SYSTEM_MONITOR_WIDTH, height=constants.SYSTEM_MONITOR_HEIGHT)
    main.top_frame.components['system_monitor'] = system_monitor_widget
    main.top_frame.layout_manager.fill('system_monitor', 'Y')
    main.top_frame.layout_manager.split('system_monitor', 'X')


    tracking_widget = tracking.TrackingWidget(main, size=400)
    main.top_frame.components['tracking'] = tracking_widget
    main.top_frame.layout_manager.fill('tracking', 'Y')
    main.top_frame.layout_manager.split('tracking', 'X')


    fuel_monitor_widget = fuel_monitor.FuelWidget(main, width=constants.FUEL_MONITOR_WIDTH, height=constants.FUEL_MONITOR_HEIGHT)
    main.bottom_frame.components['fuel_monitor'] = fuel_monitor_widget
    main.bottom_frame.layout_manager.fill('fuel_monitor', 'X')
    main.bottom_frame.layout_manager.fill('fuel_monitor', 'Y')
    
    main.overlay(main.create_oval(10,10,30,30, fill='red', width=0))
    
    main.pack()

    #event.event_scheduler.schedule(system_monitor.WarningLightEventGenerator(), sleep=1000, repeat=True)
    #event.event_scheduler.schedule(system_monitor.ScaleEventGenerator(), sleep=1000)
    #event.event_scheduler.schedule(tracking.TrackingEventGenerator(), sleep=100, repeat=True)

    #This is just for testing
    def highlight_event_generator():
        import random
        while True:
            dst = random.choice(list(highlight.all_highlights().keys()))
            yield event.Event('high_light_generator', dst, label='highlight', value=random.choice([True,False]))

    #event.event_scheduler.schedule(highlight_event_generator(), sleep=1000, repeat=True)

    #print("ALL COMPONENTS: ")
    #pprint(component.all_components())



    if constants.JOYSTICK:
        global_key_hander = keyhandler.JoyStickHandler(root)
    else:
        global_key_handler = keyhandler.KeyHandler(root)

    event.event_scheduler.schedule(tracking.KeyEventGenerator(global_key_handler), sleep=50, repeat=True)

    # ================= EYE TRACKING ================= 

    eyetracker = None
    if constants.EYETRACKING:
        eyetracker = eyetracking.eyetracker(root, sample_rate=100, stub=True)
        eyetracker.start()
    
    pprint(event.EVENT_SINKS)

    #ensure the program exits properly
    def exit_handler():
        if eyetracker is not None:
            eyetracker.close()
        os.system('xset r on') #back to how it was before?

    atexit.register(exit_handler) 

    root.mainloop()

    if eyetracker is not None:
        eyetracker.close()






