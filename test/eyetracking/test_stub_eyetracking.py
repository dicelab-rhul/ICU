""" 
    Test for `icu.eyetracking.tobii.TobiiEyetracker` that displays where the user is currently 
    looking on a pygame window. The test requires a calibrated tobii eyetracker and its uri 
    (see `EYETRACKER_ADDRESS_URI` in source).
"""

import asyncio
from icu.event2.event import EventSystem
from icu.eyetracking.stub import StubEyetracker
from icu.logging import logger
from icu.ui.root import Root


async def run():
    try:
        # create event system
        event_system = EventSystem()
        # add a logger
        event_system.add_sink(logger)

        root = Root(event_system)

        # eye_event_sink = SinkLocal(print)
        # event_system.add_sink(eye_event_sink)
        # eye_event_sink.subscribe(UI_INPUT_EYETRACKING)
        # eye_event_sink.subscribe(UI_WINDOW_WINDOWMOVED)
        # eye_event_sink.subscribe(UI_WINDOW_WINDOWRESIZED)

        eyetracker = StubEyetracker(sample_rate=30)
        event_system.add_source(eyetracker)
        event_system.add_sink(eyetracker)

        async def run_event_loop():
            for _ in root.start_pygame_event_loop():
                eyetracker.draw_debug(root.canvas)
                await asyncio.sleep(1 / 60)

        await asyncio.create_task(run_event_loop())

    except Exception as exception:
        raise exception
    finally:
        event_system.pull_events()
        event_system.publish()


if __name__ == "__main__":
    asyncio.run(run())
