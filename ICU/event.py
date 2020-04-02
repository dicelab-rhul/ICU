'''
TODO
'''


import time
import copy
from types import SimpleNamespace

global finish
finish = False


# create unique event ids (ids do not reflect time)
EVENT_NAME = 0
def next_name():
    global EVENT_NAME
    EVENT_NAME += 1
    return str(EVENT_NAME)

class Event:

    def __init__(self, src, dst, timestamp=None, **data):
        super(Event, self).__init__()
        self.name = next_name()
        self.dst = dst
        self.src = src
        self.data = SimpleNamespace(**data)
        self.timestamp = None
        if timestamp is None:
            self.timestamp = time.time()

    def __str__(self):
        return "{0}:{1} - ({2}->{3}): {4}".format(self.name, self.timestamp, self.src, self.dst, self.data.__dict__)

    def to_tuple(self):
        return (self.timestamp, self.name, (self.src, self.dst), copy.deepcopy(self.data.__dict__))


EVENT_SINKS = {}
EVENT_SOURCES = {}

class GlobalEventCallback:

    def __init__(self):
        self.callbacks = []

    def add_event_callback(self, callback):
        self.callbacks.append(callback)

    def __call__(self, *args):
        for callback in self.callbacks:
            callback(*args)
    
GLOBAL_EVENT_CALLBACK = GlobalEventCallback()

class EventCallback:

    def __init__(self, *args, **kwargs):
        super(EventCallback, self).__init__(*args, **kwargs)

    def register(self, name):
        self.__name = "{0}:{1}".format(type(self).__name__, name)
        EVENT_SINKS[self.__name] = self
        EVENT_SOURCES[self.__name] = self
        #print("INFO: registered event callback: {0}".format(self.__name))

    def source(self, dst, timestamp=None, **data):
        e = Event(self.name, dst, timestamp=timestamp, **data)
        GLOBAL_EVENT_CALLBACK(e)

    def sink(self, event): #override this method
        pass

    @property
    def name(self):
        return self.__name

def sleep_repeat_int(sleep):
    while True:
        yield sleep

def sleep_repeat_list(sleep):
    while True:
        for i in sleep:
            yield i

class TKSchedular: #might be better to detach events from the GUI? quick and dirt for now...

    def __init__(self, tk_root):
        self.tk_root = tk_root

    def schedule(self, generator, sleep=1000, repeat=True):
        if isinstance(sleep, float):
            sleep = int(sleep)

        if isinstance(sleep, int):
            sleep = sleep_repeat_int(sleep)
        elif isinstance(sleep, (list,tuple)):
            sleep = sleep_repeat_list(sleep)

        if repeat:
            self.after(next(sleep), self.gen_repeat, generator, sleep)
        else:
            self.after(next(sleep), self.gen, generator)

    def gen(self, e):
        try:
            e = next(generator)
            if e is not None:
                if e.dst is not None:
                    EVENT_SINKS[e.dst].sink(e)
                GLOBAL_EVENT_CALLBACK(e)
        except StopIteration:
            pass

    def gen_repeat(self, generator, sleep):
        try:
            e = next(generator)
            self.after(next(sleep), self.gen_repeat, generator, sleep)
            if e is not None:
                if e.dst in EVENT_SINKS:
                    EVENT_SINKS[e.dst].sink(e)
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