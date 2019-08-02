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
        print("%s-2、sendComplete\r\n"%self.getName())
        self.recvMsg()

    def onRecv(self,*args,**kw):
        print("%s-3、recving\r\n"%self.getName())
        self.setRuning()
        #print("Client Recv: \r\n\t%s\r\n" % args)
        

    def onError(self,*args,**kw):
        print("%s-Client:\r\n\terror %s\r\n" % (self.getName(),args))

    def onconnection(self,*args,**kw):
        print("%s-1、connction\r\n"%self.getName())
        self.sendMsg(b"clientSend")
    
    def onRecvComplete(self,*args,**kw):
        print("%s-4、recvComplete\r\n"%self.getName())
        

    def __registerEvent(self):
        self.registerEvent(SOCKET_EVENT.onRecv,self.onRecv)
        self.registerEvent(SOCKET_EVENT.onRecvComplete,self.onRecvComplete)
        self.registerEvent(SOCKET_EVENT.onError,self.onError)
        self.registerEvent(SOCKET_EVENT.onConnection,self.onconnection)
        self.registerEvent(SOCKET_EVENT.onSendComplete,self.onsendComplete)
'''

def s(num):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect(("127.0.0.1",39841))
        client.send(b"ddddddd")
        while True:
            buff=client.recv(1024)
            if not buff:
                break
            print("%d%s"%(num,buff))
            break
        print("close")
        client.close()
'''
'''
cle("127.0.0.1",39841).start()
'''

for i in range(0,10):
    '''threading.Thread(target=s,args=(i,)).start()'''
    cle("127.0.0.1",39841).start()