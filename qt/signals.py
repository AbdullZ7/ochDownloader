import threading
import logging
logger = logging.getLogger(__name__)

from core import idle_queue


class Event:
    def __init__(self, name=None):
        self.name = name
        self.callbacks = []
        self.lock = threading.Lock()

    def connect(self, callback):
        with self.lock:
            self.callbacks.append(callback)

    def disconnect(self, callback):
        with self.lock:
            self.callbacks.remove(callback)

    def emit(self, *args, **kwargs):
        with self.lock:
            if not self.callbacks:
                logger.debug("No signals assosiated to: {}".format(self.name))
            else:
                #connected_methods = [callback.__name__ for callback in self.callbacks]
                logger.debug("Event emitted: {}".format(self.name))

            for callback in self.callbacks:
                idle_queue.idle_add(callback, *args, **kwargs)


class Signals:
    switch_tab = Event('switch_tab')
    store_items = Event('store_items')
    add_downloads_to_check = Event('add_downloads_to_check')
    on_stop_all = Event('on_stop_all')
    status_bar_pop_msg = Event('status_bar_pop_msg')
    status_bar_push_msg = Event('status_bar_push_msg')
    captured_links_count = Event('captured_links_count')

signals = Signals()