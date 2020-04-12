import re
import datetime

from Spider.spiderByRegex import reg_spider
from Spider.models.spider_event import event
from Spider.models.status import STATUS as SPIDER_STATUS
from db.mysql.base import db_pool
from test_logger import *

def page_index(args):
    if args.getStatus == SPIDER_STATUS.SPIDER_SUCCESS:
        m_data= args.getData
        if m_data:
            # TODO
            # test suppose read url in cache
            logging.info("- spider url: " + args.currentUrl + ", complete.")
            for item in m_data['data']:
                if not args.debug:
                    saveTopType(item['type'])
                spider_Cache.push(item['url'], args.currentUrl)
        else:
            # TODO
            m_str= m_data['str']

    

def page_list(args):
    if args.getStatus == SPIDER_STATUS.SPIDER_SUCCESS:
        m_data= args.getData
        if m_data['data']:
            # TODO
            logging.info("- spider url: " + args.currentUrl + ", complete")
            for item in m_data['data']:
                if not args.debug:
                    saveChildType(item['top_type'], item['c_type'])
                spider_Cache.push(item['url'], args.currentUrl)
        else:
            # TODO
            m_str= m_data['str']
    if args.getNextUrl:
        spider_Cache.push(args.getNextUrl, args.currentUrl)
    #args.next()

def page_detail(args):
    if args.getStatus == SPIDER_STATUS.SPIDER_SUCCESS:
        m_data= args.getData
        if m_data:
            if m_data['data']:
                # TODO
                logging.info("- spider url: " + args.currentUrl + ", complete")
                for item in m_data['data']:
                    if not args.debug:
                        saveMsg(**item)
            else:
                # TODO
                m_str= m_data['str']

def error(msg, code, spider_object):
    logging.error(msg)
    if code == SPIDER_STATUS.SPIDER_PAGE_ANALYSIS_FILTER_FAIL:
        session= db_helper.getSession()
        cursor= session.cursor()
        sql= "delete from spider_fingerprint where url=\"{0}\"".format(spider_object.currentUrl)
        cursor.execute(sql)
        session.commit()
        session.close()
    elif code == SPIDER_STATUS.REQUEST_CONNECT_ERROR:
        spider_Cache.push(spider_object.currentUrl)

def debug(msg):
    logging.debug(msg)

'''
    校验HTML签名，检查内容是否已经爬取，如果一致放弃爬取
    - Parameters
        args: reg_spider object, object.getFingerprint 获取爬取的页面指纹.
    - Return
        Type: Boolen, 如果校验无此内容返回false, 反之返回true.
'''
def fingerprint(args):
    result= False
    if not args.debug:
        session= db_helper.getSession()
        cursor= session.cursor()
        if args.getFingerprint:
            sql= "select *from spider_fingerprint where url= \"{0}\"".format(args.currentUrl)
            cursor.execute(sql)
            data= cursor.fetchall()
            if cursor.rowcount <= 0:
                result= False
                sql= "insert into spider_fingerprint(fingerprint,url) values(\"{0}\",\"{1}\")".format(args.getFingerprint, args.currentUrl)
                cursor.execute(sql)
                session.commit()
            else:
                if data[0][1] == args.getFingerprint:
                    result= True
                else:
                    sql= "update spider_fingerprint set fingerprint=\"{0}\" where url=\"{1}\"".format(args.getFingerprint, args.currentUrl)
                    cursor.execute(sql)
                    session.commit()
                    result= False
        session.close()
    return result

def saveTopType(m_type_name):
    session= db_helper.getSession()
    cursor= session.cursor()
    m_type_name= m_type_name.replace(" ","")
    if m_type_name:
        cursor.execute("select *from category where name= \"{0}\"".format(m_type_name))
        data= cursor.fetchall()
        if cursor.rowcount <= 0:
            logging.info("- save type:{0}".format(m_type_name))
            sql= "insert into category(name, parent_id) values(\"{0}\",0)".format(m_type_name)
            cursor.execute(sql)
            session.commit()
    session.close()

def saveChildType(m_top_type, m_child_type):
    session= db_helper.getSession()
    cursor= session.cursor()
    m_top_type= m_top_type.replace(" ","")
    m_child_type= m_child_type.replace(" ","")
    if m_top_type:
        if m_child_type:
            cursor.execute("select *from category where name=\"{0}\"".format(m_child_type))
            data= cursor.fetchall()
            if cursor.rowcount <= 0:
                cursor.execute("select *from category where name=\"{0}\"".format(m_top_type))
                data= cursor.fetchall()
                if cursor.rowcount >= 0:
                    logging.info("- save child type:{1}, parent type is {0}".format(m_top_type, m_child_type))
                    sql= "insert into category(name, parent_id) values(\"{0}\",{1})".format(m_child_type, data[0][0])
                    cursor.execute(sql)
                    session.commit()
    session.close()

