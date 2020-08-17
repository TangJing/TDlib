from multiprocessing import Process, Lock
from threading import Thread
import queue
import copy


class threadPools:
    def __init__(self, threadfunc, daemon=True, isJoin=False, maxSize=10):
        self.Daemon = daemon
        self.isJoin = isJoin
        self._processFlag = True
        self._threadLockArgs = Lock()
        self._threadLockThreadFunc = Lock()
        self._threadLockThreadFunc = Lock()
        self._activeThread = {}
        self._list = queue.Queue(maxSize)
        self._args = []
        for offset in range(0, maxSize):
            self._list.put((offset, threadfunc))

    def stop(self):
        self._processFlag = False

    def restart(self):
        self._processFlag = True

    def pushArgs(self, param: any):
        self._threadLockArgs.acquire()
        self._args.append(param)
        self._threadLockArgs.release()
        self.popThread()

    def popArgs(self):
        value = None
        self._threadLockArgs.acquire()
        if len(self._args) > 0:
            value = self._args[0]
            del self._args[0]
        self._threadLockArgs.release()
        return value

    def getArgsLength(self):
        value = 0
        self._threadLockArgs.acquire()
        value = len(self._args)
        self._threadLockArgs.release()
        return value

    def popThread(self):
        try:
            if not self._list.empty():
                self._threadLockThreadFunc.acquire()
                m_thread = self._list.get()
                self._threadLockThreadFunc.release()
                if m_thread:
                    self._activeThread[m_thread[0]] = m_thread[1]
                    m_args = self.popArgs()
                    if m_args:
                        m_thread = Thread(target=self._activeThread[m_thread[0]], name='Thread%s' % str(
                            m_thread[0]), args=(self, m_thread[0], m_args,))
                        m_thread.setDaemon = self.Daemon
                        m_thread.start()
                        if self.isJoin:
                            m_thread.join()
                    else:
                        self.threadComplete(m_thread[0])
                else:
                    raise Exception('thread func is none.')
        except Exception as e:
            raise e

    def pushThread(self, m_thread: tuple):
        if not self._list.full():
            self._threadLockThreadFunc.acquire()
            self._list.put(m_thread)
            self._threadLockThreadFunc.release()
            if self.getArgsLength() > 0:
                self.popThread()
        else:
            raise Exception('thread pools is full.')

    def threadComplete(self, offset):
        m_thread = (offset, self._activeThread.pop(offset))
        self.pushThread(m_thread)



