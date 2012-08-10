import logging #registro de errores, van a consola y al fichero de texto.
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

import core.cons as cons
from core.conf_parser import conf

from qt.addons import AddonCore
from clipboard_gui import Clipboard


class Addon(AddonCore):
    """"""
    def __init__(self, parent, *args, **kwargs):
        """"""
        AddonCore.__init__(self)
        self.event_id = None
        self.clipboard_monitor = Clipboard(parent)
        self.parent = parent
        self.config = conf
    
    def set_menu_item(self):
        self.action = self.parent.menu.addAction(_("Clipboard watcher"), self.on_toggle) #can toggle
        self.action.setCheckable(True)
        if self.config.get_clipboard_active():
            self.action.setChecked(True)
            self.clipboard_monitor.enable()
    
    def on_toggle(self):
        if self.action.isChecked(): #se activo
            self.config.set_clipboard_active("True")
            self.clipboard_monitor.enable()
        else:
            self.config.set_clipboard_active("False")
            self.clipboard_monitor.disable()


