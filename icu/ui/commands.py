from dataclasses import dataclass 
from typing import Tuple, Union

UI_CANVAS = "UI::CANVAS"

# possible draw commands
DRAW_CIRCLE = "DRAW_CIRCLE"
DRAW_RECT   = "DRAW_RECT"
DRAW_LINE   = "DRAW_LINE"
CLEAR       = "CLEAR"

UI_WINDOW_QUIT = "UI::WINDOW::QUIT"

UI_WINDOW_WINDOWFOCUSGAINED = "UI::WINDOW::WINDOWFOCUSGAINED"
UI_WINDOW_WINDOWFOCUSLOST   = "UI::WINDOW::WINDOWFOCUSLOST"
UI_WINDOW_WINDOWRESIZED     = "UI::WINDOW::WINDOWRESIZED"
UI_WINDOW_WINDOWMOVED       = "UI::WINDOW::WINDOWMOVED"

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

PYGAME_INPUT_MOUSEMOTION = "PYGAME::" + INPUT_MOUSEMOTION
PYGAME_INPUT_MOUSEDOWN   = "PYGAME::" + INPUT_MOUSEDOWN
PYGAME_INPUT_MOUSEUP     = "PYGAME::" + INPUT_MOUSEUP
PYGAME_INPUT_KEYDOWN     = "PYGAME::" + INPUT_KEYDOWN
PYGAME_INPUT_KEYUP       = "PYGAME::" + INPUT_KEYUP

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
