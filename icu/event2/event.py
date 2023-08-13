

from collections import defaultdict, deque
from dataclasses import dataclass, field
import time
import os

from multiprocessing import Queue
from typing import Dict, Set
import uuid

from .dict.eventdict import EventDict
from ..exception import EventSystemException

@dataclass(frozen=True)
class Event:
    id: str = field(init=False, default_factory=lambda: str(uuid.uuid4().int))
    timestamp : float = field(init=False, default_factory=lambda : time.time())
    type: str
    data: dict = field(default_factory=dict)
    
    def __eq__(self, other):
        if isinstance(other, Event):
            return self.id == other.id
        return False

    def __hash__(self):
        return hash(self.id)


class SinkBase:

    def __init__(self):
        self.id = str(uuid.uuid4().int)

    def close(self):
        pass 

    def sink(self, event):
        raise NotImplementedError()

    def get_subscriptions(self):
        raise NotImplementedError()

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, SourceBase):
            return self.id == other.id
        return False

class SourceBase:

    def __init__(self):
        self.id = str(uuid.uuid4().int)
        
    def source(self, event_type : str, data : Dict):
        raise NotImplementedError() 

    def close(self):
        raise NotImplementedError()

    def get_events(self):
        raise NotImplementedError()
    
    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, SourceBase):
            return self.id == other.id
        return False
    
class SinkLocal(SinkBase):

    def __init__(self, callback):
        super().__init__()
        self._subscriptions = set()
        self._callback = callback

    def subscribe(self, subscription : str):
        self._subscriptions.add(subscription)

    def unsubscribe(self, subscription : str):
        self._subscriptions.remove(subscription)
    
    def get_subscriptions(self):
        return self._subscriptions.copy()
    
    def sink(self, event : Event):
        return self._callback(event)
    
class SinkRemote(SinkBase, SourceBase):

    def __init__(self):
        super().__init__()
        self._subscriptions = set()
        self._subscription_queue = Queue() # queue that updates subscriptions remotely
        self._buffer = Queue()

    def close(self):
        list(self.get_events())         # clear the queue
        self._buffer.close() 
        list(self.get_subscriptions())  # clear subscriptions
        self._subscription_queue.close()
       
    def subscribe(self, subscription : str):
        self._subscriptions.add(subscription)
        self._subscription_queue.put((True, subscription)) # add command

    def unsubscribe(self, subscription : str):
        self._subscriptions.remove(subscription)
        self._subscription_queue.put((False, subscription)) # remove command
    
    def get_subscriptions(self):
        # update subscriptions from remote
        while not self._subscription_queue.empty():
            (add, sub) = self._subscription_queue.get()
            if add:
                self._subscriptions.add(sub)
            else:
                self._subscriptions.remove(sub)
        return self._subscriptions.copy()
    
    def sink(self, event : Event):
        #print(f"SINK remote: {event}")
        return self._buffer.put(event)
    
    def get_events(self): # get any buffered events
        while not self._buffer.empty():
            event = self._buffer.get()
            #print(event)
            yield event
    
class SourceLocal(SourceBase):

    def __init__(self):
        super().__init__()
        self._buffer = deque() # simplest kind of buffer...

    def close(self):
        pass # nothing to close...

    def source(self, event_type, data):
        self._buffer.append(Event(event_type, data))

    def get_events(self): # get any buffered events
        while len(self._buffer) > 0:
            yield self._buffer.popleft()

class SourceRemote(SourceBase):

    def __init__(self):
        super().__init__()
        self._buffer = Queue() # simplest kind of buffer...

    def close(self):
        list(self.get_events())         # clear the queue
        self._buffer.close() 

    def source(self, event_type, data):
        self._buffer.put(Event(event_type, data))

    def put(self, event): # this is cheating a bit, but it is useful for forwarding events
        self._buffer.put(event) 


    def get_events(self): # get any buffered events
        while not self._buffer.empty():
            yield self._buffer.get()

class EventSystem:

    def __init__(self):
        self.sinks : Set[SinkBase] = set() 
        self.sources : Set[SourceBase] = set()
        self._events : EventDict = EventDict()
        self.__closed : bool = False

    def pull_events(self):
        # get all events from sources and store them in the event dict
        for source in self.sources:
            try:
                for event in source.get_events():
                    self._events.add(event.type, event)
            except TypeError:
                print(source) # TODO
                raise EventSystemException("")

    def publish(self):
        print(os.getpid(), len(self._events))
        for sink in self.sinks:
            events = set()
            for subscription in sink.get_subscriptions():
                events = events.union(self._events[subscription])
            for event in sorted(events, key = lambda x : x.timestamp):
                sink.sink(event)  
        self._events.clear()   
        
    def remove_sink(self, sink : SinkBase):
        self.sinks.remove(sink)
    
    def add_sink(self, sink : SinkBase):
        if sink is None:
            raise EventSystemException("Sink cannot be None.")
        self.sinks.add(sink)

    def remove_source(self, source : SourceBase):
        self.sources.remove(source)

    def add_source(self, source : SourceBase):
        if source is None:
            raise EventSystemException("Source cannot be None.")
        self.sources.add(source)

    def close(self):
        self.pull_events()
        for sink in self.sinks:
            sink.close()
        for source in self.sources:
            source.close()
        self.__closed = True

    @property
    def is_closed(self):
        return self.__closed
    
