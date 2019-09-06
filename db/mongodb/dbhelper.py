#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from db.mongodb.base import mongodbclient
'''
class\r\n
    db(dbConfig)\r\n 
description\r\n
    mongodb db helper class\r\n
'''
class db(mongodbclient):
    
    def __init__(self,uri,dbName):
        try:
            super(db,self).__init__(uri,dbName)
        except Exception as e:
            raise

    def setCollection(self,collectionName):
        try:
            if self.db:
                self.collection=self.db[collectionName]
        except Exception as e:
            raise e

    def save(self,args,flag="one"):
        '''
        Feature\r\n
            save(self,args,flag)\r\n
        Description\r\n
            保存\r\n
        Args\r\n
            args\r\n
                type:Model Class\r\n
                description:实体\r\n
            flag\r\n
                type:string,[one|many]\r\n
                description:one->insert one record,many->insert some records\r\n
                example:save([model1,model2...,modeln])\r\n
        '''
        try:
            if self.collection:
                if flag.lower()=="one":
                    return self.collection.insert_one(args)
                elif flag.lower()=="many":
                    return self.collection.insert_many(args)
            return None
        except Exception as e:
            raise e
   
    def update(self,query,args):
        try:
            if self.collection:
                return self.collection.update(query,{'$set':args})
            return None
        except Exception as e:
            raise e

    def remove(self,query=None):
        try:
            if self.collection:
                if query:
                    return self.collection.remove(query)
                else:
                    return self.collection.remove()
            return None
        except Exception as e:
            raise e

    def findOne(self,query):
        try:
            if self.collection:
                return self.collection.find_one(query)
            return None
        except Exception as e:
            raise e
    
    def find(self,**kwargs):
        try:
            if self.collection:
                if "query" in kwargs:
                    if "limit" in kwargs:
                        return self.collection.find(kwargs["query"]).limit(kwargs["limit"])
                    return self.collection.find(kwargs["query"])
                return None
        except Exception as e:
            raise e