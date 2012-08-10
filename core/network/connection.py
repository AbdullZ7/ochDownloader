import urllib2
import urllib
import cookielib
import socket
import logging
logger = logging.getLogger(__name__)

#Local Libs
from core.conf_parser import conf
import core.cons as cons


class Request:
    def __init__(self):
        self.proxy = None #system proxy
        #self.__socket = socket.socket
        self.timeout = 20
        self.load_proxy()

    def get(self, url, data=None, **kwargs):
        if data: url += '?' + urllib.urlencode(data)
        return self.url_open(url, **kwargs)

    def post(self, url, data=None, **kwargs):
        data = data or {}
        return self.url_open(url, data=data, **kwargs)

    def url_open(self, url, cookie=None, data=None, range=(None, None), headers=None, timeout=None):
        timeout = timeout or self.timeout
        if cookie is None: cookie = cookielib.CookieJar()
        opener = self.build_opener(cookie)
        return opener.open(url, form=data, range=range, headers=headers, timeout=timeout)

    def build_opener(self, cookie):
        return URLOpen(cookie, self.proxy)

    def load_proxy(self):
        if conf.get_proxy_active():
            proxy_tup = conf.get_proxy()
            if proxy_tup is not None:
                ptype, ip, port = proxy_tup
                self.set_proxy(ptype, ip, port)

    def set_proxy(self, ptype, ip, port):
        if ptype == cons.PROXY_HTTP:
            self.proxy = {cons.PROXY_HTTP: ":".join((ip, str(port)))}
            #socket.socket = self.__socket
        #elif ptype in (cons.PROXY_SOCKS5, socks.PROXY_TYPE_SOCKS4):
            #self.__proxy = None
            #socks.setdefaultproxy(ptype, ip, port)
            #socket.socket = socks.socksocket

    def no_proxy(self, system=True):
        self.proxy = None if system else {}
        #socket.socket = self.__socket

request = Request()


class SmartRedirectHandler(urllib2.HTTPRedirectHandler): #subclass
    """
    Extend HTTPRedirectHandler for better error handling.
    """
    def http_error_302(self, req, fp, code, msg, headers):
        result = urllib2.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)
        #new attribute
        result.status = code #= 302, now we can call s.status
        return result


class URLOpen:
    """"""
    def __init__(self, cookie=None, proxy=None):
        """"""
        self.opener = urllib2.build_opener(SmartRedirectHandler(),
                                            urllib2.HTTPHandler(debuglevel=0),
                                            urllib2.HTTPSHandler(debuglevel=0),
                                            urllib2.HTTPCookieProcessor(cookie),
                                            urllib2.ProxyHandler(proxy))
    
    def open(self, url, form=None, headers=None, range=(None, None), referer=None, timeout=20):
        """"""
        url = urllib.quote_plus(url.strip(), safe="%/:=&?~#+!$,;'@()*[]") #fix url. replace spaces by plus sign and more. Solved on python 2.7+
        headers_ = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:10.0.1) Gecko/20100101 Firefox/10.0.1",
                    "Accept": "*/*",
                    "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
                    "Accept-Language": "en-US,en",
                    "Connection": "close"}
        range_start, range_end = range
        if headers:
            headers_.update(headers) #overwrite duplicated keys.
        if range_start is not None and range_end is not None:
            headers_["Range"] = "bytes={0}-{1}".format(range_start, range_end)
        elif range_start is not None:
            headers_["Range"] = "bytes={0}-".format(range_start)
        if referer is not None:
            headers_["Referer"] = referer
        if form is not None: #may be empty (ex: urllib.urlencode({})).
            headers_["Content-type"] = "application/x-www-form-urlencoded"
            form = urllib.urlencode(form)
        return self.opener.open(urllib2.Request(url, None, headers_), form, timeout=timeout)


class URLClose:
    """
    Enhanced closing.
    #Uso:
        #try:
        #    with URLClose(URLOpen().open(link_file)) as s:
        #        source = s
        #    except urllib2.URLError as e:
        #        err = e
        #        source = None #??
        #        print"except"
    """
    def __init__(self, thing, always_close=True):
        self.thing = thing
        self.always_close = always_close
    def __enter__(self): #"yield"
        return self.thing
    def __exit__(self, type, value, traceback):
        if traceback: #se lanzo una exception.
            self.thing.close()
            return False #re-lanzar exception.
        elif self.always_close:
            self.thing.close()
