"""
    Defines key input event handlers.

    @Author: Benedict Wilkins
    @Date: 2020-04-02 21:48:10
"""

from collections import defaultdict
from .event import Event

MAX_KEY_CODES = 120
# TODO define commonly used key codes  (Left, Right, Up, Down, A, S, W, D) + Joystick??

#consider using os.system('xset r off') 

class KeyHandler:
    """ 
        A KeyHandler records keyboard key press and release events. 
    """
    
    def __init__(self, root):
        self.keys = defaultdict(lambda: False)
        root.bind_all('<KeyPress>', self.press)
        root.bind_all('<KeyRelease>', self.release)

    def press(self, event):
        """ Called when a keyboard key is pressed.
        Args:
            event (keyevent): A key event, should contain the attribute keysym (a unique identifier for the key).
        """
        self.keys[event.keysym] = True

    def release(self, event):
        """ Called when a keyboard key is released.
        Args:
            event (keyevent): A key event, should contain the attribute keysym (a unique identifier for the key).
        """
        self.keys[event.keysym] = False

    def isPressed(self, key):
        """ is the given key currently being pressed?
        
        Args:
            key ( -- ): the unique identifier associated with the key (see press, release) 
        
        Returns:
            bool: True if the key is currently pressed, False otherwise.
        """
        return self.keys[key]

class JoyStickHandler:

    def __init__(self, root):
        raise NotImplementedError("TODO are we using a joystick!?")

    def press(self, event):
        pass #TODO

    def release(self, event):
        pass #TODO

    def isPressed(self, key):
        pass #TODO