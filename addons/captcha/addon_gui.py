import logging
logger = logging.getLogger(__name__)

from core import events

from qt.addons import AddonCore

from captcha_gui import CaptchaDialog


class Addon(AddonCore):
    """"""
    def __init__(self, parent, *args, **kwargs):
        """"""
        AddonCore.__init__(self, parent)
        self.connect()
    
    def set_menu_item(self):
        """"""
        pass
    
    def connect(self):
        """"""
        events.captcha_dialog.connect(self.trigger) #connect event
    
    #def disconnect(self):
        #""""""
        #events.disconnect(cons.EVENT_CAPTCHA_DLG, self.event_id)
    
    def trigger(self, *args, **kwargs):
        self.captcha(*args, **kwargs)
    
    def captcha(self, host, challenge, set_solution, *args, **kwargs):
        dialog = CaptchaDialog(host, challenge, self.parent)
        set_solution(dialog.solution)

