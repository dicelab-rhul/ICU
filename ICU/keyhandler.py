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
        print(event)
        self.keys[event.keysym] = True

    def release(self, event):
        print(event)
        self.keys[event.keysym] = False

    def isPressed(self, key):
        #print(key, self.keys[key])
        return self.keys[key]

