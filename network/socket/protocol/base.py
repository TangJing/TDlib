from enum import Enum
import enum
import hashlib
import copy


class Protocol:
    def __init__(self, charset='utf-8'):
        self.index = 0  # 包序号
        self.charset = charset  # 数据块编码
        self.dataLength = 0  # 数据块长度
        self.dataMd5 = None  # 数据哈希
        self.data = b''  # 数据

    def decode(self):
        '''
            将封装好的协议包转为bytes数据准备发送
        '''
        m_str = 'T-Protocol:\r'
        for item in self.__dict__:
            m_str += str(self.__dict__[item]) + '\r'
        return bytes(m_str, encoding=self.charset)

    def encode(self, buff: str, index=0, charset='utf-8'):
        '''
            对数据进行协议封装
        '''
        self.data = buff
        m_md5 = hashlib.md5()
        m_md5.update(buff.encode(encoding=charset))
        self.dataMd5 = m_md5.hexdigest()
        self.dataLength = len(self.data)
        self.charset = charset
        self.index = index

    def checkMD5(self):
        m_md5 = hashlib.md5()
        m_md5.update(self.data.encode(encoding=self.charset))
        if self.dataMd5 == m_md5.hexdigest():
            return True
        else:
            return False

    def clear(self):
        self.index = 0  # 包序号
        self.charset = ''  # 数据块编码
        self.dataLength = 0  # 数据块长度
        self.dataMd5 = None  # 数据哈希
        self.data = b''  # 数据


class analysis:
    def __init__(self, protocol: Protocol):
        self._protocol = protocol  # 协议
        self._buff = b''  # 接受缓存
        self._buffOffset = 0  # 数据缓存游标
        self._counter = 0  # 包头计数器
        self.state = ANALYSIS_STATUS.WAIT_RECV_HEADER  # 状态
        self._recvDataLength = 0  # 获取数据长度
        self.RecvPacketList = []  # 已经接收包列表

    def recv(self, buffer: bytes):
        self._buff += buffer
        if self.state == ANALYSIS_STATUS.WAIT_RECV_HEADER:
            self._getHeader()
        elif self.state == ANALYSIS_STATUS.GET_DATA:
            self.__getData()

    def _getHeader(self):
        if len(self._buff) >= 12 and self._buffOffset == 0 and self._protocol.dataLength == 0:
            if bytes.decode(self._buff[0:12], encoding='utf-8') == 'T-Protocol:\r':
                self._buffOffset += len(b'T-Protocol:\r')
            else:
                print(bytes.decode(self._buff[0:12], encoding='utf-8'))
                raise Exception(
                    'protocol header hav''t found T-Protocol field.')
            m_count = 0
            for m_item in self._buff[self._buffOffset:len(self._buff)]:
                if m_item == 13:
                    if self._counter == 0:
                        self._protocol.index = int(bytes.decode(
                            self._buff[self._buffOffset:self._buffOffset+m_count], encoding='utf-8'))
                    elif self._counter == 1:
                        self._protocol.charset = bytes.decode(
                            self._buff[self._buffOffset:self._buffOffset+m_count], encoding='utf-8')
                    elif self._counter == 2:
                        self._protocol.dataLength = int(bytes.decode(
                            self._buff[self._buffOffset:self._buffOffset+m_count], encoding='utf-8'))
                    elif self._counter == 3:
                        self._protocol.dataMd5 = bytes.decode(
                            self._buff[self._buffOffset:self._buffOffset+m_count], encoding='utf-8')
                        self.state = ANALYSIS_STATUS.GET_DATA
                    self._counter += 1
                    self._buffOffset += m_count+1
                    m_count = 0
                    if self.state == ANALYSIS_STATUS.GET_DATA:
                        if len(self._buff) - self._buffOffset > 0:
                            self.__getData()
                        break
                else:
                    m_count += 1
        else:
            pass  # 数据缓存不够包头等待数据

    def __getData(self):
        m_buffLength = len(self._buff)
        if self._recvDataLength < self._protocol.dataLength:
            if m_buffLength >= self._buffOffset + self._protocol.dataLength:
                self._protocol.data += self._buff[self._buffOffset:self._buffOffset+(
                    self._protocol.dataLength-self._recvDataLength)]
                self._buffOffset += self._protocol.dataLength - self._recvDataLength
                self.__getDataComplete()
        else:
            self.__getDataComplete()

    def __getDataComplete(self):
        self.RecvPacketList.append(copy.deepcopy(self._protocol))
        self._protocol.clear()
        self._recvDataLength = 0
        self._buff = self._buff[self._buffOffset+1:len(self._buff)]
        self._buffOffset = 0
        self._counter = 0
        if len(self._buff) > 0:
            self.state = ANALYSIS_STATUS.WAIT_RECV_HEADER
            self._getHeader()
            if self.state != ANALYSIS_STATUS.RECV_COMPLETE:
                self._protocol.clear()
                self._buffOffset = 0
                self._counter = 0
                self._recvDataLength = 0
        self.state = ANALYSIS_STATUS.RECV_COMPLETE

    def getRecvData(self):
        m_ret=[]
        while True:
            m_ret.append(self.RecvPacketList[0])
            del(self.RecvPacketList[0])
            if len(self.RecvPacketList) == 0:
                break
        return m_ret

    def resetState(self):
        self.state= ANALYSIS_STATUS.WAIT_RECV_HEADER

    def getSendBuffer(self):
        return self._protocol.decode()


class ANALYSIS_STATUS(Enum):
    ERROR = 0
    WAIT_RECV_HEADER = 1
    GET_DATA = 2
    RECV_COMPLETE = 3
