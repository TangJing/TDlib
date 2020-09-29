import json
import copy
from urllib import parse
from TDhelper.network.http.REST_HTTP import GET, POST
from TDhelper.Decorators.log import logging, logging_setup

class RPC:
    '''
        RPC. 此类只能配合webservice/rpc使用, 独立使用将会报错.
    '''

    def __init__(self, service_center_uri, secret, logging_config= None):
        '''
            初始化
            - params:
            -   service_center_uri:<string>, 服务中心获取API接口URI.
            -   secret: <string>, 访问密钥
        '''
        self._access_token = secret
        self._sc_uri = service_center_uri
        self._apisTable = {}
        self._current_service= None
        self._logging= False
        if logging_config:
            self._logging= True
            logging_setup(logging_config)

    def _log(self, msg, type="info"):
        if self._logging:
            if type.lower()=="info":
                logging.info(msg)
            elif type.lower()=="error":
                logging.error(msg)

    def _getApi(self, service, method):
        if service+method not in self._apisTable:
            # 远程获取
            m_heads = {"api-token": self._access_token}
            status, body = GET(uri=self._sc_uri+"rpc/?key="+service +
                               "&method="+method, time_out=15, http_headers=m_heads)
            if status == 200:
                self._apisTable[service+method] = json.loads(
                    str(body, encoding='utf-8'))
        # 从本地获取API配置
        if service+method in self._apisTable:
            if self._apisTable[service+method]['state'] == 200:
                return True, self._apisTable[service+method]['msg']
            else:
                return False, self._apisTable[service+method]['msg']
        else:
            return False, "can't found %s api." % service+method

    def register(self, service: dict, hosts: [], methods: []):
        '''
            注册服务
            - params:
            -   service: <dict>, 服务信息. formatter:{"name":"","description":"","key":"","httpProtocol":""}
            -   hosts: <[]>, 服务器信息. formatter:[{"host":"ip地址","port":端口}]
            -   methods: <[]>, 方法. formatter: [{"key":"方法索引","uri":"api url","method":"GET|POST|PUT|DELETE","version":"版本号","description":"描述", "params":[{"key":"参数名称","description":"描述","defaultValue":"默认值(调用不传参时默认值)"}]}]
            - Returns:
            -   bool, str: 状态，信息.
        '''
        m_service_post_data = ''
        m_count = 0
        # 生成注册服务参数.
        for k, v in service.items():
            if k.lower() != 'description':
                if not v:
                    raise Exception("service '%s' value can't is none." % k)
            m_service_post_data += k+"="+ parse.quote(str(v))
            m_count += 1
            if m_count < len(service):
                m_service_post_data += "&"
        # 注册服务基本信息.
        state, ret = POST(self._sc_uri+"services/",
                          post_data=bytes(m_service_post_data, encoding='utf-8'), time_out=15)
        if state == 200:
            if ret:
                ret = json.loads(str(ret, encoding='utf-8'))
                if ret['state'] == 200:
                    m_service_id = ret['msg']['id']
                    # 注册服务器信息.
                    for i in range(0, len(hosts)):
                        hosts[i]['service'] = m_service_id
                        #hosts[i]['state']= True
                        m_count = 0
                        m_service_hosts_post_data = ''
                        for k, v in hosts[i].items():
                            if v:
                                m_service_hosts_post_data += k+"="+parse.quote(str(v))
                                m_count += 1
                                if m_count < len(hosts[i]):
                                    m_service_hosts_post_data += "&"
                            else:
                                raise Exception(
                                    "register hosts {} can't is none." % k)
                        state, ret = POST(self._sc_uri+"hosts/", post_data=bytes(
                            m_service_hosts_post_data, encoding='utf-8'), time_out=15)
                        if state != 200:
                            return False, 'register service hosts failed. msg:{}' % str(ret, encoding='utf-8')
                        else:
                            ret = json.loads(str(ret, encoding='utf-8'))
                            if ret['state'] != 200:
                                m_msg = 'register service hosts failed. http code({}), msg:{}' % (ret[
                                    'state'], ret['msg'])
                                return False, m_msg
                    # 注册方法
                    for i in range(0, len(methods)):
                        # todo register method.
                        methods[i]['service'] = m_service_id
                        m_service_uri_post_data = ''
                        m_count = 0
                        for k, v in methods[i].items():
                            if k.lower() != 'params':
                                if k.lower() == 'key' or k.lower() == 'uri' or k.lower() == 'method':
                                    if not v:
                                        raise Exception(
                                            'methods (%s) is none.' % k.lower())
                                if k.lower() != 'method':
                                    m_service_uri_post_data += k + "=" + parse.quote(str(v))
                                else:
                                    m_value = 0
                                    if v.upper() == u"GET":
                                        m_value = 1
                                    elif v.upper() == u"POST":
                                        m_value = 2
                                    elif v.upper() == u"PUT":
                                        m_value = 3
                                    elif v.upper() == u"DELETE":
                                        m_value = 4
                                    m_service_uri_post_data += k + \
                                        "=" + str(m_value)
                                m_count += 1
                                if 'params' in methods[i]:
                                    if m_count < len(methods[i])-1:
                                        m_service_uri_post_data += "&"
                                else:
                                    if m_count < len(methods[i]):
                                        m_service_uri_post_data += "&"
                        state, ret = POST(self._sc_uri+"uri/", post_data=bytes(
                            m_service_uri_post_data, encoding='utf8'), time_out=15)
                        if state != 200:
                            return False, 'register service methods failed. msg:{}' % str(ret, encoding='utf-8')
                        else:
                            ret = json.loads(str(ret, encoding='utf-8'))
                            if ret['state'] != 200:
                                m_msg = 'register service methods failed. http code(%d), msg:%s' % (
                                    ret['state'], ret['msg'])
                                return False, m_msg
                            else:
                                if ret:
                                    if 'params' in methods[i]:
                                        params = methods[i]['params']
                                        m_method_id = ret['msg']["id"]
                                        if params:
                                            # 有参数能注册.
                                            for param_offset in range(0, len(params)):
                                                params[param_offset]['serviceUri'] = m_method_id
                                                m_service_method_params_post_data = ''
                                                m_count = 0
                                                for k, v in params[param_offset].items():
                                                    if not v:
                                                        raise Exception(
                                                            'methods params (%s) is none.' % k.lower())
                                                    m_service_method_params_post_data += k + \
                                                        "=" + parse.quote(str(v))
                                                    m_count += 1
                                                    try:
                                                        if m_count < len(params[param_offset]):
                                                            m_service_method_params_post_data += "&"
                                                    except Exception as e:
                                                        raise e
                                                state, ret = POST(
                                                    self._sc_uri+"params/", post_data=bytes(m_service_method_params_post_data, encoding='utf-8'), time_out=15)
                                    # 注册返回值
                                    if 'returns' in methods[i]:
                                        m_returns= methods[i]['returns']
                                        if m_returns:
                                            # 有返回值设置进行注册.
                                            reg_returns_params=''
                                            m_count=0
                                            m_returns['serviceUri']= m_method_id
                                            for k,v in m_returns.items():
                                                if k.lower()!= 'descriptions':
                                                    reg_returns_params+= k+"="+parse.quote(str(v))
                                                    m_count+=1
                                                    if 'descriptions' in m_returns:
                                                        if m_count< len(m_returns)-1:
                                                            reg_returns_params+="&"
                                                    else:
                                                        if m_count < len(m_returns):
                                                            reg_returns_params+="&"
                                            state, ret= POST(self._sc_uri+"returns/",post_data= bytes(reg_returns_params,encoding='utf-8'),time_out=15)
                                            if state == 200:
                                                ret = json.loads(str(ret, encoding='utf-8'))
                                                if ret['state'] != 200:
                                                    m_msg = 'register service methods failed. http code(%d), msg:%s' % (ret['state'], ret['msg'])
                                                    return False, m_msg
                                                else:
                                                    m_returns_id= ret['msg']['id']
                                                    if 'descriptions' in m_returns:
                                                        # 注册返回值说明
                                                        for item in m_returns['descriptions']:
                                                            m_returns_description= 'returns='+ str(m_returns_id)
                                                            m_returns_description+= '&key='+parse.quote(item['key'])
                                                            m_description= item['valueDescription']
                                                            m_description= m_description.replace("<","&lt;")
                                                            m_description= m_description.replace(">","&gt;")
                                                            m_description= m_description.replace("\r\n","<br />")
                                                            m_returns_description+= '&valueDescription='+parse.quote(m_description)
                                                            state, ret= POST(self._sc_uri+ "returnDescriptons/", post_data=bytes(m_returns_description,encoding='utf-8'),time_out=15)
                                                            if state!=200:
                                                                m_msg = 'register return description failed. http code(%d)'% state
                                                                return False, m_msg
                                                            else:
                                                                ret = json.loads(str(ret, encoding='utf-8'))
                                                                if ret['state']!=200:
                                                                    m_msg= 'register return description failed. state(%d), msg(%s), key()'%(ret['state'],ret['msg'], item['key'])
                                                                    return False, m_msg
                                            else:
                                                m_msg = 'register returns failed. http code(%d)'% state
                                                return False, m_msg

                                else:
                                    if ret['state'] != 200:
                                        m_msg = 'register service hosts failed. http code(%d), msg:%s' % (ret[
                                            'state'], ret['msg'])
                                        return False, m_msg
                    return True, 'register service success.'
                else:
                    msg = "register service http error. http code(%s), msg:%s" % (ret[
                        'state'], ret['msg'])
                    return False, msg
            else:
                raise Exception(
                    "register return body is none, please checked.")
        else:
            msg = "register service http error. http code(%d), msg:%s" % (
                state, str(ret, encoding='utf-8'))
            return False, msg

    def handle(self, service):
        '''
            获取服务句柄
            - params:
            -   service: <string>, 服务key
            - returns
            -   self: <RPC>, 返回一个RPC服务句柄.
        '''
        self._current_service= service
        return copy.deepcopy(self)

    def call(self, method, **kwargs):
        '''
            调用方法
            - params:
            -   method: <string>, 方法key值.
            - **kwargs: 参数字典
            - returns:
            -   json: <json>, formatter: {"httpCode":"调用网络状态", "data":"调用的方法的返回值"}
        '''
        if not self._current_service:
            raise Exception('service is not set, first call self.handle method to set service.')
        state, ret = self._getApi(self._current_service, method)
        if state:
            try:
                m_uri = ret['uri']
                m_params = ret['params']
                m_method = ret['method']
                params_data = ''
                m_count = 0
                for param in m_params:
                    if param['key'].lower() != 'pk':
                        if param['key'] in kwargs:
                            params_data += param['key'] + \
                                '=' + parse.quote(str(kwargs[param['key']]))
                        else:
                            if param['defaultValue']:
                                params_data += param['key'] + '=' + parse.quote(param['defaultValue'])
                        m_count += 1
                        if m_count < len(kwargs):
                            params_data += "&"
                    else:
                        m_uri.replace("{pk}", parse.quote(str(kwargs[param['key']])))
                try:
                    if m_method == u"GET":
                        m_uri += "?" + params_data
                        self._log(m_uri)
                        state, ret = GET(uri= m_uri, time_out=15)
                        if state == 200:
                            try:
                                ret= json.loads(str(ret, encoding="utf-8"))
                                return {"httpCode": ret['state'], "data": ret['msg']}
                            except Exception as e:
                                raise e
                        else:
                            try:
                                ret= json.loads(str(ret, encoding="utf-8"))
                                return {"httpCode": ret['state'], "data": ret['msg']}
                            except:
                                return {"httpCode": ret['state'], "data": ret}
                    elif m_method == u"POST":
                        self._log(m_uri+", postdata:%s"%params_data)
                        state, ret = POST(m_uri, bytes(
                            params_data, encoding='utf-8'), time_out=15)
                        if state == 200:
                            try:
                                ret= json.loads(str(ret, encoding="utf-8"))
                                return {"httpCode": ret['state'], "data": ret['msg']}
                            except Exception as e:
                                raise e
                        else:
                            try:
                                ret= json.loads(str(ret, encoding="utf-8"))
                                return {"httpCode": ret['state'], "data": ret['msg']}
                            except:
                                return {"httpCode": ret['state'], "data": ret}
                    elif m_method == u"PUT":
                        # 还没有写PUT方法
                        raise Exception('urllib PUT方法还没写.')
                    elif m_method == u"DELETE":
                        # 还没有写DELETE方法
                        raise Exception("urllib delete 方法还没写.")
                    else:
                        raise Exception('restful method is error.')
                except Exception as e:
                    return {"httpCode": -1, "data": e}
            except Exception as e:
                raise e
        else:
            return {"httpCode": -1, "data": ret}


