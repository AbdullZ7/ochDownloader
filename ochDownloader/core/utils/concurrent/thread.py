#-*- coding: utf-8 -*-

from queue import Queue
from threading import Thread

from .base import FutureBase


class Future(FutureBase):

    def __init__(self, target, args=(), kwargs=None):
        super().__init__(Thread, Queue, target=target, args=args, kwargs=kwargs)

        self._future.start()