
class property_event(property):
    def __set__(self, obj, value):
        old_value = super().__get__(obj)
        result = super().__set__(obj, value)
        new_value = super().__get__(obj)
        print(old_value, new_value)
        #obj.source(obj.address + DELIMITER + CHANGED, dict(old = {self.fset.__name__ : old_value}, new = {self.fset.__name__  : new_value}) ) # this decorator can only be used on an event source... TODO check this? 
        return result 
    
def cosmetic_options(**options):
    def decorator(cls):
        original_init = cls.__init__
        def _cosmetic_init_(self, *args, **kwargs):
            for option, value in options.items():
                backing = "_" + option
                setattr(self, backing, value)
            return original_init(self, *args, **kwargs)
        # set properties for the class
        for option, _ in options.items():
            backing = "_" + option
            setattr(cls, option, property_event(lambda self, backing=backing: getattr(self, backing), lambda self, v, backing=backing: setattr(self, backing, v)))
        cls.__init__ = _cosmetic_init_
        return cls
    return decorator

@cosmetic_options(
    a = 1,
    b = 2,
    c = 3,
)
class Test:
    
    def __init__(self):
        self._z = 1


t = Test()

print(dir(t))

print(t.a)
print(t.b)
print(t.c)
print(t._z)