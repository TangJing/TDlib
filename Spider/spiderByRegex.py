import gc
import json
import os
import re
import hashlib
import threading
from TDlib.generic.http_helper import m_http
from TDlib.Event.Event import Event
from TDlib.Spider.models.spider_event import event
from TDlib.Spider.models.status import STATUS as SPIDER_STATUS

class reg_spider(Event):
    """
    reg_spider

    - description: spider content by regular expression.
    """
    
    def __init__(self, configPath= None, max_reconnect= 0):
        """
        init reg_spider

        - Parameters:
            configPath: target website config file, format is json. example file(spider.json).
            max_reconnect: default value is 0, if reuqests is timeout then try reconnect.
        """
        super(reg_spider,self).__init__()
        self.__lock= threading.Lock() #线程锁主要用于同步回调函数.
        self.__is_to_fingerprint= True # 默认开启验证页面内容重复.
        self.debug= False #调试模式开关
        self.__max_reconnect= max_reconnect
        self.__request= m_http()
        self.__config= None
        self.__response_html= None
        self.__status= SPIDER_STATUS.SPIDER_SUCCESS
        self.__prefix_domain= None
        # now spider url
        self.__current_url= None
        self.__data= None
        self.__spider_url=[]
        # if has next_url, then get current_url has complete, next get page url is next_url.
        self.__next_url= None
        self.__fingerprint= None
        self.__rules_type= None
        if configPath:
            self.loadConig(configPath)

    @property
    def getData(self):
        return self.__data
    
    @property
    def getSpiderUrl(self):
        return self.__spider_url
    
    @property
    def currentUrl(self):
        '''
        get spider current url.
        '''
        return self.__current_url

    @property
    def getPrefixDoamin(self):
        return self.__prefix_domain
    
    @property
    def getFingerprint(self):
        return self.__fingerprint
    
    @property
    def getStatus(self):
        return self.__status

    @property
    def getNextUrl(self):
        return self.__next_url

    def loadConig(self, configPath):
        if configPath:
            # test config file path.
            if os.path.exists(configPath):
                # read config file, open by read mode.
                with open(configPath, 'r', encoding= "utf-8") as json_file:
                    self.__config = json.load(json_file)
                    json_file.close()

    def spider_start(self, url= None):
        '''
        begin get url by spider.

        - Parameters:
            url: default value is None, if has url then spider will get the url.
        '''
        if self.__config:
            self.__is_to_fingerprint= True
            self.__response_html= None
            self.__status= SPIDER_STATUS.SPIDER_SUCCESS
            self.__prefix_domain= None
            self.__current_url= None
            self.__data= None
            self.__spider_url=[]
            self.__next_url= None
            self.__fingerprint= None
            self.__rules_type= None
            if url == None:
                if "entrance" not in self.__config:
                    # if config hav't 'entrance' key, return.
                    msg= "-{0}, {1}".format(self.__current_url, "can't found config: root.entrance .")
                    return self.__onError(msg, SPIDER_STATUS.SPIDER_CONFIG_CAN_NOT_FOUND_KEY)
                url= self.__config['entrance']

            # 验证URL是否是入口地址，入口地址不检测页面重复性
            if 'entrance' not in self.__config:
                self.__is_to_fingerprint= True
            else:
                m_result= re.fullmatch(self.__config['entrance'], url, re.M | re.I)
                if m_result:
                    self.__is_to_fingerprint= False
                else:
                    self.__is_to_fingerprint= True
            # test url prefix
            if "prefix_domain" not in self.__config:
                msg= "-{0}\r\n\t{1}".format(self.__current_url, "can't found config: root.prefix_domain .")
                return self.__onError(msg, SPIDER_STATUS.SPIDER_CONFIG_CAN_NOT_FOUND_KEY)
            self.__prefix_domain= self.__config['prefix_domain']
            if re.match(self.__prefix_domain, url, re.M | re.I) == None:
                url= self.__prefix_domain + url
            self.__current_url= url
            self.__gethtml()
            if self.__status == SPIDER_STATUS.HTTP_SUCCESS:
                self.__rules_route()
                if self.__status == SPIDER_STATUS.SPIDER_SUCCESS:
                    self.__verify_serialize()
                # jion event func
                page_type= self.__rules_type
                if page_type == "index":
                    try:
                        self.__lock.acquire()
                        self.on(event.onIndexComplete, self)
                    finally:
                        self.__lock.release()
                elif page_type == 'list':
                    try:
                        self.__lock.acquire()
                        self.on(event.onListComplete, self)
                    finally:
                        self.__lock.release()
                elif page_type == 'detail':
                    try:
                        self.__lock.acquire()
                        self.on(event.onDetailComplete, self)
                    finally:
                        self.__lock.release()
                else:
                    msg= "-{0}, {1}".format(self.__current_url, "未找到对应的页面类型({0}).".format(page_type))
                    self.__onError(msg, SPIDER_STATUS.SPIDER_PAGE_TYPE_NOT_FOUND)
            else:
                msg= "-{0}, {1}".format(self.__current_url, "REQUEST获取网页失败.")
                self.__onError(msg, SPIDER_STATUS.REQUEST_CONNECT_ERROR)
        else:
            # config is none
            msg= "-{0}, {1}".format(self.__current_url, "配置文件没有加载.")
            return self.__onError(msg, SPIDER_STATUS.SPIDER_CONFIG_IS_NOT_LOAD)

    def next(self):
        if self.__next_url:
            self.spider_start(self.__next_url)

    def __gethtml(self):
        '''
        get url's html
        '''
        if self.__request:
            # if request object is ready
            if self.__current_url:
                try:
                    response_html, response_status= self.__request.getcontent(self.__current_url)
                    if response_status == 200:
                        # if http status is 200, return response_html
                        self.__response_html= response_html
                        self.__status= SPIDER_STATUS.HTTP_SUCCESS
                    else:
                        if response_status == "CONNECT_IS_ERROR":
                            # try reconnect url
                            self.__status= SPIDER_STATUS.REQUEST_CONNECT_ERROR
                            m_count= 0
                            for count in range(0,self.__max_reconnect):
                                m_count+= 1
                                response_html, response_status= self.__request.getcontent(self.__current_url)
                                if response_status == 200:
                                    self.__response_html= response_html
                                    self.__status= SPIDER_STATUS.HTTP_SUCCESS
                                    break
                            if m_count == self.__max_reconnect:
                                self.__status= SPIDER_STATUS.REQUEST_REQUEST_RECONNECT_EXCEED_LIMIT_MAX
                                self.generate_next_url(self.__current_url)
                        else:
                            msg= "-{0}, {1}".format(self.__current_url, "HTTP获取资源失败(http status：{0}).".format(self.__status))
                            return self.__onError(msg, response_status)
                except Exception as e:
                    msg= "-{0}, {1}".format(self.__current_url, e)
                    return self.__onError(msg, SPIDER_STATUS.REQUEST_ERROR)
            else:
                # config can not found the key "entrance"
                msg= "-访问地址为空."
                return self.__onError(msg, SPIDER_STATUS.REQUEST_URL_IS_NONE)
        else:
            msg= "-REQUEST对象未定义."
            return self.__onError(msg, SPIDER_STATUS.REQUEST_IS_NONE)

    def __rules_route(self):
        '''
        rules route

        - Parameters:
            url: spider current url
        '''
        # generate next url
        self.generate_next_url(self.__current_url)
        if "rules" in self.__config:
            rules_count= 0
            for item in self.__config['rules']:
            # begin for self.__config['rules']
                if "type" in item:
                    self.__rules_type= item["type"]
                if "url_checking" in item:
                    check_url= re.fullmatch(item['url_checking'], self.__current_url, re.I | re.S)
                    if not check_url:
                        continue

                    url_check_end_offset= check_url.end()
                    len_url= len(self.__current_url)
                    if url_check_end_offset == len_url:
                        # get spider_url
                        if "spider_url" in item:
                            if len(item['spider_url']) > 0:
                                for spider_url_item in re.finditer(item['spider_url'], self.__response_html, flags= 0):
                                    self.__spider_url.append(str(spider_url_item.group()))
                                self.__spider_url= list(set(self.__spider_url))
                        # intercept html
                        if "start_anchor" not in item:
                            msg= "-{0}, {1}".format(self.__current_url, "can't found config: root.rules.{0}.start_anchor .".format(str(rules_count)))
                            self.__onError(msg, SPIDER_STATUS.SPIDER_CONFIG_CAN_NOT_FOUND_KEY)
                            break
                        if "end_anchor" not in item:
                            msg= "-{0}, {1}".format(self.__current_url, "can't found config: root.rules.{0}.end_anchor .".format(str(rules_count)))
                            self.__onError(msg, SPIDER_STATUS.SPIDER_CONFIG_CAN_NOT_FOUND_KEY)
                            break
                        # get intercept offset
                        offset_start= None
                        m_re_result= re.search(item['start_anchor'], self.__response_html, re.M | re.I)
                        if m_re_result:
                            offset_start= m_re_result.start()
                        offset_end= None
                        m_re_result= re.search(item['end_anchor'], self.__response_html, re.M | re.I)
                        if m_re_result:
                            offset_end= m_re_result.start()
                        if offset_start == None:
                            msg= "-{0}, {1}".format(self.__current_url, "没有匹配到起始位置.")
                            self.__onError(msg, SPIDER_STATUS.SPIDER_REGAULE_MATCH_IS_ERROR)
                            break
                        if offset_end == None:
                            msg= "-{0}, {1}".format(self.__current_url, "没有匹配到结束位置.")
                            self.__onError(msg, SPIDER_STATUS.SPIDER_REGAULE_MATCH_IS_ERROR)
                            break
                        if offset_start >= offset_end:
                            msg= "-{0}, {1}".format(self.__current_url, "截取范围有误({0}:{1})".format((offset_start,offset_end)))
                            self.__onError(msg, SPIDER_STATUS.SPIDER_INTERCEPT_ERROR)
                            break
                        self.__response_html= self.__response_html[offset_start : offset_end]

                        # create file fingerprint
                        if self.__is_to_fingerprint:
                            m_md5= hashlib.md5()
                            m_md5.update(self.__response_html.encode('UTF-8'))
                            m_fingerprint= m_md5.hexdigest()
                            self.__fingerprint= m_fingerprint
                            try:
                                self.__lock.acquire()
                                m_check_status= self.on(event.onFingerprintComplete,self)
                            finally:
                                self.__lock.release()
                            if m_check_status:
                                msg= "-{0}, {1}".format(self.__current_url, "内容没有变更.")
                                self.__onError(msg, SPIDER_STATUS.SPIDER_FINGERPRINT_IS_REPEAT)
                                self.__next_url= None
                                break

                        # filter page html
                        self.__pagefilter(item, rules_count)
                        # spider action
                        self.__action(item, rules_count)
                        if self.__status == SPIDER_STATUS.SPIDER_SUCCESS:
                            # serialize_data
                            self.__serialize_data(item, rules_count)
                        break
                    rules_count+= 1
                else:
                    msg= "-{0}, {1}".format(self.__current_url, "can't found config: root.rules.{0}.url_checking .".format(str(rules_count)))
                    self.__onError(msg, SPIDER_STATUS.SPIDER_CONFIG_CAN_NOT_FOUND_KEY)
            # end for self.__config['rules']
            if rules_count >= len(self.__config['rules']):
                msg= "-{0}, {1}".format(self.__current_url, "未找页面对应的分析规则.")
                self.__onError(msg, SPIDER_STATUS.SPIDER_PAGE_ANALYSIS_RULES_CAN_NOT_FOUND)
        else:
            msg= "-{0}, {1}".format(self.__current_url, "can't found config: root.rules .")
            self.__onError(msg, SPIDER_STATUS.SPIDER_CONFIG_CAN_NOT_FOUND_KEY)

    def generate_next_url(self, url):
        item= self.__config
        if item:
            if "page_url" in item:
                if "verification_page_url" in item['page_url']:
                    page_str= re.search(item['page_url']['verification_page_url'], url, re.M | re.I)
                    if page_str:
                        page_str= page_str.group()
                        page_param= re.findall(r"[1-9]\d*", page_str, flags= 0)
                        if page_param:
                            if 'page_param_index' in item['page_url']:
                                if len(page_param) < item['page_url']['page_param_index']:
                                    # default next page index is 2.
                                    page_param.append("2")
                                else:
                                    # calculation next page index
                                    page_param_index= item['page_url']['page_param_index']
                                    if page_param_index != 0:
                                        page_param_index -= 1 
                                        page_param[page_param_index] = str(int(page_param[page_param_index]) + 1)
                                if 'template' in item['page_url']:
                                    self.__next_url= item['page_url']['template'].format(page_param)
                                    self.__next_url= re.sub(item['page_url']['verification_page_url'], self.__next_url, url, count= 0, flags= 0)


    def __pagefilter(self, item, rules_count= 0):
        # filter page html
        try:
            if "page_filter" in item:
                for page_item in item['page_filter']:
                    if len(page_item) != 2:
                        continue
                    self.__response_html= re.sub(page_item[0], page_item[1], self.__response_html, count=0, flags=0)
        except Exception as e:
            msg= "-{0}, {1}".format(self.__current_url, e)
            self.__onError(msg, SPIDER_STATUS.SPIDER_PAGE_FILTER_ERROR)
            # 页面过滤不影响后续分析， 不终止此次分析.
            self.__status=  SPIDER_STATUS.SPIDER_SUCCESS

    def __action(self, item, rules_count= 0):
        try:
            if "actions" not in item:
                msg= "-{0}, {1}".format(self.__current_url, "can't found config: root.rules.{0}.actions .".format(str(rules_count)))
                return self.__onError(msg, SPIDER_STATUS.SPIDER_CONFIG_CAN_NOT_FOUND_KEY)
            action_count=0
            for action_item in item['actions']:
            # begin for item['acctions']
                if not action_item:
                    msg= "-{0}, {1}".format(self.__current_url, "root.rules.{0}.actions 为空.".format(str(rules_count)))
                    return self.__onError(msg, SPIDER_STATUS.SPIDER_PAGE_ANALYSIS_ACTIONS_ERROR)
                if "action" not in action_item:
                    msg= "-{0}, {1}".format(self.__current_url, "can't found config: root.rules{0}.actions.{1}.action .".format(str(rules_count), str(action_count)))
                    return self.__onError(msg, SPIDER_STATUS.SPIDER_CONFIG_CAN_NOT_FOUND_KEY)
                action_type= action_item['action'].lower()
                if action_type == "filter":
                    # filter html
                    if 'extract_regex' not in action_item:
                        msg= "-{0}, {1}".format(self.__current_url, "can't found config: root.rules.{0}.actions.{1}.extract_regex .".format(str(rules_count), str(action_count)))
                        return self.__onError(msg, SPIDER_STATUS.SPIDER_CONFIG_CAN_NOT_FOUND_KEY)
                    self.__filter(action_item)
                    if self.__status != SPIDER_STATUS.SPIDER_SUCCESS:
                        msg= "-{0}, {1}".format(self.__current_url, "提取内容失败(regex: {0}).".format(action_item['extract_reg']))
                        return self.__onError(msg, SPIDER_STATUS.SPIDER_PAGE_ANALYSIS_ACTION_FAIL)
                elif action_type == "replace":
                    # replace html
                    if 'extract_regex' not in action_item:
                        msg= "-{0}, {1}".format(self.__current_url, "can't found config: root.rules.{0}.actions.{1}.extract_regex .".format(str(rules_count), str(action_count)))
                        return self.__onError(msg, SPIDER_STATUS.SPIDER_CONFIG_CAN_NOT_FOUND_KEY)
                    if 'replace_str' not in action_item:
                        msg= "-{0}, {1}".format(self.__current_url, "can't found config: root.rules.{0}.actions.{1}.replace_str .".format(str(rules_count), str(action_count)))
                        return self.__onError(msg, SPIDER_STATUS.SPIDER_CONFIG_CAN_NOT_FOUND_KEY)
                    self.__replace(action_item)
                elif action_type == "inserhtml":
                    if 'html' not in action_item:
                        msg= "-{0}, {1}".format(self.__current_url, "can't found config: root.rules.{0}.actions.{1}.html .".format(str(rules_count), str(action_count)))
                        return self.__onError(msg, SPIDER_STATUS.SPIDER_CONFIG_CAN_NOT_FOUND_KEY)
                    self.__inserHTML(action_item)
                else:
                    msg= "-{0}, {1}".format(self.__current_url, "找不到分析器(root.rules.{0}.actions.{1}.action({2})) .".format(str(rules_count), str(action_count), action_type))
                    return self.__onError(msg, SPIDER_STATUS.SPIDER_PAGE_ANALYSIS_ACTION_FAIL)
                action_count+= 1
            # end for item['actions']
        except Exception as e:
            msg= "-{0}, {1}".format(self.__current_url, e)
            return self.__onError(msg, SPIDER_STATUS.SPIDER_PAGE_ANALYSIS_ACTION_FAIL)
    
    def __filter(self,action_item):
        backups_response_html= self.__response_html
        filter_html= ""
        m_re_statu= re.search(action_item['extract_regex'], self.__response_html, flags= 0)
        if not m_re_statu:
            self.__status= SPIDER_STATUS.SPIDER_PAGE_ANALYSIS_FILTER_FAIL
            self.__next_url= None
        else:
            for filter_item in re.finditer(action_item['extract_regex'], self.__response_html, flags= 0):
                filter_html+= str(filter_item.group())
            if filter_html:
                self.__response_html= filter_html        
                self.__status= SPIDER_STATUS.SPIDER_SUCCESS
            else:
                self.__status= SPIDER_STATUS.SPIDER_ERROR
            if 'debug' in action_item:
                if action_item['debug']:
                    try:
                        self.__lock.acquire()
                        self.on(event.onDebug, "-{0}, regular:{1}\r\n\t- befor:{2}\r\n\t- after:{3}".format(self.currentUrl,action_item['extract_regex'],backups_response_html, self.__response_html))
                    finally:
                        self.__lock.release()
        backups_response_html= None
    
    def __replace(self, action_item):
        backups_response_html= self.__response_html
        self.__response_html= re.sub(action_item['extract_regex'], action_item['replace_str'], self.__response_html, count= 0, flags= 0)
        if 'debug' in action_item:
            if action_item['debug']:
                try:
                    self.__lock.acquire()
                    self.on(event.onDebug, "-{0}, regular:{1}\r\n\t- befor:{2}\r\n\t- after:{3}".format(self.currentUrl,action_item['extract_regex'],backups_response_html, self.__response_html))
                finally:
                    self.__lock.release()
        backups_response_html= None

    def __inserHTML(self, action_item):
        backups_response_html= self.__response_html
        self.__response_html+= action_item['html']
        if 'debug' in action_item:
            if action_item['debug']:
                try:
                    self.__lock.acquire()
                    self.on(event.onDebug, "-{0}\r\n\t- befor:{1}\r\n\t- after:{2}".format(self.currentUrl, backups_response_html, self.__response_html))
                finally:
                    self.__lock.release()
        backups_response_html= None

    def __serialize_data(self, item, rules_count):
        try:
            result= None
            if 'type' not in item:
                result= dict({"type" : item["type"], "data" : None, "str" : self.__response_html})
            serialize_item= item['serialize_data']
            if 'serialize_type' not in serialize_item:
                msg= "-{0}, {1}".format(self.__current_url, "can't found config: root.rules.{0}.serialize_data.serialize_type .".format(str(rules_count)))
                return self.__onError(msg, SPIDER_STATUS.SPIDER_CONFIG_CAN_NOT_FOUND_KEY)  
            if serialize_item['serialize_type'] == "split":
                if 'split_str' not in serialize_item:
                    msg= "-{0}, {1}".format(self.__current_url, "can't found config: root.rules.{0}.serialize_data.split_str .".format(str(rules_count)))
                    return self.__onError(msg, SPIDER_STATUS.SPIDER_CONFIG_CAN_NOT_FOUND_KEY)
                # 过滤换行符、制表符.
                m_html= re.sub(r"\r\n|\r|\n|\t", "", self.__response_html, count= 0, flags= 0)

                # 序列化数据
                split_html= re.split(serialize_item['split_str'], m_html, maxsplit= 0, flags= 0)
                if 'fields' not in serialize_item:
                    msg= "-{0}, {1}".format(self.__current_url, "can't found config: root.rules.{0}.serialize_data.fields .".format(str(rules_count)))
                    return self.__onError(msg, SPIDER_STATUS.SPIDER_CONFIG_CAN_NOT_FOUND_KEY)
                # 删除空数据
                split_html= [i for i in split_html if i != '']
                split_html= self.__check_result(serialize_item, split_html) #检查数据完整性.
                len_fields= len(serialize_item['fields'])
                len_split= len(split_html)
                if len_split == 0:
                    msg= "-{0}, {1}".format(self.__current_url, "数据为空.")
                    self.__onError(msg, SPIDER_STATUS.SPIDER_SERIALIZE_ERROR)
                    self.__data= dict({"type" : item["type"], "data" : None, "str" : self.__response_html})
                    return None 
                if len_fields == 0:
                    msg= "-{0}, {1}".format(self.__current_url, "映射字段为空.")
                    self.__onError(msg, SPIDER_STATUS.SPIDER_SERIALIZE_ERROR)
                    self.__data= dict({"type" : item["type"], "data" : None, "str" : self.__response_html})
                    return None
                if len(split_html) % len(serialize_item['fields']):
                    msg= "-{0}, {1}".format(self.__current_url, "数据长度与字段长度不一致: length({0}:{1})\r\n\tsplit_html({2})\r\n\tfields({3})".format(len(split_html), len(serialize_item['fields']), str(split_html), str(serialize_item['fields'])))
                    return self.__onError(msg, SPIDER_STATUS.SPIDER_SERIALIZE_ERROR)
                result= []
                for step_split in range(0, len_split, len_fields):
                    m_dict= dict()
                    for step_fields in range(0, len_fields):
                        m_dict[serialize_item['fields'][step_fields]]= split_html[step_split + step_fields]
                    if len(m_dict) > 0:
                        result.append(m_dict)
                if len(result) <= 0:
                    msg= "-{0}, {1}".format(self.__current_url, "序列化数据为空.")
                    return self.__onError(msg, SPIDER_STATUS.SPIDER_SERIALIZE_ERROR)
                result= dict({"type" : item["type"], "data" : result, "str" : self.__response_html})
            else:
                msg= "-{0}, {1}".format(self.__current_url, "暂时只能使用split模式分割数据.")
                return self.__onError(msg, SPIDER_STATUS.SPIDER_SERIALIZE_ERROR)
            self.__data= result
        except Exception as e:
            msg= "-{0}, {1}".format(self.__current_url, e)
            return self.__onError(msg, SPIDER_STATUS.SPIDER_SERIALIZE_ERROR)

    def __check_result(self, serialize_config, result):
        '''
            检查数据集结果规范, 根据serialize_data.check_fields_type配置项进行检查.如果检查结果不匹配则使用默认值替代

            参数：
                serialize_config: serialize_data配置项.
                result: []
        '''
        if "check_fields_type" in serialize_config:
            for check_config in serialize_config['check_fields_type']:
                if len(check_config) == 3:
                    if len(result) >= check_config[0]:
                        m_re_result= re.search(check_config[1], result[check_config[0]], re.I | re.M)
                        if not m_re_result:
                            result.insert(check_config[0], check_config[2])
        return result

    def __onError(self, msg, errCode= -1):
        '''
        spider error process

        - Parameters:
            msg: error msg.
            status: error code.
        '''
        self.__status= errCode
        try:
            self.__lock.acquire()
            self.on(event.onError, msg, self.__status, self)
        finally:
            self.__lock.release()
        return None

    def __verify_serialize(self):
        '''
        verification result format
        '''
        if 'type' not in self.__data:
            self.__onError("-{0}, {1}".format(self.__current_url, "serialize result can't found key(type)"), SPIDER_STATUS.SPIDER_SERIALIZE_DATA_VERIFY_FAIL)
        if 'data' not in self.__data:
            self.__onError("-{0}, {1}".format(self.__current_url, "serialize result can't found key(data)"), SPIDER_STATUS.SPIDER_SERIALIZE_DATA_VERIFY_FAIL)
        if 'str' not in self.__data:
            self.__onError("-{0}, {1}".format(self.__current_url, "serialize result can't found key(str)"), SPIDER_STATUS.SPIDER_SERIALIZE_DATA_VERIFY_FAIL)
    
    def close(self):
        del self.debug
        del self.__max_reconnect
        del self.__request
        del self.__config
        del self.__response_html
        del self.__status
        del self.__prefix_domain
        del self.__current_url
        del self.__data
        del self.__spider_url
        del self.__next_url
        del self.__fingerprint
        del self.__rules_type
        gc.collect()