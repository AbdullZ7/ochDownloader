import logging
logger = logging.getLogger(__name__)

from qt.addons import AddonCore

from grabber_gui import GrabberDialog


class Addon(AddonCore):
    """"""
    def __init__(self, parent, *args, **kwargs):
        """"""
        AddonCore.__init__(self)
        self.name = _("Video grabber")
        self.parent = parent

    def set_menu_item(self):
        self.action = self.parent.menu.addAction(self.name, self.on_clicked)

    def on_clicked(self):
        GrabberDialog(self.parent)
