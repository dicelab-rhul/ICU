#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tkinter as tk
import os
import atexit

from pprint import pprint
import random
import copy
import traceback
from types import SimpleNamespace
from itertools import cycle

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
from . import generator
from . import config as configuration

__all__ = ('panel', 'system_monitor', 'constants', 'event', 'main_panel', 'tracking', 'fuel_monitor', 'process')


# extend these classes externally to add them (send and receive events to/from ICU system)
ExternalEventSink = event.ExternalEventSink
ExternalEventSource = event.ExternalEventSource

# some constants ... 
NAME = "ICU"
#TODO others?



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

    send, receive = PipedMemory(event_sinks=None, event_sources=None, config=None, window_properties=None) #TODO more?
    send.aquire() #this will block the current process from accessing memory attributes until ICU has finished loading

    p = Process(target=run, args=(send, sinks, sources))
    p.daemon = True 
    p.start()

    return p, receive

global config
config = None

def run(shared=None, sinks=[], sources=[], config_file=os.path.split(__file__)[0]):
    """ Starts the ICU system. Call blocks until the GUI is closed.

    Args:
        shared: shared memory - one end of a pipe that can receive data, used to expose various useful attributes in ICU.
        sinks (list, optional): A list of external sinks, used to receive events from the ICU system. Defaults to [].
        sources (list, optional): A list of external sources, used to send events to the ICU system. Defaults to [].
    """
    print("USING CONFIG FILE: {0}".format(config_file))

    global config # this is used in other places and should be accessible
    config = SimpleNamespace(**configuration.load(config_file)) #load local config file
    
    pprint(config.__dict__)


    config_schedule = SimpleNamespace(**config.schedule)
    window_properties = {}
                         
                         



    #os.system('xset r off') #problem with key press/release otherwise
    eyetracker = None #prevent exit errors

    #ensure the program exits properly
    def exit_handler():
        if eyetracker is not None:
            eyetracker.close() #close eye tracker if it was used
        os.system('xset r on') #back to how it was before? TODO find a better fix for this, it is not an issue on windows (test on macos)
        if shared is not None:
            shared.release() #release shared process memory (if it was used)
        event.close() #close all external sources/sink buffers
        print("ICU EXIT") #TODO remove

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
                self.root.bind("<Escape>", self.toggle)
                self.root.bind("<F11>", self.toggle)
            def toggle(self, event):
                self.fullscreen = not self.fullscreen
                root.attributes("-fullscreen", self.fullscreen)

        root = tk.Tk()
        full_screen = None

        if config.screen_aspect is not None: 
            root.aspect(*config.screen_aspect, *config.screen_aspect)
       
        if config.screen_resizable:
            full_screen = Fullscreen(root, config.screen_full)
            root.minsize(*config.screen_min_size)
            root.maxsize(*config.screen_max_size) 
        else:
            root.resizable(0,0)
        
        root.title("ICU")
        root.protocol("WM_DELETE_WINDOW", quit)
        root.geometry('%dx%d+%d+%d' % (config.screen_width, config.screen_height, config.screen_x, config.screen_y))
  



        event.tk_event_schedular(root) #initial global event schedular
        
        main = main_panel.MainPanel(root, width=config.screen_width, height=config.screen_height)
        root.bind("<Configure>", main.resize) #for resizing the window
        




        # ==================== SYSTEM MONITOR WIDGET ==================== #

        task = SimpleNamespace(**config.task)

        if task.system:
            system_monitor_widget = system_monitor.SystemMonitorWidget(main, copy.deepcopy(config.__dict__), width=constants.SYSTEM_MONITOR_WIDTH, height=constants.SYSTEM_MONITOR_HEIGHT)
            main.top_frame.components['system_monitor'] = system_monitor_widget
            main.top_frame.layout_manager.fill('system_monitor', 'Y')
            main.top_frame.layout_manager.split('system_monitor', 'X', 250/800)

            #main.top_frame.components['top_padding'] = component.EmptyComponent()
            #main.top_frame.layout_manager.split('top_padding', 'X', prop=0.3)

        if task.track:
            tracking_widget = tracking.Tracking(main, copy.deepcopy(config.__dict__), size=config.screen_height/2) #scaled anyway
            main.top_frame.components['tracking'] = tracking_widget
            main.top_frame.layout_manager.fill('tracking', 'Y')
            main.top_frame.layout_manager.split('tracking', 'X', 550/800)
            #tracking_widget.debug()
            main.top_frame.layout_manager.anchor('tracking', 'E')

        if task.fuel:
            main.bottom_frame.components['coms'] = component.EmptyComponent()
            main.bottom_frame.layout_manager.split('coms', 'X', prop=250/800)

            fuel_monitor_widget = fuel_monitor.FuelWidget(main, copy.deepcopy(config.__dict__), width=constants.FUEL_MONITOR_WIDTH, height=constants.FUEL_MONITOR_HEIGHT)
            main.bottom_frame.components['fuel_monitor'] = fuel_monitor_widget
            main.bottom_frame.layout_manager.split('fuel_monitor', 'X', prop=550/800)
            main.bottom_frame.layout_manager.fill('fuel_monitor', 'Y')

            

        
        #arrow = main.create_polygon(-20,-10, 0,-10, 0,-20, 10,0,0,20, 0,10, -20,10,fill='red', width=0) #TODO components with polygons

        if config.overlay['arrow']:
            circle = main.create_oval(10,10,30,30, fill='red', width=0)
            main.overlay(circle)

        if config.overlay['transparent']:
            pass #TODO

        if config.overlay['outline']:
            pass #TODO
        
        main.pack()

        # ==================== SYSTEM MONITOR EVENT SCHEDULES ==================== #
        if task.system:
            task_system_monitor(config)

        # ====================   TRACKING EVENT SCHEDULES     ==================== #
        if task.track:
            task_tracking(config)
            # EVENT SCHEDULER FOR KEYBOARD INPUT (checks every 50ms whether a key is pressed)
            if config.input['joystick']:
                global_key_hander = keyhandler.JoyStickHandler(root)
            else:
                global_key_handler = keyhandler.KeyHandler(root)
            event.event_scheduler.schedule(tracking.KeyEventGenerator(global_key_handler), sleep=cycle([50]))

        # ==================== FULE MONITOR EVENT SCHEDULES   ==================== #
        if task.fuel:
            task_fuel_monitor(config)
            
        # ==================== ============================== ==================== #

        #event.event_scheduler.schedule(tracking.TrackingEventGenerator(), sleep=config.schedule_tracking)

        #This is just for testing
        def highlight_event_generator():
            import random
            while True:
                dst = random.choice(list(highlight.all_highlights().keys()))
                yield event.Event('high_light_generator', dst, label='highlight', value=random.choice([True,False]))
        event.event_scheduler.schedule(highlight_event_generator(), sleep=cycle([1000]))
       

        # ================= EYE TRACKING ================= 

        eyetracker = None
        if config.input['eye_tracker']:
            filter = eyetracking.filter.TobiiFilter(10, 70) #some default thing...
            eyetracker = eyetracking.eyetracker(root, filter=filter, sample_rate=100, stub=True)
            eyetracker.start()

        #pprint(event.get_event_sinks()) #TODO remove
  

        atexit.register(exit_handler) 

        #add any external event sinks/sources
        for sink in sinks:
            event.add_event_sink(sink)
        for source in sources:
            event.add_event_source(source)

        if shared is not None:
            # update shared memory
            shared.event_sinks = get_event_sinks()
            shared.event_sources = get_event_sources()
            shared.config = config
            # get all window properties
            root.update_idletasks() 
            shared.window_properties = dict(window = dict(position = (root.winfo_rootx(), root.winfo_rooty()),
                                                          size     = (root.winfo_width(), root.winfo_height())),
                                            tracking = dict(position = tracking_widget.position,
                                                            size     = tuple([min(tracking_widget.size)]*2)), #TODO fix this in tracking widget...?
                                            system   = dict(position = system_monitor_widget.position,
                                                            size     = system_monitor_widget.size,
                                                            **{k:dict(position=v.position, size=v.size) for k,v in system_monitor_widget.warning_lights.items()},
                                                            **{k:dict(position=v.position, size=v.size) for k,v in system_monitor_widget.scales.items()}),
                                            fuel     = dict(position = fuel_monitor_widget.position,
                                                            size     = fuel_monitor_widget.size,
                                                            **{k:dict(position=v.position, size=v.size) for k,v in fuel_monitor_widget.tanks.items()},
                                                            **{k:dict(position=v.position, size=v.size) for k,v in fuel_monitor_widget.pumps.items()})
                                            )
            
            #root.bind( "<Configure>", d ) update window properties ???

            shared.release() # the parent process can now access attributes in shared memory
        
        root.mainloop()

    except:
        traceback.print_exc()
    finally:
        exit_handler()

        #save state
        import pickle






