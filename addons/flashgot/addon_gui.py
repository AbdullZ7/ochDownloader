import threading
import logging
logger = logging.getLogger(__name__)

from core import misc

from qt.addons import AddonCore

import server


class Addon(AddonCore):
    """"""
    def __init__(self, parent, *args, **kwargs):
        """"""
        AddonCore.__init__(self, parent)
        misc.register_app_path()
        self.start_server()

    def set_menu_item(self):
        pass

    def starter(self):
        try:
            server.start()
        except Exception as err:
            logger.exception(err)

    def start_server(self):
        th = threading.Thread(group=None, target=self.starter, name=None)
        th.daemon = True
        th.start()