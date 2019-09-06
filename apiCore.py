import urllib.request
import io
import os
import json
from bin.globalvar import *

class apiCore():
    def __init__(self,apiName,version="v1",apiRouteFileName="apiRoutePath"):
        '''Initializing and load api route
            
            Params:
                apiName:api name
                version:api version,default value is 'v1'
                apiRouteFileName:api cache file name
        '''
        self._apiName=apiName+"_"+version
        self._path=os.path.dirname(__file__)+"\\"+apiName+"\\"+version+"\\"
        if not os.path.exists(self._path):
            os.makedirs(self._path)
        self._routePath=os.path.join(self._path,apiRouteFileName+".arp")
        if not hasKey(apiName+version):
            #create global route tables
            setGlobalVariable(self._apiName,dict())
        if self._routePath:
            if os.path.exists(self._routePath):
                #read apiRouteFile and init apiroute
                with open(self._routePath,mode='r',encoding='utf-8', errors=None, newline=None) as f:
                    while True:
                        line = f.readline().replace("\n","")
                        if line:
                            jsondoc=json.loads(line)
                            if jsondoc["key"]:
                                if jsondoc["value"]:
                                    self.addapi(jsondoc["key"],jsondoc["value"]["uri"],jsondoc["value"]["method"])
                        else:
                            break
                    f.close()

    '''
        Add a new api,and save route to file
    '''
    def addapi(self,key,apiUri,method="GET"):
        #if key.lower() not in self._apiRoute:
        if key.lower() not in getGlobalVariable(self._apiName):
            getGlobalVariable(self._apiName)[key.lower()]={"uri":apiUri,"method":method.lower()}
            return True
        else:
            return False

    
    def delapi(self,key):
        '''Delete a api
        '''
        if key.lower() in getGlobalVariable(self._apiName):
            del getGlobalVariable(self._apiName)[key.lower()]
            return True
        else:
            return False
    
    def save(self):
        '''Save api route to file
        '''
        wBuffer=""  #create file write buffer
        for item in getGlobalVariable(self._apiName):
            wBuffer+=json.dumps({"key":item,"value":getGlobalVariable(self._apiName)[item]})+"\r\n"
        if not wBuffer:
            wBuffer="\r\n"
        if wBuffer:  #save buffer to file
            with open(self._routePath,mode='w',encoding='utf-8', errors=None, newline=None) as f:
                f.write(wBuffer)
                f.flush()
                f.close()

    
    def call(self,key,data):
        '''Call remote api
        '''
        if key.lower() in getGlobalVariable(self._apiName):
            method = getGlobalVariable(self._apiName)[key.lower()]["method"]
            uri = getGlobalVariable(self._apiName)[key.lower()]["uri"]
            if uri:
                if method.lower()=="get":
                    uri+="?"+data
                    return self._restfulGET(uri)
                elif method.low()=="post":
                    return self._restfulPOST(uri,data)
            return False
        return False


    def _restfulGET(self,uri):
        try:
            with urllib.request.urlopen(uri) as result:
                if result.getcode()==200:
                    return result.read()
                else:
                    return None
        except Exception as e:
            return e

    def _restfulPOST(self,uri,data):
        try:
            with urllib.request.urlopen(uri,data) as result:
                if result.getcode()==200:
                    return result.read()
                return None
        except Exception as e:
            return e