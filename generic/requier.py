
#!/usr/bin/env python3.6
# -*- encoding: utf-8 -*-
'''
@File    :   requier.py
@Time    :   2020/04/18 06:48:15
@Author  :   Tang Jing
@Version :   1.0.0
@Contact :   yeihizhi@163.com
@License :   (C)Copyright 2020
@Desc    :   None
'''

# here put the import lib

# code start


class R:
    def __init__(self, namespace, *args, **kwargs):
        '''
        热加载一个类
        参数
         - namespace: string, 格式：generic.requier:R
        '''
        self.__userNamespace = namespace
        self.__namespace = None  # namespace or import path
        self.__instance = None  # instance class
        self.__importt()  # run import method

    def __importt(self):
        '''
        Import package
        if import fail will return None
        '''
        try:
            if self.__userNamespace:
                self.__namespace = __import__(
                    self.__userNamespace, fromlist=(True))
            else:
                return None
        except Exception as e:
            return None

    def Instance(self, classname, *args):
        '''
        Instance class
        If instance fail will return None
        '''
        try:
            if classname:
                if hasattr(self.__namespace, classname):
                    self.__instance = getattr(
                        self.__namespace, classname)(*args)
                    if self.__instance:
                        return self.__instance
                    else:
                        return None
                else:
                    return None
            else:
                return None
        except Exception as e:
            return None

    def Call(self, methodname, *args, **kw):
        '''
            Call method
        '''
        try:
            if methodname:
                if self.__instance:
                    method = getattr(self.__instance, methodname)
                    if method:
                        return method(*args, **kw)
                    else:
                        return None
                else:
                    return None
            else:
                return None
        except Exception as e:
            return None

def InstanceCall(handle, method, *args, **kwargs):
    try:
        method= getattr(handle, method)
        if method:
            return method(*args, **kwargs)
        else:
            raise Exception('%s not have method %s'%(handle, method))
    except Exception as e:
        raise e