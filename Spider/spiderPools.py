import datetime
from enum import Enum
from TDlib.Event.Event import Event
from TDlib.Spider.regex import Analysis
from TDlib.Spider.models.spider_event import event as Analysis_Event
from TDlib.Spider.models.status import STATUS as SPIDER_STATUS
from TDlib.Spider.models.fingerprint import fingerprint
from TDlib.Cache.pools import pools
from TDlib.Spider.models.Cache_L1 import L1, event as L1_EVENT
from TDlib.Spider.models.Cache_L2 import L2
from threading import Thread

import copy


class event(Enum):
    onListen = 'onlisten'


class spiderPools(pools):
    def __init__(self, configPath=None, pool_length=10, cache_size=50):
        super(spiderPools, self).__init__(pool_length)
        self._cache = L1()
        self._exclude_url = {}
        self._cache.registerEvent(L1_EVENT.onPush, self.onPush)
        # 初始化爬虫线程池
        for i in range(0, pool_length):
            m_spider = Analysis(configPath)
            m_spider.registerEvent(
                Analysis_Event.onIndexComplete, self.onIndexComplete)
            m_spider.registerEvent(
                Analysis_Event.onListComplete, self.onListComplete)
            m_spider.registerEvent(Analysis_Event.onDebug, self.onDebug)
            m_spider.registerEvent(
                Analysis_Event.onDetailComplete, self.onDetailComplete)
            m_spider.registerEvent(Analysis_Event.onError, self.onError)
            m_spider.registerEvent(
                Analysis_Event.onFingerprintComplete, self.onFingerprintComplete)
            self.push(m_spider)

    def pushCache(self, value):
        self._cache.push(value[0], value[1])

    def onPush(self, *args, **kwargs):
        if self.available_resources > 0:
            self.__startSpiderThread()

    def __startSpiderThread(self):
        thread_spider = Thread(target=self.__process)
        thread_spider.start()

    def listen(self, *args, **kwargs):
        '''向外部抛出监听事件'''
        return self.on(event.onListen, *args, **kwargs)

    def __process(self):
        # 爬虫线程
        process_spider = self.pop()
        m_state = True
        while m_state:
            m_url = self._cache.pop()
            if m_url:
                if m_url[0]:
                    # 如果内容未更改则跳过；并认为后续翻页内容均为未更改内容,并同时跳过后续翻页爬取.
                    if m_url[0] not in self._exclude_url:
                        process_spider.start(m_url[0])
                        if process_spider.getStatus == SPIDER_STATUS.SPIDER_FINGERPRINT_IS_REPEAT:
                            if m_url[1]:
                                if process_spider.getNextUrl:
                                    self._exclude_url[m_url[1]
                                                      ] = process_spider.getNextUrl
                else:
                    m_state = False
            else:
                m_state = False
        self.push(process_spider)

    # 事件监听
    def onIndexComplete(self, *args, **kwargs):
        if len(args) > 0:
            m_analysis = args[0]
            if m_analysis.getStatus == SPIDER_STATUS.SPIDER_SUCCESS:
                data = m_analysis.getData
                if data:
                    for item in data['data']:
                        self.pushCache([item['url'], m_analysis.getNextUrl])
                    return self.on(event.onListen, *args, **kwargs)

    def onListComplete(self, *args, **kwargs):
        if len(args) > 0:
            m_analysis = args[0]
            if m_analysis.getStatus == SPIDER_STATUS.SPIDER_SUCCESS:
                m_data = m_analysis.getData
                if m_data['data']:
                    # TODO
                    for item in m_data['data']:
                        # 为了解决自动判断页面抓取重复取消下一页，此处存的来源为下一页
                        self.pushCache([item['url'], m_analysis.getNextUrl])
                    self.on(event.onListen, *args, **kwargs)
            if m_analysis.getNextUrl:
                self.pushCache(
                    [m_analysis.getNextUrl, m_analysis.getCurrentUrl])

    def onDetailComplete(self, *args, **kwargs):
        if len(args) > 0:
            m_analysis = args[0]
            if m_analysis.getStatus == SPIDER_STATUS.SPIDER_SUCCESS:
                m_data = m_analysis.getData
                return self.on(event.onListen, *args, **kwargs)

    def onDebug(self, *args, **kwargs):
        return self.on(event.onListen, *args, **kwargs)

    def onError(self, *args, **kwargs):
        return self.on(event.onListen, *args, **kwargs)

    def onFingerprintComplete(self, *args, **kwargs):
        if len(args) > 0:
            m_analysis = args[0]
            page_fingerprint = m_analysis.getFingerprint
            result = fingerprint().findOne(
                query={'url': m_analysis.getCurrentUrl})
            if result:
                if page_fingerprint == result['fingerprint']:
                    # 删除爬虫库数据
                    repeat_url = result['url']
                    m_L2 = L2()
                    m_L2.remove(
                        {'$or': [{'url': repeat_url}, {'sources': repeat_url}]})
                    m_L2 = None
                    self._exclude_url[repeat_url]= m_analysis.getCurrentUrl
                    return True
                else:
                    m_fingerprint = fingerprint()
                    m_fingerprint.update(
                        {
                            'url': m_analysis.getCurrentUrl
                        },
                        {
                            'fingerprint': page_fingerprint,
                            'lastupdatetime': datetime.datetime.now()
                        }
                    )
                    return False
            else:
                m_fingerprint = fingerprint()
                m_fingerprint.Fingerprint = page_fingerprint
                m_fingerprint.Url = m_analysis.getCurrentUrl
                m_fingerprint.LastUpdateTime = datetime.datetime.now()
                m_fingerprint.toSave()
                return False
        return False
