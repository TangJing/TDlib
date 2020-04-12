from Cache.ring import Ring as R
from apiCore import *
import random
import threading
'''
rBuffer=R(10)
m_lock=threading.Lock()

def readBuffthread():
    while True:
        if not rBuffer.IsEmpty():
            m_lock.acquire()
            print(rBuffer.Pop())
            m_lock.release()

def writeBuffthread():
    i=0
    while True:
        if not rBuffer.IsFull():
            m_lock.acquire()
            rBuffer.Push(i)
            i+=1
            m_lock.release()

threading.Thread(target=writeBuffthread).start()
threading.Thread(target=readBuffthread).start()
'''



'''
api=apiCore("stock","v1","api")
api.addapi("getStockPrice","http://web.juhe.cn:8080/finance/stock/hs")
api.save()
print(api.call("getStockPrice","gid=sh600251&type=&key=e2ff32e1425577c504ba23bb69c2c11b"))
'''

from Scheduler.service import *

service=SchedulerService("ng")
service.start()