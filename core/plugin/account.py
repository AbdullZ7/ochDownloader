import re
import urllib2
import httplib
import socket
import cookielib
import logging
logger = logging.getLogger(__name__)

from core.network.connection import URLClose, request

BUFF_SZ = 1024 * 1024 #1MB


class StopParsing(Exception): pass
class ParsingError(Exception): pass


class PluginAccountBase:
    """"""
    def __init__(self, username, password, wait_func=None):
        """"""
        self.username = username
        self.password = password
        self.wait_func = wait_func
        self.cookie = cookielib.CookieJar()
        self.account_status = None

    def parse(self):
        raise NotImplementedError()

    def get_page(self, link, form=None):
        #return source code.
        if self.is_running():
            try:
                with URLClose(request.url_open(link, self.cookie, form)) as s:
                    return s.read(BUFF_SZ)
            except (urllib2.URLError, httplib.HTTPException, socket.error) as err:
                logger.debug(link)
                raise ParsingError(err)

    def get_match(self, pattern, page):
        if self.is_running():
            for line in page.splitlines():
                m = re.search(pattern, line)
                if m is not None:
                    return m
        # if we got here, no match was found
        raise ParsingError("Pattern not found: %s" % pattern)

    def is_running(self):
        if self.wait_func is not None and not self.wait_func():
            return True
        else:
            raise StopParsing("Stop Parsing")


if __name__ == "__main__":
    pass