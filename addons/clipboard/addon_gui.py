import logging #registro de errores, van a consola y al fichero de texto.
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

import core.cons as cons
from core.config import conf

from qt.addons import AddonCore
from clipboard_gui import Clipboard
from preferences_gui import Preferences


class Addon(AddonCore):
    """"""
    def __init__(self, parent, *args, **kwargs):
        """"""
        AddonCore.__init__(self, parent)
        self.name = _("Clipboard")
        self.clipboard_monitor = Clipboard()
    
    def set_menu_item(self):
        self.action = self.parent.menu.addAction(_("Clipboard watcher"), self.on_toggle) #can toggle
        self.action.setCheckable(True)
        if conf.get_clipboard_active():
            self.action.setChecked(True)
            self.clipboard_monitor.enable()

    def get_preferences(self):
        """"""
        return Preferences()
    
    def on_toggle(self):
        if self.action.isChecked(): #se activo
            conf.set_clipboard_active(True)
            self.clipboard_monitor.enable()
        else:
            conf.set_clipboard_active(False)
            self.clipboard_monitor.disable()


