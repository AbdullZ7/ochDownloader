import threading
import logging
logger = logging.getLogger(__name__)

from core import idle_queue
from core.events import events

_thread_lock = threading.Lock()


class QualityChoice:
    """"""
    def __init__(self, f_name, choices_dict, wait_func):
        """"""
        self.f_name = f_name
        self.choices_dict = choices_dict
        self.wait_func = wait_func
        self.solution = None
        self.event = threading.Event()

    def set_solution(self, solution=None):
        self.solution = solution
        self.event.set()
        logger.debug(solution)

    def run_choice(self):
        #must be called from a child thread
        with _thread_lock: #one at the time please
            if not self.wait_func(): #dl stopped?
                self.make_choice()
            else: #reset solution.
                self.solution = None

    def make_choice(self):
        if idle_queue.register_event(self.event):
            events.quality_choice_dialog.emit(self.f_name, self.choices_dict, self.set_solution)
            self.event.wait()
            self.event.clear() #re-use.
            idle_queue.remove_event(self.event)
            if not self.solution:
                logger.warning("No choice selected") #should not be possible