from multiprocessing import Process, Queue

class Event:

    def __init__(self):
        self.x = 0
        self.y = 1

def f(q):
    q.put(Event())

if __name__ == '__main__':
    q = Queue()
    p = Process(target=f, args=(q,))
    p.start()
    print(q.get())    # prints "[42, None, 'hello']"

    

    p.join()