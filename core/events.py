import threading
import logging
logger = logging.getLogger(__name__)

import cons
from idle_queue import idle_add

#thread safety
_thread_lock = threading.Lock()


class _Events:
    """
    Observer pattern
    """
    def __init__(self):
        self.events_dict = {} #{event: {signal_id: (mtd_emit, args), }, } emit signals.
        self.id_count = 0
        logger.debug("events instanced.")
    
    def connect(self, event_name, callback, *args): #callback = emit method.
        with _thread_lock:
            event_values = self.events_dict.get(event_name, {}) #get values, if name doesnt exists return a dict.
            event_values[self.id_count] = (callback, args)
            self.events_dict[event_name] = event_values
            return_id = self.id_count
            self.id_count += 1
        return return_id
    
    def disconnect(self, event_name, event_id):
        try:
            with _thread_lock:
                event_values = self.events_dict[event_name]
                del event_values[event_id] #binding
        except KeyError as err:
            logger.exception(err)
    
    def trigger(self, event_name, *args):
        try:
            with _thread_lock:
                event_values = self.events_dict[event_name].values()
        except KeyError as err:
            logger.debug("No signals assosiated with: {0}".format(err))
        else:
            logger.debug("Event triggered: {0}".format(event_name))
            for callback, args2 in event_values:
                idle_add(callback, *(args + args2)) #call in the main thread.
    
    def trigger_captcha_dialog(self, service, get_captcha_img, set_solution):
        self.trigger(cons.EVENT_CAPTCHA_DLG, service, get_captcha_img, set_solution)
    
    def trigger_download_complete(self, download_item):
        self.trigger(cons.EVENT_DL_COMPLETE, download_item)
    
    def trigger_all_downloads_complete(self):
        self.trigger(cons.EVENT_ALL_COMPLETE)
    
    def trigger_quit(self):
        self.trigger(cons.EVENT_QUIT)
    
    def trigger_limit_exceeded(self):
        self.trigger(cons.EVENT_LIMIT_EXCEEDED)
    
    def trigger_pwd(self, pwd):
        self.trigger(cons.EVENT_PASSWORD, pwd)

    def trigger_captured_links_count(self, count):
        self.trigger(cons.EVENT_CAPTURED_LINKS_COUNT, count)

#modules are singletons-like in python :)
events = _Events() #make it global.

