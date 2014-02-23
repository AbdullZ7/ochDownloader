from time import time
from threading import Lock


class TokenBucket:
    """
    An implementation of the token bucket algorithm.
    """
    def __init__(self):
        self.tokens = 0
        self.rate = 0
        self.last = time()
        self.lock = Lock()

    def set_rate(self, rate_kb):
        with self.lock:
            self.rate = rate_kb * 1024
            self.tokens = self.rate

    def consume(self, tokens):
        with self.lock:
            if not self.rate:
                return 0

            now = time()
            lapse = now - self.last
            self.last = now
            self.tokens += lapse * self.rate

            if self.tokens > self.rate:
                self.tokens = self.rate

            self.tokens -= tokens

            if self.tokens >= 0:
                return 0
            else:
                return -self.tokens / self.rate