#!/usr/bin/env python
#-*- coding:utf-8 -*-

class reflect:
    def __init__(self,namespace):
        self.__userNamespace = namespace
        self.__namespace = None #命名空间
        self.__instance = None  #实例
        self.__importt()

    def __importt(self):
        try:
            if self.__userNamespace:
                self.__namespace = __import__(self.__userNamespace,fromlist=(True))
            else:
                return None
        except Exception as e:
            return None

    def Instance(self,classname,*args):
        try:
            if classname:
                if hasattr(self.__namespace,classname):
                    self.__instance = getattr(self.__namespace,classname)(*args)
                    return self
                else:
                    return None
            else:
                return None
        except Exception as e:
            return None

    def Call(self,methodname,*args,**kw):
        try:
            if methodname:
                if self.__instance:
                    method = getattr(self.__instance,methodname)
                    if method:
                       return method(*args,**kw)
                    else:
                        return None
                else:
                    return None
            else:
                return None
        except Exception as e:
            return None

        