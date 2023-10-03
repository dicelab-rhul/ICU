from .eventlog import EventLogger

# this is a logger for events that are triggered via the event system.
logger = EventLogger("./logs")

# aliases for the logger above
debug = logger.logger.debug
info = logger.logger.info
warning = logger.logger.warning
error = logger.logger.error
exception = logger.logger.exception
