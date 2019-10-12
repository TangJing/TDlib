
from Scheduler.interface import *
from Scheduler.base import *
from Scheduler.service import *
import time

class testTask(Scheduler):
    def __init__(self, name:str, plug:str, taskType:str='interval', startTime:time=time.localtime(), sleep:int=0):
        super(testTask,self).__init__(name, plug, taskType=taskType, startTime=startTime, sleep=sleep)

    def run(self,*args:tuple,**kw:dict):
        print("testTask")


#testT=testTask("test","tasktest.Task","interval","",1)

#SchedulerService.Install(testT)

from Msg.InterfaceMsg import *
from Msg.Config import *
from Msg.SMS import *

phoneConig=Config()
phoneMsg=SMS()

