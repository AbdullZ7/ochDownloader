import logging
logger = logging.getLogger(__name__)

from core import events
from core.config import conf

from qt import signals as qt_signals
from qt.addons import AddonCore

import signals
from .preferences_gui import Preferences
from .unrar_gui import UnRARGUI
from .passwords_handler import passwords_handler


#Config parser
OPTION_UNRAR_ACTIVE = "unrar_active"


class Addon(AddonCore):
    """"""
    def __init__(self, parent, *args, **kwargs):
        """"""
        # TODO: add preference choice to extract on all_dl_complete or just dl_complete
        AddonCore.__init__(self, parent)
        self.name = _("Auto extraction")
        self.unrar_gui = UnRARGUI(parent)
        qt_signals.add_password.connect(passwords_handler.add)
        #self.ip_renewer_cls = IPRenewer()

    def get_preferences(self):
        """"""
        return Preferences()

    def set_menu_item(self):
        self.action = self.parent.menu.addAction(self.name, self.on_toggle)  # can toggle
        self.action.setCheckable(True)
        if conf.get_addon_option(OPTION_UNRAR_ACTIVE, default=False, is_bool=True):
            self.action.setChecked(True)
            self.connect()

    def on_toggle(self):
        if self.action.isChecked():  # se activo
            conf.set_addon_option(OPTION_UNRAR_ACTIVE, "True")
            self.connect()
        else:
            conf.set_addon_option(OPTION_UNRAR_ACTIVE, "False")
            self.disconnect()
    
    def connect(self):
        """"""
        events.download_complete.connect(self.trigger)
        signals.unrar_file.connect(self.trigger)

    def disconnect(self):
        events.download_complete.disconnect(self.trigger)
        signals.unrar_file.disconnect(self.trigger)
    
    def trigger(self, download_item, *args, **kwargs):
        """"""
        self.unrar_gui.add_file(download_item)
