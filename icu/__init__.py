#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tkinter as tk
import os
import atexit

from pprint import pprint
import random
import traceback

from multiprocessing import Pipe

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
from . import process

__all__ = ('panel', 'system_monitor', 'constants', 'event', 'main_panel', 'tracking', 'fuel_monitor', 'process')


# extend these classes externally to add them (send and receive events to/from ICU system)
ExternalEventSink = event.ExternalEventSink
ExternalEventSource = event.ExternalEventSource

def get_event_sources():
    return event.get_event_sources()

def get_event_sinks():
    return event.get_event_sinks()

def get_external_event_sinks():
    return event.GLOBAL_EVENT_CALLBACK.external_sinks

def get_external_event_sources():
    return event.GLOBAL_EVENT_CALLBACK.external_sources

def start(sinks=[], sources=[]):
    """ Start ICU as a seperate process. 
    
    Args:
        sinks (list, optional): [description]. Defaults to [].
        sources (list, optional): [description]. Defaults to [].
    """
    from multiprocessing import Process, Lock
    from .process import PipedMemory



    send, receive = PipedMemory(event_sinks=None, event_sources=None) #TODO more?
    send.aquire() #this will block the current process from accessing memory attributes until ICU has finished loading

    p = Process(target=run, args=(send, sinks, sources))
    p.daemon = True 
    p.start()

    #TODO wait until intial values have been set

    return p, receive

def run(shared, sinks=[], sources=[]):
    """ Starts the ICU system. Call blocks until the GUI is closed.

    Args:
        shared: shared memory - one end of a pipe that can receive data, used to expose various useful attributes about ICU.
        sinks (list, optional): A list of external sinks, used to receive events from the ICU system. Defaults to [].
        sources (list, optional): A list of external sources, used to send events to the ICU system. Defaults to [].
    """

    #os.system('xset r off') #problem with key press/release otherwise
    eyetracker = None #prevent exit errors
    #ensure the program exits properly
    def exit_handler():
        if eyetracker is not None:
            eyetracker.close()
        os.system('xset r on') #back to how it was before?
        shared.release()
        event.close() #close all external sources/sink buffers

        print("ICU EXIT")

    try:

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

        event.event_scheduler.schedule(system_monitor.WarningLightEventGenerator(), sleep=1000)
        event.event_scheduler.schedule(system_monitor.ScaleEventGenerator(), sleep=1000)
        event.event_scheduler.schedule(tracking.TrackingEventGenerator(), sleep=100)

        #This is just for testing
        def highlight_event_generator():
            import random
            while True:
                dst = random.choice(list(highlight.all_highlights().keys()))
                yield event.Event('high_light_generator', dst, label='highlight', value=random.choice([True,False]))

        #event.event_scheduler.schedule(highlight_event_generator(), sleep=1000)

        if constants.JOYSTICK:
            global_key_hander = keyhandler.JoyStickHandler(root)
        else:
            global_key_handler = keyhandler.KeyHandler(root)

        #EVENT SCHEDULAR FOR KEYBOARD INPUT (checks every 50ms whether a key is pressed)
        event.event_scheduler.schedule(tracking.KeyEventGenerator(global_key_handler), sleep=50)

        # ================= EYE TRACKING ================= 

        eyetracker = None
        if constants.EYETRACKING: #TODO move this to start?
            eyetracker = eyetracking.eyetracker(root, sample_rate=100, stub=True)
            eyetracker.start()

        pprint(event.get_event_sinks()) #TODO remove
  

        atexit.register(exit_handler) 

        #add any external event sinks/sources
        for sink in sinks:
            event.add_event_sink(sink)
        for source in sources:
            event.add_event_source(source)
        
        # update shared memory
        shared.event_sinks = get_event_sinks()
        shared.event_sources = get_event_sources()
        shared.release() # the parent process can now access attributes in shared memory
        
        root.mainloop()

    except:
        traceback.print_exc()
    finally:
        exit_handler()