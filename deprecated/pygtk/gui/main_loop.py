import gobject

#import time
import Queue

from core.idle_queue import idle_loop


_loop = gobject.MainLoop(is_running=True)

def run():
    context = _loop.get_context()
    while _loop.is_running():
        try:
            callback = idle_loop.get_nowait()
            callback()
        except Queue.Empty:
            pass
        context.iteration(True)
        #time.sleep(.001) #+iteration(block=False) may be better?

def quit():
    _loop.quit()
