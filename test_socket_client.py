from Socket.Client import Client
from Socket.model.SOCKET_MODELS import *
import threading
import time
import socket

class cle(Client):
    def __init__(self, ip, port, buffSize=1024):
        super(cle,self).__init__(ip, port, buffSize)
        self.__registerEvent()

    def onsendComplete(self,*args,**kw):
        pass

    def onRecv(self,*args,**kw):
        print("%s:\r\n\tClient Recv: \r\n\t%s\r\n" % (self.getName(),args[0]))
        self.sendMsg(self.getName().encode("utf8"))
        #self.setRuning()
        
        

    def onError(self,*args,**kw):
        print("%s:\r\n\t %s\r\n" % (self.getName(),args))

    def onconnection(self,*args,**kw):
        print("%s:\r\n\tconnction\r\n" % self.getName())
        sb=self.getName().encode("utf8")
        self.sendMsg(sb)
        self.recvMsg()
    
    def onRecvComplete(self,*args,**kw):
        pass
        

    def __registerEvent(self):
        self.registerEvent(SOCKET_EVENT.onRecv,self.onRecv)
        self.registerEvent(SOCKET_EVENT.onRecvComplete,self.onRecvComplete)
        self.registerEvent(SOCKET_EVENT.onError,self.onError)
        self.registerEvent(SOCKET_EVENT.onConnection,self.onconnection)
        self.registerEvent(SOCKET_EVENT.onSendComplete,self.onsendComplete)

for i in range(0,1):
    '''threading.Thread(target=s,args=(i,)).start()'''
    cle("yeihizhi.gicp.net",50118).start()