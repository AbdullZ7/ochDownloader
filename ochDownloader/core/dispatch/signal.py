import threading
import logging

from core.dispatch import idle
from .weak_ref import weak_ref

logger = logging.getLogger(__name__)


class Signal:

    def __init__(self):
        self.callbacks = []
        self.lock = threading.Lock()

    def connect(self, callback):
        with self.lock:
            callback = weak_ref(callback)
            self.callbacks.append(callback)

    def disconnect(self, callback):
        with self.lock:
            for index, weakref_callback in enumerate(self.callbacks):
                if callback == weakref_callback():
                    del self.callbacks[index]
                    break

    def emit(self, *args, **kwargs):
        with self.lock:
            for weakref_callback in self.callbacks[:]:
                callback = weakref_callback()

                if callback is not None:
                    idle.add(callback, *args, **kwargs)
                else:  # lost reference
                    self.callbacks.remove(weakref_callback)