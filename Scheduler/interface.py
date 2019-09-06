import abc
import six
from scheduler.base import *
@six.add_metaclass(abc.ABCMeta)
class InterfaceScheduler(Scheduler):
    @abc.abstractmethod
    def __init__(self,name,plug,taskType="interval",startTime=None,sleep=0):
        """Init

            Params:
                name:taskName
                plug:call task module
                taskType:task type
                    realtime:run at now
                    interval:loop run and sleep N millisecond,default value
                    timing:run at one datetime
                startTime:first run time
                sleep:sleep millisecond
        """
        super(InterfaceScheduler,self).__init__(name,plug,taskType,startTime,sleep)

    @abc.abstractmethod
    def Run(self,*args,**kw):
        """Run process
        """