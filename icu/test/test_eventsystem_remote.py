
from icu.event2 import EventSystem, SourceLocal, SinkLocal, SourceRemote, SinkRemote
import multiprocessing


def run(source):
    source.source("A::B::C", data=dict(a=1))

if __name__ == "__main__":


    es = EventSystem()

    ui_event_processor = SinkLocal(print)
    


    ui_source = SourceRemote()
    sink_remote = SinkRemote()

    es.add_source(source)
    es.add_sink(sink)

    

    ui = multiprocessing.Process(target=run, args=[source])
    ui.start()
    ui.join()
    
    es.pull_events()
    es.publish()
    