def task_system_monitor(config):
    """ Set up system monitoring task event schedules

    Args:
        config (SimpleNamespace): configuration options
    """
    scales = system_monitor.Scale.all_components()
    for scale in scales:
        schedule = config.schedule.get(scale, configuration.default_scale_schedule())
        event.event_scheduler.schedule(generator.ScaleEventGenerator(scale), sleep=schedule)
        #print(scale, schedule)

    warning_lights = system_monitor.WarningLight.all_components()
    for warning_light in warning_lights:
        schedule = config.schedule.get(warning_light, configuration.default_warning_light_schedule())
        event.event_scheduler.schedule(generator.WarningLightEventGenerator(warning_light), sleep=schedule)
        #print(scale, schedule)

def task_tracking(config):
    """ Set up tracking task event schedules

    Args:
        config (SimpleNamespace): configuration options
    """
    targets = tracking.Tracking.all_components()
    for target in targets:
        schedule = config.schedule.get(target, configuration.default_target_schedule())
        event.event_scheduler.schedule(generator.TargetEventGenerator(target, **config.__dict__[target]), sleep=schedule)

def task_fuel_monitor(config):
    """ Set up fuel monitoring task event scheduless

    Args:
        config (SimpleNamespace): configuration options
    """
    pumps = fuel_monitor.Pump.all_components()
    for pump in pumps:
        schedule = config.schedule.get(pump, configuration.default_pump_schedule())
        event.event_scheduler.schedule(generator.PumpEventGenerator(pump, False), sleep=schedule)


