#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymongo
'''
class\r\n
    lib.db.mongodb.mongodbclient\r\n
description\r\n
    Mongodb database helper class\r\n
'''
class mongodbclient:
    client=None
    db=None
    def __init__(self):
        self.collection= None
        pass
       
    def loadCfg(self, **kwargs):
        '''
        加载MONGODB配置文件
        - parameters:
            kwargs: {url=mongodb://username:password@localhost:port, db= db_name}
        '''
        if not self.client or not self.db:
            if kwargs['url']:
                try:
                    self.client=pymongo.MongoClient(kwargs['url'])
                    if kwargs['db']:
                        self.db=self.client[kwargs['db']]
                except Exception as e:
                    raise