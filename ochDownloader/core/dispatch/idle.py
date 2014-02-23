import threading
import logging
from queue import Queue

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_events = []
_shutdown = False
queue = Queue()


def add(func, *args, **kwargs):
    def wrapper():
        func(*args, **kwargs)

    queue.put(wrapper)


def add_and_wait(func, *args, **kwargs):
    event = threading.Event()

    def wrapper():
        try:
            func(*args, **kwargs)
        finally:
            event.set()

    if register_event(event):
        queue.put(wrapper)
        event.wait()  # wait for set()
        remove_event(event)


def set_events():  # call at exit
    global _shutdown

    with _lock:
        for event in _events:
            event.set()
        _shutdown = True


def register_event(event):
    global _shutdown

    with _lock:
        if _shutdown:
            return False
        else:
            _events.append(event)
            return True


def remove_event(event):
    with _lock:
        _events.remove(event)