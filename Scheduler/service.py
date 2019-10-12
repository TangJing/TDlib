import shelve
import os
import io
import time
import configparser
import threading

from bin.globalvar import *
from TDlib.reflect import *
from Scheduler.base import *


class SchedulerService(threading.Thread):
    def __init__(self,serializeFile):
        threading.Thread.__init__(self)
        self._cacheFile=serializeFile
        self._eventLock=threading.Event()
        self._eventLock.set()
        self._timeArray=[0]*86400  #一天的86400秒
        self._index=time.localtime().tm_hour * 60 * 60 + time.localtime().tm_min * 60 + time.localtime().tm_sec  #当前秒索引
        threading.Thread(target=self.Scheduler).start()  #启动任务列表线程
        #with shelve.open("",flag="r") as serialize:
        #    self._timeArray=serialize["taskScheduler"]  #从缓存中获取调度配置

    def Scheduler(self,*args,**kw):
        """Scheduler method"""
        while True:
            self._eventLock.wait()
            #print("%d.scheduler\r\n" % self._index)
            if(self._timeArray[self._index] != 0):
                threading.Thread(self._timeArray[self._index]).start()
            self._eventLock.clear()
            if self._index >= 86400:
                self.LoadConfig()
                self.run()

    def LoadConfig(self):
        """Load scheduler config"""
        pass
    def Install(self,task:Scheduler):
        """Install task"""
        config=task.Config()
        '''config params
        config["type"]
        config["starttime"]
        config["sleep"]
        config["plug"]
        config["name"]'''
        with shelve.open(self._cacheFile,flag="c",writeback=True) as cFile:  #open config cache file
            try:
                if config["type"].lower() == "realtime":   #run on now
                    pass
                elif config["type"].lower() == "interval":  #loop run task
                    pass
                elif config["type"].lower() == "timming":  #run on datetime with oncee
                    pass
            finally:
                cFile.close()

    def Uninstall(self,task):
        """Uninstall task
        """
        pass

    def run(self,*args,**kw):
        while True:
            self._index += 1
            self._eventLock.set()
            if self._index >= 86400:  #当日计时完毕
                break  #等待当日任务执行完毕
            time.sleep(1)