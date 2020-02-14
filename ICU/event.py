import time

global finish
finish = False

EVENT_SINKS = {}
EVENT_SOURCES = {}

GLOBAL_EVENT_CALLBACK = lambda *args: print(*args)

class EventCallback:

    def __init__(self, *args, **kwargs):
        super(EventCallback, self).__init__(*args, **kwargs)

    def register(self, name):
        self.__name = "{0}:{1}".format(type(self).__name__, name)

        EVENT_SINKS[self.__name] = self
        EVENT_SOURCES[self.__name] = self
        print("INFO: registered event callback: {0}".format(self.__name))

    def source(self, *args):
        GLOBAL_EVENT_CALLBACK(Event(self.__name, *args))

    def sink(self, event):
        pass

EVENT_NAME = 0
def next_name():
    global EVENT_NAME
    EVENT_NAME += 1
    return str(EVENT_NAME)

class Event:

    def __init__(self, *args):
        self.name = next_name()
        self.args = args

    def __str__(self):
        return "{0}{1}".format(self.name, str(self.args))

class TKSchedular: #might be better to detach events from the GUI? quick and dirt for now...

    def __init__(self, tk_root):
        self.tk_root = tk_root

    def schedule(self, generator, sleep=1000, repeat=True):
        if repeat:
            self.after(sleep, self.gen_repeat, generator, sleep)
        else:
            self.after(sleep, self.gen, generator)

    def gen(self, e):
        try:
            e = next(generator)
            EVENT_SINKS[e.args[0]].sink(e)
            GLOBAL_EVENT_CALLBACK(e)
        except StopIteration:
            pass

    def gen_repeat(self, generator, sleep):
        try:
            e = next(generator)
            self.after(sleep, self.gen_repeat, generator, sleep)
            EVENT_SINKS[e.args[0]].sink(e)
            GLOBAL_EVENT_CALLBACK(e)
        except StopIteration:
            pass
        
    def after(self, sleep, fun, *args):
        self.tk_root.after(sleep, fun, *args)

global event_scheduler
event_scheduler = None

def tk_event_schedular(root):
    global event_scheduler
    event_scheduler = TKSchedular(root)