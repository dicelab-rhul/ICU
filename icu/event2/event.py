""" This module defines key classes for the event system such as `Event` and useful `Source` and `Sink` implementations. """

from collections import deque
from dataclasses import dataclass, field
from multiprocessing import Queue
from typing import Dict, Set, Callable
import time
import uuid

from .dict.eventdict import EventDict
from ..utils.exception import EventSystemError


@dataclass(frozen=True)
class Event:
    """Class for events."""

    id: str = field(init=False, default_factory=lambda: f"{uuid.uuid4().int:>039d}")
    timestamp: float = field(init=False, default_factory=time.time)
    type: str
    data: dict = field(default_factory=dict)

    def __eq__(self, other):
        if isinstance(other, Event):
            return self.id == other.id
        return False

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        formatted_timestamp = f"{self.timestamp:.6f}"
        return (
            f"Event(id={self.id}, timestamp={formatted_timestamp}, "
            f"type='{self.type}', data={self.data})"
        )


class SinkBase:
    """Base class for the `Sink` pattern."""

    def __init__(self):
        super().__init__()
        self.id = str(uuid.uuid4().int)

    def close(self):
        """Closes this sink."""
        raise NotImplementedError()

    def sink(self, event: Event):
        """Sinks the given `event`. Any subclass should implement specific functionality
        to process the `event`.

        Args:
            event (Event): event to process.
        """
        raise NotImplementedError()

    def get_subscriptions(self):
        """Getter for the event types that this `Sink` subscribes to."""
        raise NotImplementedError()

    def subscribe(self, subscription):
        """Subscribe this `Sink` to receive certain event types.

        Args:
            subscription (str): event type to subscribe to.
        """
        raise NotImplementedError()

    def unsubscribe(self, subscription):
        """Unsubscribe this `Sink` to no longer receive certain event types.

        Args:
            subscription (str): event type to unsubscribe.
        """
        raise NotImplementedError()

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, SourceBase):
            return self.id == other.id
        return False


class SourceBase:
    """Base class for the `Source` pattern."""

    def __init__(self):
        super().__init__()
        self.id = str(uuid.uuid4().int)

    def source(self, event_type: str, data: Dict):
        """Produces (or buffers) a new event.

        Args:
            event_type (str): type of the event.
            data (Dict): event data.
        """
        raise NotImplementedError()

    def close(self):
        """Closes this `Source`."""
        raise NotImplementedError()

    def get_events(self):
        """Getter for the events that this `Source` currently buffers (if any).
        This is called by the event system to obtain events that are to be sent around.
        """
        raise NotImplementedError()

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, SourceBase):
            return self.id == other.id
        return False


class SinkLocal(SinkBase):
    """A simple implementation of a `Sink` with am event callback."""

    def __init__(self, callback: Callable):
        """Constructor for `SinkLocal`

        Args:
            callback (Callable): called when an event is received by this `Sink`.
        """
        super().__init__()
        self._subscriptions = set()
        self._callback = callback

    def subscribe(self, subscription: str):
        self._subscriptions.add(subscription)

    def unsubscribe(self, subscription: str):
        self._subscriptions.remove(subscription)

    def get_subscriptions(self):
        return self._subscriptions.copy()

    def sink(self, event: Event):
        return self._callback(event)

    def close(self):
        """This has no effect on a `LocalSink`."""


class SinkRemote(SinkBase, SourceBase):
    """A implementation of a `Sink` that works with Pythons `multiprocess` package
    acting as a bridge between two Python processes and their event systems.
    A `SinkRemote` should be created in one process and treated as a `Sink`, it
    should then be sent to another process and treated as a `Source`.

    ```
        TODO code example.
    ```
    """

    def __init__(self):
        super().__init__()
        self._subscriptions = set()
        self._subscription_queue = Queue()  # queue that updates subscriptions remotely
        self._buffer = Queue()

    def close(self):
        list(self.get_events())  # clear the queue
        self._buffer.close()
        list(self.get_subscriptions())  # clear subscriptions
        self._subscription_queue.close()

    def subscribe(self, subscription: str):
        self._subscriptions.add(subscription)
        self._subscription_queue.put((True, subscription))  # add command

    def unsubscribe(self, subscription: str):
        self._subscriptions.remove(subscription)
        self._subscription_queue.put((False, subscription))  # remove command

    def get_subscriptions(self):
        # update subscriptions from remote
        while not self._subscription_queue.empty():
            (add, sub) = self._subscription_queue.get()
            if add:
                self._subscriptions.add(sub)
            else:
                self._subscriptions.remove(sub)
        return self._subscriptions.copy()

    def sink(self, event: Event):
        return self._buffer.put(event)

    def get_events(self):  # get any buffered events
        while not self._buffer.empty():
            event = self._buffer.get()
            # print(event)
            yield event

    def source(self, event_type: str, data: Dict):
        raise EventSystemError(
            "Invalid use of `RemoteSink`: `source` should never be called."
        )


class SourceLocal(SourceBase):
    """A simple implementation of a `Source` which can be used locally to buffer
    and provide events to an `EventSystem`.
    """

    def __init__(self):
        """Constructor."""
        super().__init__()
        self._buffer = deque()  # simplest kind of buffer...

    def close(self):
        """This has no effect on a `LocalSource`."""

    def source(self, event_type, data):
        self._buffer.append(Event(event_type, data))

    def get_events(self):  # get any buffered events
        while len(self._buffer) > 0:
            yield self._buffer.popleft()


class SourceRemote(SourceBase):
    """TODO docstring - is this class even used?"""

    def __init__(self):
        super().__init__()
        self._buffer = Queue()  # simplest kind of buffer...

    def close(self):
        list(self.get_events())  # clear the queue
        self._buffer.close()

    def source(self, event_type, data):
        self._buffer.put(Event(event_type, data))

    def put(
        self, event
    ):  # this is cheating a bit, but it is useful for forwarding events
        self._buffer.put(event)

    def get_events(self):  # get any buffered events
        while not self._buffer.empty():
            yield self._buffer.get()


class EventSystem:
    """TODO docstrings for this class, its an important one!"""

    def __init__(self):
        self.sinks: Set[SinkBase] = set()
        self.sources: Set[SourceBase] = set()
        self._events: EventDict = EventDict()
        self.__closed: bool = False

    def pull_events(self):
        # get all events from sources and store them in the event dict
        for source in self.sources:
            try:
                for event in source.get_events():
                    self._events.add(event.type, event)
            except TypeError as e:
                print(source, e)  # TODO
                raise EventSystemError("")

    def publish(self):
        # print(os.getpid(), len(self._events))
        for sink in self.sinks:
            events = set()
            for subscription in sink.get_subscriptions():
                events = events.union(self._events[subscription])
            for event in sorted(events, key=lambda x: x.timestamp):
                sink.sink(event)
        self._events.clear()

    def remove_sink(self, sink: SinkBase):
        self.sinks.remove(sink)

    def add_sink(self, sink: SinkBase):
        if sink is None:
            raise EventSystemError("Sink cannot be None.")
        self.sinks.add(sink)

    def remove_source(self, source: SourceBase):
        self.sources.remove(source)

    def add_source(self, source: SourceBase):
        if source is None:
            raise EventSystemError("Source cannot be None.")
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
