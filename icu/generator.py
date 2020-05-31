import random
import time

from . import constants as C
from .event import Event


from .tracking import Tracking


class EventGenerator:

    def __iter__(self):
        return self

class ScaleEventGenerator(EventGenerator):

    def __init__(self, scale):
        self.__scale = scale
       
    def __next__(self):
        y = random.randint(0, 1) * 2 - 1 #slide+- 1
        return Event(self.__class__.__name__, self.__scale, label=C.EVENT_LABEL_SLIDE, slide=y)
        
class WarningLightEventGenerator(EventGenerator):

    def __init__(self, warning_light):
        self.__warning_light = warning_light

    def __next__(self):
        return Event(self.__class__.__name__, self.__warning_light, label=C.EVENT_LABEL_SWITCH)

class TargetEventGenerator(EventGenerator):

    def __init__(self, target, speed=10, **kwargs):
        self.__target = target
        self.__speed = speed
        self.__time = time.time()

    def unit_vector(self):
        v = (random.gauss(0, 1), random.gauss(0,1))
        m = ((v[0]**2) + (v[1]**2)) ** .5
        return (v[0]/m,v[1]/m)
        
    def __next__(self):
        ctime = time.time()
        dt = ctime - self.__time
        self.__time = ctime
        s = self.__speed * dt
        v = self.unit_vector() 
        return Event(self.__class__.__name__, self.__target, label=C.EVENT_LABEL_MOVE, dx=v[0]*s, dy=v[1]*s)

class PumpEventGenerator:

    def __init__(self, pump, failed=False, **kwargs):
        super(PumpEventGenerator, self).__init__()
        self.__pump = pump
        self.__failed = failed

    def __next__(self):
        self.__failed = not self.__failed
        return Event(self.__class__.__name__, self.__pump, label=(C.EVENT_LABEL_REPAIR, C.EVENT_LABEL_FAIL)[int(self.__failed)]) 