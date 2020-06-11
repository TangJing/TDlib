import socket
from TDhelper.network.socket.model.SOCKET_MODELS import SOCKET_TYPE,SOCKET_EVENT
from TDhelper.Event.Event import *

class base(Event):
        def __init__(self):
                self.__mysocket=None
                super(base,self).__init__()

        def createsocket(self,sType=SOCKET_TYPE.TCPIP):
                if sType==SOCKET_TYPE.TCPIP:
                        self.__mysocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        #self.__mysocket.setsockopt(socket.SOL___mysocket,socket.SO_REUSEADDR,1)
                else:
                        self.__mysocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
                        #self.__mysocket.setsockopt(socket.SOL___mysocket,socket.SO_REUSEADDR,1)

        def setTimeout(self,timeout):
                self.__mysocket.settimeout(timeout)

        def bind(self,uri):
                if self.__mysocket:
                        self.__mysocket.bind(uri)

        def listen(self,count):
                if self.__mysocket:
                        self.__mysocket.listen(count)

        def accept(self):
                return self.__mysocket.accept()

        def recv(self,connect,recvLen=100):
                return connect.recv(recvLen)

        def send(self,connect,buff):
                connect.send(buff)

        def connection(self,uri):
                self.__mysocket.connect(uri)
        
        def getSocket(self):
                return self.__mysocket

        def close(self):
                #self.___mysocket.shutdown(socket.SHUT_RDWR)
                self.__mysocket.close()