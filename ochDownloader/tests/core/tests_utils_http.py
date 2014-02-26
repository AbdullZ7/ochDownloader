import logging
import time

import unittest
from unittest.mock import patch

from core.utils.http import rate_limit, request

logging.disable(logging.CRITICAL)


class UtilsHTTPRateLimitTest(unittest.TestCase):

    def setUp(self):
        self.bucket = rate_limit.TokenBucket()
    
    def tearDown(self):
        pass

    def test_set_rate(self):
        self.bucket.set_rate(1024)
        self.assertEqual(self.bucket.rate, 1024*1024)
        self.assertEqual(self.bucket.tokens, self.bucket.rate)

    def test_consume(self):
        self.assertEqual(self.bucket.consume(0), 0)
        self.assertEqual(self.bucket.consume(999), 0)
        self.bucket.set_rate(1024)
        self.assertEqual(self.bucket.consume(1024*1024), 0)
        self.assertLessEqual(self.bucket.consume(1024*1024*2), 2)
        self.assertLessEqual(self.bucket.consume(1024*1024*4), 6)
        self.assertLessEqual(self.bucket.consume(1024*1024*6), 12)
        self.bucket.set_rate(1024)
        #time.sleep(1)
        self.assertEqual(self.bucket.consume(1024*1024), 0)
        self.assertGreater(self.bucket.consume(1024*1024), 0)