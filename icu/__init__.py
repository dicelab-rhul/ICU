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

import logging
logging.basicConfig() 
#logging.root.setLevel(logging.DEBUG)
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

from multiprocessing import Pipe
from itertools import cycle

import math


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
from . import log


__all__ = ('panel', 'system_monitor', 'constants', 'event', 'main_panel', 'tracking', 'fuel_monitor', 'process')

DEFAULT_CONFIG_FILE = os.path.join(os.path.split(__file__)[0], 'config.json')
DEFAULT_LOG_FILE = os.path.join(".", 'event_log.txt')

def get_parser(): # command line arguments for ICU
    import argparse
    class PathAction(argparse.Action):
        def __call__(self, parser, namespace, path, option_string=None):
            setattr(namespace, self.dest, os.path.abspath(path))

    parser = argparse.ArgumentParser(description='ICU')
    parser.add_argument('--config', '-c', metavar='C', action=PathAction, type=str, 
            default= DEFAULT_CONFIG_FILE,
            help='path of the config file to use.')
    parser.add_argument('--logger', '-l', metavar='L', action=PathAction, type=str, 
            default= DEFAULT_LOG_FILE,
            help='path of the config file to use.')
    return parser

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

def start(sinks=[], sources=[], **kwargs):
    """ Start ICU as a seperate process. 
    
    Args:
        sinks (list, optional): TODO . Defaults to [].
        sources (list, optional): TODO . Defaults to [].
        config_hook (str): TODO
    """
    from multiprocessing import Process, Lock
    from .process import PipedMemory

    send, receive = PipedMemory(event_sinks=None, event_sources=None, config=None, window_properties=None) #TODO more?
    send.aquire() #this will block the current process from accessing memory attributes until ICU has finished loading

    p = Process(target=run, args=(send, sinks, sources), kwargs=kwargs)
    p.daemon = True 
    p.start()

    return p, receive

#global config
#config = None

