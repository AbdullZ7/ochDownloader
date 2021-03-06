import logging
logger = logging.getLogger(__name__)

from core.config import conf
from core import events

from qt.addons import AddonCore

from shutdown_gui import ShutdownDialog


RETRIES_LIMIT = 0


class Addon(AddonCore):
    """"""
    def __init__(self, parent, *args, **kwargs):
        """"""
        AddonCore.__init__(self, parent)
        self.name = _("Shutdown")
        self.old_retries_count = conf.get_retries_limit()
        if self.old_retries_count == RETRIES_LIMIT:
            conf.set_retries_limit(str(99))
            self.old_retries_count = 99
    
    def set_menu_item(self):
        self.action = self.parent.menu.addAction(self.name, self.on_toggle) #can toggle
        self.action.setCheckable(True)
    
    def on_toggle(self):
        if self.action.isChecked(): #se activo
            #self.config.set_shutdown_active("True")
            events.all_downloads_complete.connect(self.trigger)
            conf.set_retries_limit(str(RETRIES_LIMIT))
        else:
            #self.config.set_shutdown_active("False")
            events.all_downloads_complete.disconnect(self.trigger)
            conf.set_retries_limit(str(self.old_retries_count))
    
    def trigger(self, *args, **kwargs):
        """"""
        ShutdownDialog(self.parent)
