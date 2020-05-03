
from .event import EventCallback
from .component import BaseComponent, BoxComponent

def all_highlights():
    return Highlight.__all_highlights__

class Highlight(EventCallback):

    __all_highlights__ = {}

    def __init__(self, canvas, component, state=False, highlight_thickness=4, highlight_colour='red'):
        assert isinstance(component, BaseComponent)
        super(Highlight, self).__init__()
        
        EventCallback.register(self, component.name)

        self.__canvas = canvas 
        self.__component = component
        self.__highlight_thickness = highlight_thickness

        self.component.observe('size', self.resize)
        self.component.observe('position', self.move)

        self.__box = BoxComponent(self.canvas, x=component.x, y=component.y, width=component.width, height=component.height, outline_thickness=highlight_thickness, outline_colour=highlight_colour)
        #self.__box.front()
        self.off()

        Highlight.__all_highlights__[self.name] = self

    def sink(self, event):
        #print("HIGHLIGHT: ", event)
        (self.off, self.on)[int(event.data.value)]() #love it
    
    def to_dict(self):
        return dict(state=self.is_on(), highlight_thickness=self.highlight_thickness, highlight_colour=self.highlight_colour)

    def on(self):
        self.__box.show()
       
    def off(self):
        self.__box.hide()

    @property
    def is_on(self):
        return not self.__box.is_hidden()
    
    @property
    def is_off(self):
        return self.__box.is_hidden()

    @property
    def highlight_thickness(self):
        return self.__box.outline_thickness
    
    @highlight_thickness.setter
    def highlight_thickness(self, value):
        self.__box.highlight_thickness = value

    @property
    def highlight_colour(self):
        return self.__box.outline_colour

    @highlight_colour.setter
    def highlight_colour(self, value):
         self.__box.outline_colour = value
        
    @property
    def component(self):
        return self.__component

    @property
    def canvas(self):
        return self.__canvas

    def move(self, _):
        self.__box.front() #TODO this is a work around until the layout manager supports layering
        self.__box.position = self.component.position

    def resize(self, _):
        self.__box.size = self.component.size

    def __call__(self):
        self.state = not self.state