def run(shared=None, sinks=[], sources=[], config=None, config_hook=None, logger=None):
    """ Starts the ICU system. Call blocks until the GUI is closed.

    Args:
        shared: shared memory - one end of a pipe that can receive data, used to expose various useful attributes in ICU.
        sinks (list, optional): A list of external sinks, used to receive events from the ICU system. Defaults to [].
        sources (list, optional): A list of external sources, used to send events to the ICU system. Defaults to [].
        config (str): Path of configuration file.
        config_hook (str): file to get configuration information for an external process, this allows configuration to be handled by 
        ICU (written in the same config.json file) and may be made avaliable via shared memory.
        logger (str): name of logger to log ICU events. 
    """
    if config is None:
        config = os.path.join(os.path.split(__file__)[0], 'config.json')
    
    # update config parser using config_hook
    if config_hook is not None:
        configuration.hook(config_hook)

    #global config, this is used in other places and needs to be accessible TODO fix it... ?? 
    config = SimpleNamespace(**configuration.load(config)) #load config file
    
    # initialise global event callback (required for all events to be processed)
    logger = log.get_logger(logger) # get logger for events
    event.initialise_global_event_callback(logger)
    
    #pprint(config.__dict__)

    #config_schedule = SimpleNamespace(**config.schedule)
    window_properties = {}
                         
    eyetracker = None #prevent exit errors

    try:
     

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
        root.lower()
        full_screen = None

        if config.screen_aspect is not None: 
            root.aspect(*config.screen_aspect, *config.screen_aspect)
       
        if config.screen_resizable:
            full_screen = Fullscreen(root, config.screen_full)
            root.minsize(*config.screen_min_size)
            root.maxsize(*config.screen_max_size) 
        else:
            root.resizable(0,0)
        
        class System(event.EventCallback):

            def __init__(self, root, config):
                super(System, self).__init__()
                self.root = root
                event.EventCallback.register(self, "System")
                if config.shutdown > 0:
                    root.after(config.shutdown, self.shutdown)
                    
            def shutdown(self, *args, **kwargs): # WARNING -- GETS CALLED MULTIPLE TIME (sigterm etc)
                #print("SHUTDOWN")

                # subvert the usual scheduling mechanism (otherwise it wont trigger as root is destroyed...)
                if not event.GLOBAL_EVENT_CALLBACK.is_closed: # shutdown has already been called...
                    e = event.Event(self.name, "Global", label="system", command="shutdown")
                    event.GLOBAL_EVENT_CALLBACK.trigger(e)

                if eyetracker is not None:
                    eyetracker.close() #close eye tracker if it was used
                if shared is not None:
                    shared.release() #release shared process memory (if it was used)
                event.close() #close all external sources/sink buffers
                try: 
                    root.destroy()
                except:
                    pass # oh no ...?? 

            def resize(self):
                raise NotImplementedError("TODO - resize events") # TODO move from main_panel.resize?
        
        system = System(root, config) # system commands

        root.title("ICU")
        root.protocol("WM_DELETE_WINDOW", system.shutdown)
        root.geometry('%dx%d+%d+%d' % (config.screen_width, config.screen_height, config.screen_x, config.screen_y))
  
        event.tk_event_schedular(root) #initial global event schedular
         
        main = main_panel.MainPanel(root, width=config.screen_width, height=config.screen_height, background_colour=config.background_colour)
        root.bind("<Configure>", main.resize) #for resizing the window

        task = SimpleNamespace(**config.task)

        if task.system:
            system_monitor_widget = system_monitor.SystemMonitorWidget(main, copy.deepcopy(config.__dict__), width=constants.SYSTEM_MONITOR_WIDTH, height=constants.SYSTEM_MONITOR_HEIGHT)
            main.top_frame.components['system_monitor'] = system_monitor_widget
            main.top_frame.layout_manager.fill('system_monitor', 'Y')
            main.top_frame.layout_manager.split('system_monitor', 'X', 250/800)

            main.top_frame.components['top_padding1'] = component.EmptyComponent()
            main.top_frame.layout_manager.split('top_padding1', 'X', prop=100/800)

        if task.track:
            tracking_widget = tracking.Tracking(main, copy.deepcopy(config.__dict__), size=config.screen_height/2) #scaled anyway
            main.top_frame.components['tracking'] = tracking_widget
            #main.components["top_sep"] = component.EmptyComponent()

            main.top_frame.layout_manager.fill('tracking', 'Y')
            main.top_frame.layout_manager.split('tracking', 'X', 350/800)

            main.top_frame.components['top_padding2'] = component.EmptyComponent()
            main.top_frame.layout_manager.split('top_padding2', 'X', prop=100/800)
            
            #main.top_frame.layout_manager.anchor('tracking', 'E')

        if task.fuel:
            main.bottom_frame.components['coms'] = component.EmptyComponent()
            main.bottom_frame.layout_manager.split('coms', 'X', prop=250/800)

            fuel_monitor_widget = fuel_monitor.FuelWidget(main, copy.deepcopy(config.__dict__), width=constants.FUEL_MONITOR_WIDTH, height=constants.FUEL_MONITOR_HEIGHT)
            main.bottom_frame.components['fuel_monitor'] = fuel_monitor_widget
            main.bottom_frame.layout_manager.split('fuel_monitor', 'X', prop=550/800)
            main.bottom_frame.layout_manager.fill('fuel_monitor', 'Y')

        if config.overlay['enable']:
            if config.overlay['arrow']:
                #TODO the arrow should rotate
                #arrow = main.create_oval(-20,-20,20,20, fill="red", width=0)
                arrow = main.create_polygon([-10,-5,10,-5,10,-10,20,0,10,10,10,5,-10,5], fill='red', width=0)
                main.overlay(arrow)
                # subvert the event system, get the arrow to point to a highlight always... TODO this is a hack to
                # get things working quickly for experiments. Really it should be done elsewhere...
                class ArrowRotator:
                    def __init__(self):
                        super().__init__()
                        self.highlights = highlight.Highlight.__all_highlights__ # hack..
                        self.angle = 0
                        self.highlighted = None
                        event.event_scheduler.schedule(self.rotate_arrow(), sleep=cycle([50]))

                    @property
                    def position(self):
                        return main.eye_position

                    def get_highlight_position(self, k):
                            x, y = self.highlights[k].position
                            w, h = self.highlights[k].size
                            return x + w/2, y + h/2

                    def get_min_distance(self, positions):
                        min_d = (None, float('inf'))
                        for k, (px, py) in positions.items():
                            d = ((px - self.position[0]) ** 2 + (py - self.position[1]) ** 2) ** .5
                            if d < min_d[1]:
                                min_d = (k, d)
                        return min_d

                    def rotate_arrow(self):
                        while True:
                            # get positions of all active highlights
                            positions = {k:self.get_highlight_position(k) for k in highlight.all_highlighted()}
                            # compute closest to eye position
                            if len(positions) > 0:
                                (h, _) = self.get_min_distance(positions)
                                assert h is not None
                                hx, hy = positions[h]
                                # compute angle between eyes and highlight
                                angle = math.atan2(hy - self.position[1], hx - self.position[0]) * (180 / math.pi)
                                dangle = angle - self.angle
                                self.angle = angle
                                yield event.Event('arrow_rotator_TEST', "Overlay:0", label='rotate', angle=dangle)
                            else:
                                main.hide_overlay() # hide it if possible...
                                yield None # no event... (nothing is highlighted)
                arrow_rotator = ArrowRotator() # TODO move somewhere more suitable :) 

        # DEBUG 
        # debug_highlights()

        main.pack()

        #tracking_widget.debug()
        #system_monitor_widget.debug()
        #fuel_monitor_widget.debug()

        global_key_handler = keyhandler.KeyHandler(root)

        # ==================== SYSTEM MONITOR EVENT SCHEDULES ==================== #
        if task.system:
            task_system_monitor(config)

        # ====================   TRACKING EVENT SCHEDULES     ==================== #
        if task.track:
            task_tracking(config)
            # EVENT SCHEDULER FOR KEYBOARD INPUT (checks every 50ms whether a key is pressed)
            input_handler = global_key_handler
            if config.input['joystick']:
                input_handler = keyhandler.JoyStickHandler(root)
            #event.event_scheduler.schedule(tracking.KeyEventGenerator(input_handler), sleep=cycle([50]))

        # ==================== FUEL MONITOR EVENT SCHEDULES   ==================== #
        if task.fuel:
            task_fuel_monitor(config)
            
        # ==================== ============================== ==================== #

        #event.event_scheduler.schedule(tracking.TrackingEventGenerator(), sleep=config.schedule_tracking)

        # ================= EYE TRACKING ================= 

        et_config = config.input['eyetracker']
        if et_config.get('enabled', False):
            eyetracker = None
            filter = eyetracking.filter.TobiiFilter(5, 200) # TODO some default thing...
            eyetracker = eyetracking.eyetracker(root, filter=filter, **et_config)
            eyetracker.start()

        atexit.register(system.shutdown) 

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
                                                          size     = (root.winfo_width(), root.winfo_height())))
            if task.track:
                shared.window_properties['track'] =  dict(position = tracking_widget.position,
                                                          size     = tuple([min(tracking_widget.size)]*2)) #TODO fix this in tracking widget...?
            if task.system:
                shared.window_properties['system'] = dict(position = system_monitor_widget.position,
                                                        size     = system_monitor_widget.size,
                                                        **{k:dict(position=v.position, size=v.size) for k,v in system_monitor_widget.warning_lights.items()},
                                                        **{k:dict(position=v.position, size=v.size) for k,v in system_monitor_widget.scales.items()})
            if task.fuel:
                shared.window_properties['fuel'] = dict(position = fuel_monitor_widget.position,
                                                        size     = fuel_monitor_widget.size,
                                                        **{k:dict(position=v.position, size=v.size) for k,v in fuel_monitor_widget.tanks.items()},
                                                        **{k:dict(position=v.position, size=v.size) for k,v in fuel_monitor_widget.pumps.items()})
            #from pprint import pprint
            #pprint(shared.window_properties)

            shared.release() # the parent process can now access attributes in shared memory
        
        #pprint(highlight.all_highlights())
        root.mainloop()

    except:
        traceback.print_exc()
    finally:
        system.shutdown() # ensure shutdown properly...

