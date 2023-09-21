""" This module defines the publish-subscribe event system that is used by the ICU(a) system."""

from .dict import EventDict
from .event import Event, EventSystem
from .event import SourceBase, SourceLocal, SourceRemote, SinkBase, SinkLocal, SinkRemote
from .schedule import load_schedule

# delimiter used between event types, e.g. ICU::LOG::INFO
DELIMITER = "::"
# wild card used to signify "any" in a subscription, e.g. ICU::LOG::* will subscribe to any logging event (INFO, WARNING, ERROR, ...)
WILDCARD = "*"

__all__ = ("Event", "EventSystem", "SourceBase", "SourceLocal", "SourceRemote", "SinkBase", "SinkLocal", "SinkRemote", "load_schedule")
