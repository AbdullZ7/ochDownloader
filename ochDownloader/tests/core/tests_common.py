import logging

import unittest
from unittest.mock import patch, Mock

from core import cons
from core.common.item import uid, get_host_from_url

logging.disable(logging.CRITICAL)


class CommonItemTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_uid(self):
        self.assertEqual(uid(), "1")
        self.assertEqual(uid(), "2")

    def test_get_host_from_url(self):
        self.assertIs(get_host_from_url("http://foo.com"), None)

        with patch.dict('core.common.item.services_dict', {'foo.com': None, }):
            self.assertEqual(get_host_from_url("http://foo.com"), 'foo.com')
            self.assertEqual(get_host_from_url("http://bar.foo.com"), 'foo.com')
            self.assertEqual(get_host_from_url("https://foo.com"), 'foo.com')
            self.assertEqual(get_host_from_url("https://bar.foo.com"), 'foo.com')