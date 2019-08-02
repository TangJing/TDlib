global _globaldict
_globaldict={}

def setGlobalVariable(key,value):
    _globaldict[key]=value

def deleteGlobalVariable(key):
    del _globaldict[key]

def getGlobalVariable(key,defaultValue=None):
    try:
        return _globaldict[key]
    except Exception as e:
        return defaultValue

setGlobalVariable("EventList",{})