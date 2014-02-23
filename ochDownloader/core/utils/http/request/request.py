#-*- coding: utf-8 -*-

from http import cookiejar
from urllib.parse import urlencode, quote_plus
from urllib.error import URLError
import urllib.request

from . import const
from .exceptions import RequestError
from .response import Response

__all__ = ['get', 'post', 'url_open']


def get(url, data=None, **kwargs):
    if data:
        url += '?' + urlencode(data)
    return url_open(url, **kwargs)


def post(url, data=None, **kwargs):
    return url_open(url, data=data, **kwargs)


def url_open(url, data=None, timeout=20, cookie=None, proxy=None, req_range=None):
    if cookie is None:
        cookie = cookiejar.CookieJar()

    headers = const.HEADERS.copy()

    if req_range is not None:
        range_start, range_end = req_range

        if range_start is not None and range_end is not None:
            headers["Range"] = "bytes={0}-{1}".format(range_start, range_end)
        elif range_start is not None:
            headers["Range"] = "bytes={0}-".format(range_start)

    if data is not None:
        headers["Content-type"] = "application/x-www-form-urlencoded"
        data = urlencode(data)

    return _request(url, data=data, timeout=timeout, cookie=cookie, proxy=proxy, headers=headers)


def _request(url, data=None, timeout=20, cookie=None, proxy=None, headers=None, debuglevel=0):
    opener = urllib.request.build_opener(urllib.request.HTTPHandler(debuglevel=debuglevel),
                                         urllib.request.HTTPSHandler(debuglevel=debuglevel),
                                         urllib.request.HTTPCookieProcessor(cookie),
                                         urllib.request.ProxyHandler(proxy))
    #url = quote_plus(url.strip(), safe="%/:=&?~#+!$,;'@()*[]")
    request = urllib.request.Request(url, data)
    request.headers = headers or {}

    try:
        res = opener.open(request, timeout=timeout)
    except URLError as err:
        raise RequestError(err)

    return Response(res)