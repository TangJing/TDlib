from enum import Enum
from threading import Condition
from queue import Queue
from TDlib.Event.Event import Event
from TDlib.Spider.models.Cache_L2 import L2, RecordStatus
import copy
thread_condition = Condition()


class L1(Event):
    def __init__(self, size=10):
        super(L1, self).__init__()
        self._L1_Size = size
        self._L1 = Queue(size)

    def push(self, value, source_url=None):
        try:
            thread_condition.acquire()
            if not self._L1.full():
                self._L1.put([value, source_url])
                self.on(event.onPush, self)
            else:
                # L1缓存数据存满了，将数据缓存到L2
                m_L2 = L2()
                m_L2.URL = value
                m_L2.Source = source_url
                m_L2.status = RecordStatus.WAIT.value
                m_L2.toSave()
                m_L2 = None
        finally:
            thread_condition.release()

    def pop(self):
        try:
            thread_condition.acquire()
            if self._L1.empty():
                # L1缓存数据读取完毕，从L2缓存读取数据
                m_L2= L2()
                m_records = m_L2.find(**{'limit': self._L1_Size})
                if m_records.count() > 0:
                    for item in m_records:
                        self._L1.put([item['url'], item['source']])
                        m_L2.model = item
                        m_L2.deleteById()
                else:
                    return None
                self.on(event.onPop, self)
            return self._L1.get()
        finally:
            thread_condition.release()

    def getSize(self):
        return self.L1.qsize()


class event(Enum):
    onPush = 'onPush'
    onPop = 'onPop'
