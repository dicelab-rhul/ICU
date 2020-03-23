from abc import ABC, abstractmethod

class Component(ABC):

    __components__ = {} #all of the visual components, tanks, pumps, tracking etc

    def __init__(self, *args, **kwargs):
        super(Component, self).__init__(*args, **kwargs)
    
    def register(self, name):
        self.__name = "{0}:{1}".format(type(self).__name__, name)
        Component.__components__[self.__name] = self
        #print("INFO: registered component: {0}".format(self.__name))

    @property
    def name(self):
        return self.__name

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

    def add(self, component, prop, max_size=float('inf'), min_size=-float('inf')):
        self.__split.append(component)
        self.__split_p.append(prop)
        _sp = sum(self.__split_p)
        px = self.manager.component_x
        gt = self.__inner_sep * (len(self.__split) - 1)
        for i, component in enumerate(self.__split):
            _p = self.__split_p[i] / _sp
            component.x = px
            _s = (self.manager.component_width - gt) * _p
            component.width = max(min(_s, max_size), min_size)
            px = px + component.width + self.__inner_sep

class SplitLayoutY:

    def __init__(self, manager, inner_sep=0.):
        self.manager = manager
        self.__split = []
        self.__split_p = []
        self.__inner_sep = inner_sep

    def add(self, component, prop, max_size=float('inf'), min_size=-float('inf')):
        self.__split.append(component)
        self.__split_p.append(prop)
        _sp = sum(self.__split_p)
        py = self.manager.component_y
        gt = self.__inner_sep * (len(self.__split) - 1)
        for i, component in enumerate(self.__split):
            _p = self.__split_p[i] / _sp
            component.y = py
            _s = (self.manager.component_height - gt) * _p
            component.height = max(min(_s, max_size), min_size)
            py = py + component.height + self.__inner_sep

class SimpleLayoutManager:

    def __init__(self, component, inner_sep=0., inner_sep_x=0., inner_sep_y=0.):
        self.component = component
        self.__split_x = SplitLayoutX(self, inner_sep=max(inner_sep, inner_sep_x))
        self.__split_y = SplitLayoutY(self, inner_sep=max(inner_sep, inner_sep_y))

    def split(self, component, axis, prop=1., max_size=float('inf'), min_size=-float('inf')): #X,Y or combination
        component = self.component.components[component]

        if 'X' in axis:
            self.__split_x.add(component, prop, max_size=max_size, min_size=min_size)

        if 'Y' in axis:
            self.__split_y.add(component, prop, max_size=max_size, min_size=min_size)

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


from collections import defaultdict

class BaseComponent:

    def __init__(self, canvas, x=0., y=0., width=0., height=0., padding=0.):
        self.canvas = canvas
        self.__x = x
        self.__y = y
        self.__width = width
        self.__height = height
        self.__padding = __validate_padding__(padding)

        self.__observers = defaultdict(list)

    def observe(self, attr, callback):
        self.__observers[attr].append(callback)
    
    def unobserve(self, attr, callback):
        self.__observers[attr].remove(callback) #hmm...

    @property
    def observers(self):
        return self.__observers

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
        
        for observer in self.observers['size']:
            observer((dw, dh))

    @property
    def width(self):
        return self.__width

    @width.setter
    def width(self, value):
        dw = value -  self.__width
        self.__width = value
        self.resize(dw, 0)
        for observer in self.observers['size']:
            observer((dw, 0))

    @property
    def height(self):
        return self.__height

    @height.setter
    def height(self, value):
        dh = value - self.height
        self.__height = value
        self.resize(0, dh)
        for observer in self.observers['size']:
            observer((0, dh))
    
    @property
    def position(self):
        return (self.__x, self.__y)

    @position.setter
    def position(self, value):
        dx, dy = value[0] - self.__x, value[1] - self.__y
        self.__x, self.__y = value
        self.move(dx, dy)
        for observer in self.observers['position']:
            observer((dx, dy))

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, value):
        dy = value - self.__y
        self.__y = value
        self.move(0, dy)
        for observer in self.observers['position']:
            observer((0, dy))

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, value):
        #print(self.observers['position'])
        dx = value - self.__x
        self.__x = value
        self.move(dx, 0)
        for observer in self.observers['position']:
            observer((dx, 0))

    @abstractmethod
    def move(self, dx, dy):
        pass

    @abstractmethod
    def resize(self, dw, dh):
        pass

#TODO bind doesnt seem to work for some reason...?

class SimpleComponent(BaseComponent):

    def __init__(self, canvas, component, padding=0.):
        super(SimpleComponent, self).__init__(canvas, padding=padding)
        self.component = component
        x1,y1,x2,y2 = self.canvas.coords(self.component)
        self._BaseComponent__x = x1
        self._BaseComponent__y = y1
        self._BaseComponent__width = x2-x1
        self._BaseComponent__height = y2-y1

        #print(x1,y1,x2,y2)

    def move(self, dx, dy):
        self.canvas.move(self.component, dx, dy)

    def resize(self, dw, dh):
        #print(self, "resize:", self.width - dw, self.height - dh, "to:", self.width, self.height)
        x1,y1,_,_ = self.canvas.coords(self.component)
        self.canvas.coords(self.component, x1, y1, x1 + self.width, y1 + self.height)
 
    def bind(self, event, callback):
        self.canvas.tag_bind(self.component, event, callback)

    def front(self):
        self.canvas.tag_raise(self.component)

    def back(self):
        self.canvas.tag_lower(self.component)

