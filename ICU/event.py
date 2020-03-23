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

def new_event_class(name, *labels): #see list of event types below
    cls = type(name, (Event,), {})
    cls.labels = SimpleNamespace(**{l:l for l in labels})
    return cls

class Event:

    def __init__(self, label, data, timestamp=None):
        super(Event, self).__init__()
        cls = self.__class__
        if label not in cls.labels.__dict__:
            raise ValueError("label '{0}' for event type '{1}' must be one of: {2}".format(label, cls.__name__, list(cls.labels.__dict__.keys())))
        self.name = next_name()
        self.label = label
        self.data = data

        if timestamp is None:
            self.timestamp = time.time()

    def __str__(self):
        return "{0} - {1}".format(self.name, self.to_dict())

    def to_dict(self):
        return copy.deepcopy(self.__dict__)

# ================================================= #
# ================= EVENT SHEMA =================== #
# ================================================= #

click_event = new_event_class('click_event', )


warning_light_event = new_event_class('warning_light_event', 'click', 'flip')
scale_event = new_event_class('scale_event', 'move')
track_event = new_event_class('track_event', 'move')
pump_event = new_event_class('pump_event', 'click', 'transfer', 'fail', 'repair')
highlight_event = new_event_class('highlight_event', 'flip')




# ================================================= #
# ================================================= #
# ================================================= #



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

    def source(self, *args):
        GLOBAL_EVENT_CALLBACK(Event(self.__name, *args))

    def sink(self, event): #override this method
        pass













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
                if e.args[0] is not None:
                    EVENT_SINKS[e.args[0]].sink(e)
                GLOBAL_EVENT_CALLBACK(e)
        except StopIteration:
            pass

    def gen_repeat(self, generator, sleep):
        try:
            e = next(generator)
            self.after(next(sleep), self.gen_repeat, generator, sleep)
            if e is not None:
                if e.args[0] in EVENT_SINKS:
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