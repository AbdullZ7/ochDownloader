from PySide.QtGui import *
from PySide.QtCore import *

from core import idle_queue


class ThreadDispacher(QThread):
    def __init__(self, parent):
        QThread.__init__(self)
        self.parent = parent
        self.stop_flag = False

    def run(self):
        while True:
            callback = idle_queue.idle_loop.get()
            if self.stop_flag:
                break
            else:
                QApplication.postEvent(self.parent, _Event(callback))

    def stop(self):
        self.stop_flag = True
        idle_queue.idle_add(None)
        self.wait()


class _Event(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, callback):
        #thread-safe
        QEvent.__init__(self, _Event.EVENT_TYPE)
        self.callback = callback