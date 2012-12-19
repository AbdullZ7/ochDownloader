from core import events

from qt.addons import AddonCore
from qt import signals

from unlock_gui import UnLockDialog


class Addon(AddonCore):
    """"""
    def __init__(self, parent, *args, **kwargs):
        """"""
        AddonCore.__init__(self, parent)
        signals.window_hide.connect(self.show_unlock_dialog)

    def set_menu_item(self):
        pass

    def show_unlock_dialog(self):
        dialog = UnLockDialog(self.parent)
        print dialog.entry_input.text()