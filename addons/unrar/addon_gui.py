import logging
logger = logging.getLogger(__name__)

import core.cons as cons
from core.events import events
from core.conf_parser import conf

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
        self.name = _("Auto extraction")
        self.parent = parent
        self.unrar_gui = UnRARGUI(parent)
        events.add_password.connect(passwords_handler.add)
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
        if conf.get_addon_option(OPTION_UNRAR_ACTIVE, default=False, is_bool=True):
            self.action.setChecked(True)
            self.connect()

    def on_toggle(self):
        if self.action.isChecked(): #se activo
            conf.set_addon_option(OPTION_UNRAR_ACTIVE, "True")
            self.connect()
        else:
            conf.set_addon_option(OPTION_UNRAR_ACTIVE, "False")
            events.download_complete.disconnect(self.trigger)
    
    def connect(self):
        """"""
        events.download_complete.connect(self.trigger)
    
    def trigger(self, download_item, *args, **kwargs):
        """"""
        self.unrar_gui.add_file(download_item)
