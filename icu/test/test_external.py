import icu

import time
import random 

from threading import Thread
from multiprocessing import Process

from icu.process import PipedMemory


class EventSink(icu.ExternalEventSink):

    def __init__(self):
        super(EventSink, self).__init__()

class EventSource(icu.ExternalEventSource):

    def __init__(self):
        super(EventSource, self).__init__()
        
if __name__ == '__main__':
    sink = EventSink()
    source = EventSource()

    p, m = icu.start(sinks=[sink], sources=[source])
    
    print("get_event_sinks")
    print(m.event_sinks) #this will block until ICU has finished loading
    print("EVENT SINKS!")
    print(m.event_sources)

    #all of the hightlightable sinks
    highlight = [h for h in m.event_sinks if 'Highlight' in h]

    def _sink():
        if not sink.empty():
            event = sink.get()
            print("SINK", event)
        
    
    def _source():
        #time.sleep(0.1)
        source.source('agent-1', random.choice(highlight), label='highlight', value=random.choice([True,False]))

    while p.is_alive():
        #_sink()
        #print(m._in.qsize(), source.size(), sink.size())
        time.sleep(0.01)
        _source()
        _sink()

    #clear buffer after ICU has closed - clean up code, this might be OS dependant... 
    #while not sink.empty():
    #    sink.get()

    print(m._in.qsize(), source.size(), sink.size())
    p.join()

    print("DONE")