import re
import urllib, urllib2, httplib, socket
import cookielib
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

import misc
from network.connection import URLClose, request

BUFF_SZ = 1024 * 1024 #1MB


class CaptchaException(Exception): pass


class PluginsCore:
    """"""
    def __init__(self, link, content_range, wait_func, account_item):
        """"""
        self.link = link #host link
        self.dl_link = link #file ready to download link
        self.next_link = link #go to next link
        self.content_range = content_range
        self.wait_func = wait_func
        self.limit_exceeded = False
        self.username = None
        self.password = None
        if account_item is not None:
            self.username = account_item.username
            self.password = account_item.password
        self.err_msg = None
        self.source = None
        self.cookie = cookielib.CookieJar()

    def parse(self):
        raise NotImplementedError()

    def get_page(self, link, form=None, default=None, close=True):
        #return source code.
        if self.is_running():
            range = (None, None) if close else (self.content_range, None)
            try:
                with URLClose(request.url_open(link, self.cookie, form, range), close) as s:
                    if close:
                        return s.read(BUFF_SZ)
                    else:
                        self.dl_link = link
                        return s
            except (urllib2.URLError, httplib.HTTPException, socket.error, ValueError) as err:
                self.err_msg = err
                logger.warning(err)
                logger.debug(link)
        return default
    
    def click(self, pattern, page, close=True):
        #find link and return source.
        if self.is_running():
            m = self.get_match(pattern, page)
            if m is not None:
                link = m.group('link')
                #default = page if close else None
                return self.get_page(link, close=close)
        #not running or pattern not found
        if close:
            return page
    
    def recaptcha_post(self, pattern, page, challenge, response, extra_fields=None):
        #POST
        form_list = [("recaptcha_challenge_field", challenge), ("recaptcha_response_field", response)]
        if extra_fields:
            form_list.extend(extra_fields)
        page = self.get_page(self.next_link, form=form_list, default=page)
        m = self.get_match(pattern, page)
        return (m, page)
    
    def recaptcha(self, pattern, page, extra_fields=None):
        #find catpcha and prompt captcha window
        #return source
        from addons.captcha.recaptcha import Recaptcha

        if self.is_running():
            try:
                m = self.get_match(pattern, page)
                if m is not None:
                    link = "http://www.google.com/recaptcha/api/challenge?k=%s" % m.group('key')
                    for retry in range(3):
                          c = Recaptcha(misc.get_host(self.link), link, self.wait_func)
                          c.run_captcha()
                          if c.solution is not None:
                             m, page = self.recaptcha_post(pattern, page, c.captcha_challenge, c.solution, extra_fields)
                             if not self.is_running() or m is None:
                                  return page
                          else:
                              raise CaptchaException("No response from the user")
                    raise CaptchaException("Captcha, max retries reached")
                else:
                    return page
            except CaptchaException as err:
                self.err_msg = err
                logger.debug(err)
        return page
    
    def get_match(self, pattern, page, warning=True):
        #TODO: re.search does not releases the GIL. Searching line by line is wiser.
        if self.is_running():
            m = re.search(pattern, page, re.S)
            if warning and m is None:
                logger.warning("Pattern not found: %s" % pattern)
            return m
        return None
    
    def countdown(self, pattern, page, limit, default):
        if self.is_running():
            m = self.get_match(pattern, page)
            if m is not None:
                wait = int(m.group('count'))
                if wait >= limit:
                    self.limit_exceeded = True
                    self.err_msg = "Limit Exceeded"
                    logger.warning(self.err_msg)
                else:
                    self.wait_func(wait)
            else:
                self.wait_func(default)

    def validate(self, err_list, page):
        if self.is_running():
            for err in err_list:
                if self.get_match(err, page, False) is not None:
                    self.err_msg = err
                    logger.warning(err)

    def is_running(self):
        if not self.wait_func() and not self.limit_exceeded and self.err_msg is None:
            return True
        return False
    

if __name__ == "__main__":
    pass