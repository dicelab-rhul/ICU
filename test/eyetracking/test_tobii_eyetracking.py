""" 
    Test for `icu.eyetracking.tobii.TobiiEyetracker` that displays where the user is currently 
    looking on a pygame window. The test requires a calibrated tobii eyetracker and its uri 
    (see `EYETRACKER_ADDRESS_URI` in source).
"""

from icu.event2.event import EventSystem
from icu.eyetracking.tobii import TobiiEyetracker
from icu.logging import logger
from icu.ui.root import Root

# update this for the test to work properly!
EYETRACKER_ADDRESS_URI = "tet-tcp://172.28.195.1"

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
            eyetracker.draw_debug(root.canvas)
    except Exception as e:
        raise e
    finally:
        event_system.pull_events()
        event_system.publish()
