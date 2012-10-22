import threading
import weakref
import logging
logger = logging.getLogger(__name__)

from core import idle_queue


class _BoundMethodWeakref:
    def __init__(self, func):
        self.func_name = func.__name__
        self.wref = weakref.ref(func.__self__) #__self__ returns the class http://docs.python.org/reference/datamodel.html

    def __call__(self):
        func_cls = self.wref()
        if func_cls is None: #lost reference
            return None
        else:
            func = getattr(func_cls, self.func_name)
            return func

    def __cmp__(self, other):
        func = self.__call__()
        return cmp(func, other)

def weak_ref(callback):
    if hasattr(callback, '__self__') and callback.__self__ is not None: #is a bound method?
        return _BoundMethodWeakref(callback)
    else:
        return weakref.ref(callback)


class Event:
    def __init__(self, name):
        self.name = name
        self.callbacks = []
        self.lock = threading.Lock()

    def connect(self, callback):
        with self.lock:
            callback = weak_ref(callback)
            self.callbacks.append(callback)

    def disconnect(self, callback):
        with self.lock:
            self.callbacks.remove(callback)

    def emit(self, *args, **kwargs):
        with self.lock:
            callbacks = self.callbacks[:]

        if not callbacks:
            logger.debug("No signals assosiated to: {}".format(self.name))
        else:
            #connected_methods = [callback.__name__ for callback in self.callbacks]
            logger.debug("Event emitted: {}".format(self.name))

        for weakref_callback in callbacks:
            callback = weakref_callback()
            if callback is not None:
                idle_queue.idle_add(callback, *args, **kwargs)
            else:
                self.disconnect(callback) #callback = None


class Signals:
    switch_tab = Event('switch_tab')
    store_items = Event('store_items')
    add_downloads_to_check = Event('add_downloads_to_check')
    on_stop_all = Event('on_stop_all')
    status_bar_pop_msg = Event('status_bar_pop_msg')
    status_bar_push_msg = Event('status_bar_push_msg')
    captured_links_count = Event('captured_links_count')

signals = Signals()