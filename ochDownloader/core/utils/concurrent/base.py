#-*- coding: utf-8 -*-

import functools


class FutureBase:

    def __init__(self, future, queue, target=None, args=(), kwargs=None):
        kwargs = kwargs or {}
        self._queue = queue(1)
        self._future = future(target=self._target_handler(target), args=args, kwargs=kwargs)

    def _target_handler(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
            except BaseException as err:
                # Python 3.3 stores the traceback into err
                self._queue.put(err, block=False)
            else:
                self._queue.put(result, block=False)

        return wrapper

    def done(self):
        return not self._future.is_alive()

    def result(self, wait=False):
        if wait:
            self._future.join()

        result = self._queue.get(block=False)

        if isinstance(result, BaseException):
            raise result
        else:
            return result