import socket
from TDhelper.network.socket.model.SOCKET_MODELS import SOCKET_TYPE, SOCKET_EVENT
from TDhelper.Event.Event import *


class base(Event):
    def __init__(self):
        self._mysocket = None
        self._socket_type = SOCKET_TYPE.TCPIP
        super(base, self).__init__()

    def createsocket(self, sType=SOCKET_TYPE.TCPIP):
        self._socket_type = sType
        if self._socket_type == SOCKET_TYPE.TCPIP:
            self._mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # self._mysocket.setsockopt(socket.SOL___mysocket,socket.SO_REUSEADDR,1)
        else:
            self._mysocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # self._mysocket.setsockopt(socket.SOL___mysocket,socket.SO_REUSEADDR,1)

    def setTimeout(self, timeout):
        self._mysocket.settimeout(timeout)

    def bind(self, uri):
        if self._mysocket:
            self._mysocket.bind(uri)

    def listen(self, count):
        if self._mysocket:
            self._mysocket.listen(count)

    def accept(self):
        return self._mysocket.accept()

    def recv(self, connect=None, recvLen=100):
        if self._socket_type == SOCKET_TYPE.TCPIP:
            return connect.recv(recvLen),connect
        else:
            return self._mysocket.recvfrom(recvLen)

    def send(self, connect, buff):
        if self._socket_type == SOCKET_TYPE.TCPIP:
            connect.send(buff)
        else:
            self._mysocket.sendto(buff, connect)

    def connection(self, uri):
        self._mysocket.connect(uri)

    def getSocket(self):
        return self._mysocket

    def close(self):
        # self.___mysocket.shutdown(socket.SHUT_RDWR)
        self._mysocket.close()
