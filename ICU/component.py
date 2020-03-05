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

class BaseComponent:

    def __init__(self, canvas):
        self.canvas = canvas
        self.__x = 0
        self.__y = 0

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, value):
        dy = value - self.__y
        self.move(0, dy)

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, value):
        dx = value - self.__x
        self.move(dx, 0)

    @abstractmethod
    def move(self, dx, dy):
        pass
    
class SimpleComponent(BaseComponent):

    def __init__(self, canvas, component):
        super(SimpleComponent, self).__init__(canvas)
        self.component = component

    def move(self, dx, dy):
        self._BaseComponent__x += dx
        self._BaseComponent__y += dy
        self.canvas.move(self.component, dx, dy)

    def bind(self, event, callback):
        self.canvas.tag_bind(self.component, event, callback)

class BoxComponent(SimpleComponent):

    def __init__(self, canvas, width, height, colour=None, outline_colour=None, outline_thickness=None):
        rect = canvas.create_rectangle(0, 0, width, height, width=0)
        super(BoxComponent, self).__init__(canvas, rect)

        self.colour = colour
        self.outline_colour = outline_colour
        self.outline_thickness = outline_thickness

    @property
    def width(self):
        box = self.canvas.bbox(self.component)
        return box[2] - box[0]

    @property
    def height(self):
        box = self.canvas.bbox(self.component)
        return box[3] - box[1]

    @property
    def colour(self):
        return self.canvas.itemcget(self.component, "fill")

    @colour.setter
    def colour(self, value):
        self.canvas.itemconfigure(self.component, fill=value)

    @property
    def outline_thickness(self):
        return self.canvas.itemcget(self.component, "width") 

    @outline_thickness.setter
    def outline_thickness(self, value):
        self.canvas.itemconfigure(self.component, width=value)

    @property
    def outline_colour(self):
        return self.canvas.itemcget(self.component, "outline") 

    @outline_colour.setter
    def outline_colour(self, value):
        self.canvas.itemconfigure(self.component, outline=value)

class CanvasWidget(BaseComponent):

    def __init__(self, canvas, width, height, components={}, background_colour=None, outline_colour=None, outline_thickness=None):
        super(CanvasWidget, self).__init__(canvas)
        self.width = width
        self.height = height

        self.components = dict(**components)
      
        self.components['background'] = SimpleComponent(self.canvas, self.canvas.create_rectangle(0, 0, width, height,width=0))
        self.background_colour = background_colour
        self.outline_colour = outline_colour
        self.outline_thickness = outline_thickness

        self.canvas.tag_lower(self.components['background'].component)
    
        self.__debug = None
        #self.components['__debug'] = None

    def anchor(self, component, anchor): #anchor N,E,S,W,C #north east south west or center
        #TODO refactor this garbage
        component = self.components[component]
        if anchor == 'W': 
            component.x = self.x
        elif anchor == 'E':
            component.x = self.x + self.width - component.width
        else:
            raise NotImplementedError("TODO")

    @property
    def background(self):
        return self.components['background']

    @property
    def background_colour(self):
        return self.canvas.itemcget(self.background.component, "fill")

    @background_colour.setter
    def background_colour(self, value):
        self.canvas.itemconfigure(self.background.component, fill=value)

    @property
    def outline_thickness(self):
        return self.canvas.itemcget(self.background.component, "width") 

    @outline_thickness.setter
    def outline_thickness(self, value):
        self.canvas.itemconfigure(self.background.component, width=value)

    @property
    def outline_colour(self):
        return self.canvas.itemcget(self.background.component, "outline") 

    @outline_colour.setter
    def outline_colour(self, value):
        self.canvas.itemconfigure(self.background.component, outline=value)

    def move(self, dx, dy):
        self._BaseComponent__x += dx
        self._BaseComponent__y += dy
        for component in self.components:
            self.components[component].move(dx,dy)
        if self.__debug is not None:
            self.__debug.move(dx, dx)

    def scale(self, x, y):
        raise NotImplementedError("TODO...")

    def debug(self):
        print(self.x, self.y, self.x+self.width, self.y+self.height)
        self.__debug = SimpleComponent(self.canvas, self.canvas.create_rectangle(self.x, self.y, self.x+self.width, self.y+self.height, width=1, outline='red'))


        
        