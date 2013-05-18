import logging
logger = logging.getLogger(__name__)

import core.cons as cons

BASE_URL = "http://rapidgator.net"


class LinkChecker:
    """"""
    def check(self, link):
        """"""
        name = "Unknown"
        size = 0
        status_msg = None
        link_status = cons.LINK_ERROR
        return link_status, name, size, status_msg
