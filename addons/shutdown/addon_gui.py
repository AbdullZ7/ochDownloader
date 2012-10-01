import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

from core.conf_parser import conf
from core.events import events
import core.cons as cons

from qt.addons import AddonCore

from shutdown_gui import ShutdownDialog


RETRIES_LIMIT = 0


class Addon(AddonCore):
    """"""
    def __init__(self, parent, *args, **kwargs):
        """"""
        AddonCore.__init__(self)
        self.name = _("Shutdown")
        self.event_id = None
        self.parent = parent
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
            self.event_id = events.connect(cons.EVENT_ALL_COMPLETE, self.trigger)
            conf.set_retries_limit(str(RETRIES_LIMIT))
        else:
            #self.config.set_shutdown_active("False")
            events.disconnect(cons.EVENT_ALL_COMPLETE, self.event_id)
            conf.set_retries_limit(str(self.old_retries_count))
    
    def trigger(self, *args, **kwargs):
        """"""
        ShutdownDialog(self.parent)
