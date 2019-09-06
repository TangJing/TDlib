import mysqlx

session=None
schema=None
collection=None
clients={}

def getSession(connection_str):
    session=mysqlx.get_session(connection_str)

def createSessionPool(connection_str,options_str):
    clients=mysqlx.get_client(connection_str,options_str)

def getConnectionStr(host,port,user,password):
    return {
        'host':host if host else "localhost",
        'port':port if port else 33060,
        'user':user,
        'password':password
    }

def getPoolOptionsStr(enabled=True,maxSize=1,max_idle_time=0,queue_timeout=0):
    return {
            'pooling':{
                'enabled':enabled,
                'max_size':maxSize,
                'max_idle_time':max_idle_time,
                'queue_timeout':queue_timeout
            }
    }

def openDataBase(dataBaseName):
    if session:
        schema=session.get_schema(dataBaseName)

def openTable(tableName):
    if schema:
        collection=schema.get_collection(tableName)