if __name__ == '__main__':
    m_rpc = RPC("http://127.0.0.1:8000/api/", "349304398403804983048034")
    '''
    print(m_rpc.register(
        service={"name": "test", "description": "测试添加服务",
                 "key": "gg", "httpProtocol": "http://"},
        hosts=[{"host": "127.0.0.1", "port": 8002}, {
            "host": "192.168.0.100", "port": 8000}],
        methods=[{"key": "test_method", "uri": "api/uri/", "method": "POST", "version": "1.0.0", "description": "测试添加方法", "params": [{"key": "test_method_p1", "description": "P1参数", "defaultValue": "0"}]}]))
    #print(m_rpc.call("remote_config","remote_config_register", **{"name":"测试远程配置服务注册","serivce_key":"test_rpc_register"}))
    '''
    serviceConfig = {
    "services": [
        {
            # 服务配置
            "service": {
                "name": "TEST",
                "description":"TEST",
                "key":"TEST",
                "accessSecret": "slkjflkjdfejfoejfoefef",
                "httpProtocol":"http://"
            },
            # 服务器配置
            "hosts":[
                {
                    "host": "127.0.0.1",
                    "port": 8004
                }
            ],
            # 方法配置
            "methods":[
                # 帐号相关 begin
                {
                    "key": "TEST" + "_ACCOUNTS_LIST",
                    "uri": "api/accounts/",
                    "method": "GET",
                    "version": "1.0.0",
                    "description": "获取帐号列表",
                    "params": [
                        {
                            "key":"page",
                            "descript":"页码",
                            "defaultValue": "1"
                        }
                    ],
                    "returns":{
                        "valueType":"json",
                        "examples": json.dumps({"state":200,"msg":{"count": 0,"next": None,"previous": None,"results": []}}),
                        "descriptions":[
                            {
                                "key":"state",
                                "valueDescription":"200:success,\r\n-1:failed."
                            },
                            {
                                "key":"msg",
                                "valueDescription":"success returns json({count:<int>(total records count),next:<string>(next page url),previous:<string>(previous page url),results:[json(<account>)]}),\r\nfailed returns error msg(<string>)."
                            }
                        ]
                    }
                }
            ]
        }
    ]
    }
    '''
    count=0
    for item in serviceConfig["services"]:
        print(m_rpc.register(
            service=item['service'],
            hosts=item['hosts'],
            methods=item['methods']))
    '''
    g=m_rpc.handle("GENERAL_SERVICE")
    ret= g.call(
        "GENERAL_SERVICE_VALIDATE_CODE_VALIDATE",
        **{
            "validateType": 1,
            "triggerEvent": "手机验证码登录",
            "receive": '8615013782894',
            "code": '22222'
        })
    print(ret)
    #m_id= ret['data']['id']
    #ret=g.call('REMOTE_CONFIG_CONFIG_REGISTER',**{"config_key":"test1","config_value":"testvalue","service":m_id})
    #print(ret)