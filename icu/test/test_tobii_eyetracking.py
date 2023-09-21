
from icu.event2.event import EventSystem
from icu.eyetracking.tobii import TobiiEyetracker
from icu.logging import logger
from icu.ui.root import Root

EYETRACKER_ADDRESS_URI = "tet-tcp://172.28.195.1" # update this for the test to work properly!

if __name__ == "__main__":
    try:
        event_system = EventSystem()
        event_system.add_sink(logger)

        root = Root(event_system)
    
        # eyetracker must be created AFTER pygame has been initialised
        eyetracker = TobiiEyetracker(EYETRACKER_ADDRESS_URI)
        event_system.add_source(eyetracker)
        event_system.add_sink(eyetracker)
    
        for dt in root.start_pygame_event_loop():
            pass # do some intermediate thing? 
            eyetracker.draw_debug(root.canvas)
    except Exception as e:
        raise e
    finally:
        event_system.pull_events()
        event_system.publish() 