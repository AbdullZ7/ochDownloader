import weakref

from PySide.QtGui import *
from PySide.QtCore import *

from core.dispatch.idle_queue import idle_loop


class ThreadDispatcher(QThread):
    def __init__(self, parent):
        QThread.__init__(self)
        self.weak_parent = weakref.ref(parent)

    @property
    def parent(self):
        return self.weak_parent()

    def run(self):
        while True:
            callback = idle_loop.get()
            if callback is None:
                break
            QApplication.postEvent(self.parent, _Event(callback))

    def stop(self):
        idle_loop.put(None)
        self.wait()


class _Event(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, callback):
        #thread-safe
        QEvent.__init__(self, _Event.EVENT_TYPE)
        self.callback = callback