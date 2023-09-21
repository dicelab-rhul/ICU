
from .event_types import ICU_LOG
from ..event2 import SinkLocal

import pathlib
from datetime import datetime

class EventLogger(SinkLocal):

    def __init__(self, path, file=None):
        super().__init__(self.__call__)
        if file is None:
            path = pathlib.Path(path).expanduser().resolve().absolute()
            path.mkdir(exist_ok=True, parents=True)
            dt = datetime.now().strftime("%Y%m%d%H%M%S")
            file = pathlib.Path(path, f"event-log-{dt}.log")
        else:
            file = pathlib.Path(file).expanduser().resolve().absolute()
            file.parent.mkdir(exist_ok=True, parents=True)
        if file.exists():
            raise FileExistsError(f"Log file {file} already exists.")
        self._file = open(str(file), 'w')

        self.subscribe(ICU_LOG + "::*")

    def __call__(self, event):
        self._file.write(str(event))
        self._file.write("\n")

    def close(self):
        self._file.close()
        super().close()