import logging
logger = logging.getLogger(__name__)

from qt.addons import AddonCore

import register


class Addon(AddonCore):
    """"""
    def __init__(self, parent, *args, **kwargs):
        """"""
        AddonCore.__init__(self, parent)
        register.register_app_path()
        register.register_och_uri_scheme()

    def set_menu_item(self):
        pass