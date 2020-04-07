import ICU

from threading import Thread


class EventSink(ICU.ExternalEventSink, Thread):

    def __init__(self):
        pass
    
    def run(self):
        while True:
            if not self.empty():
                event = self.get()
                print(event)

sink = EventSink()
sink.start()

ICU.run()


