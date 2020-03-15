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

def __validate_padding__(padding):
    if isinstance(padding, (int, float)):
        return (padding, padding)
    elif isinstance(padding, (tuple, list)) and len(padding) == 2:
        return padding
    else:
        raise ValueError("Invalid argument padding: {0}, must be int, float, tuple/2 or list/2".format(padding))


#TODO REFACTOR!

class SplitLayoutX:

    def __init__(self, manager, inner_sep=0.):
        self.manager = manager
        self.__split = []
        self.__split_p = []
        self.__inner_sep = inner_sep

    def add(self, component, prop):
        self.__split.append(component)
        self.__split_p.append(prop)
        _sp = sum(self.__split_p)
        px = self.manager.component_x
        gt = self.__inner_sep * (len(self.__split) - 1)
        for i, component in enumerate(self.__split):
            _p = self.__split_p[i] / _sp
            component.x = px
            component.width = (self.manager.component_width - gt) * _p
            px = px + component.width + self.__inner_sep

class SplitLayoutY:

    def __init__(self, manager, inner_sep=0.):
        self.manager = manager
        self.__split = []
        self.__split_p = []
        self.__inner_sep = inner_sep

    def add(self, component, prop):
        self.__split.append(component)
        self.__split_p.append(prop)
        _sp = sum(self.__split_p)
        py = self.manager.component_y
        gt = self.__inner_sep * (len(self.__split) - 1)
        for i, component in enumerate(self.__split):
            _p = self.__split_p[i] / _sp
            component.y = py
            component.height = (self.manager.component_height - gt) * _p
            py = py + component.height + self.__inner_sep

class SimpleLayoutManager:

    def __init__(self, component, inner_sep=0., inner_sep_x=0., inner_sep_y=0.):
        self.component = component
        self.__split_x = SplitLayoutX(self, inner_sep=max(inner_sep, inner_sep_x))
        self.__split_y = SplitLayoutY(self, inner_sep=max(inner_sep, inner_sep_y))

    def split(self, component, axis, prop=1.): #X,Y or combination
        component = self.component.components[component]

        if 'X' in axis:
            self.__split_x.add(component, prop)

        if 'Y' in axis:
            self.__split_y.add(component, prop)

    def fill(self, component, axis):
        component = self.component.components[component]

        if 'X' in axis:
            component.x = self.component.x + self.padding[0]
            component.width = self.component.content_width
        
        if 'Y' in axis:
            component.y = self.component.y + self.padding[1]
            component.height = self.component.content_height
    
    def anchor(self, component, anchor): #anchor N,E,S,W,C #north east south west or center
        #TODO refactor this garbage
        if isinstance(component, str):
            component = self.component.components[component]

        if anchor == 'W': 
            component.x = self.component.x + self.padding[0]
        elif anchor == 'E':
            component.x = self.component.x + self.component.width - component.width - self.padding[0]
        elif anchor == 'N':
            component.y = self.component.y + self.padding[1]
        elif anchor == 'S':
            component.y  =self.component.y + self.component.height - component.height - self.padding[1]
        else:
            raise NotImplementedError("TODO")


    @property
    def component_width(self):
        return self.component.content_width

    @property
    def component_height(self):
        return self.component.content_height

    @property
    def component_x(self):
        return self.component.x + self.component.padding[0]

    @property
    def component_y(self):
        return self.component.y + self.component.padding[1]

    @property
    def padding(self):
        return self.component.padding
    
    @padding.setter
    def padding(self):
        self.component.padding = padding
     
