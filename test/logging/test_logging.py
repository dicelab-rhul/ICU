from icu import logging


logging.debug("This is a debug message.")
logging.info("This is an info message.")
logging.warning("This is a warning message.")
logging.error("This is an error message.")
try:
    1 / 0
except ZeroDivisionError:
    logging.exception("This is an exception message.")
