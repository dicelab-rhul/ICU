import copy

from sys import version_info

from types import SimpleNamespace
from json import dumps
from multiprocessing import Queue
from time import time

global finish
finish = False

# create unique event ids (ids do not reflect time)
EVENT_NAME = 0
def next_name():
    global EVENT_NAME
    EVENT_NAME += 1
    return str(EVENT_NAME)



class etuple(tuple):
    
    def __new__(self, value, cause=None):
        return super(etuple, self).__new__(etuple, (value, cause))

class event_property(property):

    def __set__(self, obj, value):
        cause = None
        if isinstance(value, etuple):
            assert len(value) == 2
            value, cause = value
        super(event_property, self).__set__(obj, value)
        nvalue = self.__get__(obj)
        obj.source("Global", label="change", attr=self.fget.__name__, value=nvalue, cause=cause)

class Event:

    def __init__(self, src, dst, timestamp=None, **data):
        super(Event, self).__init__()
        self.name = next_name()
        self.dst = dst
        self.src = src
        self.data = SimpleNamespace(**data)
        self.timestamp = timestamp
        if timestamp is None:
            self.timestamp = time()

    def __str__(self):
        return "{0}:{1} - ({2}->{3}): {4}".format(self.name, self.timestamp, self.src, self.dst, self.data.__dict__)
    
    def __repr__(self):
        return str(self)


    def to_tuple(self):
        return (self.timestamp, self.name, (self.src, self.dst), copy.deepcopy(self.data.__dict__))

    def serialise(self) -> dict:
        return {
            "src": self.src,
            "dst": self.dst,
            "data": self.data.__dict__,
            "name": self.name,
            "timestamp": self.timestamp,
        }

    def serialise_to_str(self) -> str:
        return dumps(self.serialise())

    @staticmethod
    def empty_event() -> "Event":
        return Event(src="empty", dst="empty")


class ExternalEventSource: 
    """ 
        A thread-safe event source to be used externally as a
        mechanism for sending events to the ICU system.
    """
    __NAME = 0

    def __init__(self, *args, **kwargs):
        super(ExternalEventSource, self).__init__(*args, **kwargs)
        self.__buffer = Queue()
        ExternalEventSource.__NAME += 1
        self.__name =  "{0}:{1}".format(type(self).__name__, ExternalEventSource.__NAME)
    
    
    def source(self, src, dst, timestamp=None, **data):
        """
            Send a new event to the ICU system.
        
        Args:
            src (str): the name of the source object (a unique ID)
            dst (str): the name of the destination (sink) object (a unique ID), see get_event_sources() for a list of source IDs.
            timestamp (float, optional): floating point number expressed in seconds since the epoch, in UTC (see time.time()). Defaults to the current time (on event instantiation).
        """
        event = Event(src, dst, timestamp=timestamp, **data)
        #print("EXTERNAL-{0}: {1}".format(os.getpid(), event))
        self.__buffer.put(event)

    def empty(self):
        return self.__buffer.empty()

    def size(self):
        return self.__buffer.qsize()

    def close(self):
        return self.__buffer.close()

    @property
    def name(self):
        return self.__name

    def __str__(self):
        return "{0}:{1}".format(self.name, self.size())

    def __repr__(self):
        return str(self)

class ExternalEventSink:
    """
        A thread-safe event sink to be used externally as a 
        mechanism for receiving events from the ICU system.
    """
    __NAME = 0


    def __init__(self, *args, **kwargs):
        super(ExternalEventSink, self).__init__(*args, **kwargs)
        self.__buffer = Queue()
        ExternalEventSink.__NAME += 1
        self.__name =  "{0}:{1}".format(type(self).__name__, ExternalEventSink.__NAME)
    
    def get(self):
        '''
            Pop from event buffer.
        '''
        event = self.__buffer.get()
        return event
        
    def full(self):
        return self.__buffer.full()

    def empty(self):
        return self.__buffer.empty()

    def size(self):
        return self.__buffer.qsize()

    def close(self):
        return self.__buffer.close()

    @property
    def name(self):
        return self.__name
    
    def __str__(self):
        return "{0}:{1}".format(self.name, self.size())

    def __repr__(self):
        return str(self)

#EVENT_SINKS = {}
#EVENT_SOURCES = {}
    
