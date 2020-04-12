
from Event.Event import Event
import threading
import queue
class testThread(threading.Thread):
    def __init__(self, a_length):
        super(testThread, self).__init__()

    def run(self):

class cache:
    def __init__(self, max_length):
        self._m_arr= queue.Queue(max_length)

    def push(self, args):
        if not self._m_arr.full():
            self._m_arr.put(args)

    def pop(self, args):
        if not self._m_arr.empty():
            return self._m_arr.get()

if __name__ == "__main__":
    m_cache= cache(10)
    for i in range(0,1000):
        m_cache.push(i)


'''
import threading,time
from random import randint
class Producer(threading.Thread):
    def run(self):
        global L
        while True:
            val=randint(0,100)
            # print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            print('生产者',self.name,' Append'+str(val),L)
            if lock_con.acquire():
                L.append(val)
                lock_con.notify()
                lock_con.release()
            time.sleep(3)
class Consumer(threading.Thread):
    def run(self):
        global L
        while True:
            lock_con.acquire()
            if len(L)==0:
                lock_con.wait()
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            print('消费者',self.name,'Delete'+str(L[0]),L)
            del L[0]
            lock_con.release()
            time.sleep(0.5)
if __name__=='__main__':
    L=[]
    lock_con=threading.Condition()
    threads=[]
    for i in range(5):
        threads.append(Producer())
    threads.append(Consumer())
    for t in threads:
        t.start()
    for t in threads:
        t.join()
'''