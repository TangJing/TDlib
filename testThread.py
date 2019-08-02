import threading
from Event.Event import *
from Socket.model.SOCKET_MODELS import *

class tt(Event,threading.Thread):
    def __init__(self, igg):
        threading.Thread.__init__(self)
        super(tt,self).__init__()
        self.ig=0
        self.myName=igg
        self.__runing=threading.Event()
        self.__runing.set()
        print(self.Cd)
        self.registerEvent(SOCKET_EVENT.onConnection,self.Cd)
    def run(self):
        pass#self.out()

    def Cd(self,*args,**kw):
        self.ig+=1

    @trigger("connection")
    def out(self):
        while self.__runing.is_set():
            if self.ig>=100:
                self.__runing.clear()
                break
            print("%s-%s-%s\r\n" % (self.myName,self.getName(),self.ig))
            #self.ig+=1
            self.on(SOCKET_EVENT.onConnection)
        print("%s-%s-Close\r\n" % (self.myName,self.getName()))




for i in range(0,10):
    tt(i).start()