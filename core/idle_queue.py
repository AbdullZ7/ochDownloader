import threading
import Queue
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

import core.cons as cons


#thread safety
_thread_lock = threading.RLock()
_event_list = []
_block = False
idle_loop = Queue.Queue()

def idle_add(func, *args, **kwargs):
    def idle():
        func(*args, **kwargs)
        return False
    idle_loop.put(idle)

def idle_add_and_wait(func, *args, **kwargs):
    event = threading.Event()
    def idle():
        try:
            func(*args, **kwargs)
            return False
        finally:
            event.set()
    with _thread_lock:
        _event_list.append(event)
    if not _block:
        #gobject.idle_add(idle)
        idle_loop.put(idle)
        event.wait() #wait for set().
    with _thread_lock:
        _event_list.remove(event)

def set_events(): #execute at exit.
    logger.debug("Setting pending events.")
    _block = True
    with _thread_lock:
        for event in _event_list:
            event.set()

def register_event(event):
    with _thread_lock:
        _event_list.append(event)
    if not _block:
        return True
    return False

def remove_event(event):
    try:
        with _thread_lock:
            _event_list.remove(event)
    except ValueError:
        pass


if __name__ == "__main__":
    def some():
        print "some"
    idle_add(some, priority=0)
    try:
        _, callback = idle_loop.get_nowait()
        callback()
    except Queue.Empty as err:
        print err

