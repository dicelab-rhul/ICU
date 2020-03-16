
def rgb(*colour):
    return "#%02x%02x%02x" % colour 


# GENERAL

JOYSTICK = False #are we using a joystick?
EYETRACKING = True #are we using eyetracking?

COLOUR_GREEN = '#90c73e'
COLOUR_RED = '#f2644d'


BACKGROUND_COLOUR = 'lightgray'
OUTLINE_WIDTH = 2
OUTLINE_COLOUR = 'black'

WARNING_OUTLINE_COLOUR = 'red'
WARNING_OUTLINE_WIDTH = 7







MAIN_BANNER_COLOUR = '#0000fe'
MAIN_BANNER_HEIGHT = 16

#SYSTEM MONITOR
SYSTEM_MONITOR_WIDTH = 400
SYSTEM_MONITOR_HEIGHT = 400


#WARNING_LIGHT_MIN_WIDTH = 90
#WARNING_LIGHT_MIN_HEIGHT = 60

SYSTEM_MONITOR_SCALE_BACKGROUND_COLOUR = '#add9e6'
SYSTEM_MONITOR_SCALE_BACKGROUND_COLOUR_FILL = '#4882b2'
SYSTEM_MONITOR_SCALE_POSITIONS = [0,1,2,3,4] #this can be random...

#---------- TRACKING MONITOR ----------
TRACKING_LINE_COLOUR = '#268fea'

#No. pixels to move when a target move event is triggered
TRACKING_TARGET_SPEED = 2


#---------- FUEL MONITOR ----------

FUEL_MONITOR_WIDTH = 800
FUEL_MONITOR_HEIGHT = 400

FUEL_TANK_LINE_THICKNESS = 2
FUEL_TANK_LINE_COLOUR = 'black'


PUMP_HEIGHT = 20
PUMP_WIDTH = 40

#N fuel-transfer events per second
PUMP_EVENT_RATE = 10 

#fuel-transfer per second
PUMP_FLOW_RATE = {
    'AB': 100,
    'BA': 100,
    'CA': 20,
    'DB': 20,
    'EA': 30,
    'EC': 30,
    'FB': 30,
    'FD': 30
}

def RANDOM_SLEEP_SCHEDULE(min=0, max=30000):
    import random
    while True:
        yield random.randint(min, max)

#PUMP_FAIL_SCHEDULE = 3000 #fail every 3 seconds
#PUMP_FAIL_SCHEDULE = [10000,5000,7000,1000] #fail after N seconds and repeat
PUMP_FAIL_SCHEDULE = RANDOM_SLEEP_SCHEDULE()

