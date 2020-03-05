from abc import ABC, abstractmethod

class Component(ABC):

    __components__ = {} #all of the visual components, tanks, pumps, tracking etc

    def __init__(self, *args, **kwargs):
        super(Component, self).__init__(*args, **kwargs)
    
    def register(self, name):
        self.__name = "{0}:{1}".format(type(self).__name__, name)
        Component.__components__[self.__name] = self
        print("INFO: registered component: {0}".format(self.__name))

    @abstractmethod
    def highlight(self, *args, **kwargs):
        pass

def all_components():
    return Component.__components__