import threading
import logging
logger = logging.getLogger(__name__)

from core.dispatch import idle_queue
from core.network.connection import request

import signals


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