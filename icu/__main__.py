
import time
import math
from datetime import datetime

from icu.ui import start
from icu.event2 import EventSystem, SourceLocal, SinkLocal, SourceRemote, SinkRemote
from icu.event2.utils import ConditionalTimer


from icu.config import DEFAULT_CONFIGURATION

es = EventSystem()

# this is a remote source that will receive UI events from the UI 
ui_remote_source = SourceRemote()
es.add_source(ui_remote_source)

# this is a remote sink that will supply command events to the UI
# subscriptions will be set remotely in the UI
ui_remote_sink = SinkRemote()
ui_remote_sink.subscribe("ICU::TRACKINGTASK::*")
es.add_sink(ui_remote_sink)

# local event processor, subscribes to all UI events
ui_event_processor = SinkLocal(lambda event : print(f"MAIN RECEIVED: {event}"))
ui_event_processor.subscribe("UI::*")

es.add_sink(ui_event_processor)

ui_event_gen = SourceLocal()
es.add_source(ui_event_gen)

ui_process = start(ui_remote_source, ui_remote_sink, DEFAULT_CONFIGURATION) # TODO we dont want to provide the full default configuration!?
# wait for the ui_process to finish setup before starting the event system

#with ConditionalTimer(0.1) as ct:

while ui_process.is_alive():
    time.sleep(0.01)
    
    #if ct.should_execute():
    x = 0.05 + (1 + math.sin(datetime.now().timestamp())) / 6
    ui_event_gen.source("ICU::TRACKINGTASK::SET_PROPERTY", dict(failure_boundary_proportion = x))

    #ui_event_gen.source("UI::CANVAS::CLEAR", dict(color='red'))
    #x = 100 + math.sin(datetime.now().timestamp()) * 100
    #ui_event_gen.source("UI::CANVAS::DRAW_LINE", dict(start_position=(x,100), end_position=(200 - x,200), color='white'))
    #ui_event_gen.source("UI::CANVAS::DRAW_RECT", dict(position=(500,100), size=(100,100), color='white', rotation=x))
    #ui_event_gen.source("UI::CANVAS::DRAW_CIRCLE", dict(position=(400,400), radius=x, color='white'))
    #ui_event_gen.source("UI::CANVAS::CLEAR", dict(color='red'))
    es.pull_events()
    es.publish()

es.close()
ui_process.join()
