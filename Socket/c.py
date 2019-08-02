'''
import threading
from Socket.socketbase import EasySocket as socket
from Socket.model.SOCKET_MODELS import SOCKET_EVENT,SOCKET_TYPE

class client(socket,threading.Thread):
    def __init__(self,ip,remotePort):
        threading.Thread.__init__(self)
        super(client,self).__init__((ip,remotePort))

    def run(self):
        self.registerEvent()
        if self.connection():
            self.send(b"dlkfdlkfjdfdf")

    def registerEvent(self):

        self.RegisterEvent(SOCKET_EVENT.onRecv,self.onRecv)
        self.RegisterEvent(SOCKET_EVENT.onRecvComplete,self.onRecvComplete)
        self.RegisterEvent(SOCKET_EVENT.onSend,self.onSend)
        self.RegisterEvent(SOCKET_EVENT.onSendComplete,self.onSendComplete)
        self.RegisterEvent(SOCKET_EVENT.onClose,self.onClose)
        self.RegisterEvent(SOCKET_EVENT.onError,self.onError)
    
    def onSend(self,*args,**kw):
        pass

    def onSendComplete(self,*args,**kw):
        self.recv()

    def onRecv(self,*args,**kw):
        pass

    def onRecvComplete(self,*args,**kw):

        if args:
            print("Server Send:%s" % args[0])
        self.recv()
            
        
    def onClose(self,*args,**kw):
        pass

    def onError(self,*args,**kw):
        for item in args:
            print("server %s\r\n" % item)

'''