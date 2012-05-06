import urllib2
import urllib
import socket
import logging
logger = logging.getLogger(__name__)

#Local Libs
import core.cons as cons


class Request:
    def __init__(self):
        self.__proxy = None #system proxy
        #self.__socket = socket.socket
        self.timeout = 20

    def get(self, url, cookie=None, headers=None, timeout=None, range=(None, None)):
        url_open = URLOpen(cookie, self.__proxy)
        return url_open.open(url, range=range, headers=headers, time_out=timeout)

    def post(self, url, form, cookie=None, headers=None, timeout=None):
        url_open = URLOpen(cookie, self.__proxy)
        return url_open.open(url, form=form, headers=headers, time_out=timeout)

    def set_proxy(self, ptype, ip, port):
        if ptype == cons.PROXY_HTTP:
            self.__proxy = {cons.PROXY_HTTP: ":".join((ip, str(port)))}
            #socket.socket = self.__socket
        #elif ptype in (cons.PROXY_SOCKS5, socks.PROXY_TYPE_SOCKS4):
            #self.__proxy = None
            #socks.setdefaultproxy(ptype, ip, port)
            #socket.socket = socks.socksocket

    def no_proxy(self, system=True):
        self.__proxy = None if system else {}
        #socket.socket = self.__socket

request = Request()


class SmartRedirectHandler(urllib2.HTTPRedirectHandler): #subclass
    """
    Extend HTTPRedirectHandler for better error handling.
    """
    def http_error_302(self, req, fp, code, msg, headers):
        result = urllib2.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)
        #new attribute
        result.status = code #= 302, we now can call (URLOpen.)open.status
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
    
    def open(self, url, form=None, data=None, headers=None, range=(None, None), referer=None, time_out=20):
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
        return self.opener.open(urllib2.Request(url, data, headers_), form, timeout=time_out)


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


