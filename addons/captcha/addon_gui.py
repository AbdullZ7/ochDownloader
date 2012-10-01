import logging
logger = logging.getLogger(__name__)

from core.events import events
import core.cons as cons

from qt.addons import AddonCore

from captcha_gui import CaptchaDialog


class Addon(AddonCore):
    """"""
    def __init__(self, parent, *args, **kwargs):
        """"""
        AddonCore.__init__(self)
        self.event_id = None
        self.parent = parent
        self.connect()
    
    def set_menu_item(self):
        """"""
        pass
    
    def connect(self):
        """"""
        self.event_id = events.connect(cons.EVENT_CAPTCHA_DLG, self.trigger) #connect event
    
    #def disconnect(self):
        #""""""
        #events.disconnect(cons.EVENT_CAPTCHA_DLG, self.event_id)
    
    def trigger(self, *args, **kwargs):
        self.captcha(*args, **kwargs)
    
    def captcha(self, service, get_captcha_img, set_solution, *args, **kwargs):
        captcha_dlg = CaptchaDialog(service, get_captcha_img, self.parent)
        solution = captcha_dlg.get_solution() #user input solution
        set_solution(solution)

