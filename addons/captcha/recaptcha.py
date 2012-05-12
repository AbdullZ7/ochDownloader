import threading
import logging
logger = logging.getLogger(__name__)

import core.cons as cons
import core.idle_queue as idle_queue
from core.events import events
from core.network.connection import request


class Recaptcha:
    """"""
    def __init__(self, service, url, wait_func):
        """"""
        self.service_name = service
        self.captcha_link = url
        self.wait_func = wait_func
        self.solution = None
        self.event = threading.Event()

    def set_solution(self, solution=None):
        self.solution = solution
        self.event.set()
        logger.debug(solution)

    def solve_captcha(self):
        """"""
        self.captcha_challenge = None
        if idle_queue.register_event(self.event):
            events.trigger_captcha_dialog(self.wait_func, self.service_name, self.get_captcha, self.set_solution)
            self.event.wait()
            self.event.clear() #re-use.
            idle_queue.remove_event(self.event)
            if not self.solution:
                logger.warning("No response for {0} event".format(cons.EVENT_CAPTCHA_DLG))
        return self.captcha_challenge, self.solution

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
        except Exception, e:
            logger.exception("%s :%s" % (self.captcha_link, e))
        return image_type, image_data
