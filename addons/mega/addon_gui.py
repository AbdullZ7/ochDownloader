import logging
logger = logging.getLogger(__name__)

from core import events

from qt.addons import AddonCore

from .tab import Tab
from .manager import DecryptManager

HOST_MEGA = "mega"


class Addon(AddonCore):
    """"""
    def __init__(self, parent, *args, **kwargs):
        """"""
        AddonCore.__init__(self, parent)
        self.name = _("Mega decrypter")
        self.decrypt_manager = DecryptManager()
        self.tab = Tab(parent, self.decrypt_manager)
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
        if download_item.host == HOST_MEGA:
            self.decrypt_manager.add(download_item)

            self.tab.setup_tab()
            self.tab.store(download_item)
