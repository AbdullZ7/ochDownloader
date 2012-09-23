import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

import core.cons as cons


class LinkChecker:
    """"""
    def check(self, link):
        """"""
        name = "Unknown"
        size = 0
        status_msg = None
        link_status = cons.LINK_ERROR
        return link_status, name, size, status_msg
