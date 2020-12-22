import urllib
import socket
import json
from urllib import request,parse
from urllib.error import HTTPError, URLError

def serializePostData(post_data:dict, isBytes= True):
    if isinstance(post_data,dict):
        post_data_params=""
        m_result= post_data.items()
        m_count=0
        for k,v in m_result:
            if isinstance(v,dict):
                post_data_params+= k+"="+ json.dumps(v)
            else:
                post_data_params+= k + '=' + parse.quote(str(v))
            m_count+=1
            if m_count< len(m_result):
                post_data_params+= "&"
        if post_data_params:
            if isBytes:
                return bytes(post_data_params, encoding='utf-8')
            else:
                return post_data_params
        else:
            return None
    return post_data

def GET(uri:str, post_data={}, http_headers:dict= None, time_out:int= 1):
    """
    http GET method
    
    - Parameters:
        uri: an uri, it can be an domain or ip, type must is cls<str>.
        post_data: <dict>, params.
        http_headers: set request's headers, default is None.
        time_out: time out for access remote uri , default value is 1 seconds.

    - Returs:
        stauts, body

        example: 
            
            200, <html><body>this is an example</body></html>
    """
    try:
        req= None
        if post_data:
            m_params_data_str= serializePostData(post_data,isBytes= False)
            if uri.find('?')>-1:
                uri+="&"+ m_params_data_str
            else:
                uri+="?"+ m_params_data_str
        if http_headers:
            req= request.Request(uri, headers= http_headers, method= 'GET')
        else:
            req= request.Request(uri, method= 'GET')
        with request.urlopen(req,timeout= time_out) as response:
            return response.getcode(),response.read()
    except HTTPError as e:
        return e.code, e.reason
    except URLError as e:
        if isinstance(e.reason, socket.timeout):
            return 408, None
        else:
            return e.reason, None

def POST(uri, post_data:bytes, http_headers= None, time_out= 1, charset= 'UTF-8'):
    """
    http POST method

    - Paramters:
        uri: an uri, it can be an domain or ip, type must is cls<str>.
        data: submit request post data.
        http_headers: set request's headers, default is None.
        time_out: time out for access remote uri , default value is 1 seconds.
        charset: set the http charset, default is UTF-8
    
    - Returns:
        status, body

        example:
            
            200, <html><body>this is an example</body></html>
    """
    try:
        req= None
        if post_data:
            post_data= serializePostData(post_data)
        if http_headers:
            req= request.Request(uri, data= post_data, headers= http_headers)
        else:
            req= request.Request(uri, data= post_data, method= 'POST')
        with request.urlopen(req, timeout= time_out) as response:
            return response.getcode(),response.read()
    except HTTPError as e:
        return e.code, e.reason
    except URLError as e:
        if isinstance(e.reason, socket.timeout):
            return 408, None
        else:
            return e.reason.errno, e.reason.strerror

def DELETE(uri, post_data={}, http_headers= None, time_out= 1):
    try:
        req= None
        if post_data:
            m_params_data_str= serializePostData(post_data, isBytes= False)
            if uri.find('?')>-1:
                uri+="&"+ m_params_data_str
            else:
                uri+="?"+ m_params_data_str
        if http_headers:
            req= request.Request(uri, headers= http_headers, method= u'DELETE')
        else:
            req= request.Request(uri, method= u'DELETE')
        with request.urlopen(req, timeout= time_out) as response:
            return response.getcode(),response.read()
    except HTTPError as e:
        return e.code, e.reason
    except URLError as e:
        if isinstance(e.reason, socket.timeout):
            return 408, None
        else:
            return e.reason, None

def PUT(uri, post_data:bytes, http_headers= None, time_out= 1, charset= 'UTF-8'):
    try:
        req= None
        if post_data:
            post_data= serializePostData(post_data)
        if http_headers:
            req= request.Request(uri, data= post_data, headers= http_headers, method= u'PUT')
        else:
            req= request.Request(uri, data= post_data, method= u'PUT')
        with request.urlopen(req, timeout= time_out) as response:
            return response.getcode(),response.read()
    except HTTPError as e:
        return e.code, e.reason
    except URLError as e:
        if isinstance(e.reason, socket.timeout):
            return 408, None
        else:
            return e.reason, None