import json
import logging
import functools
import re
from rest_framework.response import Response
from rest_framework.request import Request
from types import FunctionType
from TDhelper.generic.classDocCfg import doc
from TDhelper.generic.dictHelper import createDictbyStr, findInDict
from TDhelper.network.http.REST_HTTP import GET, POST, PUT, DELETE, serializePostData
from TDhelper.generic.recursion import recursion, recursionCall


class register:
    def __init__(self, host, platformKey: str, secret=None, httpHeaders={}):
        self._host = host
        self._platformKey = platformKey
        self._secret = secret
        self._httpHeaders = httpHeaders

    def Register(self, serviceClass=None):
        '''
            使用方法描述进行注册
            - params:
            -   serviceClass: <class>, 类
        '''
        if not serviceClass:
            serviceClass = type(self)
        for k, v in serviceClass.__dict__.items():
            if isinstance(v, FunctionType):
                if not k.startswith("__"):
                    if not k.startswith("_"):
                        self._handleRegister(v)

    def RegisterByCfg(self, Cfg: dict):
        '''
            使用配置文件进行注册
            - params:
            -   Cfg:<dict>, 注册配置文件.
        '''
        if Cfg:
            kwargs = {"params": Cfg}
            recursionCall(self._register_permission, **kwargs)

    def _handleRegister(self, v):
        k = v.__qualname__.replace('.', "_").upper()
        config = v.__doc__
        config = doc(v.__doc__, "permission")
        if config:
            config = re.sub(r'[\r|\n]', r'', config, count=0, flags=0).strip()
            try:
                config = json.loads(config, encoding='utf-8')
            except:
                config = None
            # todo register permission
            if config:
                kwargs = {"params": config}
                recursionCall(self._register_permission, **kwargs)
        else:
            raise Exception("config is none.")

    @recursion
    def _register_permission(self, *args, **kwargs):
        if self._platformKey:
            kwargs['params']['permission_key'] = self._platformKey + \
                "."+kwargs['params']['permission_key']
        if not self._host.endswith('/'):
            self._host += '/'
        post_data = {
            "permission_name": kwargs['params']['permission_name'],
            "permission_key": kwargs['params']['permission_key'],
            "permission_domain": kwargs['params']['permission_domain'],
            "permission_uri": kwargs['params']['permission_uri'],
            "permission_enable": kwargs['params']['permission_enable'],
            "permission_parent": 0 if 'permission_parent' not in kwargs['params'] else kwargs['params']['permission_parent']
        }
        state, body = POST(uri=self._host+"permissions/", post_data=post_data,
                           http_headers=self._httpHeaders, time_out=15)
        m_parent_id = 0
        if state == 200:
            m_ret = str(body, encoding='utf-8')
            m_ret_json = json.loads(m_ret, encoding='utf-8')
            if m_ret_json['state'] == 200:
                m_parent_id = m_ret_json['msg']["permission_id"]
                logging.info("create permission '%s' success." %
                             kwargs['params']['permission_name'])
            else:
                logging.info("create permission '%s' failed.error(%s)" % (
                    kwargs['params']['permission_name'], m_ret_json['msg']))
        else:
            logging.info("create permission '%s' failed." %
                         kwargs['params']['permission_name'])
        if 'children' not in kwargs['params']:
            kwargs['break'] = True
            return args, kwargs
        else:
            for item in kwargs['params']['children']:
                kwargs['params'] = item
                kwargs['params']['permission_parent'] = m_parent_id
                return self._register_permission(*args, **kwargs)
            if not kwargs['params']['children']:
                kwargs['break'] = True
                return args, kwargs
        return args, kwargs


class perACL:
    def __init__(self, rpc_key, params_container_class, platformKey=None, tokenKey="usr-token"):
        self._params_container = params_container_class
        self._platformKey = platformKey
        self._tokenKey = tokenKey
        self._rpc = None
        self._rpc_key = rpc_key

    def addRPCHandle(self, handle):
        self._rpc = handle

    def AccessControlLists(self, premissionKey=None, debug=False):
        def decorator(func):
            @functools.wraps(func)
            def wapper(*args, **kwargs):
                validate_state = True
                if not debug:
                    if self._platformKey:
                        self._platformKey += "."
                        self._platformKey = self._platformKey.upper()
                    if premissionKey:
                        _eventKey = self._platformKey + premissionKey.upper()
                    else:
                        _eventKey = self._platformKey + \
                            func.__qualname__.replace('.', '_').upper()
                    params_instance = None
                    for k in args:
                        if isinstance(k, self._params_container):
                            params_instance = k
                            break
                    if not params_instance:
                        for k, v in kwargs:
                            if isinstance(v, self._params_container):
                                params_instance = v
                                break
                    if not params_instance:
                        return Response("can found context.", status=500)
                    if isinstance(params_instance, Request):
                        if self._tokenKey in params_instance._request.headers:
                            token = params_instance._request.headers[self._tokenKey]
                        else:
                            return Response("http headers can not found '%s' key." % self._tokenKey, status=500)
                    elif isinstance(params_instance, dict):
                        token = params_instance[self._tokenKey]
                    elif isinstance(params_instance, (int, str, float)):
                        token = params_instance
                    else:
                        token = getattr(params_instance, self._tokenKey)
                    if token:
                        if self._rpc:
                            validate_ret = self._rpc.call(
                                self._rpc_key, **{"token": token, "event": _eventKey})
                            if validate_ret:
                                if validate_ret['state'] == 200:
                                    validate_state = True
                                else:
                                    return Response("access error.(%s)" % validate_ret['msg'], status=500)
                            else:
                                return Response("access http error.", status=500)
                        else:
                            return Response("rpc handle is none.", status=500)
                    else:
                        return Response("token(%s) is None.", status=500)
                if validate_state:
                    ret = func(*args, **kwargs)
                    return ret
                else:
                    return Response(data="Unauthorized", status=401)
            return wapper
        return decorator
