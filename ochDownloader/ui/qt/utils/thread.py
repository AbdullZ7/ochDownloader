import threading
import logging
from queue import Queue

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_queues = []
_shutdown = False


# Decorator
def run_in_main_thread(func, *args, **kwargs):
    q = Queue()

    def wrapper():
        result = func(*args, **kwargs)
        q.put(result, block=False)

    #post_in_main_thread(wrapper)

    if not _register_queue(q):
        return

    res = q.get()
    _remove_queue(q)
    return res


# at exit
def set_waiting_threads():
    global _shutdown

    with _lock:
        for q in _queues:
            q.put(None)

        _shutdown = True


def _register_queue(q):
    global _shutdown

    with _lock:
        if _shutdown:
            return False

        _queues.append(q)

    return True


def _remove_queue(q):
    with _lock:
        _queues.remove(q)