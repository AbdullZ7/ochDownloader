import logging
logger = logging.getLogger(__name__)

from core import events

from qt.addons import AddonCore


class Addon(AddonCore):
    """"""
    def __init__(self, parent, *args, **kwargs):
        """"""
        AddonCore.__init__(self, parent)
        self.name = _("Mega decryptor")
        #self.unrar_gui = UnRARGUI(parent)
        events.download_complete.connect(self.trigger)

    def set_menu_item(self):
        self.action = self.parent.menu.addAction(self.name, self.on_action)

    def on_action(self):
        # Open tab
        pass

    def trigger(self, download_item, *args, **kwargs):
        """"""
        # Open tab, start decrypting
        pass
