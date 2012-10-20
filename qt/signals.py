import threading
import logging
logger = logging.getLogger(__name__)

from core import idle_queue


class Event:
    def __init__(self, name=None):
        self.name = name
        self.callbacks = []

    def connect(self, callback):
        self.callbacks.append(callback)

    def disconnect(self, callback):
        self.callbacks.remove(callback)

    def emit(self, *args, **kwargs):
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