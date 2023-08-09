

import uuid
from json import dumps
from datetime import datetime
from copy import deepcopy
from dataclasses import dataclass

@dataclass(frozen=True)
class Event:

    def __init__(self, src, dst, **data):
        super(Event, self).__init__()
        assert isinstance(src, str)
        assert isinstance(src, str)
        self.id = str(uuid.uuid5(src, dst).int)
        self.dst = dst
        self.src = src
        self.data = deepcopy(data)
        self.timestamp = datetime.now()
        
    def __str__(self):
        return "{0}:{1} - ({2}->{3}): {4}".format(self.id, self.timestamp, self.src, self.dst, self.data)
    
if __name__ == "__main__":
    event = Event('test', 'test', a=1)
    print(event)