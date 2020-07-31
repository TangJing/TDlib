from TDhelper.document.excel.meta.modelMeta import modelMeta
class model(metaclass=modelMeta):
    def __enter__(self):
        return self

    def readLine(self, lineOffset=1):
        return True

    def close(self):
        return None