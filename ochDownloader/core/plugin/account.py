import re
import logging
from http import cookiejar
from contextlib import closing

from .exceptions import StopParsing, ParsingError
from core import utils
from core.utils.http import request

logger = logging.getLogger(__name__)

BUFF_SZ = 1024 * 1024  # 1MB


class PluginAccountBase:
    # TODO: create base class
    """"""
    def __init__(self, username, password, wait_func=None):
        """"""
        self.username = username
        self.password = password
        self.wait_func = wait_func
        self.cookie = cookiejar.CookieJar()
        self.account_status = None

    def parse(self):
        raise NotImplementedError()

    def get_page(self, link, form=None):
        #return source code.
        if not self.is_running():
            return

        link = utils.url_unescape(link)
        try:
            with closing(request.url_open(link, cookie=self.cookie, data=form)) as s:
                return str(s.read(BUFF_SZ), encoding="utf-8")
        except request.RequestError as err:
            logger.debug(link)
            raise ParsingError(err)

    def get_match(self, pattern, page):
        if not self.is_running():
            return

        for line in page.splitlines():
            m = re.search(pattern, line)
            if m is not None:
                return m

        # if we got here, no match was found
        raise ParsingError("Pattern not found: %s" % pattern)

    def is_running(self):
        if self.wait_func is None or not self.wait_func():
            return True
        else:
            raise StopParsing("Stop Parsing")