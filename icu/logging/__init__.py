
from icu.event2.event import Event
from .event_types import ICU_LOG_ERROR, ICU_LOG_INFO
from .eventlog import EventLogger
from .event_types import *

import traceback

__all__ = ("info", "EventLogger")

logger = EventLogger("./logs")
logger.subscribe(ICU_LOG + "::*")

def info(message, file=None, **kwargs): 
    data = {"message" : message, **kwargs}
    if file:
        data['file'] = file
    logger(Event(ICU_LOG_INFO, data = data))

def error(message, file=None, exception=None, **kwargs):
    data = {"message" : message, **kwargs}
    if file:
        data['file'] = file
    if exception:
        data['exception'] = str(exception)
        stack_trace = traceback.format_tb(exception.__traceback__)
        data['stacktrace'] = "".join(stack_trace)
    logger(Event(ICU_LOG_ERROR, data = data))
