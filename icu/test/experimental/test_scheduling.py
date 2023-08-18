
from icu.event2 import EventSystem, SourceLocal, SinkLocal, load_schedule

import asyncio
import time 

async def run(event_system):
    while True:
        await asyncio.sleep(0.1)
        event_system.pull_events()
        event_system.publish()

async def main():
    
    event_system = EventSystem()
    scheduler = Scheduler()

    source = SourceLocal()
    sink = SinkLocal(print)
    sink.subscribe("*")
    
    event_system.add_sink(sink)
    event_system.add_source(source)

    source.source("TEST", data=dict(time = time.strftime("%X")))
    
    schedule = load_event_schedule("./icu/example_schedule.sch")
    for sch in schedule:
        asyncio.create_task(sch(source))

    asyncio.create_task(run(event_system))

    print("??")
    await asyncio.sleep(3) 
    print("FINISHED")

if __name__ == "__main__":

    asyncio.run(main())

