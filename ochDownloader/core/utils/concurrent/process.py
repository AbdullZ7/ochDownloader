#-*- coding: utf-8 -*-

from multiprocessing import Process, Queue

from .base import FutureBase


class Future(FutureBase):

    def __init__(self, target, args=(), kwargs=None):
        super().__init__(Process, Queue, target=target, args=args)

        self._future._kwargs = kwargs or {}
        self._future.daemon = True

        self._future.start()