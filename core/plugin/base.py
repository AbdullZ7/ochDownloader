import re
import urllib2
import httplib
import socket
import cookielib
import logging
logger = logging.getLogger(__name__)

try:
    from addons.captcha.recaptcha import Recaptcha
except ImportError as err:
    logger.warning(err)
    Recaptcha = None

from core import utils
from core.network.connection import URLClose, request

BUFF_SZ = 1024 * 1024 #1MB
CAPTCHA_MAX_RETRIES = 3


class CaptchaException(Exception): pass
class StopParsing(Exception): pass
class ParsingError(Exception): pass
class LimitExceededError(Exception): pass


class PluginBase:
    """"""
    def __init__(self, link, content_range, wait_func, cookie, video_quality):
        """"""
        self.link = link # host link
        self.dl_link = link # file ready to download link
        self.content_range = content_range
        self.wait_func = wait_func
        self.cookie = cookie or cookielib.CookieJar() # if empty or None do not use it
        self.video_quality = video_quality
        self.source = None
        self.save_as = None # file name for videos

        # recaptcha
        self.recaptcha_post_link = link
        self.recaptcha_challenge_field = "recaptcha_challenge_field"
        self.recaptcha_response_field = "recaptcha_response_field"

    def parse(self):
        raise NotImplementedError()

    def get_page(self, link, form=None, close=True):
        #return source code.
        if self.is_running():
            link = utils.url_unescape(link)
            range = (None, None) if close else (self.content_range, None)
            try:
                with URLClose(request.url_open(link, self.cookie, form, range), close) as s:
                    if close:
                        return s.read(BUFF_SZ)
                    else:
                        self.dl_link = link
                        return s
            except (urllib2.URLError, httplib.HTTPException, socket.error) as err:
                logger.debug(link)
                raise ParsingError(err)

    def click(self, pattern, page, close=True):
        #find link and return source.
        m = self.get_match(pattern, page, "Link not found")
        link = m.group('link')
        return self.get_page(link, close=close)

    def recaptcha_post(self, pattern, page, challenge, response, extra_fields=None):
        #POST
        form_list = [(self.recaptcha_challenge_field, challenge), (self.recaptcha_response_field, response)]
        if extra_fields:
            form_list.extend(extra_fields)
        page = self.get_page(self.recaptcha_post_link, form=form_list)
        return page

    def recaptcha_success(self, pattern, page):
        m = self.get_match_or_none(pattern, page, warning=False)
        if m is None:
            return True
        else:
            return False

    def recaptcha(self, pattern, page, extra_fields=None):
        if Recaptcha is None:
            return page
        m = self.get_match_or_none(pattern, page, "Recaptcha not found")
        if m is not None:
            link = "http://www.google.com/recaptcha/api/challenge?k=%s" % m.group('key')
            for retry in range(CAPTCHA_MAX_RETRIES):
                c = Recaptcha(utils.get_host(self.link), link, self.wait_func)
                c.run_captcha()
                if c.solution is not None:
                    page = self.recaptcha_post(pattern, page, c.captcha_challenge, c.solution, extra_fields)
                    if self.recaptcha_success(pattern, page) or not self.is_running():
                        return page
                else:
                    raise CaptchaException("Captcha, no response from the user")
            raise CaptchaException("Captcha, max retries reached")
        else:
            return page

    def get_match(self, pattern, page, err=None):
        if self.is_running():
            for line in page.splitlines():
                m = re.search(pattern, line)
                if m is not None:
                    return m
        # if we got here, no match was found
        err = err or "Pattern not found"
        raise ParsingError("%s, pattern: %s" % (err, pattern))

    def get_match_or_none(self, pattern, page, err=None, warning=True):
        try:
            return self.get_match(pattern, page, err)
        except ParsingError as err:
            if warning:
                logger.warning("%s %s" % (utils.get_host(self.link), err))
            return

    def countdown(self, pattern, page, limit, default):
        m = self.get_match_or_none(pattern, page)
        if m is not None:
            wait = int(m.group('count'))
            if wait >= limit:
                raise LimitExceededError("Limit Exceeded")
            else:
                self.wait_func(wait)
        else:
            self.wait_func(default)

    def validate(self, err_list, page):
        for err in err_list:
            if self.get_match_or_none(err, page, warning=False) is not None:
                raise ParsingError(err)

    def is_running(self):
        if not self.wait_func():
            return True
        else:
            raise StopParsing("Stop Parsing")


if __name__ == "__main__":
    pass