class LineComponent(SimpleComponent):

    def __init__(self, canvas, x1,y1,x2,y2, colour='black', thickness=None):
        line = canvas.create_line(x1,y1,x2,y2,fill=colour,width=thickness)
        super(LineComponent, self,).__init__(canvas, line)

class BoxComponent(SimpleComponent):

    def __init__(self, canvas, x=0., y=0., width=1., height=1., colour=None, outline_colour=None, outline_thickness=None):
        rect = canvas.create_rectangle(x, y, x+width, y+height, width=outline_thickness, fill=colour, outline=outline_colour)
        super(BoxComponent, self).__init__(canvas, rect)

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
        if value == 0:
            self.outline_colour = "" #?? for some reason it crashes otherwise... TODO 
        else:
            self.canvas.itemconfigure(self.component, width=value)

    @property
    def outline_colour(self):
        return self.canvas.itemcget(self.component, "outline") 

    @outline_colour.setter
    def outline_colour(self, value):
        self.canvas.itemconfigure(self.component, outline=value)

class CanvasWidget(BaseComponent):

    def __init__(self, canvas, x=0,y=0, width=1., height=1., components={}, layout_manager=None, background_colour=None, outline_colour="black", outline_thickness=0, 
                padding=0., inner_sep=0., inner_sep_x=0., inner_sep_y=0.):

        width = max(max([c.width for c in components.values()], default=0), width)
        height = max(max([c.height for c in components.values()], default=0), height)
        super(CanvasWidget, self).__init__(canvas, x=x, y=y, width=width, height=height, padding=padding)

        if layout_manager is None:
            self.layout_manager = SimpleLayoutManager(self, inner_sep=inner_sep, inner_sep_x=inner_sep_x, inner_sep_y=inner_sep_y)

        self.components = dict(**components)
        
        self.components['background'] = BoxComponent(self.canvas, x=x,y=y,width=width,height=height, colour=background_colour,
                                                         outline_colour=outline_colour, outline_thickness=outline_thickness)
        self.__debug = None
    
    def front(self):
        #TODO does not preserve ordering...
        for c in self.components.values():
            self.canvas.tag_raise(c)

    def back(self):
        #TODO does not preserve ordering...
        for c in self.components.values():
            self.canvas.tag_lower(c)

    def bind(self, event, callback):
        self.components['background'].bind(event, callback)
  
    @property
    def background(self):
        return self.components['background']

    @property
    def background_colour(self):
        return self.background.colour

    @background_colour.setter
    def background_colour(self, value):
        self.background.colour = value

    @property
    def outline_thickness(self):
        return self.background.outline_thickness

    @outline_thickness.setter
    def outline_thickness(self, value):
        self.background.outline_thickness = value

    @property
    def outline_colour(self):
        return self.background.outline_colour

    @outline_colour.setter
    def outline_colour(self, value):
        self.background.outline_colour = value
        
    def move(self, dx, dy):
        for component in self.components:
            c = self.components[component]
            c.position = (c.x + dx, c.y + dy)

        if self.__debug is not None:
            self.__debug.position = (self.__debug.x + dx, self.__debug.y + dy)

    def resize(self, dw, dh):
        pw, ph = self.width - dw, self.height - dh

        sw, sh = self.width / pw, self.height / ph
        #print(self, "scale:", sw, sh, "from:", pw,ph, "to:", self.width, self.height)
        for c in self.components.values(): #scale each widget
            c.size = (c.width * sw, c.height * sh)
           
            c.x = self.x + (c.x - self.x) * sw
            c.y = self.y + (c.y - self.y) * sh

        #x1,y1,_,_ = self.canvas.coords(self.components['background'].component)
        #self.canvas.coords(self.components['background'].component, x1, y1, x1 + width, y1 + height)
 

    def debug(self):
        print(self.x, self.y, self.x+self.width, self.y+self.height)
        if self.__debug is not None:
            raise NotImplementedError()
            #TODO remove component

        self.__debug = SimpleComponent(self.canvas, self.canvas.create_rectangle(self.x, self.y, self.x+self.width, self.y+self.height, width=1, outline='red'))


class Highlight:

    def __init__(self, canvas, component, state=False, highlight_thickness=4, highlight_colour='red'):
        assert isinstance(component, BaseComponent)
        self.canvas = canvas 
        self.component = component
        self.state = state # initial state False=OFF, True=ON

        self.component.observe('size', self.resize)
        self.component.observe('position', self.move)

        self.__box = BoxComponent(self.canvas, x=component.x, y=component.y, width=component.width, height=component.height, outline_thickness=highlight_thickness, outline_colour=highlight_colour)
        self.__box.front()

    @property
    def highlight_thickness(self):
        return self.__box.outline_thickness
    
    @highlight_thickness.setter
    def highlight_thickness(self, value):
        self.__box.outline_thickness = value
    
    @property
    def highlight_colour(self):
        return self.__box.outline_colour

    @highlight_colour.setter
    def highlight_colour(self, value):
         self.__box.outline_colour = value

    def move(self, _):
        self.__box.front() #TODO this is a work around until the layout manager supports layering
        self.__box.position = self.component.position

    def resize(self, _):
        self.__box.size = self.component.size

    def __call__(self):
        self.state = not self.state

        
