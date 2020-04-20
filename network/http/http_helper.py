#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__autho__ = "Tony.Don"
__lastupdatetime__ = "2017/09/20"

import requests
'''
class
    TDlib.generic.m_http
description
    http帮助类
'''
class m_http:
    context = None
    res = None 
    def __init__(self):
        self.context = requests
        
        
    #url:wetsite url address
    def getcontent(self,p_url, p_timeout= 5):
        '''
        Featuren\r\n
            getcontent(self,url)\r\n
        Description\r\n
            获取url内容\r\n
        Args\r\n
            url\r\n
                type:string\r\n
                description:目标URL\r\n
        '''
        if self.context:
            try:
                self.res=self.context.get(url= p_url, timeout= p_timeout)
                if self.res:
                    return self.res.text, self.res.status_code
                return p_url, "REQUESTS_OBJECT_IS_NULL"
            except Exception as e:
                return e, "CONNECT_IS_ERROR"

    def https(self,url,*args,**kwargs):
        '''
        certificate
        '''
        pass