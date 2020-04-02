from collections import defaultdict
from .event import Event

MAX_KEY_CODES = 120

#consider using os.system('xset r off') 

class KeyHandler:

    def __init__(self, root):
        self.keys = defaultdict(lambda: False)
        root.bind_all('<KeyPress>', self.press)
        root.bind_all('<KeyRelease>', self.release)

    def press(self, event):
        self.keys[event.keysym] = True

    def release(self, event):
        self.keys[event.keysym] = False

    def isPressed(self, key):
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