import re
import logging
from contextlib import closing

from core import utils
from core.plugin.exceptions import StopParsing, ParsingError, LimitExceededError
from core.utils.http import request


logger = logging.getLogger(__name__)

BUFF_SZ = 1024 * 1024  # 1MB


class PluginBase:

    def __init__(self, download_item, wait_func):
        self.item = download_item
        self.wait_func = wait_func
        self.url = self.item.url  # shortcut

    def parse(self):
        raise NotImplementedError()

    def get_source(self, link, form=None):
        self.check_is_running()
        link = utils.url_unescape(link)
        self.item.url_source = link

        try:
            return request.url_open(link,
                                    cookie=self.item.cookie,
                                    data=form,
                                    req_range=(self.item.content_range, None))
        except request.RequestError as err:
            logger.debug(link)
            raise ParsingError(err)

    def get_page(self, link, form=None):
        self.check_is_running()
        link = utils.url_unescape(link)

        try:
            with closing(request.url_open(link, cookie=self.item.cookie, data=form)) as s:
                return str(s.read(BUFF_SZ), encoding="utf-8")
        except request.RequestError as err:
            logger.debug(link)
            raise ParsingError(err)

    def click(self, pattern, page, close=True):
        # find link and return source.
        m = self.get_match(pattern, page, "Link not found")
        link = m.group('link')

        if close:
            return self.get_page(link)
        else:
            return self.get_source(link)

    def get_match(self, pattern, page, err=None):
        self.check_is_running()
        err = err or "Pattern not found"

        for line in page.splitlines():
            m = re.search(pattern, line)
            if m is not None:
                return m

        raise ParsingError("%s, pattern: %s" % (err, pattern))

    def get_match_or_none(self, pattern, page, err=None, warning=True):
        try:
            return self.get_match(pattern, page, err)
        except ParsingError as err:
            if warning:
                logger.warning("%s %s" % (self.item.host, err))

    def countdown(self, pattern, page, limit, default):
        wait = default
        m = self.get_match_or_none(pattern, page)

        if m is not None:
            wait = int(m.group('count'))
            if wait >= limit:
                raise LimitExceededError("Limit Exceeded")

        self.wait_func(wait)

    def validate(self, err_list, page):
        for err in err_list:
            if self.get_match_or_none(err, page, warning=False) is not None:
                raise ParsingError(err)

    def check_is_running(self):
        if self.item.is_stopped():
            raise StopParsing("Stopped parsing")