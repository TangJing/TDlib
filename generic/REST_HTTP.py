import urllib
from urllib import request
from urllib.error import HTTPError

def GET(uri:str, http_headers:dict= None, time_out:int= 1):
    """
    http GET method
    
    - Parameters:
        uri: an uri, it can be an domain or ip, type must is cls<str>.
        http_headers: set request's headers, default is None.
        time_out: time out for access remote uri , default value is 1 seconds.

    - Returs:
        stauts, body

        example: 
            
            200, <html><body>this is an example</body></html>
    """
    try:
        req= None
        if http_headers:
            req= request.Request(uri, headers= http_headers, method= 'GET')
        else:
            req= request.Request(uri, method= 'GET')
        with request.urlopen(req,timeout= time_out) as response:
            return response.getcode(),response.read()
    except Exception as e:
        return 500, repr(e)

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
        if http_headers:
            req= request.Request(uri, data= post_data, headers= http_headers, method= 'POST')
        else:
            req= request.Request(uri, data= post_data, method= 'POST')
        with request.urlopen(req, timeout= time_out) as response:
            return response.getcode(),response.read()
    except urllib.error.URLError as e:
        return 500, repr(e)