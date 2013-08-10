from time import time
from threading import Lock


class TokenBucket:
    """
    An implementation of the token bucket algorithm.
    """
    def __init__(self):
        """
        __tokens is the total tokens in the bucket. fill_rate is the
        rate in tokens/second that the bucket will be refilled.
        """
        self._tokens = 0
        self.fill_rate = 0
        self.timestamp = time()
        self.lock = Lock()

    def rate_limit(self, limit):
        """
        Change the bandwidth rate-limit.
        """
        self.fill_rate = limit * 1024
        self._tokens = 0

    def consume(self, tokens):
        """
        Consume tokens from the bucket.
        """
        with self.lock:
            self.calc_tokens()
            self._tokens -= tokens
            if self._tokens < 0:
                time = abs(self._tokens) / self.fill_rate
            else:
                time = 0
        return time

    def calc_tokens(self):
        """"""
        if self._tokens < self.fill_rate:
            now = time()
            delta = self.fill_rate * (now - self.timestamp)
            self._tokens = min(self.fill_rate, self._tokens + delta)
            self.timestamp = now
        return self._tokens