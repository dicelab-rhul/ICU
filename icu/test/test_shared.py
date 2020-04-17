import multiprocessing
#multiprocessing.set_start_method('spawn')
from multiprocessing import Process, Queue, Pipe
import os

import time 
from icu.process import PipedMemory

def init(send, receive):
    print("INIT")
    send.event_sources = ['source1']
    send.event_sinks = ['sink1']

    print(send.event_sources)

    time.sleep(.5)

    print(receive.event_sources)

    #print(q.event_sources)

if __name__ == '__main__':
    send1, receive1 = PipedMemory(event_sources=[], event_sinks=[])
    send2, receive2 = PipedMemory(event_sources=[], event_sinks=[])

    p = Process(target=init, args=(send1, receive2))
    p.daemon = True
    p.start()

    send2.event_sources = ["send2"]

    time.sleep(1)

    print(receive1.event_sources)

    print("DONE?")