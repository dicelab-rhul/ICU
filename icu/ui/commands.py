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

COSMETIC = "COSMETIC"
PROPERTY = "PROPERTY"
SET_RESPONSE = "SET_RESPONSE"
GET_RESPONSE = "GET_RESPONSE"



INPUT_MOUSEMOTION        = "INPUT::MOUSEMOTION"
INPUT_MOUSEDOWN          = "INPUT::MOUSEDOWN"
INPUT_MOUSEUP            = "INPUT::MOUSEUP"
INPUT_MOUSECLICK         = "INPUT::MOUSECLICK"


PYGAME_INPUT_MOUSEMOTION = "PYGAME::INPUT::MOUSEMOTION"
PYGAME_INPUT_MOUSEDOWN   = "PYGAME::INPUT::MOUSEDOWN"
PYGAME_INPUT_MOUSEUP     = "PYGAME::INPUT::MOUSEUP"


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
