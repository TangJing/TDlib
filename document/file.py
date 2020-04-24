import os

class stream:

    def __init__(self):
        pass

    def openStream(streamPath, *args, **kwargs):
        if self._exsiteFolder(streamPath):
            os.open(streamPath, )

    def _exsiteFolder(streamPath):
        if not os.path.exists(streamPath.rsplit(r'\\',1)[0]):
            try:
                os.mkdir(streamPath)
                return True
            except Exception as e:
                return False
        else:
            return True