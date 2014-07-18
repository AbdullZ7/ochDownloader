import logging
import threading

from .weak_ref import weak_ref

logger = logging.getLogger(__name__)


class Signal:

    def __init__(self):
        self.callbacks = []

    def connect(self, callback):
        assert threading.current_thread().name == 'MainThread'

        callback = weak_ref(callback)
        self.callbacks.append(callback)

    def disconnect(self, callback):
        assert threading.current_thread().name == 'MainThread'

        for index, weakref_callback in enumerate(self.callbacks):
            if callback == weakref_callback():
                del self.callbacks[index]
                break

    def emit(self, *args, **kwargs):
        assert threading.current_thread().name == 'MainThread'

        for weakref_callback in self.callbacks[:]:
            callback = weakref_callback()

            if callback is not None:
                callback(*args, **kwargs)
            else:  # lost reference
                self.callbacks.remove(weakref_callback)