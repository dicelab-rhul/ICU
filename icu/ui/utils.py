
import math

# TODO useful utility class... maybe it should be used elsewhere rather than tuple-2?
class Point:
    # constructed using a normal tupple
    def __init__(self, x, y=None):
        if y is None:
            x, y = x
        self.x = float(x)
        self.y = float(y)
        
    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            raise IndexError(f"Index {index} out of range 2")
        
    def __setitem__(self, index, value):
        if index == 0:
            self.x = value
        elif index == 1:
            self.y = value
        else:
            raise IndexError(f"Index {index} out of range 2")

    def sum(self):
        return self.x + self.y
    
    def abs(self):
        return abs(self)
    
    def __abs__(self):
        return Point(abs(self.x), abs(self.y))

    # define all useful operators
    def __add__(self, other):
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        elif isinstance(other, (list, tuple)):
            return Point(self.x + other[0], self.y + other[1])
        elif isinstance(other, (int, float)):
            return Point(self.x + other, self.y + other)
        raise ValueError(f"Cannot add {other} from {self}.")
        
    def __sub__(self, other):
        if isinstance(other, Point):
            return Point(self.x - other.x, self.y - other.y)
        elif isinstance(other, (list, tuple)):
            return Point(self.x - other[0], self.y - other[1])
        elif isinstance(other, (int, float)):
            return Point(self.x - other, self.y - other)
        raise ValueError(f"Cannot subtract {other} from {self}.")
        
    def __mul__(self, other):
        if isinstance(other, Point):
            return Point(self.x * other.x, self.y * other.y)
        elif isinstance(other, (list, tuple)):
            return Point(self.x * other[0], self.y * other[1])
        elif isinstance(other, (int, float)):
            return Point(self.x * other, self.y * other)
        raise ValueError(f"Cannot multiply {other} from {self}.")
    
    def __div__(self, scalar):
        return Point((self.x/scalar, self.y/scalar))
    
    def __truediv__(self, scalar):
        return Point((self.x/scalar, self.y/scalar))
    
    def __len__(self):
        return int(math.sqrt(self.x**2 + self.y**2))
    
    def normalised(self):
        d = len(self)
        return Point(self.x/d, self.y/d)


    def __str__(self):
        return f"({self.x},{self.y})"
    
    def __repr__(self):
        return str(self)

    # get back values in original tuple format
    def get(self):
        return (self.x, self.y)
    
    