import urllib.request
import io
import os
import json

class apiCore():
    def __init__(self,apiName,version="v1",apiRouteFileName="/apiRoutePath"):
        self._path=os.path.dirname(__file__)+"\\"+apiName+"\\"+version+"\\"
        if not os.path.exists(self._path):
            os.makedirs(self._path)
        self._routePath=os.path.join(self._path,apiRouteFileName+".arp")
        self._apiRoute = dict()
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
        add a new api,and save route
    '''
    def addapi(self,key,apiUri,method="GET"):
        if key.lower() not in self._apiRoute:
            self._apiRoute[key.lower()]={"uri":apiUri,"method":method.lower()}
            #save to apiRouteFile
            return True
        else:
            return False

    '''
        delete a api
    '''
    def delapi(self,key):
        if key.lower() in self._apiRoute:
            del self._apiRoute[key.lower()]
            return True
        else:
            return False

    def save(self):
        #create file write buffer
        wBuffer=""
        for item in self._apiRoute:
            wBuffer+=json.dumps({"key":item,"value":self._apiRoute[item]})+"\r\n"
        #save buffer to file
        if not wBuffer:
            wBuffer="\r\n"
        if wBuffer:
            with open(self._routePath,mode='w',encoding='utf-8', errors=None, newline=None) as f:
                f.write(wBuffer)
                f.flush()
                f.close()

    '''""
        Call remote api
    '''
    def call(self,key,data):
        if key.lower() in self._apiRoute:
            method=self._apiRoute[key.lower()]["method"]
            uri=self._apiRoute[key.lower()]["uri"]
            if uri:
                if method.lower()=="get":
                    uri+="?"+data
                    return self._restfulGET(uri)
                elif method.low()=="post":
                    return self._restfulPOST(uri,data)
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