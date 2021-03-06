from enum import Enum

class STATUS(Enum):
    '''
        HTTP状态
    '''
    HTTP_SUCCESS= 200
    HTTP_BAD_REQUEST= 400
    HTTP_NOT_FOUND= 404
    HTTP_REQUEST_TIME= 408
    HTTP_UNAVAILABLE_FOR_LEGAL_REASONS= 451
    HTTP_INTERNAL_SERVER_ERROR= 500
    HTTP_BAD_GATEWAY=502
    HTTP_SERVICE_UNAVAILABLE= 503
    HTTP_GATEWAY_TIME_OUT= 504

    '''
        REQUEST对象错误
    '''
    REQUEST_CONNECT_ERROR= 10001
    REQUEST_REQUEST_RECONNECT_EXCEED_LIMIT_MAX= 10002
    REQUEST_ERROR= 10003
    REQUEST_URL_IS_NONE= 10004
    REQUEST_IS_NONE= 10005
    '''
        SPIDER错误
    '''

    SPIDER_SUCCESS= 20000
    # 配置文件未加载
    SPIDER_CONFIG_IS_NOT_LOAD= 20001
    # 找不到配置文件对应的KEY
    SPIDER_CONFIG_CAN_NOT_FOUND_KEY= 20002
    # 无法获取页面类型
    SPIDER_PAGE_TYPE_NOT_FOUND= 20003
    # 内容未变更
    SPIDER_FINGERPRINT_IS_REPEAT= 20004
    # 按规则未匹配到内容
    SPIDER_REGAULE_MATCH_IS_ERROR= 20005
    # 截取内容错误
    SPIDER_INTERCEPT_ERROR= 20006
    # 找不到页面的分析规则
    SPIDER_PAGE_ANALYSIS_RULES_CAN_NOT_FOUND= 20007
    # 页面过滤出出错
    SPIDER_PAGE_FILTER_ERROR= 20008
    # 页面分析过滤出错
    SPIDER_PAGE_ANALYSIS_FILTER_FAIL= 20009
    # 页面分析ACTION错误
    SPIDER_PAGE_ANALYSIS_ACTIONS_ERROR= 20010
    # 页面分析失败
    SPIDER_PAGE_ANALYSIS_ACTION_FAIL= 20011
    # 序列化数据出错
    SPIDER_SERIALIZE_ERROR= 20012
    # 序列化数据校验失败
    SPIDER_SERIALIZE_DATA_VERIFY_FAIL= 20013
    # 跳过爬取
    SPIDER_EXCLUDE= 20014

    #CONFIG 状态
    CONFIG_SUCCESS= 30000
    CONFIG_ERROR= 30001
    # 错误
    SPIDER_ERROR= -1