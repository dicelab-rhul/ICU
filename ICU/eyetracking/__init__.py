__EYETRACKING_ENABLED = True
__EYETRACKING_EXCEPTION = None

try:
    #import whatever
    pass
except Exception as e:
    __EYETRACKING_EXCEPTION = e
    __EYETRACKING_ENABLED = False

from threading import Thread

from .. import event

def start():
    if not __EYETRACKING_ENABLED:
        print("failed to start eye tracking - not enabled")
        return False

    #calibrate eye tracking
    #block the main thread while this is happening...?
    #trigger an event for this?
    return True #was calibration successful?

def run(event_handler, pull_every=100):
    if not __EYETRACKING_ENABLED:
        print("failed to start eye tracking - not enabled")
        return False

    import time
    import random
    
    def event_generator():
        #stub code
        while True:
            #pull events from the eyetracking buffer
            time.sleep(1/60) #data every 60th of a second
            x = y = 0
            yield event.Event(None, x,y) #x,y + other data?

    event.event_scheduler.schedule(event_generator(), sleep=pull_every, repeat=True)

