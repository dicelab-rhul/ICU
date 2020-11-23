#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Defaults for all configuration options + some documentation.
"""
__author__ = "Benedict Wilkins"
__email__ = "benrjw@gmail.com"
__status__ = "Development"

from .validate import validate_schedule

def default_config_screen():
    return dict(#screen_width=None,  #handled by post processing
                #screen_height=None, #handled by post processing
                screen_size = (800,700),                              # size of the ICU window
                #screen_x = None, #handled by post processing       # x position of the ICU window
                #screen_y = None, #handled by post processing       # y position of the ICU window
                screen_position = (0,0),                              # position of the ICU window
                screen_min_size = (100,100),                          # minimum ICU window size
                screen_max_size = (2000,2000),                        # maximum ICU window size
                screen_full = False,                                  # ICU window full screen ?
                screen_resizable = True,                              # ICU window resizable ? 
                screen_aspect = None,                                 # ICU window aspect ratio (if fixed)
                background_colour = 'grey',                           # ICU window background colour
                shutdown = -1)                                      # system shutdown after x/seconds (-1 = never)

def default_task_options():                                         # turn on/off specific tasks
    return dict(system = True,                                      
                track = True, 
                fuel = True)

def default_scale_schedule():
    return validate_schedule([["uniform(1000,10000)"]])

def default_warning_light_schedule():
    return validate_schedule([["uniform(1000,10000)"]])

def default_pump_schedule():
    return validate_schedule([["uniform(1000,20000)"]])

def default_target_schedule():
    return validate_schedule([[100]])

def default_scales():                       
    return {"Scale:0" : default_scale("<F1>"),
            "Scale:1" : default_scale("<F2>"),
            "Scale:2" : default_scale("<F3>"),
            "Scale:3" : default_scale("<F4>")}

def default_scale(key):
    return dict(schedule = default_scale_schedule(),    
                size = 11,
                position = 5,
                key = key)

def default_warning_lights():
    return {'WarningLight:0' : default_warning_light(state=1, key = "<F5>"),
            'WarningLight:1' : default_warning_light(state=0, key = "<F6>")}

def default_warning_light(state, key):
    return dict(schedule = default_warning_light_schedule(),
                state = state,
                key = key,
                grace = 2)

def  default_tanks():
    return {
        "FuelTank:A" : {"capacity":2000, "fuel":1000, "burn_rate":6, "accept_position":0.5, "accept_proportion":0.3},
        "FuelTank:B" : {"capacity":2000, "fuel":1000, "burn_rate":6, "accept_position":0.5, "accept_proportion":0.3},
        "FuelTank:C" : {"capacity":1000, "fuel":100},
        "FuelTank:D" : {"capacity":1000, "fuel":100},
        "FuelTank:E" : {"capacity":1000, "fuel":1000},
        "FuelTank:F" : {"capacity":1000, "fuel":1000}}

def default_pumps():
    return {"Pump:AB" : default_pump(),
            "Pump:BA" : default_pump(), 
            "Pump:FD" : default_pump(),
            "Pump:EA" : default_pump(),
            "Pump:CA" : default_pump(),
            "Pump:EC" : default_pump(),
            "Pump:DB" : default_pump(),
            "Pump:FB" : default_pump()}
    
def default_pump():
    return dict(schedule = default_pump_schedule(),
                flow_rate = 100, 
                event_rate = 10, 
                state = 1)

def default_tracking():
    return {"Target:0" : 
                dict(schedule = default_target_schedule(),
                step = 2,   
                invert = False)} #TODO

def default_input():
    return {"mouse" : True,
            "keyboard" : True,
            "joystick" : False,
            "eyetracker" : {
                "stub" : True,
                "enabled" : True,
                "sample_rate" : 100,
                "calibrate" : False
            }}


def default_overlay():
    return dict(enable=True,
                transparent=True, 
                outline=True, 
                arrow=True)

def default_config():
    return dict(**default_config_screen(), 
                task=default_task_options(),
                overlay=default_overlay(), 
                input=default_input(),
                **default_scales(), 
                **default_warning_lights(), 
                **default_tanks(), 
                **default_pumps(), 
                **default_tracking())
