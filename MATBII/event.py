import time

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

