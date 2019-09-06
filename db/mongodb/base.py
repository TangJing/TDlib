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
    def __init__(self,uri=None,dbName=None):
        '''
        Feature\r\n
            __init__(self,uri)\r\n
        Description\r\n
            初始化
        Args\r\n
            uri\r\n
                type:string,example("mongodb://username:password@localhost:port")\r\n
                description:mongodb server address\r\n
            dbName
                type:string
                description:database name
        '''
        self.collection=None
        if not self.client or not self.db:
            if uri:
                try:
                    self.client=pymongo.MongoClient(uri)
                    if dbName:
                        self.db=self.client[dbName]
                except Exception as e:
                    raise