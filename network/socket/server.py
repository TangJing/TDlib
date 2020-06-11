import threading
from TDhelper.network.socket import base,SOCKET_TYPE,SOCKET_EVENT, Event,trigger,call
from TDhelper.network.socket.cache.queue import Q

class Server(base,threading.Thread):
    def __init__(self, ip,port, listenCount=100,buffSize=1024):
        threading.Thread.__init__(self)
        super(Server,self).__init__()
        self._uri=(ip,port)
        self._listenCount=listenCount
        self._runing=threading.Event()
        self._flag=threading.Event()
        self._buffSize=buffSize

    def run(self):
        try:
            self._runing.set()
            self._flag.set()
            self.createsocket(SOCKET_TYPE.TCPIP)
            self.bind(self._uri)
            self.on(SOCKET_EVENT.onListen.value, self._uri)
            self.listen(self._listenCount)
            self._accept()
        except Exception as e:
            self.on(SOCKET_EVENT.onError.value,e)

    @trigger("accept")
    def _accept(self):
        try:
            self.on(SOCKET_EVENT.onListenComplete.value, self._uri)
            while self._flag.is_set():
                connection,address = self.accept()
                if connection:
                    '''
                        Accept event
                    '''
                    self.on(SOCKET_EVENT.onAccept.value,connection)
                    '''
                    start recv thread
                    '''
                    recvwork=threading.Thread(target=self._recv,args={connection,})
                    recvwork.setDaemon(True)
                    recvwork.start()
            if self._flag.is_set():
                self._flag.set()
        except Exception as e:
            self.on(SOCKET_EVENT.onError.value,e)

    @trigger("recv")
    def _recv(self,connection):
        try:
            while self._runing.is_set():
                buff = connection.recv(self._buffSize)
                if not buff:
                    #if client socket is closed set flag is flase,and close connection
                    break
                '''
                Recv Event
                '''
                self.on(SOCKET_EVENT.onRecv.value,buff,connection)
        except Exception as e:
            self.on(SOCKET_EVENT.onError.value,e)
        finally:
            # print("关闭 %s" % connection)
            connection.close()

    @trigger("send")
    def _send(self,connection,buff):
        try:
            if connection:
                if len(buff)>0:
                    connection.send(buff)
        except Exception as e:
            self.on(SOCKET_EVENT.onError.value,e)

    @trigger("close")
    def close(self):
        try:
            self._runing.clear()
            self._flag.clear()
            self.close()
        except Exception as e:
            self.on(SOCKET_EVENT.onClose,e)
