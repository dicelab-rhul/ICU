class property_event(property):

    def __set__(self, obj, value):
        old_value = super().__get__(obj)
        result = super().__set__(obj, value)
        new_value = super().__get__(obj)
        #obj.source(obj.address + DELIMITER + CHANGED, dict(old = old_value, new = new_value) ) # this decorator can only be used on an event source... TODO check this? 
        print(old_value, new_value)
        return result 
    
class MyClass:

    def __init__(self):
        self._event_frequency = 0

    @property_event
    def event_frequency(self):
        return self._event_frequency

    @event_frequency.setter
    def event_frequency(self, value):
        if value <= 0:
            raise ValueError(f"event_frequency must be greater than 0, got {value}")
        self._event_frequency = value

# Create an instance of MyClass
obj = MyClass()

# Set the event_frequency property (this will trigger the custom setter)
obj.event_frequency = 5

setattr(obj, 'event_frequency', 5)
