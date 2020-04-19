import threading
import re
from TDlib.Socket.sBase import *
from TDlib.Event.Event import *
from TDlib.Socket.model.SOCKET_MODELS import *

class Client(eSocket,threading.Thread):
    def __init__(self,ip,port,buffSize=1024):
        threading.Thread.__init__(self)
        super(Client,self).__init__()
        if re.match(r"^(?=^.{3,255}$)[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+$", ip, re.I | re.M):
            ip= socket.gethostbyname(ip)
        self.uri=(ip,port)
        self.__runing=threading.Event()
        self._buffSize=buffSize
        self.__state=True
        self.createsocket(SOCKET_TYPE.TCPIP)
        self.setTimeout(10)
        self.__runing.set()

    def run(self):
        self.__connection()

    @trigger("connection")
    def __connection(self):
        try:
            self.connection(self.uri)
            self.on(SOCKET_EVENT.onConnection,self)
        except Exception as e:
            self.__state=False
            self.on(SOCKET_EVENT.onError,e)

    @trigger("send")
    def sendMsg(self,buff):
        try:
            self.send(self.getSocket(),buff)
        except Exception as e:
            self.on(SOCKET_EVENT.onError,e)

    @trigger("recv")
    def recvMsg(self):
        try:
            while self.__runing.is_set():      
                buff=self.recv(self.getSocket(),self._buffSize)
                if not buff:
                    self.__runing.clear()
                    break
                self.on(SOCKET_EVENT.onRecv,buff)
        except Exception as e:
            self.on(SOCKET_EVENT.onError,e)
        finally:
            self.closeClient()

    def setRuning(self):
        if self.__runing.is_set():
            self.__runing.clear()

    def closeClient(self):
        try:
            self.__state=False
            self.setRuning()
            self.close()
        except Exception as e:
            self.on(SOCKET_EVENT.onError,e)