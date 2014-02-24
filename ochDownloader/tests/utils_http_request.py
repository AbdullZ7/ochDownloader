import logging
import urllib.request
from io import BytesIO
from urllib.parse import urlencode
from http import cookiejar

import unittest
from unittest.mock import patch

from core.utils.http.request import request, const

logging.disable(logging.CRITICAL)


class UtilsHTTPRequestTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_request(self):
        with patch.object(urllib.request, 'Request') as Request:
            with patch.object(urllib.request.OpenerDirector, 'open') as open:
                url = "http://foo.bar"
                data = urlencode({"Foo": "bar", })
                request._request(url, data=data, headers={"Foo-Header": "bar", }, timeout=1)
                Request.assert_called_with(url, data)
                # fix: test the open and headers

    def test_url_open(self):
        with patch.object(request, '_request') as _request:
            url = "http://foo.bar"
            data = {"field1": "value1", }
            cookie = cookiejar.CookieJar()
            proxy = {"http": "http://localhost:8080", }
            req_range = (0, 100)
            request.url_open(url, data=data, timeout=1, cookie=cookie, proxy=proxy, req_range=req_range)
            # assert
            headers = const.HEADERS.copy()
            headers.update({
                'Range': 'bytes=0-100',
                'Content-type': 'application/x-www-form-urlencoded'
            })
            data = urlencode(data)
            _request.assert_called_with(url, data=data, timeout=1, cookie=cookie, proxy=proxy, headers=headers)

    def test_get(self):
        with patch.object(request, 'url_open') as url_open:
            url = "http://foo.bar"
            data = {"foo": 'bar', }
            request.get("http://foo.bar", data=data, foo='bar')
            url_open.assert_called_with(url + '?foo=bar', foo='bar')

    def test_post(self):
        with patch.object(request, 'url_open') as url_open:
            url = "http://foo.bar"
            data = {"foo": 'bar', }
            request.post("http://foo.bar", data=data, foo='bar')
            url_open.assert_called_with(url, data=data, foo='bar')


class MockResponse(BytesIO):

    def info(self):
        return {}


class UtilsHTTPResponseTest(unittest.TestCase):

    def setUp(self):
        fp = MockResponse()
        fp.write(b'foo\nbar')
        fp.seek(0)
        self.response = request.Response(fp)

    def tearDown(self):
        pass

    def test_readlines(self):
        self.assertEqual([l for l in self.response.readlines()], [b'foo\n', b'bar'])
        self.response.close()
        self.assertRaises(request.RequestError, lambda: [l for l in self.response.readlines()])

    def test_read(self):
        self.assertEqual(self.response.read(), b'foo\nbar')
        self.response.res.seek(0)
        self.assertEqual(self.response.read(1), b'f')
        self.response.close()
        self.assertRaises(request.RequestError, self.response.read)

    def test_close(self):
        self.assertFalse(self.response.res.closed)
        self.response.close()
        self.assertTrue(self.response.res.closed)
        # calling close multiple times should do nothing
        self.response.close()