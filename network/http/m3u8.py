#!/usr/bin/env python3.6
# -*- encoding: utf-8 -*-
'''
@File    :   m3u8.py
@Time    :   2020/04/23 10:12:13
@Author  :   Tang Jing
@Version :   1.0.0
@Contact :   yeihizhi@163.com
@License :   (C)Copyright 2020
@Desc    :   None
'''

# here put the import lib
import re
import os
import io
from threading import Thread
from threading import Lock
from threading import Event as ThreadEvent
from urllib.parse import urlparse
from io import StringIO, BytesIO
from TDlib.Cache.pools import pools
from TDlib.network.http.http_helper import m_http
from TDlib.network.http.status.M3U8_STATUS import M3U8_STATUS
# code start
m3u8Cfg = {
    "cfg": {
            'timeout': 5,
            'reconnect': 3
        },
    "tmpfolder": "tmp",
        "download-poolsize": 20
}


class m3u8:
    def __init__(self, setting=None):
        '''
        params:
            setting: meu8Cfg(dict)
        '''
        if not setting:
            setting = m3u8Cfg
        try:
            self._http = m_http()
            # requests 连接失败重连次数
            self._reconnect = setting['cfg']['reconnect']
            # requests超时时间
            self._timeout = setting['cfg']['timeout']
            # 临时文件夹
            self._tmp_folder = setting['tmpfolder']
            # 下载文件线程池配置
            self._lock__ = Lock()  # 线程锁
            self._event__ = ThreadEvent()  # 线程事件
            self._download_thread_active_ = 0  # 下载线程活跃数,用于判断文件是否下载完成.
            self._downlaod_buffer_length = 0  # 下载缓存长度, 用于计算快偏移量
            self._download_pool_size = setting['download-poolsize']
            self._download_pool = pools(
                self._download_pool_size)
            for i in range(0, self._download_pool_size):
                self._download_pool.push(m_http())

            # 检查临时文件夹路径是否完整
            if not re.search(r':\\', self._tmp_folder, re.I | re.M):
                self._tmp_folder = os.path.join(os.getcwd(), self._tmp_folder)
            self._stream = None  # 最终文件句柄
            self._ts_tmp_stream = None  # TS缓存文件句柄
            # 建立TS临时文件
            self._ts_tmp_stream = open(os.path.join(
                self._tmp_folder, 'tmp.ts'), mode="wb")

            # 建立播放临时文件
            self._stream = self.__tmp_stream__()

            # M3U8 TAGS
            self._prefix_url = None
            self._EXT_X_TARGETDURATION__ = None
            self._EXTINF__ = []
            self._EXT_X_VERSION__ = None
            self._EXT_X_BYTERANGE__ = None
            self._EXT_X_KEY__ = None
            self._EXT_X_MAP__ = None
            self._EXT_X_PROGRAM_DATE_TIME__ = None
            self._EXT_X_DATERANGE__ = None
            self._EXT_X_MEDIA_SEQUENCE__ = None
            self._EXT_X_DISCONTINUITY_SEQUENCE__ = None
            self._EXT_X_PLAYLIST_TYPE__ = None
            self._EXT_X_MEDIA__ = None
            self._EXT_X_STREAM_INF__ = None
            self._EXT_X_I_FRAME_STREAM_INF__ = None
            self._EXT_X_SESSION_DATA__ = None
            self._EXT_X_SESSION_KEY__ = None
            self._EXT_X_START__ = None
            self._EXT_X_DISCONTINUITY__ = None
            self._EXT_X_ENDLIST__ = None
            self._EXT_X_I_FRAMES_ONLY__ = None
            self._EXT_X_INDEPENDENT_SEGMENTS__ = None

            # 自己定义M3U8 处理属性
            self._EXT_X_M3U8_FILE_LIST__ = []  # 直播类有主m3u8有多个m3u8文件地址
            self._EXT_X_M3U8_PLAY_LIST__ = []  # m3u8播放列表TS文件列表
            self._EXT_X_M3U8_PLAY_LIST_INDEX__ = 0  # m3u8播放列表TS文件列表索引

        except Exception as e:
            raise e

    def get(self, m3u8_path):
        # setattr(self, )
        if m3u8_path:
            self._EXTINF__ = []
            self._EXT_X_STREAM_INF__ = None
            ret, status = self.__download_m3u8_files(m3u8_path)
            if status == M3U8_STATUS.GET_M3U8_PLAYLIST:
                self.__download_m3u8_files(ret)
            return ret, status
        else:
            return "url为空, 请设置m3u8地址.", M3U8_STATUS.ERROR

    def __download_m3u8_files(self, m3u8_path):
        m_index = 0
        self._prefix_url = m3u8_path.rsplit('/', 1)[0]
        while True:
            response, status = self.__request__(m3u8_path)
            if status == 200:
                self.__analysis__(response)
                if self._EXT_X_STREAM_INF__:
                    self._EXT_X_STREAM_INF__= None # 重置STREAM_INF属性
                    # 下载正式M3U8.
                    for m3_file in self._EXT_X_M3U8_FILE_LIST__:
                        if not re.match(r"^(http|https)://", m3_file, re.I | re.M):
                            # 接接m3u8下载地址.
                            m3_file = self._prefix_url + "/" + m3_file
                            return m3_file, M3U8_STATUS.GET_M3U8_PLAYLIST
                else:
                    if self._EXT_X_KEY__:
                        # 获取文件密钥
                        pass
                    # 下载TS文件.(还需要解决主播多M3U8文件下载文件辨别问题)
                    # self._EXT_X_M3U8_PLAY_LIST_INDEX__ = 0
                    # self._ts_tmp_stream = None
                    for item in self._EXTINF__:
                        m_file = item.split(',')[1]
                        if not re.match(r"^(http|https)://", m_file, re.I | re.M):
                            m_file = self._prefix_url + '/' + m_file
                        m_download_struct = {
                            'index': m_index, 'url': m_file, 'offset': None}
                        self._EXT_X_M3U8_PLAY_LIST__.append(m_download_struct)
                        m_index += 1
                    self.__download__()
                    if not self._EXT_X_ENDLIST__:
                        continue
                return "success.", M3U8_STATUS.SUCCESS
            else:
                return "m3u8 download error.", M3U8_STATUS.ERROR

    def __request__(self, url):
        if self._http:
            try:
                response, status = self._http.getcontent(
                    url, p_timeout=self._timeout)
                if status == 200:
                    return response, status
                else:
                    for i in range(0, self._reconnect):
                        response, status = self._http.getcontent(
                            url, p_timeout=self._timeout)
                        if status == 200:
                            return response, status
                    if i >= self._reconnect:
                        return 'timeout', 408
            except Exception as e:
                return e, -1

    def __download__(self):
        if not self._download_thread_active_ >= self._download_pool_size:
            for i in range(0, self._download_pool_size):
                Thread(target=self.__download_thread__).start()
            Thread(target=self.__create_merge_file).start()

    def __download_thread__(self):
        self._lock__.acquire()
        self._download_thread_active_ += 1
        self._lock__.release()
        m_http_control = None
        m_http_control = self._download_pool.pop()
        if m_http_control:
            while True:
                ts_struct = None
                self._lock__.acquire()
                # 从播放列表取TS文件地址
                if self._EXT_X_M3U8_PLAY_LIST_INDEX__ < len(self._EXT_X_M3U8_PLAY_LIST__):
                    ts_struct = self._EXT_X_M3U8_PLAY_LIST__[
                        self._EXT_X_M3U8_PLAY_LIST_INDEX__]
                    self._EXT_X_M3U8_PLAY_LIST_INDEX__ += 1
                else:
                    # 下载完毕跳出下载线程
                    self._download_thread_active_ -= 1
                    if self._download_thread_active_ == 0:
                        pass
                        # self._ts_tmp_stream.close()
                        # self._ts_tmp_stream = None
                    self._download_pool.push(m_http_control)
                    self._lock__.release()
                    break
                self._lock__.release()
                if ts_struct:
                    print('download:{0}'.format(ts_struct['url']))
                    file_bytes, status = m_http_control.download(
                        ts_struct['url'])
                    if status != 200:
                        i = 0
                        while True:
                            file_bytes, status = m_http_control.download(
                                ts_struct['url'])
                            if status == 200:
                                break
                    self._lock__.acquire()
                    ts_struct['offset'] = (
                        self._downlaod_buffer_length, len(file_bytes))
                    self._downlaod_buffer_length += len(file_bytes)
                    self._lock__.release()
                    self._EXT_X_M3U8_PLAY_LIST__[
                        ts_struct['index']] = ts_struct
                    tmp_file_name = ts_struct['url'].rsplit('/', 1)[1]
                    self._ts_tmp_stream.write(file_bytes)
                    self._ts_tmp_stream.flush()
                    self._event__.set()

    def __create_merge_file(self):
        i = 0
        with open(os.path.join(
                self._tmp_folder, 'tmp.ts'), mode="rb") as fd:
            while True:
                if i >= len(self._EXT_X_M3U8_PLAY_LIST__):
                    break
                if self._EXT_X_M3U8_PLAY_LIST__[i]['offset']:
                    fd.seek(self._EXT_X_M3U8_PLAY_LIST__[i]['offset'][0])
                    self._stream.write(
                        fd.read(self._EXT_X_M3U8_PLAY_LIST__[i]['offset'][1]))
                    self._stream.flush()
                    i += 1
                else:
                    self._event__.clear()
                    self._event__.wait()
            fd.close()
        self._stream.close()
        self._ts_tmp_stream.close()

    def __tmp_stream__(self):
        # 缓存文件对象
        try:
            if not os.path.exists(self._tmp_folder):
                os.mkdir(self._tmp_folder)
            # 仅是改了扩展名，可以让播放器识别.并没有将视频编码更改为MP4
            return open(os.path.join(self._tmp_folder, 'tmp.mp4'), mode="wb")
        except:
            raise Exception("缓存文件初始化.")

    def __analysis__(self, content):
        # 分析M3U8文件
        m_result = self.__match__(r"^#EXTM3U", content)
        if m_result:
            content = re.sub(r",(\r\n|\r|\n)", ",", content, count=0, flags=0)
            for line in StringIO(content):
                self.__m3u8_attr__(line)
        else:
            return '', M3U8_STATUS.TYPE_ERROR

    def __m3u8_attr__(self, content):
        '''
            设置M3U8 TAG值
        '''
        content = re.sub(r"^\r\n|\r|\n", "", content, count=0, flags=0)
        m_result = re.match(r"^#.*", content)
        if m_result:
            m_data = content.split(":", 1)
            m_key = None
            if len(m_data) == 2:
                m_key = m_data[0]
            else:
                m_key = content
            m_key += "__"
            m_key = re.sub(r"#|-", "_", m_key, count=0, flags=0)
            m_key = m_key.replace(" ", "")
            if len(m_data) == 2:
                if m_key == "_EXTINF__":
                    self._EXTINF__.append(m_data[1])
                else:
                    self.__setattr__(m_key, m_data[1])
            else:
                self.__setattr__(m_key, True)
        else:
            if re.search(r"\.m3u8", content):
                self._EXT_X_M3U8_FILE_LIST__.append(content)

    def __match__(self, regex, content):
        m_result = re.match(regex, content, re.I | re.M)
        if m_result:
            return True
        return False