class GlobalEventCallback:

    def __init__(self, logger):
        if logger is None:
            self.logger = lambda _: None
        else:
            self.logger = logger

        self.external_sinks = {}
        self.external_sources = {}

        self.sinks = {}
        self.sources = {}
        self.__closed = False

    def close(self):
        for sink in self.external_sinks.values():
            sink.close()
        for source in self.external_sources.values():
            source.close()
        if self.logger is not None:
            self.logger.close()
        self.__closed = True

    @property
    def is_closed(self):
        return self.__closed

    def _trigger(self, event):
        if event is not None:
            if event.dst in self.sinks:
                self.sinks[event.dst].sink(event)
            self.__sink_external(event) #send to all external sinks
            self.logger.log(event)

    def trigger(self, *events): 
        for event in events:
            self._trigger(event)

    def __sink_external(self, event): # TODO this could be changed at some point... a more advanced event system is needed        
        for sink in self.external_sinks.values():
            sink._ExternalEventSink__buffer.put(copy.deepcopy(event))

    def register_sink(self, name, sink):
        self.sinks[name] = sink
    
    def register_source(self, name, source):
        self.sources[name] = source

    def register_external_source(self, name, source):
        assert isinstance(source, ExternalEventSource)
        self.external_sources[name] = source

    def register_external_sink(self, name, sink):
        assert isinstance(sink, ExternalEventSink)
        self.external_sinks[name] = sink

    def schedule_external(self, sleep=50):
        def _event_iterator(source):
            while not source.empty():
                event =  source._ExternalEventSource__buffer.get()
                if isinstance(event.dst, (list, tuple)): #if multiple destinations
                    for dst in event.dst:
                        e = copy.deepcopy(event) #not efficient... oh well
                        e.dst = dst
                        yield e
                else:
                    yield event

        def _trigger():
            for source in self.external_sources.values():
                for event in _event_iterator(source):
                    #print(" -- EXTERNAL:", event)
                    if event is not None and event.dst in self.sinks:
                        self.sinks[event.dst].sink(event)
                        if self.logger is not None:
                            #print("LOG EVENT", event)
                            self.logger.log(event)

            event_scheduler.after(sleep, _trigger)

        event_scheduler.after(sleep, _trigger)

# ===  GLOBAL === #
GLOBAL_EVENT_CALLBACK = None
global event_scheduler
event_scheduler = None

def initialise_global_event_callback(logger=None):
    global GLOBAL_EVENT_CALLBACK
    GLOBAL_EVENT_CALLBACK = GlobalEventCallback(logger)

def get_event_sources():
    return list(GLOBAL_EVENT_CALLBACK.sources.keys())

def get_event_sinks():
    return list(GLOBAL_EVENT_CALLBACK.sinks.keys())

def get_external_event_sinks():
    return list(GLOBAL_EVENT_CALLBACK.external_sinks.keys())

def get_external_event_sources():
    return list(GLOBAL_EVENT_CALLBACK.external_sources.keys())

def add_event_source(source):
    '''
        Add an external event source to ICU. Any events generated by 
        this source will be propagated to an ICU event sink.
    '''
    GLOBAL_EVENT_CALLBACK.register_external_source(source.name, source)

def add_event_sink(sink):
    '''
        Add an external event sink to ICU. This event sink will receive 
        all events that are generated by the ICU system.
    '''
    GLOBAL_EVENT_CALLBACK.register_external_sink(sink.name, sink)

#TODO function for removing external event_source/sink? 

# ============ INTERNAL ============ #

class EventCallback:
    '''
        Used internally by widgets that can receive and generate events.
    '''

    def __init__(self, *args, **kwargs):
        super(EventCallback, self).__init__(*args, **kwargs)


    def register(self, name):
        self.__name = name
        GLOBAL_EVENT_CALLBACK.register_sink(self.__name, self)
        GLOBAL_EVENT_CALLBACK.register_source(self.__name, self)

    def source(self, dst, timestamp=None, **data):
        e = Event(self.name, dst, timestamp=timestamp, **data)
        global event_scheduler
        event_scheduler.schedule(e, sleep=0)

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

class EGen:
    def __init__(self, gen):
        self.gen = gen
    def __iter__(self):
        return self
    def __next__(self):
        e = next(self.gen)
        if not isinstance(e, tuple):
            return e,
        else:
            return e

class TKSchedular: #might be better to detach events from the GUI? quick and dirty for now...

    def __init__(self, tk_root):
        self.tk_root = tk_root

    def schedule(self, generator, sleep=0):
        if isinstance(sleep, float):
            sleep = int(sleep)

        if isinstance(generator, Event):
            assert isinstance(sleep, int)
            self.after(sleep, GLOBAL_EVENT_CALLBACK.trigger, generator)
            return
        
        generator = EGen(generator) # always yields (e1, ...)

        if isinstance(sleep, int):
            self.after(sleep, GLOBAL_EVENT_CALLBACK.trigger, *next(generator))
            return

        try:
            #repeated event - sleep is a generator (or iterable)
            self.after(next(sleep), self.__trigger_repeat, generator, sleep)
        except StopIteration:
            pass

    def __trigger_repeat(self, generator, sleep):
        try:
            GLOBAL_EVENT_CALLBACK.trigger(*next(generator))
        except StopIteration:
            return
        try:
            self.after(next(sleep), self.__trigger_repeat, generator, sleep)
        except StopIteration:
            pass

    def after(self, sleep, fun, *args):
        self.tk_root.after(int(sleep), fun, *args)

    def close(self):
        pass #TODO

def tk_event_schedular(root):
    global event_scheduler
    event_scheduler = TKSchedular(root)

    GLOBAL_EVENT_CALLBACK.schedule_external()

def close():
    GLOBAL_EVENT_CALLBACK.close()
    event_scheduler.close()