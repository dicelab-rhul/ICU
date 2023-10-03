from ..event2 import SinkLocal, Event

import pathlib
from datetime import datetime

ICU_LOG = "ICU::LOG"


import logging as _logging  # this is the python logging package...


class EventFormatter(_logging.Formatter):
    def format(self, record):
        # Basic data always includes the message
        data = {"message": record.getMessage()}
        # For error and exception, include exception info and stack trace
        if record.exc_info:
            data["exception"] = self.formatException(record.exc_info)
        if record.stack_info:
            data["stack_info"] = self.formatStack(record.stack_info)

        event = Event(type=f"ICU::LOG::{record.levelname}", data=data)
        return str(event)


class EventLogger(SinkLocal):
    def __init__(self, path, file=None):
        super().__init__(self.__call__)
        if file is None:
            dt = datetime.now().strftime("%Y%m%d%H%M%S")
            file = pathlib.Path(path, f"event-log-{dt}.log")
        else:
            file = pathlib.Path(path, file)

        self.handler = _logging.FileHandler(file)
        self.handler.setFormatter(EventFormatter())

        self.logger = _logging.getLogger()
        self.logger.setLevel(_logging.DEBUG)
        self.logger.addHandler(self.handler)
        self.subscribe("*")  # subscribe to everything...!

    def __call__(self, event):
        self.handler.stream.write(f"{event}\n")
        self.handler.flush()
