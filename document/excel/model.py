from TDhelper.document.excel.meta.modelMeta import modelMeta
class model(metaclass=modelMeta):
    __excelHandle__= None # excel object.
    __sheetHandle__= None # sheet object.
    __rows__= [] # all rows.
    __record_offset__= 1 # data start offset.
    __read_offset__= 0 # now record offset.
    def __init__(self, excelPath= None, record_offset= 1):
        if record_offset<1:
            record_offset=1
        self.__record_offset__= record_offset    
        if excelPath:
            self.Meta.file= excelPath
        if self.Meta.file:
            self.__initExcelHandle__()

    def __initExcelHandle__(self):
        return None

    def __enter__(self):
        return self

    def readLine(self, lineOffset=1):
        '''
            读取一行数据
            - params:
            -   lineOffset: <int>, default 1, 读取的行偏移量.
        '''
        return True
    
    def rows(self):
        '''
            获取表格所有数据.
            - params:
            - return: <arrary>, defautl return [].
        '''
        return []

    def getCount(self):
        '''
            获取总行数
            - return: <int>
        '''
        return 0

    def close(self):
        return None
    
    class Meta:
        '''
            元数据
            - file: <string>, 文件路径.
            - sheet: <string>, sheet名称.
            - extension: <string>, 文件类型(xlsx,csv)
        '''
        file= ''
        sheet= 'sheet1'
        extension= 'xlsx'