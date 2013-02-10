import threading
import logging
logger = logging.getLogger(__name__)

from qt.addons import AddonCore

import server
import register


class Addon(AddonCore):
    """"""
    def __init__(self, parent, *args, **kwargs):
        """"""
        AddonCore.__init__(self, parent)
        register.register_app_path()
        register.register_client()
        register.register_och_uri_scheme()
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