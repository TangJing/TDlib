from TDhelper.document.excel.meta.modelMeta import modelMeta
class model(metaclass=modelMeta):
    __excelHandle__= None
    __sheetHandle__= None
    def __init__(self, excelPath= None):
        if excelPath:
            self.Meta.file= excelPath
        if self.Meta.file:
            self.__initExcelHandle__()

    def __initExcelHandle__(self):
        return None

    def __enter__(self):
        return self

    def readLine(self, lineOffset=1):
        return True

    def close(self):
        return None
    
    class Meta:
        file= ''
        sheet= 'sheet1'
        extension= 'xlsx'