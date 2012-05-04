import threading
import time
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

import core.cons as cons
from core.events import events
from core.config import config_parser
from core.idle_queue import register_event, remove_event, idle_add

from qt.addons import AddonCore

from preferences_gui import Preferences
from unrar_gui import UnRARGUI
from passwords_handler import passwords_handler #init singleton


#Config parser
OPTION_UNRAR_ACTIVE = "unrar_active"


class Addon(AddonCore):
    """"""
    def __init__(self, parent, *args, **kwargs):
        """"""
        AddonCore.__init__(self)
        self.name = _("Auto Extraction")
        self.event_id = None
        self.parent = parent
        self.unrar_gui = UnRARGUI(parent)
        events.connect(cons.EVENT_PASSWORD, passwords_handler.add)
        #self.ip_renewer_cls = IPRenewer()

    def get_preferences(self):
        """"""
        return Preferences()

    def save(self):
        """"""
        passwords_handler.save()

    def set_menu_item(self):
        self.action = self.parent.menu.addAction(self.name, self.on_toggle) #can toggle
        self.action.setCheckable(True)
        if config_parser.get_addon_option(OPTION_UNRAR_ACTIVE, default=False, is_bool=True):
            self.action.setChecked(True)
            self.connect()

    def on_toggle(self):
        if self.action.isChecked(): #se activo
            config_parser.set_addon_option(OPTION_UNRAR_ACTIVE, "True")
            self.connect()
        else:
            config_parser.set_addon_option(OPTION_UNRAR_ACTIVE, "False")
            events.disconnect(cons.EVENT_DL_COMPLETE, self.event_id)
    
    def connect(self):
        """"""
        self.event_id = events.connect(cons.EVENT_DL_COMPLETE, self.trigger)
    
    def trigger(self, download_item, *args, **kwargs):
        """"""
        self.unrar_gui.add_file(download_item)
