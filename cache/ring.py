
import array

#有问题。插入数据没有按环形跑。
#试一下writeoffset 与 readoffset比较
# writeoffset == readoffset 为满
# writeoffset > readoffset 为readoffset后有空
# writeoffset < readoffset 为readoffset前有空
class Ring:
    def __init__(self, size):
        self._maxSize=size  #Array's max size
        self._readOffset=0  #Array's read offset pos
        self._writeOffset=0 #Array's write offseet pos
        self._canWriteMaxSize=self._maxSize   #Can write max size
        self._ringBuffer=[0]*self._maxSize   #Init array
        self._valueCount=0

    '''
        Push value in the array
    '''
    def Push(self,value):
        if self._writeOffset<self._canWriteMaxSize:
            self._ringBuffer[self._writeOffset]=value
            self._valueCount+=1
            self._writeOffset+=1
            if self._writeOffset==self._canWriteMaxSize:
                self._canWriteMaxSize=0 #Set can write max size value is 0
                self._writeOffset=0 #Set write offset is 0
            return True
        return False

    '''
        pop the array's value by offset
    '''
    def Pop(self):
        if self._readOffset<self._maxSize:
            result=self._ringBuffer[self._readOffset]
            if result:
                self._ringBuffer[self._readOffset]=None
                self._valueCount-=1
                self._readOffset+=1
                if self._readOffset>self._writeOffset:
                    self._canWriteMaxSize=self._readOffset
                if self._readOffset==self._maxSize:
                    self._readOffset=0
                return result
        return False

    '''
        clear the array's value 
    '''
    def Clear(self):
        self._ringBuffer=None
        self._readOffset=0
        self._maxSize=0
        self._writeOffset=0
        self._canWriteMaxSize=0
        self._valueCount=0

    