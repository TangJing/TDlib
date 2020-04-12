from Socket.Server import Server
from Socket.model.SOCKET_MODELS import *
#from Socket.Client import client
import socket
import time
import threading

s=Server("192.168.0.103",9999)
def onRecv(*args,**kw):
        print("Server:\r\n\t -%s" % args[0])
        s.send(args[1],args[0])

def onError(*args,**kw):
        print("Server:\r\n\t -Error %s\r\n"%args)

def onAccept(*args,**kw):
        print("Server:\r\n\t -%s Connection\r\n" % args[0])

def onListen(*args,**kw):
        print("Server:\r\n\t -%s try to listen, please wait...\r\n" % args)
def onListenComplete(*args, **kw):
        print("Server:\r\n\t -%s listen success!\r\n" % args)

def registerEvent():
        s.registerEvent(SOCKET_EVENT.onRecv,onRecv)
        s.registerEvent(SOCKET_EVENT.onError,onError)
        s.registerEvent(SOCKET_EVENT.onAccept,onAccept)
        s.registerEvent(SOCKET_EVENT.onListen, onListen)
        s.registerEvent(SOCKET_EVENT.onListenComplete, onListenComplete)

registerEvent()
s.start()