def task_system_monitor(config):
    """ Set up system monitoring task event schedules

    Args:
        config (SimpleNamespace): configuration options
    """
    scales = system_monitor.Scale.all_components()
    for scale in scales:
        schedule = config.__dict__[scale]['schedule']
        event.event_scheduler.schedule(generator.ScaleEventGenerator(scale), sleep=schedule)


    warning_lights = system_monitor.WarningLight.all_components()
    for warning_light in warning_lights:
        schedule = config.__dict__[warning_light]['schedule']
        event.event_scheduler.schedule(generator.WarningLightEventGenerator(warning_light), sleep=schedule)
        #print(scale, schedule)

def task_tracking(config):
    """ Set up tracking task event schedules

    Args:
        config (SimpleNamespace): configuration options
    """
    targets = tracking.Tracking.all_components()
    for target in targets:
        schedule = config.__dict__[target]['schedule']
        event.event_scheduler.schedule(generator.TargetEventGenerator(target, **config.__dict__[target]), sleep=schedule)

def task_fuel_monitor(config):
    """ Set up fuel monitoring task event scheduless

    Args:
        config (SimpleNamespace): configuration options
    """
    pumps = fuel_monitor.Pump.all_components()
    for pump in pumps:
        schedule = config.__dict__[pump]['schedule']
        event.event_scheduler.schedule(generator.PumpEventGenerator(pump, False), sleep=schedule)

def pumps():
    return list(fuel_monitor.Pump.all_components())

def targets():
    return list(tracking.Tracking.all_components())

def warning_lights():
    return list(system_monitor.WarningLight.all_components())

def scales():
    return list(system_monitor.Scale.all_components())

def tanks():
    return list(fuel_monitor.FuelTank.all_components())


# DEBUG STUFF

def debug_highlights():
    from pprint import pprint
    pprint(highlight.all_highlights())
    def random_highlight():
        while True:
            yield event.Event('DEBUG_HIGHLIGHT', "Highlight:SystemMonitorWidget", label='highlight')
    event.event_scheduler.schedule(random_highlight(), sleep=cycle([100]))