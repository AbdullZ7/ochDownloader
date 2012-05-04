import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

import pygtk
import gtk
import gobject

from core.config import config_parser
from core.events import events
import core.cons as cons

from gui.addons_gui import AddonCore

from shutdown_gui import ShutdownDlg


RETRIES_LIMIT = 0


class Addon(AddonCore):
    """"""
    def __init__(self, parent, *args, **kwargs):
        """"""
        AddonCore.__init__(self)
        self.event_id = None
        self.parent = parent
        self.config = config_parser
        self.old_retries_count = self.config.get_retries_limit()
        if self.old_retries_count == RETRIES_LIMIT:
            self.config.set_retries_limit(str(99))
            self.old_retries_count = 99
    
    def get_menu_item(self):
        return (gtk.CheckMenuItem(), _("Shutdown"), self.on_shutdown) #can toggle
    
    def on_shutdown(self, widget):
        if widget.get_active(): #se activo
            #self.config.set_shutdown_active("True")
            self.event_id = events.connect(cons.EVENT_ALL_COMPLETE, self.trigger)
            self.config.set_retries_limit(str(RETRIES_LIMIT))
        else:
            #self.config.set_shutdown_active("False")
            events.disconnect(cons.EVENT_ALL_COMPLETE, self.event_id)
            self.config.set_retries_limit(str(self.old_retries_count))
    
    def trigger(self, *args, **kwargs):
        """"""
        shutdown_dlg = ShutdownDlg(self.parent)


