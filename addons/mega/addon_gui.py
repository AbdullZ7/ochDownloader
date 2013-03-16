import logging
logger = logging.getLogger(__name__)

from core import events

from qt.addons import AddonCore

from .tab import Tab


class Addon(AddonCore):
    """"""
    def __init__(self, parent, *args, **kwargs):
        """"""
        AddonCore.__init__(self, parent)
        self.name = _("Mega decryptor")
        self.tab = Tab(parent)
        events.download_complete.connect(self.trigger)

    def set_menu_item(self):
        self.action = self.parent.menu.addAction(self.name, self.on_action)

    def on_action(self):
        # Open tab
        self.tab.setup_tab()
        self.tab.switch_tab()

    def trigger(self, download_item, *args, **kwargs):
        """"""
        # Open tab, start decrypting
        self.tab.setup_tab()
        self.tab.store(download_item)
