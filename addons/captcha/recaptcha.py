import threading
import logging
logger = logging.getLogger(__name__)

from core import idle_queue
from core import events
from core.network.connection import request

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
            events.captcha_dialog.emit(self.host, self.get_captcha, self.set_solution)
            self.event.wait()
            self.event.clear() #re-use.
            idle_queue.remove_event(self.event)
            if not self.solution:
                logger.warning("No captcha response")

    def get_captcha(self):
        """"""
        image_type = None
        image_data = None
        try:
            for line in request.get(self.captcha_link).readlines():
                if "challenge : " in line:
                    self.captcha_challenge = line.split("'")[1]
                    handle = request.get("http://www.google.com/recaptcha/api/image?c=%s" % self.captcha_challenge)
                    image_data = handle.read()
                    image_type = handle.info()["Content-Type"].split("/")[1]
                    break
        except Exception as err:
            logger.exception("%s :%s" % (self.captcha_link, err))
        return image_type, image_data