def saveMsg(**kwargs):
    session= db_helper.getSession()
    cursor= session.cursor()
    m_name= kwargs["name"]
    m_name= m_name.replace(" ","")
    m_name= re.sub(r"[0]\d*","",m_name, count= 0, flags= 0)
    sql= "select *from movie_list where name=\"{0}\"".format(m_name)
    cursor.execute(sql)
    data= cursor.fetchone()
    movie_id= 0
    if cursor.rowcount >= 0:
        # old msg update
        movie_id= data[0]
        logging.info("- update movie message.movie name is {0}".format(m_name))
        sql= "update movie_list set last_update_time=\"{0}\" where name=\"{1}\"".format(str(datetime.datetime.now()), m_name)
        cursor.execute(sql)
        session.commit()
    else:
        # new msg insert
        m_c_type= kwargs['c_type']
        m_c_type= m_c_type.replace(" ","")
        cursor.execute("select *from category where name=\"{0}\"".format(m_c_type))
        data= cursor.fetchone()
        year= kwargs["year"]
        year= year.lstrip().rstrip()
        last_update_time= kwargs["update_date"]
        last_update_time= last_update_time.lstrip().rstrip()
        last_update_time= datetime.datetime.strptime(last_update_time, '%Y-%m-%d %H:%M:%S')
        if cursor.rowcount >= 0:
            # new msg insert
            logging.info("- insert a new movie message.movie name is {0}".format(m_name))
            type_id= data[0]
            sql= "insert into movie_list(name,remark,director,performer,number,category,country,language,year,last_update_time,tag,description,cover,alias) values(\"{0}\",\"{1}\",\"{2}\",\"{3}\",\"{4}\",{5},\"{6}\",\"{7}\",\"{8}\",\"{9}\",\"{10}\",\"{11}\",\"{12}\",\"{13}\")".format(m_name, kwargs['remark'],kwargs['director'],kwargs['performer'],kwargs['number'],type_id,kwargs['country'],kwargs['language'],year,last_update_time,kwargs['tag'],kwargs['description'],kwargs['img'],kwargs['alias'])
            cursor.execute(sql)
            session.commit()
            movie_id= cursor.lastrowid
    if movie_id > 0:
        # play url process
        urls= kwargs["play_urls"].split('~#~')
        source_id=1
        for m_url in urls:
            if m_url:
                play_urls= m_url.split('|')
                for play_url in play_urls:   
                    if play_url:
                        play_url= play_url.replace(" ","")
                        sql= "select *from movie_play_list where play_url=\"{0}\"".format(play_url)
                        cursor.execute(sql)
                        data= cursor.fetchall()
                        if cursor.rowcount <= 0:
                            sql= "insert into movie_play_list(movie_id,play_url,sources) values({0},\"{1}\",\"{2}\")".format(movie_id, play_url, source_id)
                            cursor.execute(sql)
                            session.commit()
                        else:
                            break
            source_id+= 1
    session.close()

config= {
    "host": "host.5ker.com",
    "port": 3308,
    "user" : "root",
    "password" : "123",
    "database" : "spider"
}

db_helper= db_pool(config, 30)


from Cache.pools import pools
from Spider.models.Cache_L1 import L1
import threading
import time

class spider_pool(pools):
    def __init__(self, pools_length= 10):
        super(spider_pool,self).__init__(pools_length)
        for i in range(0, pools_length):
            m_spider= reg_spider("Spider\\spider.json",max_reconnect= 1)
            m_spider.registerEvent(event.onIndexComplete, page_index)
            m_spider.registerEvent(event.onListComplete, page_list)
            m_spider.registerEvent(event.onDetailComplete, page_detail)
            m_spider.registerEvent(event.onError, error)
            m_spider.registerEvent(event.onFingerprintComplete, fingerprint)
            m_spider.registerEvent(event.onDebug, debug)
            self.push(m_spider)

    def start(self, url= None):
        thread_spider= threading.Thread(target= self.toGet, args= {url,})
        thread_spider.start()

    def toGet(self, url= None):
        m_spider= self.pop()
        if m_spider:
            while True:
                try:
                    m_url= spider_Cache.pop()
                    if m_url:
                        if m_url[0]:
                            if m_url[0] not in exclude_url:
                                m_spider.spider_start(m_url[0])
                                if m_spider.getStatus == SPIDER_STATUS.SPIDER_FINGERPRINT_IS_REPEAT:
                                    if m_url[1]:
                                        exclude_url[m_url[1]]= m_spider.getNextUrl
                        else:
                            break
                    else:
                        break
                except Exception as e:
                    logging.info(e)
        self.push(m_spider)

def onThreadComplete(*args):
    pass

def onPushComplete(*args):
    if s_pools.available_resources > 0:
        s_pools.start()

exclude_url= dict()
s_pools= spider_pool(10)
s_pools.registerEvent("onThreadComplete", onThreadComplete)
spider_Cache= L1(50)
spider_Cache.registerEvent("pushComplete", onPushComplete)
spider_Cache.push("http://www.666zy.com")
s_pools.start()

