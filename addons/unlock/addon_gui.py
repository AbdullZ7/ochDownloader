from core import events

from qt.addons import AddonCore
from qt import signals


class Addon(AddonCore):
    """"""
    def __init__(self, parent, *args, **kwargs):
        """"""
        AddonCore.__init__(self, parent)

    def set_menu_item(self):
        pass

    def show_unlock_dialog(self):
        pass