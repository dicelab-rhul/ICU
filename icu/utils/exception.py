""" This module defines `Exception` subclasses. """


class EventSystemError(Exception):
    pass


class EventTypeError(EventSystemError):
    """An error that occurs in the [SinkBase.sink] method when an invalid or unexpected event is received."""

    def __init__(self, sink, event_type: str):
        super().__init__("Sink %s received invalid event type %s.", sink.id, event_type)


class ConfigurationError(Exception):
    pass
