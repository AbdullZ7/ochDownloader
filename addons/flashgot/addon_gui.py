import threading

from qt.addons import AddonCore

import server


class Addon(AddonCore):
    """"""
    def __init__(self, parent, *args, **kwargs):
        """"""
        AddonCore.__init__(self)
        self.start_server()

    def set_menu_item(self):
        pass

    def start_server(self):
        th = threading.Thread(group=None, target=server.start, name=None)
        th.daemon = True
        th.start()