from Socket.Server import Server
from Socket.model.SOCKET_MODELS import *
#from Socket.Client import client
import socket
import time
import threading

s=Server("127.0.0.1",39841)
def onRecv(*args,**kw):
        print("Server:\r\n\t %s" % args[0])
        s.send(args[1],args[0])

def onError(*args,**kw):
        print("Server:\r\n\terror %s\r\n"%args)

def onAccept(*args,**kw):
        print("Server:\r\n\taccept %s\r\n" % args)

def registerEvent():
        s.registerEvent(SOCKET_EVENT.onRecv,onRecv)
        s.registerEvent(SOCKET_EVENT.onError,onError)
        s.registerEvent(SOCKET_EVENT.onAccept,onAccept)

registerEvent()
s.start()


