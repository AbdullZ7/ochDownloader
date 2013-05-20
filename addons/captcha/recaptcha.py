import threading
import logging
logger = logging.getLogger(__name__)

from core.dispatch import idle_queue
from core.network.connection import request
from core.plugin.base import PluginBase, ParsingError

import signals

CAPTCHA_MAX_RETRIES = 3
_thread_lock = threading.Lock()


class Recaptcha:
    """"""
    def __init__(self, host, url, wait_func):
        """"""
        self.host = host
        self.captcha_link = url
        self.wait_func = wait_func
        self.solution = None
        self.event = threading.Event()

    def set_solution(self, solution=None):
        self.solution = solution
        self.event.set()
        logger.debug(solution)

    def run_captcha(self):
        with _thread_lock: #one at the time please
            if not self.wait_func(): #dl stopped?
                self.solve_captcha()
            else: #reset solution.
                self.solution = None

    def solve_captcha(self):
        """"""
        self.captcha_challenge = None
        if idle_queue.register_event(self.event):
            challenge = Challenge(self.captcha_link)
            signals.captcha_dialog.emit(self.host, challenge, self.set_solution)
            self.event.wait()
            self.event.clear() #re-use.
            idle_queue.remove_event(self.event)
            self.captcha_challenge = challenge.captcha_challenge
            if not self.solution:
                logger.warning("No captcha response")


class Challenge:
    def __init__(self, url):
        self.captcha_link = url

    def request(self):
        self.captcha_challenge = None
        self.image_data = None
        try:
            for line in request.get(self.captcha_link).readlines():
                if "challenge : " in line:
                    self.captcha_challenge = line.split("'")[1]
                    handle = request.get("http://www.google.com/recaptcha/api/image?c=%s" % self.captcha_challenge)
                    self.image_data = handle.read()
                    #self.image_type = handle.info()["Content-Type"].split("/")[1]
                    break
        except Exception as err:
            logger.exception("%s :%s" % (self.captcha_link, err))


class PluginRecaptcha(PluginBase):
    def __init__(self, *args, **kwargs):
        PluginBase.__init__(self, *args, **kwargs)
        self.recaptcha_post_link = self.link
        self.recaptcha_challenge_field = "recaptcha_challenge_field"
        self.recaptcha_response_field = "recaptcha_response_field"

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
                c = Recaptcha(self.host, link, self.wait_func)
                c.run_captcha()
                if c.solution is not None:
                    page = self.recaptcha_post(pattern, page, c.captcha_challenge, c.solution, extra_fields)
                    if self.recaptcha_success(pattern, page) or not self.is_running():
                        return page
                else:
                    raise ParsingError("Captcha, no response from the user")
            raise ParsingError("Captcha, max retries reached")
        else:
            return page