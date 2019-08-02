import queue
from multiprocessing import Process,Lock

class Q:
    def __init__(self, maxSize=100):
        self._list=queue.Queue(maxSize)
        self._lock=Lock()

    def push(self,value):
        self._lock.acquire()
        if not self.ioList.full():
            self._list.put(value)
        self._lock.release()

    def pop(self):
        self._lock.acquire()
        if not self.ioList.empty():
            return self._list.get()
        self._lock.release()