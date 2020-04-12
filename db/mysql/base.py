import mysql.connector.pooling

class db_pool:
    
    def __init__(self, config, m_pool_size= 10):
        self.__pool= mysql.connector.pooling.MySQLConnectionPool(
            pool_size= m_pool_size, **config)

    def getSession(self):
        if self.__pool:
            return self.__pool.get_connection()
        return None