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
        self.__tokens = 0
        self.fill_rate = 0
        self.timestamp = time() #0
        self.lock = Lock()

    def rate_limit(self, limit):
        """
        Change the bandwidth rate-limit.
        """
        self.fill_rate = float(limit * 1024)

    def consume(self, tokens): #tokens requeridos = cantidad de bites a leer.
        """
        Consume tokens from the bucket.
        with self.lock:
            tokens = max(tokens, self.tokens)
            expected_time = (tokens - self.tokens) / self.fill_rate
            if expected_time <= 0:
                self.__tokens -= tokens
        return max(0, expected_time)
            """
        with self.lock:
            self.calc_tokens() #calcular tokens.
            self.__tokens -= tokens #tokens disponibles - tokens requeridos
            if self.__tokens < 0: #si habia tokens disponibles suficientes no aniadir tiempo (time=0).
                time = abs(self.__tokens) / self.fill_rate #no hay tokens disponibles devolver tiempo de espera.
            else:
                time = 0
        return time

    #@property #getter
    def calc_tokens(self):
        """"""
        if self.__tokens < self.fill_rate: #self.capacity:
            now = time()
            delta = self.fill_rate * (now - self.timestamp)
            self.__tokens = min(self.fill_rate, self.__tokens + delta) #self._tokens = min(self.capacity, self._tokens + delta)
            self.timestamp = now
        return self.__tokens


if __name__ == '__main__':
    from time import sleep
    bucket = TokenBucket(80)
    print "tokens =", bucket.tokens
    consumed = bucket.consume(10)
    sleep(consumed)
