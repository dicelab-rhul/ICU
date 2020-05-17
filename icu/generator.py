class ScaleEventGenerator:

    def __init__(self, scale):
        self.__scale = scale

    def __call__(self):
        y = random.randint(0, 1) * 2 - 1
        yield Event(self.__class__.__name__, self.__scale, label=EVENT_NAME_SLIDE, slide=y)






def WarningLightEventGenerator():
    import time
    
    warning_lights = WarningLightComponent.all_components()
    while True:
        r = random.randint(0, len(warning_lights)-1)
        yield Event('warning_light_event_generator', warning_lights[r], label=EVENT_NAME_SWITCH)