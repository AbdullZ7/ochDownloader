import time
import threading
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

from core.idle_queue import idle_add_and_wait
from core.events import events
import core.cons as cons

from qt.addons import AddonCore

from captcha_gui import CaptchaDlg


class Addon(AddonCore):
    """"""
    def __init__(self, parent, *args, **kwargs):
        """"""
        AddonCore.__init__(self)
        self.event_id = None
        self.connect(parent)
        self.lock = threading.Lock()
    
    def set_menu_item(self):
        """"""
        pass
    
    def connect(self, parent):
        """"""
        self.event_id = events.connect(cons.EVENT_CAPTCHA_DLG, self.trigger, parent) #connect event
    
    #def disconnect(self):
        #""""""
        #events.disconnect(cons.EVENT_CAPTCHA_DLG, self.event_id)
    
    def trigger(self, *args, **kwargs):
        th = threading.Thread(group=None, target=self.captcha_thread, name=None, args=args)
        #th.daemon = True #exit even if the thread is alive.
        th.start()
    
    def captcha_thread(self, wait_func, service, get_captcha_img, set_solution, *args):
        """
        TODO: find a better way to wait for event complete.
        """
        with self.lock:
            if not wait_func(): #dl stopped?
                idle_add_and_wait(self.captcha, service, get_captcha_img, set_solution, *args)
            else:
                set_solution() #set event.
    
    def captcha(self, service, get_captcha_img, set_solution, parent, *args):
        captcha_dlg = CaptchaDlg(service, get_captcha_img, parent)
        solution = captcha_dlg.get_solution() #user input solution
        set_solution(solution)

