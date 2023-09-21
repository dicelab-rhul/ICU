from dataclasses import dataclass 
from typing import Tuple, Union

UI_CANVAS = "UI::CANVAS"
PYGAME = "PYGAME"
UI = "UI"
ICU = "ICU"

# possible draw commands
DRAW_CIRCLE = "DRAW_CIRCLE"
DRAW_RECT   = "DRAW_RECT"
DRAW_LINE   = "DRAW_LINE"
CLEAR       = "CLEAR"


WINDOW_QUIT              = "WINDOW::QUIT"
WINDOW_WINDOWFOCUSGAINED = "WINDOW::WINDOWFOCUSGAINED"
WINDOW_WINDOWFOCUSLOST   = "WINDOW::WINDOWFOCUSLOST"
WINDOW_WINDOWRESIZED     = "WINDOW::WINDOWRESIZED"
WINDOW_WINDOWMOVED       = "WINDOW::WINDOWMOVED"

PYGAME_WINDOW_QUIT              = PYGAME + "::" + WINDOW_QUIT
PYGAME_WINDOW_WINDOWFOCUSGAINED = PYGAME + "::" + WINDOW_WINDOWFOCUSGAINED
PYGAME_WINDOW_WINDOWFOCUSLOST   = PYGAME + "::" + WINDOW_WINDOWFOCUSLOST
PYGAME_WINDOW_WINDOWRESIZED     = PYGAME + "::" + WINDOW_WINDOWRESIZED
PYGAME_WINDOW_WINDOWMOVED       = PYGAME + "::" + WINDOW_WINDOWMOVED

UI_WINDOW_QUIT              = UI + "::" + WINDOW_QUIT               
UI_WINDOW_WINDOWFOCUSGAINED = UI + "::" + WINDOW_WINDOWFOCUSGAINED  
UI_WINDOW_WINDOWFOCUSLOST   = UI + "::" + WINDOW_WINDOWFOCUSLOST    
UI_WINDOW_WINDOWRESIZED     = UI + "::" + WINDOW_WINDOWRESIZED      
UI_WINDOW_WINDOWMOVED       = UI + "::" + WINDOW_WINDOWMOVED        

COSMETIC = "COSMETIC" # used to update cosmetic properties
SET_PROPERTY = "SET_PROPERTY" # used to set widget properties
GET_PROPERTY = "GET_PROPERTY" # used to get widget properties

SET_RESPONSE = "SET_RESPONSE" # response type that will be given by a widget if properties were changed
GET_RESPONSE = "GET_RESPONSE" # response type that will be given by a widget in response to a get request (using PROPERTY)
CHANGED = "CHANGED"

MOUSECLICK = "MOUSECLICK"
MOUSEDOWN = "MOUSEDOWN"
MOUSEUP = "MOUSEUP"
MOUSEMOTION = "MOUSEMOTION"
KEYDOWN = "KEYDOWN"
KEYUP = "KEYUP"

INPUT_MOUSEMOTION        = "INPUT::" + MOUSEMOTION
INPUT_MOUSEDOWN          = "INPUT::" + MOUSEDOWN
INPUT_MOUSEUP            = "INPUT::" + MOUSEUP
INPUT_MOUSECLICK         = "INPUT::" + MOUSECLICK
INPUT_KEYDOWN            = "INPUT::" + KEYDOWN
INPUT_KEYUP              = "INPUT::" + KEYUP

UI_INPUT_MOUSEMOTION     = UI + "::" + INPUT_MOUSEMOTION          
UI_INPUT_MOUSEDOWN       = UI + "::" + INPUT_MOUSEDOWN           
UI_INPUT_MOUSEUP         = UI + "::" + INPUT_MOUSEUP             
UI_INPUT_MOUSECLICK      = UI + "::" + INPUT_MOUSECLICK          
UI_INPUT_KEYDOWN         = UI + "::" + INPUT_KEYDOWN             
UI_INPUT_KEYUP           = UI + "::" + INPUT_KEYUP               

# TODO could use dataclasses? 

@dataclass
class CommandDrawLine:
    start_position : Tuple
    end_position : Tuple
    color : Union[Tuple, str]
    width : float

@dataclass
class CommandDrawRect:
    position : Tuple
    size : Tuple
    color : Union[Tuple, str]
    width : float

@dataclass
class CommandDrawCircle:
    position : Tuple
    radius : float
    color : Union[Tuple, str]
    width : float

@dataclass
class CommandClear:
    pass 
