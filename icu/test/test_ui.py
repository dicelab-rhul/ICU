
import time

from icu.ui import start
from icu.ui import config
from icu.event2 import EventSystem, SourceLocal, SinkLocal, SourceRemote, SinkRemote


from icu.config.utils import read_configpy_file
print(config.__file__)

WINDOW_DEFAULT_CONFIGURATION = read_configpy_file(config.__file__)
print(WINDOW_DEFAULT_CONFIGURATION)

es = EventSystem()

# this is a remote source that will receive UI events
ui_remote_source = SourceRemote()
es.add_source(ui_remote_source)

# this is a remote sink that will supply UI events to the UI
# subscriptions will be set remotely in the UI
ui_remote_sink = SinkRemote()
ui_remote_sink.subscribe("UI::*")
es.add_sink(ui_remote_sink)

# local event processor, subscribes to all UI events (remote or local)
ui_event_processor = SinkLocal(print)
#ui_event_processor.subscribe("UI::*")
ui_event_processor.subscribe("UI::CONTROL::*")

es.add_sink(ui_event_processor)

ui_event_gen = SourceLocal()
es.add_source(ui_event_gen)

ui_process = start(ui_remote_source, ui_remote_sink, WINDOW_DEFAULT_CONFIGURATION)
# wait for the ui_process to finish setup before starting the event system

while ui_process.is_alive():
    time.sleep(0.1)
    ui_event_gen.source("UI::CANVAS::CLEAR", dict(color='red'))
    
    ui_event_gen.source("UI::CANVAS::DRAW_LINE", dict(start_position=(0,0), end_position=(100,100), color='white'))
    
    #ui_event_gen.source("UI::CANVAS::CLEAR", dict(color='red'))

    es.pull_events()
    es.publish()

    

es.close()
ui_process.join()