class BaseComponent:

    def __init__(self, canvas, width=0., height=0., padding=0.):
        self.canvas = canvas
        self.__x = 0
        self.__y = 0
        self.__width = width
        self.__height = height
        self.__padding = __validate_padding__(padding)

    @property
    def padding(self):
        return self.__padding

    @property
    def content_width(self):
        return self.__width - self.__padding[0] * 2

    @property
    def content_height(self):
        return self.__height - self.__padding[1] * 2

    @property
    def size(self):
        return self.__width, self.__height

    @size.setter
    def size(self, value):
        dw, dh = value[0] - self.__width, value[1] - self.__height
        self.__width, self.__height = value
        self.resize(dw, dh)

    @property
    def width(self):
        return self.__width

    @width.setter
    def width(self, value):
        dw = value -  self.__width
        self.__width = value
        self.resize(dw, 0)

    @property
    def height(self):
        return self.__height

    @height.setter
    def height(self, value):
        dh = value - self.height
        self.__height = value
        self.resize(0, dh)
    
    @property
    def position(self):
        return (self.__x, self.__y)

    @position.setter
    def position(self, value):
        dx, dy = value[0] - self.__x, value[1] - self.__y
        self.__x, self.__y = value
        self.move(dx, dy)

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, value):
        dy = value - self.__y
        self.__y = value
        self.move(0, dy)

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, value):
        dx = value - self.__x
        self.__x = value
        self.move(dx, 0)

    @abstractmethod
    def move(self, dx, dy):
        pass

    @abstractmethod
    def resize(self, dw, dh):
        pass
    
class SimpleComponent(BaseComponent):

    def __init__(self, canvas, component, width=1., height=1., padding=0.):
        super(SimpleComponent, self).__init__(canvas, width=width, height=height, padding=padding)
        self.component = component

    def move(self, dx, dy):
        self.canvas.move(self.component, dx, dy)

    def resize(self, dw, dh):
        x1,y1,_,_ = self.canvas.coords(self.component)
        self.canvas.coords(self.component, x1, y1, x1 + self.width, y1 + self.height)
 
    def bind(self, event, callback):
        self.canvas.tag_bind(self.component, event, callback)

class BoxComponent(SimpleComponent):

    def __init__(self, canvas, width=1., height=1., colour=None, outline_colour=None, outline_thickness=None):
        rect = canvas.create_rectangle(0, 0, width, height, width=outline_thickness)
        super(BoxComponent, self).__init__(canvas, rect, width=width, height=height)

        self.colour = colour
        self.outline_colour = outline_colour
        self.outline_thickness = outline_thickness

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

    def __init__(self, canvas, width=1., height=1., components={}, layout_manager=None, background_colour=None, outline_colour=None, outline_thickness=None, 
                padding=0., inner_sep=0., inner_sep_x=0., inner_sep_y=0.):
        width = max(max([c.width for c in components.values()], default=0), width)
        height = max(max([c.height for c in components.values()], default=0), height)
        super(CanvasWidget, self).__init__(canvas, width=width, height=height, padding=padding)

        if layout_manager is None:
            self.layout_manager = SimpleLayoutManager(self, inner_sep=inner_sep, inner_sep_x=inner_sep_x, inner_sep_y=inner_sep_y)

        self.components = dict(**components)
        
        self.components['background'] = SimpleComponent(self.canvas, self.canvas.create_rectangle(0, 0, width, height, width=0))
        
        self.background_colour = background_colour
        self.outline_colour = outline_colour
        self.outline_thickness = outline_thickness

        self.canvas.tag_lower(self.components['background'].component)
    
        self.__debug = None
    
  
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
        for component in self.components:
            c = self.components[component]
            c.position = (c.x + dx, c.y + dy)

        if self.__debug is not None:
            self.__debug.position = (self.__debug.x + dx, self.__debug.y + dy)

    def resize(self, dw, dh):
        pw, ph = self.width - dw, self.height - dh
        sw, sh = pw / self.width, ph / self.height

        for c in self.components.values(): #scale each widget
            c.size = (c.width * sw, c.height * sh)

        #x1,y1,_,_ = self.canvas.coords(self.components['background'].component)
        #self.canvas.coords(self.components['background'].component, x1, y1, x1 + width, y1 + height)
 

    def debug(self):
        print(self.x, self.y, self.x+self.width, self.y+self.height)
        self.__debug = SimpleComponent(self.canvas, self.canvas.create_rectangle(self.x, self.y, self.x+self.width, self.y+self.height, width=1, outline='red'))


        
        